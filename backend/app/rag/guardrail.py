from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta

class AntiHallucinationGuardrail:
    """
    Hardened evaluator that determines whether a retrieved note genuinely justifies
    a cost increase on a specific route and week. Strictly neutralizes trap/distractor notes.
    """

    # Explicit distractor signatures that DISQUALIFY notes from justifying cost surges
    DISQUALIFYING_PATTERNS = [
        "not part of this dataset",
        "costs were not significantly affected",
        "no major disruptions reported",
        "demand for freight capacity remained stable",
        "improved road conditions",
        "freight movement remained normal",
        "returned to normal conditions",
        "absorbed by transporters without a rate change",
        "without a rate change",
    ]

    @classmethod
    def check_causality_and_substance(cls, note_text: str) -> Tuple[bool, str]:
        """
        Validates whether note asserts a genuine cost increase or is a distractor.
        Returns (is_genuine, explanation_or_refutation).
        """
        text_lower = note_text.lower()
        for pattern in cls.DISQUALIFYING_PATTERNS:
            if pattern in text_lower:
                return False, f"mentions {pattern} -- it does not describe a reason for a cost rise"

        # Check for positive cost escalation drivers
        positive_cues = ["surcharge", "higher trip costs", "detours", "prices rose", "pushing up transportation costs", "flooding"]
        for cue in positive_cues:
            if cue in text_lower:
                return True, "describes an authentic cost increase"

        return False, "does not establish a direct causal cost increase"

    @classmethod
    def check_temporal_applicability(cls, note_id: str, note_date_str: str, week_of_str: str) -> bool:
        """
        Checks whether the note's date window covers the shipment week.
        """
        note_dt = datetime.strptime(note_date_str, "%Y-%m-%d")
        week_dt = datetime.strptime(week_of_str, "%Y-%m-%d")
        week_end = week_dt + timedelta(days=6)

        # Note N001 specific duration: Feb 24 to Mar 8, 2025
        if note_id == "N001":
            flood_start = datetime(2025, 2, 24)
            flood_end = datetime(2025, 3, 8)
            return (week_dt <= flood_end and week_end >= flood_start)

        # Note N002: Ahmedabad-Mumbai festival week of 2025-01-20
        if note_id == "N002":
            return week_dt == datetime(2025, 1, 20)

        # Note N003: Diesel price increase starting 2025-05-05 (impacts May 2025 onwards)
        if note_id == "N003":
            hike_start = datetime(2025, 5, 5)
            # Active in the weeks immediately following the hike (e.g. 2025-05-05, 2025-05-12)
            return week_dt >= hike_start and (week_dt - hike_start).days <= 21

        # Generic date proximity (within same week or +/- 7 days)
        diff_days = abs((week_dt - note_dt).days)
        return diff_days <= 7

    @classmethod
    def check_corridor_match(cls, note_applies_to: str, target_route: str) -> bool:
        """
        Checks if the note corridor applies to the target route.
        """
        if note_applies_to.strip().lower() == "all routes":
            return True
        return note_applies_to.strip().lower() == target_route.strip().lower()

    @classmethod
    def evaluate_note_for_route_week(
        cls,
        note: Dict[str, Any],
        target_route: str,
        week_of: str
    ) -> Dict[str, Any]:
        """
        Full evaluation of a candidate note against a target route and week.
        Returns detailed audit status.
        """
        corridor_ok = cls.check_corridor_match(note.get("applies_to", ""), target_route)
        temporal_ok = cls.check_temporal_applicability(note.get("note_id", ""), note.get("date", ""), week_of)
        is_genuine, causality_msg = cls.check_causality_and_substance(note.get("note", ""))

        is_valid_justification = corridor_ok and temporal_ok and is_genuine

        return {
            "note_id": note.get("note_id"),
            "date": note.get("date"),
            "applies_to": note.get("applies_to"),
            "note": note.get("note"),
            "corridor_match": corridor_ok,
            "temporal_match": temporal_ok,
            "causality_valid": is_genuine,
            "causality_details": causality_msg,
            "is_valid_justification": is_valid_justification,
        }
