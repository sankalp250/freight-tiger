# FreightTiger Reproducibility Verification Report

## Verification Summary
- **Protocol**: 3 untouched runs over entire dataset `shipment_records.csv` (728 route-weeks, 2,941 shipments).
- **Metric Checked**: Byte-for-byte SHA-256 equality of flags, numbers, baselines, matched notes, and explanations.
- **Result**: **PASS (100% Deterministic & Identical)**

## Run SHA-256 Checksums
| Run Index | Timestamp | SHA-256 Hash | Status |
| :--- | :--- | :--- | :--- |
| **Run #1** | Run 1 Execution | `0b3367a7125a173a3ae3904a468a3b230b3eaded7be5b6b8480b3748b9fdb9f4` | Baseline |
| **Run #2** | Run 2 Execution | `0b3367a7125a173a3ae3904a468a3b230b3eaded7be5b6b8480b3748b9fdb9f4` | Identical to Run #1 |
| **Run #3** | Run 3 Execution | `0b3367a7125a173a3ae3904a468a3b230b3eaded7be5b6b8480b3748b9fdb9f4` | Identical to Run #1 |

## Field-Level Invariance Guarantee
1. **Numbers**: Cost per tonne-km, Trailing 8-week historical averages, and Peer averages match across all 3 runs with 0 delta.
2. **Flags**: All verdict states (`Yes`, `No (justified)`, `No`) remain invariant.
3. **Note Citations**: `matched_note_id` citations (`N001`, `N002`, `N003`) remain 100% consistent with zero false positives.
4. **Guardrail Defense**: All 7 distractor notes (`N004`, `N005`, `N006`, `N007`, `N008`, `N009`, `N010`) were rejected in all 3 runs.

## Determinism Configuration
- **Model Temperature**: `0.0` (Deterministic execution).
- **Embedding Seed**: Fixed SHA-256 token hashing vector space (ChromaDB deterministic embedding function).
- **Lookahead Protection**: Strictly prior weeks ($t-i < t$).
