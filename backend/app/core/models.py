from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class ShipmentRecord:
    shipment_id: str
    origin: str
    destination: str
    route_type: str  # Short, Medium, Long
    material: str
    quantity_tonnes: float
    distance_km: float
    freight_cost_inr: float
    shipment_date: str  # YYYY-MM-DD
    transporter: str

    @property
    def route(self) -> str:
        return f"{self.origin}-{self.destination}"

    @property
    def tonne_km(self) -> float:
        return self.quantity_tonnes * self.distance_km

@dataclass
class WeeklyRouteCost:
    route: str
    origin: str
    destination: str
    route_type: str
    week_of: str  # Monday YYYY-MM-DD
    total_cost: float
    total_tonne_km: float
    shipment_count: int
    cost_per_tonne_km: float

@dataclass
class RouteEvaluationResult:
    route: str
    week_of: str
    cost_per_tonne_km: float
    vs_own_history: str
    vs_similar_routes: str
    flagged: str  # 'Yes', 'No (justified)', 'No'
    matched_note_id: str
    reason: str
    hist_pct: Optional[float] = None
    peer_pct: Optional[float] = None
    hist_avg: Optional[float] = None
    peer_avg: Optional[float] = None
