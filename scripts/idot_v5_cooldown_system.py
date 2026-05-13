#!/usr/bin/env python3
"""
IDOT V5 - V4 + quarterly cooldown rule (hard eligibility filter)

Business rule from IDOT:
    If a firm wins a project in bulletin N, that firm is INELIGIBLE
    for any type of project in bulletin N+1.

(Bulletins are quarterly — median gap between Selection Dates is 91 days —
so "next quarter" maps directly to "next bulletin".)

Implementation:
    - During training, record every (firm_code, bulletin) where the firm
      was SELECTED FIRM (alternates do NOT trigger cooldown).
    - Before scoring projects in bulletin B, filter out any firm whose
      win set contains B-1.
"""

import os
import sys

from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from idot_v4_alternates_system import IDOTv4System


class IDOTv5System(IDOTv4System):

    def __init__(self):
        super().__init__()
        # firm_code -> set of bulletins where firm was SELECTED FIRM
        self.firm_winning_bulletins = defaultdict(set)

    def load_data(self, base='../data/'):
        super().load_data(base)
        print("Building cooldown table ...")
        self._build_cooldown_table()
        n_with_wins = sum(1 for s in self.firm_winning_bulletins.values() if s)
        print(f"  {n_with_wins} firms have at least one SELECTED FIRM win.")

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
            if bulletin:
                self.firm_winning_bulletins[firm_code].add(bulletin)

    def _is_in_cooldown(self, firm_code, current_bulletin):
        """True if firm won in the immediately preceding bulletin."""
        return (current_bulletin - 1) in self.firm_winning_bulletins.get(firm_code, set())

    # ------------------------------------------------------------------
    # Override predict_top3 to apply the cooldown filter
    # ------------------------------------------------------------------

    def predict_top3(self, project, eligible_codes, current_bulletin):
        # Hard filter: drop firms in cooldown
        filtered = [fc for fc in eligible_codes
                    if not self._is_in_cooldown(fc, current_bulletin)]
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
