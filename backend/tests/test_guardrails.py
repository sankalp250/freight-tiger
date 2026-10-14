import os
import pytest
from backend.app.rag.vector_store import NotesKnowledgeStore
from backend.app.rag.guardrail import AntiHallucinationGuardrail
from backend.app.rag.reasoner import AnomalyReasoner

NOTES_CSV = os.path.join(os.path.dirname(__file__), "..", "..", "data", "context_notes.csv")

@pytest.fixture(scope="module")
def reasoner():
    store = NotesKnowledgeStore()
    store.populate_from_csv(NOTES_CSV)
    return AnomalyReasoner(store)

def test_distractor_notes_rejected(reasoner):
    """
    Asserts that the 7 trap/distractor notes are NEVER accepted as valid justifications:
    N004 (toll on routes not in dataset)
    N005 (maintenance with no cost impact)
    N006 (stable demand, no disruptions)
    N007 (improved road condition)
    N008 (normal freight movement)
    N009 (repair complete, return to normal)
    N010 (costs absorbed without rate change)
    """
    guardrail = AntiHallucinationGuardrail()
    all_notes = reasoner.store.get_all_notes()
    distractor_ids = ["N004", "N005", "N006", "N007", "N008", "N009", "N010"]

    for note in all_notes:
        if note["note_id"] in distractor_ids:
            is_genuine, refutation = guardrail.check_causality_and_substance(note["note"])
            assert is_genuine is False, f"Distractor note {note['note_id']} was erroneously marked genuine: {refutation}"

def test_genuine_notes_accepted(reasoner):
    """
    Asserts that N001, N002, and N003 are marked genuine cost escalation drivers.
    """
    guardrail = AntiHallucinationGuardrail()
    all_notes = reasoner.store.get_all_notes()
    genuine_ids = ["N001", "N002", "N003"]

    for note in all_notes:
        if note["note_id"] in genuine_ids:
            is_genuine, reason = guardrail.check_causality_and_substance(note["note"])
            assert is_genuine is True, f"Genuine note {note['note_id']} failed causality check: {reason}"

def test_ahmedabad_mumbai_justification(reasoner):
    """
    Ahmedabad-Mumbai on 2025-01-20 should be justified by N002.
    """
    row = {"route": "Ahmedabad-Mumbai", "week_of": "2025-01-20"}
    res = reasoner.evaluate_route_week(row, is_candidate_anomaly=True)
    assert res["flagged"] == "No (justified)"
    assert res["matched_note_id"] == "N002"
    assert "festival" in res["reason"].lower()

def test_mumbai_pune_closest_distractor(reasoner):
    """
    Mumbai-Pune on 2025-09-15: closest note N006 on 2025-09-22 is a distractor.
    Must be flagged Yes, matched_note_id blank, citing N006 distractor refutation.
    """
    row = {"route": "Mumbai-Pune", "week_of": "2025-09-15"}
    res = reasoner.evaluate_route_week(row, is_candidate_anomaly=True)
    assert res["flagged"] == "Yes"
    assert res["matched_note_id"] == ""
    assert "N006" in res["reason"]
    assert "stable demand" in res["reason"].lower()

def test_delhi_jaipur_unexplained(reasoner):
    """
    Delhi-Jaipur on 2024-11-11: no note applies.
    Must be flagged Yes, matched_note_id blank, stating no matching note found.
    """
    row = {"route": "Delhi-Jaipur", "week_of": "2024-11-11"}
    res = reasoner.evaluate_route_week(row, is_candidate_anomaly=True)
    assert res["flagged"] == "Yes"
    assert res["matched_note_id"] == ""
    assert "no matching note" in res["reason"].lower()
