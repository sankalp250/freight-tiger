from typing import Dict, Tuple, List, Optional
from .models import WeeklyRouteCost

def compute_baselines_for_route_week(
    target_route: str,
    target_route_type: str,
    target_week: str,
    weekly_costs: Dict[Tuple[str, str, str], WeeklyRouteCost],
    all_sorted_weeks: List[str],
) -> Dict[str, any]:
    """
    Computes:
    1. vs. own history: trailing 8-week rolling average cost per tonne-km, strictly before current week.
       If fewer than 8 prior weeks exist, uses all prior weeks available.
    2. vs. similar routes: average cost per tonne-km in the same week across all other routes sharing the same route_type (excluding itself).
    """
    curr = weekly_costs.get((target_route, target_route_type, target_week))
    if not curr:
        return {}

    curr_cost = curr.cost_per_tonne_km

    # 1. Trailing 8 weeks strictly before target_week
    prior_weeks = [
        w for w in all_sorted_weeks
        if w < target_week and (target_route, target_route_type, w) in weekly_costs
    ]
    trailing_8 = prior_weeks[-8:]

    if trailing_8:
        hist_avg = sum(
            weekly_costs[(target_route, target_route_type, w)].cost_per_tonne_km
            for w in trailing_8
        ) / len(trailing_8)
        hist_pct = ((curr_cost - hist_avg) / hist_avg) * 100.0
        vs_own_history = f"{hist_pct:+.1f}% vs this route's past average"
    else:
        hist_avg = None
        hist_pct = None
        vs_own_history = "N/A (first available week, no prior history)"

    # 2. Peer routes in the same week with same route_type (excluding itself)
    peer_costs = [
        cost_obj.cost_per_tonne_km
        for (r, rt, w), cost_obj in weekly_costs.items()
        if w == target_week and rt == target_route_type and r != target_route
    ]

    if peer_costs:
        peer_avg = sum(peer_costs) / len(peer_costs)
        peer_pct = ((curr_cost - peer_avg) / peer_avg) * 100.0
        vs_similar_routes = f"{peer_pct:+.1f}% vs similar-length routes this week"
    else:
        peer_avg = None
        peer_pct = None
        vs_similar_routes = "N/A (no peer routes available this week)"

    return {
        "cost_per_tonne_km": round(curr_cost, 2),
        "exact_cost": curr_cost,
        "hist_avg": hist_avg,
        "hist_pct": hist_pct,
        "vs_own_history": vs_own_history,
        "peer_avg": peer_avg,
        "peer_pct": peer_pct,
        "vs_similar_routes": vs_similar_routes,
        "trailing_week_count": len(trailing_8),
        "peer_count": len(peer_costs),
    }

def compute_all_route_week_baselines(
    weekly_costs: Dict[Tuple[str, str, str], WeeklyRouteCost]
) -> List[Dict[str, any]]:
    """Computes baselines across all (route, route_type, week_of) sorted chronologically."""
    all_sorted_weeks = sorted(list(set(w for (_, _, w) in weekly_costs.keys())))
    sorted_keys = sorted(
        weekly_costs.keys(),
        key=lambda k: (k[2], k[0])  # Sort by week_of, then route
    )

    results = []
    for route, route_type, week_of in sorted_keys:
        cost_obj = weekly_costs[(route, route_type, week_of)]
        baselines = compute_baselines_for_route_week(
            route, route_type, week_of, weekly_costs, all_sorted_weeks
        )
        results.append({
            "route": route,
            "origin": cost_obj.origin,
            "destination": cost_obj.destination,
            "route_type": route_type,
            "week_of": week_of,
            "total_cost": cost_obj.total_cost,
            "total_tonne_km": cost_obj.total_tonne_km,
            "shipment_count": cost_obj.shipment_count,
            **baselines,
        })

    return results
