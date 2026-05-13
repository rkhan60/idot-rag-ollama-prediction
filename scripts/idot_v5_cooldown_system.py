#!/usr/bin/env python3
"""
IDOT V5 - V4 + district-scoped quarterly cooldown (hard eligibility filter)

Business rule from IDOT:
    If a firm wins a project in district D in bulletin N, that firm is
    INELIGIBLE for any project in district D in bulletin N+1.
    (The firm remains eligible in OTHER districts.)

Bulletins are quarterly (median 91 days between Selection Dates), so
"next quarter" maps directly to "next bulletin".

Implementation:
    - During training, record every (firm_code, district, bulletin) where
      the firm was SELECTED FIRM (alternates do NOT trigger cooldown).
    - Before scoring projects in district D, bulletin B, filter out any
      firm whose (D, B-1) is in their win set.
"""

import os
import sys

from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from idot_v4_alternates_system import IDOTv4System
from idot_v3_improved_system import normalize_district


class IDOTv5System(IDOTv4System):

    def __init__(self):
        super().__init__()
        # firm_code -> district -> set of bulletins where firm was SELECTED FIRM
        self.firm_district_winning_bulletins = defaultdict(lambda: defaultdict(set))

    def load_data(self, base='../data/'):
        super().load_data(base)
        print("Building district-scoped cooldown table ...")
        self._build_cooldown_table()
        n_pairs = sum(len(d) for d in self.firm_district_winning_bulletins.values())
        n_firms = sum(1 for d in self.firm_district_winning_bulletins.values() if d)
        print(f"  {n_firms} firms have wins across {n_pairs} (firm, district) pairs.")

    def _build_cooldown_table(self):
        """Only SELECTED FIRM wins trigger the cooldown — not alternates."""
        for _, row in self._award_df.iterrows():
            winner = self._clean_firm(row.get('SELECTED FIRM'))
            if not winner:
                continue
            firm_code = self._match_award_firm_to_code(winner)
            if not firm_code:
                continue
            bulletin = int(row.get('f') or 0)
            district = normalize_district(row.get('Region/District', ''))
            if bulletin and district:
                self.firm_district_winning_bulletins[firm_code][district].add(bulletin)

    def _is_in_cooldown(self, firm_code, district, current_bulletin):
        """True if firm won in this district in the immediately preceding bulletin."""
        if not district:
            return False  # No district info → can't apply rule
        win_set = self.firm_district_winning_bulletins.get(firm_code, {}).get(district, set())
        return (current_bulletin - 1) in win_set

    # ------------------------------------------------------------------
    # Override predict_top3 to apply the district-scoped cooldown filter
    # ------------------------------------------------------------------

    def predict_top3(self, project, eligible_codes, current_bulletin):
        district = project.get('district')
        filtered = [fc for fc in eligible_codes
                    if not self._is_in_cooldown(fc, district, current_bulletin)]
        # Safety net — if cooldown wipes out the whole pool, fall back to unfiltered
        if not filtered:
            filtered = eligible_codes
        return super().predict_top3(project, filtered, current_bulletin)


if __name__ == '__main__':
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 190
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    system = IDOTv5System()
    results, accuracy = system.run_test(start, end)
    print(f"\nFinal accuracy (Phase 2.1 fuzzy metric): {accuracy:.1%}")
