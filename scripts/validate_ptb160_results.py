#!/usr/bin/env python3
"""
Validate PTB160 Results
======================
Analyze and validate the PTB160 extraction results.
"""

import json
from collections import Counter

def validate_ptb160_results():
    """Validate PTB160 extraction results"""
    
    # Load the extracted results
    with open('ptb_processing_reports/ptb160_precise_enhanced_awards.json', 'r') as f:
        awards = json.load(f)
    
    print("🔍 PTB160 RESULTS VALIDATION")
    print("=" * 50)
    
    # Basic statistics
    total_awards = len(awards)
    successful_matches = len([a for a in awards if a.get('ptb_match_status') == 'SUCCESS'])
    missing_ptb_data = len([a for a in awards if a.get('ptb_match_status') == 'NO_PTB_DATA'])
    
    print(f"📊 BASIC STATISTICS:")
    print(f"   Total awards: {total_awards}")
    print(f"   ✅ Successful matches: {successful_matches}")
    print(f"   ❌ Missing PTB data: {missing_ptb_data}")
    print(f"   📈 Success rate: {(successful_matches/total_awards*100):.1f}%")
    print()
    
    # Analyze prequalifications found
    all_prequals = []
    awards_with_prequals = []
    
    for award in awards:
        prequals = award.get('required_prequals', [])
        if prequals:
            all_prequals.extend(prequals)
            awards_with_prequals.append(award)
    
    print(f"📋 PREQUALIFICATION ANALYSIS:")
    print(f"   Awards with prequalifications: {len(awards_with_prequals)}")
    print(f"   Total prequalifications found: {len(all_prequals)}")
    print(f"   Unique prequalifications: {len(set(all_prequals))}")
    print()
    
    # Show unique prequalifications found
    unique_prequals = sorted(set(all_prequals))
    print(f"📋 UNIQUE PREQUALIFICATIONS FOUND ({len(unique_prequals)}):")
    for i, prequal in enumerate(unique_prequals, 1):
        print(f"   {i:2d}. {prequal}")
    print()
    
    # Show prequalification frequency
    prequal_counts = Counter(all_prequals)
    print(f"📊 PREQUALIFICATION FREQUENCY:")
    for prequal, count in prequal_counts.most_common():
        print(f"   {prequal}: {count} times")
    print()
    
    # Show awards with prequalifications
    print(f"📋 AWARDS WITH PREQUALIFICATIONS:")
    for i, award in enumerate(awards_with_prequals, 1):
        print(f"   {i:2d}. {award.get('Job #')} → {award.get('SELECTED FIRM')}")
        for prequal in award.get('required_prequals', []):
            print(f"       - {prequal}")
    print()
    
    # Show awards without prequalifications
    awards_without_prequals = [a for a in awards if not a.get('required_prequals')]
    print(f"📋 AWARDS WITHOUT PREQUALIFICATIONS ({len(awards_without_prequals)}):")
    for i, award in enumerate(awards_without_prequals, 1):
        print(f"   {i:2d}. {award.get('Job #')} → {award.get('SELECTED FIRM')}")
    print()
    
    # Validate specific cases
    print(f"🔍 SPECIFIC CASE VALIDATION:")
    
    # Check P-30-006-12 (our test case)
    p30006 = [a for a in awards if a.get('Job #') == 'P-30-006-12']
    if p30006:
        award = p30006[0]
        print(f"   ✅ P-30-006-12: {len(award.get('required_prequals', []))} prequals")
        for prequal in award.get('required_prequals', []):
            print(f"       - {prequal}")
    else:
        print(f"   ❌ P-30-006-12: Not found")
    
    # Check for any generic categories
    generic_categories = ['Other', 'Special Services', 'Structures', 'Highways', 'Environmental Reports']
    found_generic = []
    for prequal in unique_prequals:
        if prequal in generic_categories:
            found_generic.append(prequal)
    
    if found_generic:
        print(f"   ⚠️  Found generic categories: {found_generic}")
    else:
        print(f"   ✅ No generic categories found - all are specific prequalifications")
    
    # Check for any awards with too many prequalifications (potential false positives)
    awards_with_many_prequals = [a for a in awards if len(a.get('required_prequals', [])) > 5]
    if awards_with_many_prequals:
        print(f"   ⚠️  Awards with >5 prequalifications (potential false positives):")
        for award in awards_with_many_prequals:
            print(f"       {award.get('Job #')}: {len(award.get('required_prequals', []))} prequals")
    else:
        print(f"   ✅ No awards with excessive prequalifications")
    
    print()
    
    # Summary
    print(f"📊 VALIDATION SUMMARY:")
    print(f"   ✅ Success rate: {(successful_matches/total_awards*100):.1f}%")
    print(f"   ✅ Awards with prequalifications: {len(awards_with_prequals)}")
    print(f"   ✅ Unique prequalifications: {len(unique_prequals)}")
    print(f"   ✅ No generic categories: {'Yes' if not found_generic else 'No'}")
    print(f"   ✅ No excessive prequalifications: {'Yes' if not awards_with_many_prequals else 'No'}")
    
    return {
        'total_awards': total_awards,
        'successful_matches': successful_matches,
        'success_rate': successful_matches/total_awards*100,
        'awards_with_prequals': len(awards_with_prequals),
        'unique_prequals': len(unique_prequals),
        'unique_prequal_list': unique_prequals,
        'no_generic_categories': not found_generic,
        'no_excessive_prequals': not awards_with_many_prequals
    }

if __name__ == "__main__":
    validation_results = validate_ptb160_results()




