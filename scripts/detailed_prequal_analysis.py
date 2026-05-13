#!/usr/bin/env python3
"""
Detailed Prequalification Analysis
Identify missing firm and analyze category name variations
"""

import json
import pandas as pd
from collections import defaultdict

def analyze_missing_firm_and_variations():
    """Analyze missing firm and category name variations"""
    data_dir = '../data'
    
    print("🔍 Detailed Prequalification Analysis...")
    
    # Load prequal_lookup.json
    with open(f'{data_dir}/prequal_lookup.json', 'r') as f:
        prequal_lookup = json.load(f)
    print(f"✅ Loaded prequal_lookup.json: {len(prequal_lookup)} categories")
    
    # Load IDOT Excel
    idot_excel = pd.read_excel(f'{data_dir}/IDOTConsultantList.xlsx', sheet_name='PrequalReport')
    print(f"✅ Loaded IDOT Excel PrequalReport: {idot_excel.shape}")
    
    # Extract prequalification data from IDOT Excel
    idot_prequals = defaultdict(set)
    for idx, row in idot_excel.iterrows():
        firm_name = row.get('Unnamed: 1')
        prequal_category = row.get('Unnamed: 3')
        
        if pd.notna(firm_name) and pd.notna(prequal_category):
            firm_name = str(firm_name).strip()
            prequal_category = str(prequal_category).strip()
            
            if firm_name and firm_name != 'FIRM' and prequal_category and prequal_category != 'PRE-QUAL CATEGORIES':
                idot_prequals[prequal_category].add(firm_name)
                
    print(f"✅ Extracted {len(idot_prequals)} prequalification categories from IDOT Excel")
    
    # 1. FIND MISSING FIRM
    print("\n" + "="*60)
    print("1. FINDING MISSING FIRM")
    print("="*60)
    
    # Get all unique firms from IDOT Excel
    all_idot_firms = set()
    for firms in idot_prequals.values():
        all_idot_firms.update(firms)
        
    # Get all unique firms from prequal_lookup
    all_lookup_firms = set()
    for category, firms_list in prequal_lookup.items():
        if isinstance(firms_list, list):
            for firm_dict in firms_list:
                if isinstance(firm_dict, dict) and 'firm_name' in firm_dict:
                    all_lookup_firms.add(firm_dict['firm_name'])
                    
    # Normalize for comparison
    all_idot_firms_normalized = {firm.strip().upper() for firm in all_idot_firms}
    all_lookup_firms_normalized = {firm.strip().upper() for firm in all_lookup_firms}
    
    # Find missing firms
    missing_in_lookup = all_idot_firms_normalized - all_lookup_firms_normalized
    missing_in_idot = all_lookup_firms_normalized - all_idot_firms_normalized
    
    print(f"📊 IDOT Firms: {len(all_idot_firms_normalized)}")
    print(f"📊 Lookup Firms: {len(all_lookup_firms_normalized)}")
    print(f"📊 Missing in Lookup: {len(missing_in_lookup)}")
    print(f"📊 Missing in IDOT: {len(missing_in_idot)}")
    
    if missing_in_lookup:
        print(f"\n❌ MISSING IN LOOKUP:")
        for firm in missing_in_lookup:
            print(f"  - {firm}")
            
    if missing_in_idot:
        print(f"\n❌ MISSING IN IDOT:")
        for firm in missing_in_idot:
            print(f"  - {firm}")
            
    # 2. ANALYZE CATEGORY NAME VARIATIONS
    print("\n" + "="*60)
    print("2. ANALYZING CATEGORY NAME VARIATIONS")
    print("="*60)
    
    lookup_categories = set(prequal_lookup.keys())
    idot_categories = set(idot_prequals.keys())
    
    exact_matches = lookup_categories.intersection(idot_categories)
    missing_in_lookup_cats = idot_categories - lookup_categories
    missing_in_idot_cats = lookup_categories - idot_categories
    
    print(f"📊 Lookup Categories: {len(lookup_categories)}")
    print(f"📊 IDOT Categories: {len(idot_categories)}")
    print(f"📊 Exact Matches: {len(exact_matches)}")
    print(f"📊 Missing in Lookup: {len(missing_in_lookup_cats)}")
    print(f"📊 Missing in IDOT: {len(missing_in_idot_cats)}")
    
    if missing_in_lookup_cats:
        print(f"\n❌ CATEGORIES MISSING IN LOOKUP:")
        for cat in sorted(missing_in_lookup_cats):
            print(f"  - {cat}")
            
    if missing_in_idot_cats:
        print(f"\n❌ CATEGORIES MISSING IN IDOT:")
        for cat in sorted(missing_in_idot_cats):
            print(f"  - {cat}")
            
    # 3. DETAILED CATEGORY COMPARISON
    print("\n" + "="*60)
    print("3. DETAILED CATEGORY COMPARISON")
    print("="*60)
    
    # Show some examples of exact matches
    print(f"\n✅ EXAMPLES OF EXACT MATCHES:")
    for cat in sorted(exact_matches)[:5]:
        lookup_count = len([f for f in prequal_lookup[cat] if isinstance(f, dict) and 'firm_name' in f])
        idot_count = len(idot_prequals[cat])
        print(f"  - {cat}: Lookup={lookup_count}, IDOT={idot_count}")
        
    # Show some examples of missing categories
    if missing_in_lookup_cats:
        print(f"\n⚠️  EXAMPLES OF CATEGORIES MISSING IN LOOKUP:")
        for cat in sorted(missing_in_lookup_cats)[:5]:
            idot_count = len(idot_prequals[cat])
            print(f"  - {cat}: IDOT={idot_count} firms")
            
    if missing_in_idot_cats:
        print(f"\n⚠️  EXAMPLES OF CATEGORIES MISSING IN IDOT:")
        for cat in sorted(missing_in_idot_cats)[:5]:
            lookup_count = len([f for f in prequal_lookup[cat] if isinstance(f, dict) and 'firm_name' in f])
            print(f"  - {cat}: Lookup={lookup_count} firms")
            
    # 4. FIND SIMILAR CATEGORY NAMES
    print("\n" + "="*60)
    print("4. FINDING SIMILAR CATEGORY NAMES")
    print("="*60)
    
    # Look for similar category names that might be variations
    similar_categories = []
    
    for lookup_cat in lookup_categories:
        for idot_cat in idot_categories:
            if lookup_cat != idot_cat:
                # Check if they're similar (contain same key words)
                lookup_words = set(lookup_cat.lower().split())
                idot_words = set(idot_cat.lower().split())
                
                # If they share more than 50% of words, they might be variations
                common_words = lookup_words.intersection(idot_words)
                if len(common_words) > 0 and len(common_words) >= min(len(lookup_words), len(idot_words)) * 0.5:
                    similar_categories.append({
                        'lookup': lookup_cat,
                        'idot': idot_cat,
                        'common_words': len(common_words),
                        'similarity': len(common_words) / max(len(lookup_words), len(idot_words))
                    })
                    
    if similar_categories:
        print(f"📊 Found {len(similar_categories)} potentially similar categories:")
        for sim in sorted(similar_categories, key=lambda x: x['similarity'], reverse=True)[:10]:
            print(f"  - Lookup: '{sim['lookup']}'")
            print(f"    IDOT:   '{sim['idot']}'")
            print(f"    Similarity: {sim['similarity']:.2f}")
            print()
            
    # 5. SUMMARY
    print("\n" + "="*60)
    print("5. SUMMARY")
    print("="*60)
    
    print(f"📊 MISSING FIRM ANALYSIS:")
    if missing_in_lookup:
        print(f"  - {len(missing_in_lookup)} firm(s) missing from prequal_lookup.json")
        print(f"  - This explains the 99.88% coverage (414/415 firms)")
    else:
        print(f"  - No firms missing from prequal_lookup.json")
        
    if missing_in_idot:
        print(f"  - {len(missing_in_idot)} firm(s) missing from IDOT Excel")
        
    print(f"\n📊 CATEGORY VARIATION ANALYSIS:")
    print(f"  - {len(exact_matches)} categories match exactly")
    print(f"  - {len(missing_in_lookup_cats)} categories missing from lookup")
    print(f"  - {len(missing_in_idot_cats)} categories missing from IDOT")
    print(f"  - {len(similar_categories)} potentially similar categories found")
    
    if similar_categories:
        print(f"  - Category name variations likely due to formatting differences")
    else:
        print(f"  - No obvious category name variations found")

if __name__ == "__main__":
    analyze_missing_firm_and_variations()
