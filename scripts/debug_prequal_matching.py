#!/usr/bin/env python3
"""
Debug Prequalification Matching
==============================
Debug the prequalification matching logic.
"""

import json

def debug_prequal_matching():
    """Debug prequalification matching"""
    
    # Load prequal_lookup
    with open('../data/prequal_lookup.json', 'r') as f:
        prequal_lookup = json.load(f)
    
    # Test case
    extracted_prequal = "Location/Design Studies (New Construction/Major Reconstruction)"
    expected_lookup = "Location Design Studies (New Construction:Major Reconstruction)"
    
    print("🔍 DEBUGGING PREQUALIFICATION MATCHING")
    print("=" * 50)
    print(f"Extracted: '{extracted_prequal}'")
    print(f"Expected:  '{expected_lookup}'")
    print()
    
    # Check if expected_lookup exists in prequal_lookup
    print("📋 CHECKING PREQUAL_LOOKUP:")
    print("-" * 30)
    if expected_lookup in prequal_lookup:
        print(f"✅ '{expected_lookup}' found in prequal_lookup")
    else:
        print(f"❌ '{expected_lookup}' NOT found in prequal_lookup")
    
    # Check what Location Design Studies entries exist
    location_entries = [k for k in prequal_lookup.keys() if 'location' in k.lower() and 'design' in k.lower()]
    print(f"\nLocation Design Studies entries: {location_entries}")
    
    # Test fuzzy matching
    print(f"\n🔍 TESTING FUZZY MATCHING:")
    print("-" * 30)
    
    # Normalize strings
    extracted = extracted_prequal.lower().replace(':', '').replace('-', ' ').strip()
    print(f"Normalized extracted: '{extracted}'")
    
    for lookup_category in prequal_lookup.keys():
        lookup = lookup_category.lower().replace(':', '').replace('-', ' ').strip()
        print(f"Normalized lookup: '{lookup}'")
        
        # Direct match
        if extracted == lookup:
            print(f"✅ DIRECT MATCH: '{lookup_category}'")
            break
        
        # Partial match
        if extracted in lookup or lookup in extracted:
            print(f"✅ PARTIAL MATCH: '{lookup_category}'")
            break
        
        # Special Location/Design Studies handling
        if 'location' in extracted and 'design' in extracted and 'studies' in extracted:
            if 'location' in lookup and 'design' in lookup and 'studies' in lookup:
                print(f"🔍 LOCATION/DESIGN STUDIES MATCH ATTEMPT:")
                print(f"  Extracted: '{extracted_prequal}'")
                print(f"  Lookup:   '{lookup_category}'")
                
                # Check subcategories
                extracted_sub = extracted_prequal.split('(')[-1].split(')')[0] if '(' in extracted_prequal else ''
                lookup_sub = lookup_category.split('(')[-1].split(')')[0] if '(' in lookup_category else ''
                
                print(f"  Extracted sub: '{extracted_sub}'")
                print(f"  Lookup sub:   '{lookup_sub}'")
                
                # Normalize subcategories
                extracted_sub_norm = extracted_sub.replace('/', ':').replace(':', ':').lower()
                lookup_sub_norm = lookup_sub.replace('/', ':').replace(':', ':').lower()
                
                print(f"  Normalized extracted sub: '{extracted_sub_norm}'")
                print(f"  Normalized lookup sub:   '{lookup_sub_norm}'")
                
                if extracted_sub_norm == lookup_sub_norm:
                    print(f"✅ SUBCATEGORY MATCH: '{lookup_category}'")
                    break
                else:
                    print(f"❌ SUBCATEGORY MISMATCH")
    
    # Show all Location Design Studies subcategories
    print(f"\n📋 ALL LOCATION DESIGN STUDIES SUBCATEGORIES:")
    print("-" * 50)
    location_data = prequal_lookup.get('Location Design Studies', {})
    for subcat_key, subcat_data in location_data.get('sub_categories', {}).items():
        print(f"  {subcat_data['full_prequal_name']}")

if __name__ == "__main__":
    debug_prequal_matching()




