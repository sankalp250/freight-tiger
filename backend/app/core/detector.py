from typing import Dict, Any

class AnomalyDetector:
    """
    Identifies cost surges where cost per tonne-km is rising out of the ordinary
    relative to trailing historical average or peer routes in that week.
    """
    def __init__(self, hist_threshold_pct: float = 10.0, peer_threshold_pct: float = 20.0):
        self.hist_threshold_pct = hist_threshold_pct
        self.peer_threshold_pct = peer_threshold_pct

    def is_candidate_anomaly(self, row: Dict[str, Any]) -> bool:
        """
        Determines if a route-week is an anomaly candidate that requires RAG investigation:
        1. Cost is rising vs. own history (hist_pct > 0)
        2. And exceeds either the historical surge threshold (>= 10%) OR peer threshold (>= 20%).
        """
        hist_pct = row.get("hist_pct")
        peer_pct = row.get("peer_pct")

        if hist_pct is None and peer_pct is None:
            return False

        # Strong historical surge (e.g., Delhi-Jaipur +35.5%, Ahmedabad-Mumbai +29.5%)
        if hist_pct is not None and hist_pct >= self.hist_threshold_pct:
            return True

        # Rising vs history while significantly higher than peers (e.g., Mumbai-Pune +9.2% hist, +23.6% peer)
        if hist_pct is not None and hist_pct > 0 and peer_pct is not None and peer_pct >= self.peer_threshold_pct:
            return True

        return False
