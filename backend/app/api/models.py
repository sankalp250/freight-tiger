from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    matched_route: Optional[str] = None
    citations: List[str] = []
    anomalies_count: Optional[int] = 0

class CorridorSummary(BaseModel):
    route: str
    origin: str
    destination: str
    route_type: str
    avg_cost_per_tonne_km: float
    total_tonne_km: float
    total_freight_cost: float
    shipment_count: int
    unjustified_anomalies_count: int
    justified_anomalies_count: int

class OverviewSummary(BaseModel):
    total_shipments: int
    total_corridors: int
    total_weeks: int
    total_unjustified_anomalies: int
    total_justified_anomalies: int
    date_range: Dict[str, str]

class AnomalyItem(BaseModel):
    route: str
    week_of: str
    cost_per_tonne_km: float
    vs_own_history: str
    vs_similar_routes: str
    flagged: str
    matched_note_id: str
    reason: str
    route_type: Optional[str] = None
