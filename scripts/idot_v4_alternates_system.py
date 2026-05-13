#!/usr/bin/env python3
"""
IDOT V4 - V3 + alternates as soft wins

The award.xlsx file records, for each project:
  - SELECTED FIRM   (the winner)
  - First Alternate  (runner-up #1)
  - Second Alternate (runner-up #2)

V3 only learned from SELECTED FIRM. V4 also learns from alternates as
weighted soft-wins:

    winner   weight = 1.0
    1st alt  weight = 0.5
    2nd alt  weight = 0.3

These weights affect:
  - firm_district_wins  (cumulative district-affinity)
  - firm_prequal_wins   (cumulative category-affinity)
  - firm_rag_indices    (per-firm pointers into the TF-IDF matrix, with weight)

Alternates are only available in award.xlsx (not in award_structure.json),
so V4 loads them directly from the spreadsheet.
"""

import os
import sys

import pandas as pd
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from idot_v3_improved_system import (
    IDOTv3System,
    normalize_district,
)

# Weights — alternates count as fractional wins
WEIGHT_WINNER = 1.0
WEIGHT_FIRST_ALT = 0.5
WEIGHT_SECOND_ALT = 0.3


class IDOTv4System(IDOTv3System):

    def __init__(self):
        super().__init__()
        # firm_code -> district -> float (weighted)
        self.firm_district_wins = defaultdict(lambda: defaultdict(float))
        # firm_code -> prequal -> float (weighted)
        self.firm_prequal_wins = defaultdict(lambda: defaultdict(float))
        # firm_code -> [(rag_idx, bulletin, weight), ...]
        self.firm_rag_indices = defaultdict(list)
        # Cache of award.xlsx contents (loaded once during load_data)
        self._award_df = None

    # ------------------------------------------------------------------
    # Override load_data to read alternates from award.xlsx
    # ------------------------------------------------------------------

    def load_data(self, base='../data/'):
        # Load award.xlsx FIRST (before parent rebuilds tables)
        print("Loading award.xlsx (with alternates) ...")
        self._award_df = pd.read_excel(os.path.join(base, 'award.xlsx'))
        # Coerce bulletin column
        self._award_df['f'] = self._award_df['f'].fillna(0).astype(int)

        # Parent loads firms_data, prequal_lookup, award_structure,
        # and calls _build_win_stats + _build_rag (now overridden).
        super().load_data(base)

    # ------------------------------------------------------------------
    # Helper: iterate (firm_name, weight) tuples for one award.xlsx row
    # ------------------------------------------------------------------

    @staticmethod
    def _clean_firm(name):
        if name is None:
            return ''
        s = str(name).strip()
        if s.lower() == 'nan':
            return ''
        if '\n' in s or len(s) > 100:
            return ''
        if s in ('WITHDRAWN', 'NO SUBMITTALS'):
            return ''
        return s

    def _firms_with_weights(self, row):
        """Yield (firm_name, weight) for SELECTED FIRM + 1st + 2nd alternates."""
        winner = self._clean_firm(row.get('SELECTED FIRM'))
        alt1 = self._clean_firm(row.get('First Alternate'))
        alt2 = self._clean_firm(row.get('Second Alternate'))
        if winner:
            yield winner, WEIGHT_WINNER
        if alt1:
            yield alt1, WEIGHT_FIRST_ALT
        if alt2:
            yield alt2, WEIGHT_SECOND_ALT

    # ------------------------------------------------------------------
    # Override _build_win_stats: weighted, includes alternates
    # ------------------------------------------------------------------

    def _build_win_stats(self):
        for _, row in self._award_df.iterrows():
            raw_district = row.get('Region/District', '')
            description = str(row.get('Description', '') or '')
            district = normalize_district(raw_district) or 'unknown'
            prequal_cat = self._infer_prequal_from_description(description)

            for firm_name, weight in self._firms_with_weights(row):
                firm_code = self._match_award_firm_to_code(firm_name)
                if not firm_code:
                    continue
                self.firm_total_wins[firm_code] += weight
                self.firm_district_wins[firm_code][district] += weight
                if prequal_cat:
                    self.firm_prequal_wins[firm_code][prequal_cat] += weight

    # ------------------------------------------------------------------
    # Override _build_rag: build TF-IDF once per project description,
    # then attach weighted firm pointers (winner + alternates)
    # ------------------------------------------------------------------

    def _build_rag(self):
        from sklearn.feature_extraction.text import TfidfVectorizer

        descriptions = []
        row_firms = []  # parallel: [(idx_in_descriptions, [(firm_code, bulletin, weight), ...]), ...]

        for _, row in self._award_df.iterrows():
            desc = str(row.get('Description', '') or '').strip()
            if not desc:
                continue
            bulletin = int(row.get('f') or 0)

            firm_entries = []
            for firm_name, weight in self._firms_with_weights(row):
                fc = self._match_award_firm_to_code(firm_name)
                if fc:
                    firm_entries.append((fc, bulletin, weight))

            if not firm_entries:
                continue  # don't add a description with no firm anchors

            idx = len(descriptions)
            descriptions.append(desc)
            self.rag_metadata.append({
                'description': desc,
                'bulletin': bulletin,
                'district': normalize_district(row.get('Region/District', '')),
                'firms': firm_entries,
            })
            row_firms.append((idx, firm_entries))

        if descriptions:
            self.vectorizer = TfidfVectorizer(
                max_features=3000, ngram_range=(1, 3), stop_words='english'
            )
            self.rag_matrix = self.vectorizer.fit_transform(descriptions)
            for idx, firm_entries in row_firms:
                for fc, bulletin, weight in firm_entries:
                    self.firm_rag_indices[fc].append((idx, bulletin, weight))

        print(f"  TF-IDF built on {len(descriptions)} project descriptions "
              f"(winners + weighted alternates).")

    # ------------------------------------------------------------------
    # Override score_firm: now uses the (idx, bulletin, weight) tuple
    # ------------------------------------------------------------------

    def score_firm(self, firm_code, district, prequal, sim_scores, current_bulletin):
        sim_score = 0.0
        for entry in self.firm_rag_indices.get(firm_code, []):
            # V4 entries are 3-tuples; V3 were 2-tuples (in case of mixed access)
            if len(entry) == 3:
                idx, bulletin, weight = entry
            else:
                idx, bulletin = entry
                weight = 1.0
            if bulletin >= current_bulletin:
                continue
            s = sim_scores[idx]
            if s > 0.01:
                recency = 1.0 + (bulletin / max(current_bulletin, 1)) * 0.3
                sim_score += s * recency * weight

        district_w = self.firm_district_wins.get(firm_code, {}).get(district or 'unknown', 0.0)
        prequal_w = self.firm_prequal_wins.get(firm_code, {}).get(prequal or '', 0.0)
        firm_home = self.firms_data.get(firm_code, {}).get('district', '') or ''
        home_match = 1.0 if district and district.split('/')[0] in firm_home else 0.0

        score = (sim_score * 10.0) + (district_w * 2.0) + (prequal_w * 1.5) + (home_match * 1.0)
        return score


if __name__ == '__main__':
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 190
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    system = IDOTv4System()
    results, accuracy = system.run_test(start, end)
    print(f"\nFinal accuracy (Phase 2.1 fuzzy metric): {accuracy:.1%}")
