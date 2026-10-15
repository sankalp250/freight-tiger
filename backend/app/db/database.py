import os
import sqlite3
from collections import defaultdict
from typing import List, Dict, Any, Tuple,Optional
from backend.app.core.aggregator import load_shipment_records, aggregate_weekly_route_costs
from backend.app.core.baselines import compute_all_route_week_baselines
from backend.app.core.detector import AnomalyDetector
from backend.app.rag.vector_store import NotesKnowledgeStore
from backend.app.rag.reasoner import AnomalyReasoner
from backend.app.rag.assistant import FreightAssistant
from backend.app.api.models import OverviewSummary, CorridorSummary, AnomalyItem

class DatabaseManager:
    """
    High-performance coordinator for data ingestion, SQLite storage,
    ChromaDB persistence, and ultra-fast in-memory cached query execution.
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
        self.raw_records_count: int = 0
        self.is_initialized: bool = False

        # In-memory pre-computed caches for sub-millisecond response latency
        self.summary_cache: Optional[OverviewSummary] = None
        self.corridors_cache: List[CorridorSummary] = []
        self.trends_cache: Dict[str, Dict[str, Any]] = {}
        self.anomalies_cache: Dict[str, List[AnomalyItem]] = {}

    @classmethod
    def get_instance(cls) -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = DatabaseManager()
        return cls._instance

    def initialize(self):
        if self.is_initialized:
            return

        print("[*] Initializing Database & Pre-Computing High-Speed Query Caches...")
        # 1. Ingest context notes into ChromaDB
        self.store.populate_from_csv(self.notes_file)

        # 2. Ingest raw shipments & compute strict mathematical baselines
        records = load_shipment_records(self.records_file)
        self.raw_records_count = len(records)
        weekly_costs = aggregate_weekly_route_costs(records)
        baselines = compute_all_route_week_baselines(weekly_costs)

        # 3. Anomaly detection & RAG reasoning
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

        # 4. Build in-memory caches
        self._build_caches()

        # 5. Persist to local SQLite
        self._init_sqlite(records)
        self.is_initialized = True
        print(f"[+] Initialized {len(results)} route-week records with sub-millisecond caches ready.")

    def _build_caches(self):
        """Pre-computes and caches API payloads to eliminate runtime recalculation."""
        routes = sorted(list(set(r["route"] for r in self.evaluated_records)))
        weeks = sorted(list(set(r["week_of"] for r in self.evaluated_records)))
        unjustified = sum(1 for r in self.evaluated_records if r["flagged"] == "Yes")
        justified = sum(1 for r in self.evaluated_records if r["flagged"] == "No (justified)")

        # Summary Cache
        self.summary_cache = OverviewSummary(
            total_shipments=self.raw_records_count,
            total_corridors=len(routes),
            total_weeks=len(weeks),
            total_unjustified_anomalies=unjustified,
            total_justified_anomalies=justified,
            date_range={"start": weeks[0], "end": weeks[-1]}
        )

        # Corridors Cache
        by_route = defaultdict(list)
        for r in self.evaluated_records:
            by_route[r["route"]].append(r)

        corridor_list = []
        for route, items in sorted(by_route.items()):
            total_cost = sum(i["total_cost"] for i in items)
            total_tkm = sum(i["total_tonne_km"] for i in items)
            avg_cost = total_cost / total_tkm if total_tkm > 0 else 0.0
            shipment_count = sum(i["shipment_count"] for i in items)
            unj = sum(1 for i in items if i["flagged"] == "Yes")
            jus = sum(1 for i in items if i["flagged"] == "No (justified)")

            corridor_list.append(CorridorSummary(
                route=route,
                origin=items[0]["origin"],
                destination=items[0]["destination"],
                route_type=items[0]["route_type"],
                avg_cost_per_tonne_km=round(avg_cost, 2),
                total_tonne_km=round(total_tkm, 2),
                total_freight_cost=round(total_cost, 2),
                shipment_count=shipment_count,
                unjustified_anomalies_count=unj,
                justified_anomalies_count=jus,
            ))
        self.corridors_cache = corridor_list

        # Trends Cache (Indexed by corridor)
        trends_map = {}
        for route, items in by_route.items():
            sorted_weeks = sorted(items, key=lambda x: x["week_of"])
            trends_map[route] = {
                "route": route,
                "route_type": sorted_weeks[0]["route_type"],
                "origin": sorted_weeks[0]["origin"],
                "destination": sorted_weeks[0]["destination"],
                "weeks": [
                    {
                        "week_of": r["week_of"],
                        "cost_per_tonne_km": r["cost_per_tonne_km"],
                        "hist_avg": round(r["hist_avg"], 2) if r["hist_avg"] else None,
                        "peer_avg": round(r["peer_avg"], 2) if r["peer_avg"] else None,
                        "hist_pct": round(r["hist_pct"], 1) if r["hist_pct"] else None,
                        "peer_pct": round(r["peer_pct"], 1) if r["peer_pct"] else None,
                        "flagged": r["flagged"],
                        "matched_note_id": r["matched_note_id"],
                        "reason": r["reason"]
                    }
                    for r in sorted_weeks
                ]
            }
        self.trends_cache = trends_map

        # Anomalies Cache
        all_anoms = [
            AnomalyItem(
                route=r["route"],
                week_of=r["week_of"],
                cost_per_tonne_km=r["cost_per_tonne_km"],
                vs_own_history=r["vs_own_history"],
                vs_similar_routes=r["vs_similar_routes"],
                flagged=r["flagged"],
                matched_note_id=r["matched_note_id"],
                reason=r["reason"],
                route_type=r["route_type"],
            )
            for r in self.evaluated_records
            if r["flagged"] in ("Yes", "No (justified)")
        ]
        self.anomalies_cache = {
            "all": all_anoms,
            "flagged": [a for a in all_anoms if a.flagged == "Yes"],
            "justified": [a for a in all_anoms if a.flagged == "No (justified)"],
        }

    def _init_sqlite(self, raw_records):
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
        cur.executemany("""
            INSERT OR REPLACE INTO shipments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (r.shipment_id, r.origin, r.destination, r.route_type, r.material,
             r.quantity_tonnes, r.distance_km, r.freight_cost_inr, r.shipment_date, r.transporter)
            for r in raw_records
        ])
        conn.commit()
        conn.close()
