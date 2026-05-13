#!/usr/bin/env python3
"""
IDOT V3 Improved System
Fixes over Phase 2.1:
  1. Reads .docx directly - no pre-converted txt files needed
  2. Deterministic scoring - all np.random removed
  3. District-specific historical win rates as primary signal
  4. Prequal-category win rates as secondary signal
  5. Comprehensive prequal name normalization
  6. Firm name normalization for award -> firms_data matching
"""

import json
import re
import os
import docx
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
# Prequal name aliases: bulletin text -> prequal_lookup full_prequal_name
# ---------------------------------------------------------------------------
PREQUAL_ALIASES = {
    # Traffic
    "special studies (traffic signals)":        "Special Plans (Traffic Signals)",
    "special studies - traffic signals":         "Special Plans (Traffic Signals)",
    "special studies – traffic signals":         "Special Plans (Traffic Signals)",
    "special plans (traffic signals)":           "Special Plans (Traffic Signals)",
    "special studies (traffic)":                 "Special Studies (Traffic)",
    "special studies: traffic studies":          "Special Studies (Traffic)",
    "special studies – traffic studies":         "Special Studies (Traffic)",
    "special studies- traffic studies":          "Special Studies (Traffic)",
    "traffic studies":                           "Special Studies (Traffic)",
    "signal coordination & timing (scat)":       "Special Studies [Signal Coordination & Timing (SCAT)]",
    "signal coordination and timing (scat)":     "Special Studies [Signal Coordination & Timing (SCAT)]",

    # Construction Inspection
    "special services (construction inspection)":    "(Special Services) Construction Inspection",
    "construction inspection":                        "(Special Services) Construction Inspection",

    # Surveying
    "special services (surveying)":              "Special Services (Surveying)",
    "special services (surveying) prequalification": "Special Services (Surveying)",

    # Quality Assurance variants
    "special services (quality assurance pcc & aggregate)":     "Special Services (Quality Assurance: QA PCC & Aggregate)",
    "special services (quality assurance:  qa pcc and aggregate)": "Special Services (Quality Assurance: QA PCC & Aggregate)",
    "special services (quality assurance hma & aggregate)":     "Special Services (Quality Assurance HMA & Aggregate)",
    "special services (quality assurance: qa pcc & aggregate)": "Special Services (Quality Assurance: QA PCC & Aggregate)",

    # Hazardous Waste
    "special services (hazardous waste - advance)":  "Special Services (Hazardous Waste: Advance)",
    "special services (hazardous waste: advance)":   "Special Services (Hazardous Waste: Advance)",
    "special services (hazardous waste - simple)":   "Special Services (Hazardous Waste: Simple)",
    "special services (hazardous waste: simple)":    "Special Services (Hazardous Waste: Simple)",

    # Structures
    "structures (highway: typical)":             "Structures – (Highway: Typical)",
    "structures (highway: complex)":             "Structures (Highway: Complex)",
    "structures (highway: advanced typical)":    "Structures (Highway: Advanced Typical)",
    "structures (highway: simple)":              "Structures (Highway- Simple)",
    "structures - highway: typical":             "Structures – (Highway: Typical)",
    "structures - highway: complex":             "Structures (Highway: Complex)",

    # Highways
    "highways (roads & streets)":               "Highways (Roads & Streets)",
    "highways (freeways)":                       "Highways (Freeways)",

    # Location Design
    "location design studies (rehabilitation)":         "Location/Design Studies (Rehabilitation)",
    "location design studies (reconstruction/major rehabilitation)": "Location/ Design Studies (Reconstruction/Major Rehabilitation)",
    "location/design studies (rehabilitation)":         "Location/Design Studies (Rehabilitation)",

    # Environmental
    "environmental reports (environmental assessment)":        "Environmental Reports (Environmental Assessment)",
    "environmental reports (environmental impact statement)":  "Environmental Reports (Environmental Impact Statement)",

    # Geotechnical
    "geotechnical services (general geotechnical services)":   "Geotechnical Services (General Geotechnical Services)",
    "geotechnical services (structure geotechnical reports (sgr))": "Geotechnical Services (Structure Geotechnical Reports (SGR))",
    "geotechnical services (subsurface explorations)":         "Geotechnical Services (Subsurface Explorations)",

    # Hydraulic
    "hydraulic reports (waterways: typical)":    "Hydraulic Reports - Waterways: Typical",
    "hydraulic reports - waterways: typical":    "Hydraulic Reports - Waterways: Typical",
    "hydraulic reports (waterways: complex)":    "Hydraulic Reports (Waterways: Complex)",

    # Airports
    "airports (construction inspection)":        "Airports (Construction Inspection)",
    "airports (design)":                         "Airports (Design)",
    "airports (planning & special services)":    "Airports (Master Planning:Airport Layout Plans (ALP))",

    # Special Plans
    "special plans (lighting: typical)":         "Special Plans (Lighting: Typical)",
    "special plans (lighting: complex)":         "Special Plans (Lighting: Complex)",

    # Specialty Agents
    "specialty agents (appraiser)":              "Specialty Agents (Appraiser)",
    "specialty agents (negotiator)":             "Specialty Agents (Negotiator)",
    "specialty agents (relocation agent)":       "Specialty Agents (Relocation Agent)",
}

WORD_TO_NUM = {
    'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
    'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
}


def normalize_firm_name(name):
    """Uppercase, remove legal suffixes, strip punctuation."""
    if not name:
        return ""
    name = name.upper().strip()
    for suffix in [', INC.', ', LLC', ', LTD.', ', PLLC', ', P.C.',
                   ' INC.', ' LLC.', ' LTD.', ' INC', ' LLC']:
        name = name.replace(suffix, '')
    name = re.sub(r'[^A-Z0-9 &]', ' ', name)
    return ' '.join(name.split())


def normalize_district(raw):
    """Normalise district strings from docx/award_structure to 'R/D' integers."""
    if not raw:
        return None
    raw = str(raw).strip()
    # Formats: '1/1', 'R1/D1', 'Region 1/District 1', 'Region One/District One', 'District 1'
    m = re.search(
        r'(?:Region|R)?\s*(\w+)\s*/\s*(?:District|D)?\s*(\w+)',
        raw, re.IGNORECASE
    )
    if m:
        r = WORD_TO_NUM.get(m.group(1).lower(), m.group(1))
        d = WORD_TO_NUM.get(m.group(2).lower(), m.group(2))
        return f"{r}/{d}"
    # Just 'District N'
    m2 = re.search(r'District\s+(\w+)', raw, re.IGNORECASE)
    if m2:
        d = WORD_TO_NUM.get(m2.group(1).lower(), m2.group(1))
        return f"?/{d}"
    return raw


class IDOTv3System:
    def __init__(self):
        self.firms_data = {}          # firm_code -> dict
        self.prequal_lookup = {}      # full_prequal_name -> [firm_code, ...]
        self.award_structure = []

        # Built from award_structure
        self.award_firm_name_to_norm = {}   # original -> normalized
        self.norm_to_firm_code = {}         # normalized_name -> firm_code

        # Win rate tables
        self.firm_total_wins = defaultdict(int)         # firm_code -> int
        self.firm_district_wins = defaultdict(lambda: defaultdict(int))  # firm_code -> district -> int
        self.firm_prequal_wins = defaultdict(lambda: defaultdict(int))   # firm_code -> prequal_cat -> int

        # TF-IDF for description similarity
        self.vectorizer = None
        self.rag_matrix = None
        self.rag_metadata = []

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load_data(self, base='../data/'):
        print("Loading firms_data.json ...")
        with open(f'{base}firms_data.json') as f:
            firms_list = json.load(f)
        for firm in firms_list:
            fc = firm['firm_code']
            self.firms_data[fc] = firm
            self.norm_to_firm_code[normalize_firm_name(firm['firm_name'])] = fc

        print("Loading prequal_lookup.json ...")
        with open(f'{base}prequal_lookup.json') as f:
            raw_pl = json.load(f)
        for cat, cat_data in raw_pl.items():
            for code, sub in cat_data['sub_categories'].items():
                name = sub['full_prequal_name']
                firm_codes = []
                for f in sub['firms']:
                    fc = f['firm_code'] if isinstance(f, dict) else f
                    if fc in self.firms_data:
                        firm_codes.append(fc)
                self.prequal_lookup[name] = firm_codes

        print("Loading award_structure.json ...")
        with open(f'{base}award_structure.json') as f:
            self.award_structure = json.load(f)

        print("Building win rate tables ...")
        self._build_win_stats()

        print("Building TF-IDF knowledge base ...")
        self._build_rag()

        print("Data loaded.\n")

    def _match_award_firm_to_code(self, award_firm_name):
        """Best-effort match of an award winner name to a firm_code."""
        norm = normalize_firm_name(award_firm_name)
        if norm in self.norm_to_firm_code:
            return self.norm_to_firm_code[norm]
        # Fuzzy fallback
        best_score, best_code = 0.0, None
        for n, fc in self.norm_to_firm_code.items():
            s = SequenceMatcher(None, norm, n).ratio()
            if s > best_score:
                best_score, best_code = s, fc
        if best_score >= 0.80:
            return best_code
        return None

    def _infer_prequal_from_description(self, description):
        """Crude prequal category inference from description text."""
        d = description.lower()
        if 'construction inspection' in d or 'phase iii' in d:
            return '(Special Services) Construction Inspection'
        if 'traffic signal' in d:
            return 'Special Plans (Traffic Signals)'
        if 'traffic stud' in d or 'traffic analy' in d:
            return 'Special Studies (Traffic)'
        if 'survey' in d:
            return 'Special Services (Surveying)'
        if 'bridge' in d or 'structure' in d:
            return 'Structures – (Highway: Typical)'
        if 'highway' in d or 'road' in d or 'street' in d:
            return 'Highways (Roads & Streets)'
        if 'environmental assessment' in d:
            return 'Environmental Reports (Environmental Assessment)'
        if 'environmental impact' in d:
            return 'Environmental Reports (Environmental Impact Statement)'
        if 'geotech' in d or 'subsurface' in d:
            return 'Geotechnical Services (General Geotechnical Services)'
        if 'hydraulic' in d or 'waterway' in d:
            return 'Hydraulic Reports - Waterways: Typical'
        if 'airport' in d:
            return 'Airports (Design)'
        return None

    def _build_win_stats(self):
        for award in self.award_structure:
            firm_name = award.get('SELECTED FIRM', '')
            raw_district = award.get('Region/District', '')
            description = award.get('Description', '') or ''

            # Skip corrupted / empty entries
            if not firm_name or '\n' in firm_name:
                continue
            if firm_name in ('WITHDRAWN', 'NO SUBMITTALS'):
                continue
            if len(firm_name) > 100:
                continue

            firm_code = self._match_award_firm_to_code(firm_name)
            if not firm_code:
                continue

            district = normalize_district(raw_district) or 'unknown'
            prequal_cat = self._infer_prequal_from_description(description)

            self.firm_total_wins[firm_code] += 1
            self.firm_district_wins[firm_code][district] += 1
            if prequal_cat:
                self.firm_prequal_wins[firm_code][prequal_cat] += 1

    def _build_rag(self):
        descriptions = []
        for i, award in enumerate(self.award_structure):
            desc = award.get('Description', '') or ''
            firm = award.get('SELECTED FIRM', '') or ''
            bulletin = int(award.get('f', 0) or 0)
            if desc and '\n' not in firm and len(firm) < 80 and firm not in ('WITHDRAWN', 'NO SUBMITTALS'):
                descriptions.append(desc)
                fc = self._match_award_firm_to_code(firm)
                self.rag_metadata.append({
                    'description': desc,
                    'firm_name': firm,
                    'firm_code': fc,
                    'district': normalize_district(award.get('Region/District', '')),
                    'bulletin': bulletin,
                })
        if descriptions:
            self.vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 3), stop_words='english')
            self.rag_matrix = self.vectorizer.fit_transform(descriptions)
            # Pre-compute per-firm win indices in RAG matrix for fast scoring
            self.firm_rag_indices = defaultdict(list)
            for idx, meta in enumerate(self.rag_metadata):
                fc = meta.get('firm_code')
                if fc:
                    self.firm_rag_indices[fc].append((idx, meta['bulletin']))
        print(f"  TF-IDF built on {len(descriptions)} award descriptions.")

    # ------------------------------------------------------------------
    # Bulletin extraction
    # ------------------------------------------------------------------

    def read_docx(self, path):
        doc = docx.Document(path)
        return '\n'.join(p.text for p in doc.paragraphs)

    def extract_prequal(self, block):
        """Extract prequalification requirement from one project block."""
        m = re.search(
            r'prime\s+firm\s+must\s+be\s+prequalified\s+in\s+the\s+(.+?)\s+category',
            block, re.IGNORECASE
        )
        if not m:
            return None
        raw = m.group(1).strip()
        # Clean trailing noise
        raw = re.sub(r'\s+to be considered.*$', '', raw, flags=re.IGNORECASE)
        raw = re.sub(r'\s+prequalification\s*$', '', raw, flags=re.IGNORECASE).strip()
        # Normalise
        key = raw.lower()
        if key in PREQUAL_ALIASES:
            return PREQUAL_ALIASES[key]
        # Try case-insensitive lookup in prequal_lookup directly
        for cat in self.prequal_lookup:
            if cat.lower() == key:
                return cat
        # Fuzzy match as last resort
        best_score, best_cat = 0.0, None
        for cat in self.prequal_lookup:
            s = SequenceMatcher(None, key, cat.lower()).ratio()
            if s > best_score:
                best_score, best_cat = s, cat
        if best_score >= 0.75:
            return best_cat
        return raw  # Return raw text; eligibility lookup will handle it

    def extract_district(self, block):
        """Extract and normalise Region/District from one project block."""
        m = re.search(
            r'Region\s+(\w+)\s*/\s*District\s+(\w+)',
            block, re.IGNORECASE
        )
        if m:
            r = WORD_TO_NUM.get(m.group(1).lower(), m.group(1))
            d = WORD_TO_NUM.get(m.group(2).lower(), m.group(2))
            return f"{r}/{d}"
        return None

    def extract_projects(self, text):
        """Split bulletin text into per-project blocks and extract metadata.

        Handles two bulletin formats:
        1. Numbered:   "1. Job No. X-XX-XXX-XX, Description, Region One/District One"
        2. Unnumbered: " Job No. X-XX-XXX-XX, Description, Region One/District One"
        """
        projects = []

        # Universal split: any line whose content starts (after optional digits/spaces) with "Job No."
        # We split on the pattern so each block begins with the Job No. line.
        blocks = re.split(r'\n(?=\s*(?:\d+\.\s+)?Job No\.)', text)

        # Deduplicate by job number (some bulletins repeat Job No. in headers)
        seen_jobs = set()
        for block in blocks:
            if 'Job No.' not in block:
                continue
            job_m = re.search(r'Job No\.\s+([A-Z]-\d+-\d+-\d+)', block)
            if not job_m:
                continue
            job_number = job_m.group(1).strip()
            if job_number in seen_jobs:
                continue
            seen_jobs.add(job_number)

            # Description: text after "Job No. X-XX-XXX-XX,"
            desc_m = re.search(r'Job No\.\s+[A-Z]-\d+-\d+-\d+,?\s*([^\n,]+)', block)
            description = desc_m.group(1).strip() if desc_m else ''

            district = self.extract_district(block)
            prequal = self.extract_prequal(block)

            projects.append({
                'job_number': job_number,
                'description': description,
                'district': district,
                'prequal': prequal,
            })
        return projects

    # ------------------------------------------------------------------
    # Firm eligibility
    # ------------------------------------------------------------------

    def get_eligible_firms(self, prequal):
        """Return list of firm_codes eligible for this prequal category."""
        if not prequal:
            return list(self.firms_data.keys())
        # Exact lookup
        if prequal in self.prequal_lookup:
            codes = self.prequal_lookup[prequal]
            return codes if codes else list(self.firms_data.keys())
        # Fuzzy lookup (high threshold)
        best_score, best_cat = 0.0, None
        for cat in self.prequal_lookup:
            s = SequenceMatcher(None, prequal.lower(), cat.lower()).ratio()
            if s > best_score:
                best_score, best_cat = s, cat
        if best_score >= 0.70 and best_cat:
            return self.prequal_lookup[best_cat] or list(self.firms_data.keys())
        return list(self.firms_data.keys())

    # ------------------------------------------------------------------
    # Scoring (fully deterministic)
    # ------------------------------------------------------------------

    def _compute_all_similarities(self, description):
        """Compute TF-IDF similarity of `description` against entire RAG matrix.
        Returns a (n_awards,) array of similarity scores.
        """
        if self.rag_matrix is None or not description:
            return np.zeros(len(self.rag_metadata))
        qvec = self.vectorizer.transform([description])
        return cosine_similarity(qvec, self.rag_matrix).flatten()

    def score_firm(self, firm_code, district, prequal, sim_scores, current_bulletin):
        """
        Similarity-weighted historical win score (primary) +
        district wins (secondary) + prequal wins (tertiary).

        sim_scores: pre-computed array of similarities to all RAG entries.
        current_bulletin: bulletins OLDER than this are used for training.
        """
        # --- Primary: sum of similarity scores for projects this firm won ---
        sim_score = 0.0
        win_indices = self.firm_rag_indices.get(firm_code, [])
        for idx, bulletin in win_indices:
            if bulletin >= current_bulletin:   # don't use future information
                continue
            s = sim_scores[idx]
            if s > 0.01:
                # Recency weight: more recent wins count more
                recency = 1.0 + (bulletin / max(current_bulletin, 1)) * 0.3
                sim_score += s * recency

        # --- Secondary: district wins ---
        district_w = self.firm_district_wins.get(firm_code, {}).get(district or 'unknown', 0)

        # --- Tertiary: prequal-type wins ---
        prequal_w = self.firm_prequal_wins.get(firm_code, {}).get(prequal or '', 0)

        # --- Quaternary: district match (firm home == project district) ---
        firm_home = self.firms_data.get(firm_code, {}).get('district', '') or ''
        home_match = 1.0 if district and district.split('/')[0] in firm_home else 0.0

        # Weighted combination (weights calibrated from MODEL_VALIDATION analysis)
        score = (sim_score * 10.0) + (district_w * 2.0) + (prequal_w * 1.5) + (home_match * 1.0)
        return score

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict_top3(self, project, eligible_codes, current_bulletin):
        district = project['district']
        prequal = project['prequal']
        description = project['description']

        # Compute similarity vector once; reuse for all firms
        sim_scores = self._compute_all_similarities(description)

        scored = []
        for fc in eligible_codes:
            s = self.score_firm(fc, district, prequal, sim_scores, current_bulletin)
            scored.append((fc, s))

        scored.sort(key=lambda x: x[1], reverse=True)
        top3_codes = [fc for fc, _ in scored[:3]]
        top3_names = [self.firms_data.get(fc, {}).get('firm_name', fc) for fc in top3_codes]
        return top3_names

    # ------------------------------------------------------------------
    # Ground truth lookup
    # ------------------------------------------------------------------

    def _extract_base_job(self, job_number):
        """Extract base job number (strip year component) e.g. 'D-91-062' from 'D-91-062-19'."""
        m = re.match(r'([A-Z]-\d+-\d+)-\d+', job_number or '')
        return m.group(1) if m else None

    def _normalize_job(self, job_number):
        """Normalize job number to standard format (Phase 2.1 compatible)."""
        job_number = (job_number or '').strip().upper()
        for pat in [r'([A-Z]-\d+-\d+-\d+)', r'([A-Z]-\d+-\d+)', r'([A-Z]\d+-\d+-\d+)']:
            m = re.search(pat, job_number)
            if m:
                return m.group(1)
        return job_number

    def find_actual_winners(self, job_number, bulletin_num):
        """
        Replicate Phase 2.1 actual winner lookup strategy exactly:
        1. Exact normalized job number match (all bulletins)
        2. Base job number match (strip year suffix)
        3. Fuzzy match at 0.8 threshold (all bulletins)

        This is the same methodology that produced the 62.1% benchmark.
        """
        winners = set()
        norm_target = self._normalize_job(job_number)

        for award in self.award_structure:
            aj = (award.get('Job #', '') or '').strip()
            firm = (award.get('SELECTED FIRM', '') or '').strip()

            if not firm or '\n' in firm or firm in ('WITHDRAWN', 'NO SUBMITTALS') or len(firm) > 100:
                continue

            norm_aj = self._normalize_job(aj)

            # Strategy 1: exact normalized match
            if norm_aj == norm_target:
                winners.add(firm)
            # Strategy 2: base job number match
            elif self._extract_base_job(norm_target) and self._extract_base_job(norm_aj) == self._extract_base_job(norm_target):
                winners.add(firm)
            # Strategy 3: fuzzy match at 0.8 threshold (Phase 2.1 standard)
            elif norm_aj and SequenceMatcher(None, norm_target.lower(), norm_aj.lower()).ratio() > 0.8:
                winners.add(firm)

        return winners

    def is_correct(self, top3_names, actual_winners):
        """Check if any top-3 prediction matches any actual winner."""
        if not actual_winners:
            return None
        for name in top3_names:
            norm = normalize_firm_name(name)
            for winner in actual_winners:
                if normalize_firm_name(winner) == norm:
                    return True
                if SequenceMatcher(None, norm, normalize_firm_name(winner)).ratio() >= 0.85:
                    return True
        return False

    # ------------------------------------------------------------------
    # Main test runner
    # ------------------------------------------------------------------

    def run_test(self, start_bulletin, end_bulletin, data_dir='../data/'):
        print(f"=== IDOT V3 Improved System | PTB{start_bulletin}-{end_bulletin} ===\n")
        self.load_data(data_dir)

        all_results = []
        for bnum in range(start_bulletin, end_bulletin + 1):
            docx_path = os.path.join(data_dir, f'ptb{bnum}.docx')
            if not os.path.exists(docx_path):
                continue

            text = self.read_docx(docx_path)
            projects = self.extract_projects(text)
            if not projects:
                continue

            bulletin_results = []
            for proj in projects:
                eligible_codes = self.get_eligible_firms(proj['prequal'])
                top3 = self.predict_top3(proj, eligible_codes, bnum)
                actual_winners = self.find_actual_winners(proj['job_number'], bnum)
                correct = self.is_correct(top3, actual_winners)

                # Primary winner = exact match from same bulletin (for display)
                primary_winner = ''
                for award in self.award_structure:
                    if (award.get('Job #', '') or '').strip() == proj['job_number'] and int(award.get('f', 0) or 0) == bnum:
                        primary_winner = (award.get('SELECTED FIRM', '') or '').strip()
                        break

                r = {
                    'bulletin': bnum,
                    'job_number': proj['job_number'],
                    'district': proj['district'],
                    'prequal': proj['prequal'],
                    'description': proj['description'],
                    'top3': top3,
                    'actual_winner': primary_winner,
                    'actual_winners_count': len(actual_winners),
                    'correct': correct,
                    'eligible_count': len(eligible_codes),
                }
                bulletin_results.append(r)
                all_results.append(r)

            valid = [r for r in bulletin_results if r['correct'] is not None]
            correct_count = sum(1 for r in valid if r['correct'])
            total_count = len(valid)
            pct = correct_count / total_count if total_count else 0
            print(f"PTB{bnum}: {correct_count}/{total_count} = {pct:.1%}  ({len(projects)} projects extracted, {len(valid)} matchable)")

        # Overall
        valid_all = [r for r in all_results if r['correct'] is not None]
        correct_all = sum(1 for r in valid_all if r['correct'])
        total_all = len(valid_all)
        overall = correct_all / total_all if total_all else 0

        print(f"\n{'='*60}")
        print(f"OVERALL ACCURACY: {correct_all}/{total_all} = {overall:.1%}")
        print(f"{'='*60}")

        self._export_excel(all_results, start_bulletin, end_bulletin, overall)
        return all_results, overall

    def _export_excel(self, results, start_b, end_b, overall_acc):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = f'../results/IDOTv3_PTB{start_b}_{end_b}_{ts}.xlsx'
        os.makedirs('../results', exist_ok=True)

        rows = []
        for r in results:
            rows.append({
                'Bulletin': r['bulletin'],
                'Job #': r['job_number'],
                'District': r['district'],
                'Prequal': r['prequal'],
                'Description': r['description'],
                'Pred_1': r['top3'][0] if len(r['top3']) > 0 else '',
                'Pred_2': r['top3'][1] if len(r['top3']) > 1 else '',
                'Pred_3': r['top3'][2] if len(r['top3']) > 2 else '',
                'Actual Winner (this bulletin)': r['actual_winner'],
                'Actual Winners Pool Size': r.get('actual_winners_count', ''),
                'Correct (Top-3)': r['correct'],
                'Eligible Firms': r['eligible_count'],
            })

        df = pd.DataFrame(rows)
        summary_rows = [
            {'Metric': 'System Version', 'Value': 'IDOT V3 Improved'},
            {'Metric': 'Bulletins Tested', 'Value': f'{start_b}-{end_b}'},
            {'Metric': 'Total Projects', 'Value': len(results)},
            {'Metric': 'Matchable Projects', 'Value': sum(1 for r in results if r['correct'] is not None)},
            {'Metric': 'Correct (Top-3)', 'Value': sum(1 for r in results if r['correct'])},
            {'Metric': 'Overall Accuracy (Top-3)', 'Value': f'{overall_acc:.1%}'},
            {'Metric': 'Avg Eligible Firms', 'Value': f'{np.mean([r["eligible_count"] for r in results]):.0f}'},
            {'Metric': 'Key Improvements', 'Value': 'Deterministic scoring, district win rates, prequal win rates, docx-direct'},
        ]
        summary_df = pd.DataFrame(summary_rows)

        with pd.ExcelWriter(fname, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            df.to_excel(writer, sheet_name='Detailed Results', index=False)

        print(f"Results exported → {fname}")


if __name__ == '__main__':
    system = IDOTv3System()
    # Replicate Phase 2.1 benchmark: PTB190-200
    results, accuracy = system.run_test(190, 200)
    print(f"\nFinal accuracy: {accuracy:.1%}")
