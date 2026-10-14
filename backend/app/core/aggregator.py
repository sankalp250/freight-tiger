import csv
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Tuple
from .models import ShipmentRecord, WeeklyRouteCost

def get_monday_of_week(date_str: str) -> str:
    """Returns the Monday date (YYYY-MM-DD) for any given ISO date string."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    monday = dt - timedelta(days=dt.weekday())
    return monday.strftime("%Y-%m-%d")

def load_shipment_records(csv_path: str) -> List[ShipmentRecord]:
    """Loads shipment records from a CSV file."""
    records = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                ShipmentRecord(
                    shipment_id=row["shipment_id"].strip(),
                    origin=row["origin"].strip(),
                    destination=row["destination"].strip(),
                    route_type=row["route_type"].strip(),
                    material=row.get("material", "").strip(),
                    quantity_tonnes=float(row["quantity_tonnes"]),
                    distance_km=float(row["distance_km"]),
                    freight_cost_inr=float(row["freight_cost_inr"]),
                    shipment_date=row["shipment_date"].strip(),
                    transporter=row.get("transporter", "").strip(),
                )
            )
    return records

def aggregate_weekly_route_costs(records: List[ShipmentRecord]) -> Dict[Tuple[str, str, str], WeeklyRouteCost]:
    """
    Groups shipment records by (route, route_type, week_of).
    Cost per tonne per km = total freight cost / (quantity carried in tonnes x distance travelled in km).
    Returns a dictionary keyed by (route, route_type, week_of).
    """
    grouped = defaultdict(list)
    for r in records:
        week_of = get_monday_of_week(r.shipment_date)
        key = (r.route, r.route_type, week_of)
        grouped[key].append(r)

    weekly_costs = {}
    for (route, route_type, week_of), items in grouped.items():
        total_cost = sum(item.freight_cost_inr for item in items)
        total_tonne_km = sum(item.tonne_km for item in items)
        cost_per_tonne_km = total_cost / total_tonne_km if total_tonne_km > 0 else 0.0

        origin, destination = route.split("-", 1)
        weekly_costs[(route, route_type, week_of)] = WeeklyRouteCost(
            route=route,
            origin=origin,
            destination=destination,
            route_type=route_type,
            week_of=week_of,
            total_cost=total_cost,
            total_tonne_km=total_tonne_km,
            shipment_count=len(items),
            cost_per_tonne_km=cost_per_tonne_km,
        )

    return weekly_costs
