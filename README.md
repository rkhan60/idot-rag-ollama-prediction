# IDOT Consultant Selection — RAG + Ollama Prediction System

Predicts the top-3 firms likely to win each project in an IDOT (Illinois Dept. of
Transportation) PTB bulletin, using TF-IDF retrieval over 2,166 historical awards
plus Ollama-LLM-derived training insights.

## Headline Results

| Metric | V3 | **V4** (alternates as soft wins) |
|---|---|---|
| Real Top-3 accuracy (PTB190–200, vs award.xlsx) | 31.4% | **36.0%** |
| Winner-in-Top-3 accuracy (PTB190–200) | 16.8% | 16.5% |
| Phase 2.1 fuzzy-metric Top-3 (PTB190–200) | 86.1% | — |
| Phase 2.1 fuzzy-metric Top-3 (PTB180–190) | 83.7% | — |
| Random-baseline | ~1.5% | ~1.5% |

V4 = V3 + First Alternate (0.5 weight) and Second Alternate (0.3 weight)
folded into training (district-wins, prequal-wins, RAG firm pointers).
Real ground truth = SELECTED FIRM + First Alternate + Second Alternate
columns in `data/award.xlsx`. Random baseline ≈ 3/200 eligible firms.

> **About the two metrics.** The original Phase 2.1 benchmark scored a prediction
> as correct if the model's top-3 matched **any** firm whose job number
> fuzzy-matched (SequenceMatcher ≥ 0.8) the target — which returned 20–57
> firms per project, inflating accuracy. The real top-3 in `data/award.xlsx`
> (the SELECTED FIRM + First Alternate + Second Alternate columns) is the
> honest measure. The new comparison script (below) uses this.

## Repository Layout

```
RAG+Ollama/
├── README.md                              ← you are here
├── requirements.txt
├── setup.sh
├── data/
│   ├── award.xlsx                         ← OFFICIAL IDOT results (2,166 records, PTB160–216)
│   ├── award_structure.json               ← JSON mirror of award.xlsx
│   ├── firms_data.json                    ← 415 IDOT-prequalified firms
│   ├── prequal_lookup.json                ← prequal-category → firm-list
│   ├── city_to_district.json
│   ├── district_mapping.json
│   └── ptb{160..216}.docx                 ← raw bulletins (gitignored, kept locally)
├── scripts/
│   ├── idot_v3_improved_system.py         ← V3 engine (SELECTED FIRM only)
│   ├── idot_v4_alternates_system.py       ← V4 engine (+ weighted alternates)
│   ├── idot_v3_compare_vs_award.py        ← side-by-side vs award.xlsx (supports v3 or v4)
│   └── …(historical/exploratory scripts)
├── results/                               ← generated Excel (gitignored)
└── documentation/
```

## How to Run

```bash
cd scripts

# 1) Run V3 vs real IDOT results
python3 idot_v3_compare_vs_award.py 190 200 v3

# 2) Run V4 (V3 + weighted alternates) vs real IDOT results
python3 idot_v3_compare_vs_award.py 190 200 v4

# 3) Just print V3 accuracy on Phase 2.1's old fuzzy metric
python3 idot_v3_improved_system.py
```

The comparison script writes a multi-sheet Excel into `results/`:

| Sheet | Contents |
|---|---|
| `Summary` | Headline metrics + run metadata |
| `Side_By_Side` | One row per project: Predicted top-3 \| Real top-3 \| Match position \| Correctness |
| `Per_Bulletin_Stats` | Extracted / matched / correct counts per bulletin |
| `Gaps_Improvements` | Catalogued model gaps with suggested fixes |

## Model — How It Works

1. **Bulletin parsing** (`extract_projects`) — read `.docx` directly with
   `python-docx`, split on `Job No.` lines (handles both numbered PTB160–194
   and unnumbered PTB195+ formats), extract job #, description, district,
   prequal.
2. **Prequal normalization** (`PREQUAL_ALIASES`) — map 50+ bulletin-text
   variants to canonical category names in `prequal_lookup.json`. Fuzzy
   fallback at 0.75 threshold.
3. **Eligibility filter** — only firms pre-qualified in the project's prequal
   category are scored (~200 firms typical).
4. **TF-IDF RAG** — vectorize 2,012 historical award descriptions
   (`max_features=3000, ngram=(1,3)`). For each project, similarity-score the
   project description against every past award.
5. **Score per firm** (deterministic, no randomness):
   ```
   score = 10·Σ_recent(similarity · recency)         ← TF-IDF win-history (primary)
         +  2·district_wins[firm][district]          ← district affinity
         +  1.5·prequal_wins[firm][prequal]          ← category affinity
         +  1.0·home_district_match                  ← firm's HQ in project district
   ```
   Future bulletins (`bulletin ≥ current`) are excluded to prevent leakage.
6. **Output** — top-3 by score.

## Known Gaps & Improvement Roadmap

(Also exported in the `Gaps_Improvements` sheet of every comparison run.)

| Area | Status | Suggested Improvement |
|---|---|---|
| Submitted-bidders pool | not used | award.xlsx `Submitted` field for PTB195+ — cuts pool from ~200 to 5–20 firms |
| Sub-consultants | not used | use 70.9%-coverage `SUBCONSULTANTS` column to learn team-frequency |
| Fee Estimate | not used | size-bracket categorical feature |
| First / Second Alternate | **DONE in V4** | weighted 0.5 / 0.3 in district-wins, prequal-wins, RAG |
| District-rotation rule | soft-scored only | hard-filter recent district winners |
| DBE detection | not used | parse bulletin for DBE-required, prefer DBE primes |
| Geographic distance | coarse | city→county distance instead of just district letter |
| Temporal decay | linear | exponential decay `0.95^Δbulletin` |
| Prequal aliases | 50+ rules | periodically audit unmatched and grow table |

## Data Provenance

- `award.xlsx` is the authoritative IDOT result file. Treat the JSON mirrors
  as derivatives.
- `firms_data.json` was scraped/compiled from IDOT's pre-qualified consultant
  list (`data/IDOTConsultantList.xlsx`).
- `prequal_lookup.json` was rebuilt from per-category PDFs in
  `data/pre-qual_d/` (gitignored).

## Requirements

```bash
pip install -r requirements.txt
# plus Ollama installed locally if regenerating training_results.json
```

Python 3.8+. Optional: Ollama with `llama3` for re-running training-insight
extraction (cached in `ollama_training_results.json`).
