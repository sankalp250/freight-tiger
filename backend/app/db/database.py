import os
import sqlite3
from typing import List, Dict, Any, Tuple
from backend.app.core.aggregator import load_shipment_records, aggregate_weekly_route_costs
from backend.app.core.baselines import compute_all_route_week_baselines
from backend.app.core.detector import AnomalyDetector
from backend.app.rag.vector_store import NotesKnowledgeStore
from backend.app.rag.reasoner import AnomalyReasoner
from backend.app.rag.assistant import FreightAssistant

class DatabaseManager:
    """
    Coordinates data ingestion, SQLite storage, RAG ChromaDB persistence,
    and fast in-memory query routing.
    """
    _instance = None

    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.data_dir = os.path.join(base_dir, "data")
        self.db_path = os.path.join(self.data_dir, "freighttiger.db")
        self.records_file = os.path.join(self.data_dir, "shipment_records.csv")
        self.notes_file = os.path.join(self.data_dir, "context_notes.csv")

        self.store = NotesKnowledgeStore()
        self.evaluated_records: List[Dict[str, Any]] = []
        self.assistant: FreightAssistant = None
        self.is_initialized = False

    @classmethod
    def get_instance(cls) -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = DatabaseManager()
        return cls._instance

    def initialize(self):
        if self.is_initialized:
            return

        print("[*] Initializing Database & RAG Knowledge Store...")
        # 1. Populate ChromaDB
        self.store.populate_from_csv(self.notes_file)

        # 2. Ingest shipments and compute baselines
        records = load_shipment_records(self.records_file)
        weekly_costs = aggregate_weekly_route_costs(records)
        baselines = compute_all_route_week_baselines(weekly_costs)

        # 3. Reason anomalies
        reasoner = AnomalyReasoner(self.store)
        detector = AnomalyDetector(hist_threshold_pct=10.0, peer_threshold_pct=20.0)

        results = []
        for row in baselines:
            is_cand = detector.is_candidate_anomaly(row)
            eval_res = reasoner.evaluate_route_week(row, is_cand)
            results.append({
                "route": row["route"],
                "origin": row["origin"],
                "destination": row["destination"],
                "route_type": row["route_type"],
                "week_of": row["week_of"],
                "cost_per_tonne_km": row["cost_per_tonne_km"],
                "total_cost": row["total_cost"],
                "total_tonne_km": row["total_tonne_km"],
                "shipment_count": row["shipment_count"],
                "hist_avg": row.get("hist_avg"),
                "hist_pct": row.get("hist_pct"),
                "vs_own_history": row["vs_own_history"],
                "peer_avg": row.get("peer_avg"),
                "peer_pct": row.get("peer_pct"),
                "vs_similar_routes": row["vs_similar_routes"],
                "flagged": eval_res["flagged"],
                "matched_note_id": eval_res["matched_note_id"],
                "reason": eval_res["reason"],
            })

        self.evaluated_records = results
        self.assistant = FreightAssistant(self.evaluated_records, self.store)
        self.raw_records_count = len(records)

        # 4. Save to SQLite for persistence
        self._init_sqlite(records, results)
        self.is_initialized = True
        print(f"[+] Initialized {len(results)} route-week records.")

    def _init_sqlite(self, raw_records, evaluated_records):
        os.makedirs(self.data_dir, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS shipments (
                shipment_id TEXT PRIMARY KEY,
                origin TEXT,
                destination TEXT,
                route_type TEXT,
                material TEXT,
                quantity_tonnes REAL,
                distance_km REAL,
                freight_cost_inr REAL,
                shipment_date TEXT,
                transporter TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route TEXT,
                origin TEXT,
                destination TEXT,
                route_type TEXT,
                week_of TEXT,
                cost_per_tonne_km REAL,
                vs_own_history TEXT,
                vs_similar_routes TEXT,
                flagged TEXT,
                matched_note_id TEXT,
                reason TEXT
            )
        """)

        # Fast insert
        cur.executemany("""
            INSERT OR REPLACE INTO shipments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (r.shipment_id, r.origin, r.destination, r.route_type, r.material,
             r.quantity_tonnes, r.distance_km, r.freight_cost_inr, r.shipment_date, r.transporter)
            for r in raw_records
        ])

        conn.commit()
        conn.close()
