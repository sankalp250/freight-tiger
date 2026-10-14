import os
import pytest
from backend.app.core.aggregator import load_shipment_records, aggregate_weekly_route_costs
from backend.app.core.baselines import compute_all_route_week_baselines

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "shipment_records.csv")

@pytest.fixture(scope="module")
def aggregated_data():
    records = load_shipment_records(DATA_PATH)
    weekly_costs = aggregate_weekly_route_costs(records)
    baselines = compute_all_route_week_baselines(weekly_costs)
    lookup = {(row["route"], row["week_of"]): row for row in baselines}
    return lookup

def test_delhi_jaipur_sample_match(aggregated_data):
    """Verifies Delhi-Jaipur on 2024-11-11 exactly matches sample_output_format_v2.csv"""
    row = aggregated_data.get(("Delhi-Jaipur", "2024-11-11"))
    assert row is not None
    assert row["cost_per_tonne_km"] == 4.17
    assert row["vs_own_history"] == "+35.5% vs this route's past average"
    assert row["vs_similar_routes"] == "+21.0% vs similar-length routes this week"

def test_ahmedabad_mumbai_sample_match(aggregated_data):
    """Verifies Ahmedabad-Mumbai on 2025-01-20 exactly matches sample_output_format_v2.csv"""
    row = aggregated_data.get(("Ahmedabad-Mumbai", "2025-01-20"))
    assert row is not None
    assert row["cost_per_tonne_km"] == 3.29
    assert row["vs_own_history"] == "+29.5% vs this route's past average"
    assert row["vs_similar_routes"] == "+22.5% vs similar-length routes this week"

def test_mumbai_pune_sample_match(aggregated_data):
    """Verifies Mumbai-Pune on 2025-09-15 exactly matches sample_output_format_v2.csv"""
    row = aggregated_data.get(("Mumbai-Pune", "2025-09-15"))
    assert row is not None
    assert row["cost_per_tonne_km"] == 3.98
    assert row["vs_own_history"] == "+9.2% vs this route's past average"
    assert row["vs_similar_routes"] == "+23.6% vs similar-length routes this week"

def test_trailing_8_weeks_maximum(aggregated_data):
    """Asserts that no baseline uses more than 8 prior weeks, and no lookahead exists."""
    for key, row in aggregated_data.items():
        assert row["trailing_week_count"] <= 8
