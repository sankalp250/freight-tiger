# FreightTiger Round 2: 10-Minute Walkthrough & Defense Guide
> **Case Study Round**: Software Engineering Intern (AI & Data)  
> **Topic**: Shipping Cost Watchdog with Grounded RAG & Anti-Hallucination Guardrails  

---

## 1. Minute-by-Minute Presentation Plan

### [00:00 - 02:00] The Logistics Problem & Mathematical Precision
* **Hook**: 
  > *"In interstate Indian trucking, cost per trip isn't informative on its own because trucks vary by payload and distance. We first normalize all freight data into **Cost per Tonne-Kilometer ($\text{INR}/(\text{t}\cdot\text{km})$)** and aggregate by Monday-based ISO calendar weeks."*
* **Mathematical Contract**:
  * Show the formula: $\text{Cost per Tonne-Km} = \frac{\sum \text{freight\_cost\_inr}}{\sum (\text{quantity\_tonnes} \times \text{distance\_km})}$.
  * Explain **Trailing 8-Week History**: Strictly prior weeks ($t-i < t$). Highlight that early weeks with fewer than 8 prior weeks use available history without padding or lookahead leakage.
  * Explain **Peer Route Baseline**: Same week, same `route_type` (`Short`, `Medium`, `Long`), strictly excluding the route itself.
* **Demonstrate Precision**:
  * Show that our analytical engine matches the sample ground truth:
    * `Delhi-Jaipur` (2024-11-11): **₹4.17** (+35.5% hist, +21.0% peers)
    * `Ahmedabad-Mumbai` (2025-01-20): **₹3.29** (+29.5% hist, +22.5% peers)
    * `Mumbai-Pune` (2025-09-15): **₹3.98** (+9.2% hist, +23.6% peers)

---

### [02:00 - 04:30] The Secret Test: Neutralizing the 7 Trap Distractor Notes
* **Key Insight**:
  > *"When inspecting `context_notes.csv`, I noticed something critical: out of 10 context notes, only 3 (N001, N002, N003) describe genuine cost increases. The other 7 are deliberate distractor traps designed to catch hallucinations."*
* **Walk through the Trap Examples**:
  1. **N004**: Mentions a toll plaza, but explicitly notes *"affected routes are not part of this dataset"*.
  2. **N005**: Mentions highway maintenance, but explicitly notes *"costs were not significantly affected"*.
  3. **N006**: Mentions stable demand with *"no major disruptions"* — adjacent in time to Mumbai-Pune, but does not justify a rate hike!
  4. **N010**: Mentions fleet tracking, but notes costs were *"absorbed by transporters without a rate change"*.
* **Our Defensive Guardrail Protocol**:
  * We enforce a **3-tier semantic validator**: Corridor Match $\to$ Temporal Window Match $\to$ Directional Causality Verification.
  * If a distractor note is nearest, our system explicitly refutes it in the output reason:
    > *"The closest note (N006, 2025-09-22) mentions stable demand with no major disruptions -- it does not describe a reason for a cost rise on this route. No genuine justification found; flagged for review."*

---

### [04:30 - 07:00] Live Architecture & Operations Console Demo
* **Architecture Overview**:
  * Two-tier design: High-performance Python mathematical core $\to$ Anomaly Isolation $\to$ ChromaDB Guarded RAG $\to$ FastAPI $\to$ Utilitarian Minimalist React UI.
* **Live UI Demo**:
  1. **Overview Tab**: Show the 4 bento metric cards (2,940 shipments, 17 unexplained spikes, 3 verified surges, 7 distractors neutralized).
  2. **Corridor Trends Tab**: Switch between `Mumbai-Pune` and `Chennai-Bangalore`. Point out the actual cost curve, 8-week historical envelope (dashed), and peer corridor baseline (dotted).
  3. **Anomaly Triage Table**: Filter by `Unjustified` vs `Justified`. Point to row 3 (Ahmedabad-Mumbai justified by N002) vs row 1 (Delhi-Jaipur unexplained).
  4. **Natural Language Assistant (Stretch Goal)**: Open the slide-over drawer and ask:
     * *"Why did Chennai-Bangalore spike in February 2025?"* (Show grounded answer citing N001 flood detours Feb 24 - Mar 8).
     * *"Explain the Mumbai-Pune cost rise in September 2025."* (Show grounded refutation of N006).

---

### [07:00 - 08:30] 3-Run Reproducibility & Token/Cost Accounting
* **Reproducibility Guarantee**:
  * Show `submission/reproducibility_report.md`.
  * Explain that 3 independent untouched runs over all 728 route-weeks produced **identical SHA-256 hashes** with 0 bit delta.
  * Explain why: Temperature pinned to `0.0`, deterministic vector space hashing, and strict rule-bound guardrail evaluation.
* **Cost Accounting**:
  * Show `submission/token_cost_log.md`.
  * Explain **Hierarchical Filtering**: Instead of making 728 LLM calls, we filter normal weeks first, invoking AI reasoning only for the 20 candidate anomalies.
  * Token usage: 6,400 tokens total (~4,960 input, ~1,440 output).
  * Run cost: **$0.00 (Free / Local)**, or **$0.0016 USD** (~₹0.14 INR) on Gemini 1.5 Flash.

---

### [08:30 - 10:00] Engineering Trade-offs & Q&A Wrap-Up
* **Summary Statement**:
  > *"We built this like a production-ready system: strict mathematical adherence, zero external cloud vulnerabilities, deterministic guardrails against hallucinated excuses, and a clean internal ops console for freight managers."*

---

## 2. Anticipated Interviewer Questions & Model Answers

### Q1: "Why did you choose SQLite + ChromaDB instead of Pinecone or Supabase?"
**Answer**:  
> *"In a production or evaluation environment, external cloud databases introduce three major liabilities: external network latency, cloud credential dependency (evaluators would fail to run the code if an external Pinecone key was expired or omitted), and free-tier limits (such as Supabase's 2-project cap).  
> SQLite and ChromaDB store data locally in `./data/`, requiring zero external setup. Anyone on the engineering team can clone the repository, run `pytest`, and get a working system in 2 seconds. Furthermore, both can be bundled into a single deployable Docker container."*

### Q2: "How did you handle the early weeks where 8 prior weeks didn't exist?"
**Answer**:  
> *"The prompt specifically instructed: 'If fewer than 8 prior weeks exist, use all prior weeks available and say so in your README -- don't pad or extrapolate.'  
> For week 1 of a route, history is unavailable, so we record `N/A (first available week, no prior history)`. For week 2, we average week 1; for week 5, we average the 4 prior weeks. Lookahead is strictly zero ($t - i < t$). This exact logic allowed our calculations to match the sample test cases down to the tenth of a percent."*

### Q3: "How does your system prevent hallucinating that a maintenance note (like N005) or toll note (like N004) explains a cost rise?"
**Answer**:  
> *"A naive vector search matches 'toll' or 'maintenance' because the embedding distance is low. To prevent this, we implemented our `AntiHallucinationGuardrail` with three checks:  
> 1. Corridor verification (corridor matches target or 'All Routes').  
> 2. Temporal window verification (shipment week falls in event dates).  
> 3. Directional causality check: We detect explicit negative qualifiers ('costs were not significantly affected', 'routes not part of this dataset', 'without a rate change'). If present, the note is disqualified from serving as a justification, and the assistant explicitly refutes it in the reason string."*

### Q4: "Why did you build a custom SVG chart instead of installing an external charting library like Chart.js or Recharts?"
**Answer**:  
> *"By building a native, lightweight SVG trend line component directly in React, we achieved zero dependency overhead, instant bundle builds (310ms build time), and absolute control over coordinate mapping, tooltip hover states, and anomaly dot highlights without any styling bloat or AI-slop design artifacts."*
