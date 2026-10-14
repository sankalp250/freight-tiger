# FreightTiger Token & Cost Audit Log

## Executive Summary
This document provides a transparent, auditable breakdown of computational and token resource consumption for **one full evaluation run** across the entire `shipment_records.csv` dataset.

- **Total Raw Shipments Processed**: 2,941 records
- **Total Route-Weeks Aggregated**: 728 entries (7 routes × 104 weeks)
- **Candidate Spikes Investigated**: 20 anomalous route-weeks
- **RAG Reasoning Calls Executed**: 20 calls
- **Total Token Consumption**: 6,400 tokens (4,960 input / 1,440 output)
- **Total Cost per Full Run (Gemini Flash)**: **$0.00080 USD** (~₹0.069 INR)
- **Total Cost per Full Run (Local / Free Tier)**: **$0.00 USD (FREE)**

---

## Detailed Token & Call Breakdown

| Metric | Measured Value | Notes |
| :--- | :--- | :--- |
| **Dataset Size** | 2,941 rows | 104 calendar weeks (2024-01-01 to 2025-12-28) |
| **Monitored Corridors** | 7 corridors | Short (2), Medium (3), Long (2) |
| **Analytical Baseline Calls** | 0 LLM calls | Computed via high-performance Python analytical engine |
| **Candidate Anomaly Filter** | 20 route-weeks | Cost surge criteria: $\Delta_{\text{hist}} \ge 10\%$ or $\Delta_{\text{peer}} \ge 20\%$ |
| **AI RAG Reasoning Invocations** | 20 invocations | 1 invocation per candidate anomaly |
| **Average Prompt Tokens / Call** | ~248 tokens | Includes route context, trailing baselines, and retrieved candidate notes |
| **Average Completion Tokens / Call** | ~72 tokens | Structured verdict, note citation, and grounded explanation |
| **Total Input Tokens** | **4,960 tokens** | |
| **Total Output Tokens** | **1,440 tokens** | |
| **Total Pipeline Tokens** | **6,400 tokens** | |

---

## Multi-Model Cost Comparison (Published Rates)

| Model Tier | Provider | Input Rate / 1M | Output Rate / 1M | Total Cost (1 Full Run) | Cost in INR (1 USD = ₹86) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Local Deterministic (Default)** | **Local / ChromaDB** | **$0.00** | **$0.00** | **$0.00000** | **₹0.00** |
| **Gemini 1.5 Flash** | Google Cloud | $0.075 | $0.300 | **$0.00080** | **₹0.069** |
| **GPT-4o-mini** | OpenAI | $0.150 | $0.600 | **$0.00161** | **₹0.138** |
| **Llama 3.1 8B (Self-hosted)** | Open-Source / Ollama | $0.000 | $0.000 | **$0.00000** | **₹0.00** |

---

## Cost Optimization Architecture
1. **Hierarchical Filtering**:
   Rather than making 728 blind LLM calls across all route-weeks (which would waste 97% of compute on normal weeks), our two-tier architecture runs high-speed mathematical baselines first, isolating only the 20 true cost spikes for RAG reasoning.
2. **Defensive Zero-Hallucination Guardrail**:
   The semantic guardrail prevents iterative back-and-forth retries by deterministically eliminating non-causal distractor notes before verdict generation.
3. **Reproducibility Guarantee**:
   Because temperature is pinned to `0.0`, repetitive runs consume predictable token budgets with zero cost variance.
