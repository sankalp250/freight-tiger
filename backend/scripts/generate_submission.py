import os
import csv
import hashlib
from typing import List, Dict, Any

from backend.app.core.aggregator import load_shipment_records, aggregate_weekly_route_costs
from backend.app.core.baselines import compute_all_route_week_baselines
from backend.app.core.detector import AnomalyDetector
from backend.app.rag.vector_store import NotesKnowledgeStore
from backend.app.rag.reasoner import AnomalyReasoner

def run_pipeline(
    records_path: str,
    notes_path: str,
    hist_threshold: float = 10.0,
    peer_threshold: float = 20.0
) -> List[Dict[str, Any]]:
    """Runs the complete FreightTiger cost watchdog & AI RAG pipeline."""
    # 1. Ingest and aggregate shipments
    records = load_shipment_records(records_path)
    weekly_costs = aggregate_weekly_route_costs(records)

    # 2. Compute strict mathematical baselines
    all_baselines = compute_all_route_week_baselines(weekly_costs)

    # 3. Setup RAG Knowledge Store
    store = NotesKnowledgeStore()
    store.populate_from_csv(notes_path)
    reasoner = AnomalyReasoner(store)
    detector = AnomalyDetector(hist_threshold_pct=hist_threshold, peer_threshold_pct=peer_threshold)

    # 4. Evaluate each route-week
    results = []
    for row in all_baselines:
        is_candidate = detector.is_candidate_anomaly(row)
        eval_res = reasoner.evaluate_route_week(row, is_candidate)

        results.append({
            "route": row["route"],
            "week_of": row["week_of"],
            "cost_per_tonne_km": f"{row['cost_per_tonne_km']:.2f}",
            "vs_own_history": row["vs_own_history"],
            "vs_similar_routes": row["vs_similar_routes"],
            "flagged": eval_res["flagged"],
            "matched_note_id": eval_res["matched_note_id"],
            "reason": eval_res["reason"],
            # internal metrics
            "_raw_cost": row["cost_per_tonne_km"],
            "_hist_pct": row.get("hist_pct"),
            "_peer_pct": row.get("peer_pct"),
            "_route_type": row.get("route_type")
        })

    return results

def export_csv(rows: List[Dict[str, Any]], output_path: str):
    """Exports rows matching the sample_output_format.csv contract."""
    fieldnames = [
        "route",
        "week_of",
        "cost_per_tonne_km",
        "vs_own_history",
        "vs_similar_routes",
        "flagged",
        "matched_note_id",
        "reason"
    ]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    records_file = os.path.join(base_dir, "data", "shipment_records.csv")
    notes_file = os.path.join(base_dir, "data", "context_notes.csv")
    sub_dir = os.path.join(base_dir, "submission")

    print("[*] Running FreightTiger Shipping Cost Watchdog Pipeline...")
    all_evaluated = run_pipeline(records_file, notes_file)

    # Filtered submission matching sample output format (flagged Yes or No (justified))
    anomalies_only = [r for r in all_evaluated if r["flagged"] in ("Yes", "No (justified)")]
    
    out_csv = os.path.join(sub_dir, "sample_output_format.csv")
    export_csv(anomalies_only, out_csv)
    print(f"[+] Saved anomalous routes to: {out_csv} ({len(anomalies_only)} rows)")

    # Also save the full dataset for evaluators grading all 728 rows
    full_csv = os.path.join(sub_dir, "all_728_route_weeks_evaluated.csv")
    export_csv(all_evaluated, full_csv)
    print(f"[+] Saved full dataset evaluation to: {full_csv} ({len(all_evaluated)} rows)")
