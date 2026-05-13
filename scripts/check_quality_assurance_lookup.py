#!/usr/bin/env python3
"""
Check Quality Assurance in Prequal Lookup
Check if the Quality Assurance category exists in prequal_lookup.json
"""

import json

def check_quality_assurance():
    """Check Quality Assurance categories in prequal_lookup.json"""
    
    print("🔍 CHECKING PREQUAL_LOOKUP.JSON FOR QUALITY ASSURANCE")
    print("=" * 80)
    
    # Load prequal_lookup.json
    with open('../data/prequal_lookup.json', 'r') as f:
        data = json.load(f)
    
    # Find quality-related categories
    quality_keys = [k for k in data.keys() if 'quality' in k.lower() or 'qa' in k.lower()]
    
    print(f"Found {len(quality_keys)} quality-related categories:")
    for k in quality_keys:
        print(f"  • {k}")
        print(f"    Number of firms: {len(data[k])}")
    
    print()
    
    # Look for exact match
    exact_match = 'Special Services (Quality Assurance: QA PCC & Aggregate)'
    print(f"🔍 LOOKING FOR EXACT MATCH:")
    print(f"Searching for: {exact_match}")
    print(f"Found in keys: {exact_match in data.keys()}")
    
    if exact_match in data.keys():
        print(f"✅ EXACT MATCH FOUND!")
        print(f"Number of firms: {len(data[exact_match])}")
    else:
        print(f"❌ EXACT MATCH NOT FOUND!")
        
        # Try fuzzy matching
        print(f"\n🔍 TRYING FUZZY MATCHING:")
        for key in data.keys():
            if 'quality' in key.lower() and 'pcc' in key.lower():
                print(f"  Potential match: {key}")
                print(f"    Number of firms: {len(data[key])}")
    
    # Show all Special Services categories
    print(f"\n🔍 ALL SPECIAL SERVICES CATEGORIES:")
    special_services = [k for k in data.keys() if k.startswith('Special Services')]
    for k in special_services:
        print(f"  • {k}")
        print(f"    Number of firms: {len(data[k])}")

if __name__ == "__main__":
    check_quality_assurance()





