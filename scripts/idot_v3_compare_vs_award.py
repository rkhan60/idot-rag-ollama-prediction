#!/usr/bin/env python3
"""
IDOT V3 - Side-by-side comparison vs award.xlsx (real IDOT results)

For each project in the bulletin range, produces:
  Predicted Top-3   |   Real Top-3 (SELECTED FIRM, First Alternate, Second Alternate)

Real top-3 is taken directly from data/award.xlsx — the official IDOT result file —
which is far more reliable than the fuzzy-job-number matching used in earlier scripts.

Outputs a multi-sheet Excel:
  - Summary               (overall + per-bulletin accuracy on real ground truth)
  - Side_By_Side          (one row per project, predictions next to real results)
  - Per_Bulletin_Stats    (extracted vs matchable vs correct counts)
  - Gaps_Improvements     (analysis of where the model misses + suggestions)
"""

import os
import sys
import re
from datetime import datetime
from collections import defaultdict
from difflib import SequenceMatcher

import pandas as pd
import numpy as np

# Reuse the V3 engine (same directory)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from idot_v3_improved_system import IDOTv3System, normalize_firm_name


# --------------------------------------------------------------------------
# Match helpers
# --------------------------------------------------------------------------

def fuzzy_equal(a, b, threshold=0.85):
    if not a or not b:
        return False
    na, nb = normalize_firm_name(a), normalize_firm_name(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    return SequenceMatcher(None, na, nb).ratio() >= threshold


def first_match(predicted_names, ground_truth_names):
    """Return (matched_pred_index, matched_truth_label) or (None, None)."""
    truth_labels = ['Winner', '1st Alt', '2nd Alt']
    for i, pred in enumerate(predicted_names):
        for j, truth in enumerate(ground_truth_names):
            if truth and fuzzy_equal(pred, truth):
                return i + 1, truth_labels[j] if j < len(truth_labels) else f'pos{j+1}'
    return None, None


# --------------------------------------------------------------------------
# Main comparison
# --------------------------------------------------------------------------

def run_comparison(start_bulletin, end_bulletin,
                   data_dir='../data/', output_dir='../results/'):

    system = IDOTv3System()
    system.load_data(data_dir)

    # Real results from IDOT
    award_df = pd.read_excel(os.path.join(data_dir, 'award.xlsx'))
    award_df['f'] = award_df['f'].astype(int, errors='ignore')

    rows = []
    per_bulletin = defaultdict(lambda: {
        'extracted': 0, 'matched_to_award': 0,
        'top3_correct': 0, 'winner_correct': 0,
        'has_real_top3': 0,
    })

    for bnum in range(start_bulletin, end_bulletin + 1):
        docx_path = os.path.join(data_dir, f'ptb{bnum}.docx')
        if not os.path.exists(docx_path):
            continue

        text = system.read_docx(docx_path)
        projects = system.extract_projects(text)
        per_bulletin[bnum]['extracted'] = len(projects)

        # Index this bulletin's award rows by job number for O(1) lookup
        bulletin_awards = award_df[award_df['f'] == bnum]
        award_by_job = {}
        for _, ar in bulletin_awards.iterrows():
            jn = str(ar.get('Job #', '') or '').strip()
            if jn:
                award_by_job[jn] = ar

        for proj in projects:
            jn = proj['job_number']
            ar = award_by_job.get(jn)

            # Run prediction
            eligible_codes = system.get_eligible_firms(proj['prequal'])
            top3 = system.predict_top3(proj, eligible_codes, bnum)
            top3 += [''] * (3 - len(top3))

            if ar is None:
                # No corresponding row in award.xlsx for this bulletin/job
                rows.append({
                    'Bulletin': bnum,
                    'Job #': jn,
                    'District': proj['district'] or '',
                    'Prequal (extracted)': proj['prequal'] or '',
                    'Description': proj['description'],
                    'Pred 1': top3[0],
                    'Pred 2': top3[1],
                    'Pred 3': top3[2],
                    'Real Winner': '— not in award.xlsx —',
                    'Real 1st Alt': '',
                    'Real 2nd Alt': '',
                    'Match Position': '',
                    'Match Type': '',
                    'Top-3 Correct': '',
                    'Winner-Only Correct': '',
                    'Eligible Firms': len(eligible_codes),
                })
                continue

            per_bulletin[bnum]['matched_to_award'] += 1

            real_winner = str(ar.get('SELECTED FIRM', '') or '').strip()
            real_alt1 = str(ar.get('First Alternate', '') or '').strip()
            real_alt2 = str(ar.get('Second Alternate', '') or '').strip()
            # Replace 'nan' strings (pandas artifacts)
            real_winner = '' if real_winner.lower() == 'nan' else real_winner
            real_alt1 = '' if real_alt1.lower() == 'nan' else real_alt1
            real_alt2 = '' if real_alt2.lower() == 'nan' else real_alt2

            has_real_top3 = bool(real_winner) and bool(real_alt1) and bool(real_alt2)
            if has_real_top3:
                per_bulletin[bnum]['has_real_top3'] += 1

            truth_top3 = [real_winner, real_alt1, real_alt2]
            match_pos, match_label = first_match(top3, truth_top3)
            top3_correct = match_pos is not None
            winner_correct = any(fuzzy_equal(p, real_winner) for p in top3 if p) if real_winner else None

            if top3_correct:
                per_bulletin[bnum]['top3_correct'] += 1
            if winner_correct:
                per_bulletin[bnum]['winner_correct'] += 1

            rows.append({
                'Bulletin': bnum,
                'Job #': jn,
                'District': proj['district'] or (str(ar.get('Region/District', '') or '')),
                'Prequal (extracted)': proj['prequal'] or '',
                'Description': proj['description'] or str(ar.get('Description', '') or '')[:120],
                'Pred 1': top3[0],
                'Pred 2': top3[1],
                'Pred 3': top3[2],
                'Real Winner': real_winner,
                'Real 1st Alt': real_alt1,
                'Real 2nd Alt': real_alt2,
                'Match Position': match_pos or '',
                'Match Type': match_label or '',
                'Top-3 Correct': 'YES' if top3_correct else 'NO',
                'Winner-Only Correct': '' if winner_correct is None else ('YES' if winner_correct else 'NO'),
                'Eligible Firms': len(eligible_codes),
            })

        st = per_bulletin[bnum]
        if st['matched_to_award']:
            print(f"PTB{bnum}: extracted={st['extracted']:3d}  matched={st['matched_to_award']:3d}  "
                  f"top3_correct={st['top3_correct']:3d} ({st['top3_correct']/st['matched_to_award']:5.1%})  "
                  f"winner={st['winner_correct']:3d} ({st['winner_correct']/st['matched_to_award']:5.1%})  "
                  f"has_real_top3={st['has_real_top3']}")

    # ----------------- Aggregate -----------------
    total_extracted = sum(s['extracted'] for s in per_bulletin.values())
    total_matched = sum(s['matched_to_award'] for s in per_bulletin.values())
    total_top3 = sum(s['top3_correct'] for s in per_bulletin.values())
    total_winner = sum(s['winner_correct'] for s in per_bulletin.values())
    total_has_real_top3 = sum(s['has_real_top3'] for s in per_bulletin.values())

    top3_acc = total_top3 / total_matched if total_matched else 0.0
    winner_acc = total_winner / total_matched if total_matched else 0.0

    print("\n" + "=" * 70)
    print(f"REAL TOP-3 ACCURACY (vs award.xlsx): "
          f"{total_top3}/{total_matched} = {top3_acc:.1%}")
    print(f"WINNER-IN-TOP3 ACCURACY (winner-only): "
          f"{total_winner}/{total_matched} = {winner_acc:.1%}")
    print("=" * 70)

    # ----------------- Build per-bulletin stats sheet -----------------
    pb_rows = []
    for bnum, st in sorted(per_bulletin.items()):
        m = st['matched_to_award']
        pb_rows.append({
            'Bulletin': bnum,
            'Projects Extracted': st['extracted'],
            'Matched to award.xlsx': m,
            'Has Real Top-3 (Winner+1st+2nd)': st['has_real_top3'],
            'Top-3 Correct': st['top3_correct'],
            'Top-3 Accuracy': f"{st['top3_correct']/m:.1%}" if m else '',
            'Winner-In-Top-3 Correct': st['winner_correct'],
            'Winner-In-Top-3 Accuracy': f"{st['winner_correct']/m:.1%}" if m else '',
        })

    # ----------------- Gaps & improvement notes -----------------
    gap_rows = [
        {'Area': 'Submitted bidders pool', 'Status': 'NOT USED',
         'Gap': 'award.xlsx Submitted field (PTB195+) lists actual bidders per project',
         'Suggested Improvement': 'Restrict scoring to actual bidders when known — cuts pool from ~200 to ~5-20 firms'},
        {'Area': 'Sub-consultants', 'Status': 'NOT USED',
         'Gap': 'SUBCONSULTANTS field (70.9% coverage) shows team partnerships',
         'Suggested Improvement': 'Add team-frequency feature: firms that frequently team with the prime'},
        {'Area': 'Fee Estimate', 'Status': 'NOT USED',
         'Gap': 'Fee Estimate field (42.4% coverage) signals project size',
         'Suggested Improvement': 'Use size bracket as a categorical feature; big firms vs small firms'},
        {'Area': 'Alternates as features', 'Status': 'NOT USED',
         'Gap': 'First/Second Alternate (54-58% coverage) = near-miss firms',
         'Suggested Improvement': 'Treat alternates as soft wins (0.5 weight) when building RAG win history'},
        {'Area': 'District rotation rule', 'Status': 'SOFT-SCORED',
         'Gap': 'Rule "winner in district D in PTB-N cannot win in same D next PTB" not enforced as hard filter',
         'Suggested Improvement': 'Hard-filter recent winners from eligible pool by district'},
        {'Area': 'Prequal aliases', 'Status': 'PARTIAL',
         'Gap': 'PREQUAL_ALIASES covers ~50 cases; new categories in PTB200+ may miss',
         'Suggested Improvement': 'Periodically audit unmatched prequals; add fuzzy 0.75 fallback (already present)'},
        {'Area': 'DBE status', 'Status': 'NOT USED',
         'Gap': 'firms_data has dbe_status; some bulletins require DBE participation',
         'Suggested Improvement': 'Detect DBE-required projects from bulletin text and prefer DBE-prime firms'},
        {'Area': 'Geographic distance', 'Status': 'COARSE',
         'Gap': 'Only district-letter match; no city-to-project-location distance',
         'Suggested Improvement': 'Use city_to_district + project county to compute proximity score'},
        {'Area': 'Temporal decay', 'Status': 'LINEAR',
         'Gap': 'Recency weight is linear bulletin/current; firms with old wins still counted heavily',
         'Suggested Improvement': 'Apply exponential decay e.g. 0.95^(bulletin_gap); test on held-out set'},
        {'Area': 'Ground truth metric', 'Status': 'IMPROVED IN THIS SCRIPT',
         'Gap': 'Phase 2.1 used fuzzy 0.8 job # match returning 20-57 winners/project (inflated)',
         'Suggested Improvement': 'Use award.xlsx exact top-3 (SELECTED + 1st Alt + 2nd Alt). Done.'},
    ]

    # ----------------- Write Excel -----------------
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = os.path.join(
        output_dir,
        f'IDOTv3_VS_Award_PTB{start_bulletin}_{end_bulletin}_{ts}.xlsx'
    )

    summary_df = pd.DataFrame([
        {'Metric': 'System', 'Value': 'IDOT V3 Improved (RAG + Ollama insights)'},
        {'Metric': 'Bulletin Range', 'Value': f'PTB{start_bulletin} – PTB{end_bulletin}'},
        {'Metric': 'Ground Truth Source', 'Value': 'data/award.xlsx (official IDOT results)'},
        {'Metric': 'Top-3 Definition', 'Value': 'SELECTED FIRM + First Alternate + Second Alternate'},
        {'Metric': 'Total Projects Extracted', 'Value': total_extracted},
        {'Metric': 'Matched to award.xlsx', 'Value': total_matched},
        {'Metric': 'Projects With Complete Real Top-3', 'Value': total_has_real_top3},
        {'Metric': 'Top-3 Correct', 'Value': total_top3},
        {'Metric': 'TOP-3 ACCURACY (Real)', 'Value': f'{top3_acc:.2%}'},
        {'Metric': 'Winner-In-Top-3 Correct', 'Value': total_winner},
        {'Metric': 'WINNER-IN-TOP-3 ACCURACY', 'Value': f'{winner_acc:.2%}'},
        {'Metric': 'Report Generated', 'Value': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
    ])

    detail_df = pd.DataFrame(rows)
    per_b_df = pd.DataFrame(pb_rows)
    gaps_df = pd.DataFrame(gap_rows)

    with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        detail_df.to_excel(writer, sheet_name='Side_By_Side', index=False)
        per_b_df.to_excel(writer, sheet_name='Per_Bulletin_Stats', index=False)
        gaps_df.to_excel(writer, sheet_name='Gaps_Improvements', index=False)

        # Auto-width columns
        for sheet_name, frame in [('Summary', summary_df),
                                  ('Side_By_Side', detail_df),
                                  ('Per_Bulletin_Stats', per_b_df),
                                  ('Gaps_Improvements', gaps_df)]:
            ws = writer.sheets[sheet_name]
            for col_idx, col in enumerate(frame.columns, start=1):
                max_len = max(
                    [len(str(col))] +
                    [len(str(v)) for v in frame[col].astype(str).head(200)]
                )
                ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = min(max_len + 2, 60)

    print(f"\nExcel report written → {out_path}")
    return out_path, top3_acc, winner_acc


if __name__ == '__main__':
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 190
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    run_comparison(start, end)
