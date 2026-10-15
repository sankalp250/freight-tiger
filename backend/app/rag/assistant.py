import re
from typing import Dict, Any, List, Optional
from .llm_client import LLMClient

class FreightAssistant:
    """
    Conversational assistant answering plain-English questions grounded in calculated
    baselines, flagged anomalies, and verified context notes, powered by Gemini/Groq LLMs.
    """
    def __init__(self, evaluation_records: List[Dict[str, Any]], knowledge_store):
        self.records = evaluation_records
        self.store = knowledge_store
        self.routes = sorted(list(set(r["route"] for r in self.records)))
        self.llm = LLMClient()

    def _resolve_route_from_query(self, query: str) -> Optional[str]:
        """
        Intelligently resolves the target corridor from natural language queries,
        handling both full route mentions ('Delhi-Jaipur', 'Delhi to Jaipur')
        and single-city landmarks ('Jaipur', 'Pune', 'Bangalore').
        """
        q_lower = query.lower()

        # 1. Exact pair matching (e.g. "delhi" and "jaipur" anywhere in query)
        for r in self.routes:
            orig, dest = r.split("-")
            if (orig.lower() in q_lower and dest.lower() in q_lower) or r.lower() in q_lower:
                return r

        # 2. Unique destination/origin anchors
        unique_anchors = {
            "jaipur": "Delhi-Jaipur",
            "pune": "Mumbai-Pune",
            "bangalore": "Chennai-Bangalore",
            "bhubaneswar": "Kolkata-Bhubaneswar",
            "ahmedabad": "Ahmedabad-Mumbai",
        }
        for city, route in unique_anchors.items():
            if re.search(r'\b' + city + r'\b', q_lower):
                return route

        # 3. Common hub disambiguation
        if "kolkata" in q_lower:
            return "Kolkata-Bhubaneswar"
        if "chennai" in q_lower:
            return "Delhi-Chennai" if "delhi" in q_lower else "Chennai-Bangalore"
        if "mumbai" in q_lower:
            if "delhi" in q_lower:
                return "Mumbai-Delhi"
            if "pune" in q_lower:
                return "Mumbai-Pune"
            return "Ahmedabad-Mumbai"

        return None

    def answer_query(self, query: str) -> Dict[str, Any]:
        """
        Interprets natural language queries, gathers grounded context, and invokes
        Gemini 2.5 Flash / Groq to generate a verified, natural explanation.
        """
        q_lower = query.lower()

        # 1. Identify corridor
        matched_route = self._resolve_route_from_query(query)

        # 2. Identify if month/year is mentioned
        months = {
            "january": ["-01-"], "february": ["-02-"], "march": ["-03-"], "april": ["-04-"],
            "may": ["-05-"], "june": ["-06-"], "july": ["-07-"], "august": ["-08-"],
            "september": ["-09-"], "october": ["-10-"], "november": ["-11-"], "december": ["-12-"],
            "jan": ["-01-"], "feb": ["-02-"], "mar": ["-03-"], "apr": ["-04-"],
            "jun": ["-06-"], "jul": ["-07-"], "aug": ["-08-"], "sep": ["-09-"],
            "oct": ["-10-"], "nov": ["-11-"], "dec": ["-12-"]
        }
        matched_month_codes = []
        for m_name, codes in months.items():
            if re.search(r'\b' + m_name + r'\b', q_lower):
                matched_month_codes.extend(codes)

        # 3. Filter relevant records
        relevant = self.records
        if matched_route:
            relevant = [r for r in relevant if r["route"] == matched_route]

        if matched_month_codes:
            relevant = [r for r in relevant if any(code in r["week_of"] for code in matched_month_codes)]

        anomalies = [r for r in relevant if r["flagged"] in ("Yes", "No (justified)")]

        # 4. Context notes relevant to the corridor
        all_notes = self.store.get_all_notes()
        relevant_notes = [
            n for n in all_notes
            if matched_route is None or n["applies_to"] == "All Routes" or n["applies_to"] == matched_route
        ]

        # 5. Build Grounded Context for the LLM
        context_lines = []
        citations = []
        for a in anomalies[:8]:
            note_id = a.get("matched_note_id", "")
            if note_id:
                citations.append(note_id)
            context_lines.append(
                f"- Route: {a['route']}, Week: {a['week_of']}, Cost: ₹{a['cost_per_tonne_km']}/t-km, "
                f"History Comparison: {a['vs_own_history']}, Peer Comparison: {a['vs_similar_routes']}, "
                f"Verdict: {a['flagged']}, Matched Note: {note_id or 'None'}, Finding: {a['reason']}"
            )

        notes_summary = "\n".join([
            f"- Note {n['note_id']} ({n['date']}, Applies to: {n['applies_to']}): {n['note']}"
            for n in relevant_notes
        ])

        system_instruction = (
            "You are the FreightTiger Shipping Cost Watchdog AI Assistant. "
            "Your job is to explain freight shipping cost changes, baselines, and anomalies across Indian trucking corridors. "
            "GROUND RULES: "
            "1. ONLY state a cost rise is justified if supported by a genuine disruption note (e.g. N001 floods, N002 festival surcharge, N003 diesel hike). "
            "2. If a note states costs were not affected (N005), routes are not in dataset (N004), demand was stable (N006), or costs were absorbed without rate changes (N010), do NOT justify the cost rise. State clearly that the note does not justify a rate increase. "
            "3. If no note matches, declare the cost rise unexplained and flagged for human review. "
            "4. Keep your answer professional, concise (2-3 paragraphs max), and grounded in the data."
        )

        prompt = f"""
User Query: "{query}"

Monitored Route: {matched_route or 'All Corridors'}
Relevant Evaluated Spikes / Anomalies in this window:
{chr(10).join(context_lines) if context_lines else 'No abnormal cost spikes found in this exact corridor/window.'}

Available Context Notes from Knowledge Base:
{notes_summary}

Please answer the user's question clearly in plain English, citing exact notes and dates if justified, or explaining why the cost rise is flagged as unexplained.
"""

        # Call live LLM (Gemini or Groq fallback)
        llm_res = self.llm.generate(prompt, system_instruction)

        if llm_res.get("success"):
            return {
                "answer": llm_res["text"],
                "matched_route": matched_route,
                "anomalies_count": len(anomalies),
                "citations": list(set(citations)),
                "provider": llm_res.get("provider", "Gemini")
            }

        # Deterministic Grounded Fallback if LLM is unavailable
        if anomalies:
            explanations = [f"• Week {a['week_of']} ({a['route']}): {a['reason']}" for a in anomalies[:3]]
            fallback_text = (
                f"Freight Watchdog evaluated {len(anomalies)} cost surges for {matched_route or 'this corridor'}:\n\n"
                + "\n\n".join(explanations)
            )
        else:
            fallback_text = f"For {matched_route or 'the queried corridor'}, shipping costs remained within normal historical and peer boundaries. No unexplained rate spikes were detected."

        return {
            "answer": fallback_text,
            "matched_route": matched_route,
            "anomalies_count": len(anomalies),
            "citations": list(set(citations)),
            "provider": "Analytical Rule Engine"
        }
