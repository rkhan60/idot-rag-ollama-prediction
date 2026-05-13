#!/usr/bin/env python3
"""
Test Fuzzy Matching for Quality Assurance
Test the fuzzy matching function directly for the C-93-084-11 case
"""

import json

def test_fuzzy_matching():
    """Test fuzzy matching for Quality Assurance case"""
    
    print("🔍 TESTING FUZZY MATCHING FOR QUALITY ASSURANCE")
    print("=" * 80)
    
    # Load prequal_lookup.json
    with open('../data/prequal_lookup.json', 'r') as f:
        prequal_lookup = json.load(f)
    
    # Test case from C-93-084-11
    extracted_prequal = 'Special Services (Quality Assurance: QA PCC & Aggregate)'
    expected_lookup = 'Special Services (Quality Assurance PCC & Aggregate)'
    
    print(f"Extracted prequalification: {extracted_prequal}")
    print(f"Expected lookup category: {expected_lookup}")
    print(f"Available in lookup: {expected_lookup in prequal_lookup.keys()}")
    print()
    
    # Test the fuzzy matching logic
    def fuzzy_match_prequal(extracted_prequal, lookup_category):
        """Fuzzy match extracted prequalification to lookup category"""
        # Normalize both strings
        extracted = extracted_prequal.lower().replace(':', '').replace('-', ' ').strip()
        lookup = lookup_category.lower().replace(':', '').replace('-', ' ').strip()
        
        print(f"Normalized extracted: '{extracted}'")
        print(f"Normalized lookup: '{lookup}'")
        
        # Direct match
        if extracted == lookup:
            print("✅ Direct match!")
            return True
        
        # Partial match
        if extracted in lookup or lookup in extracted:
            print("✅ Partial match!")
            return True
        
        # Handle common variations
        variations = {
            'roads & streets': 'roads and streets',
            'roads and streets': 'roads & streets',
            'quality assurance: qa': 'quality assurance',
            'quality assurance qa': 'quality assurance',
            'location/design': 'location design',
            'location design': 'location/design',
        }
        
        if extracted in variations and variations[extracted] == lookup:
            print("✅ Variation match!")
            return True
        if lookup in variations and variations[lookup] == extracted:
            print("✅ Variation match!")
            return True
        
        # Special handling for Quality Assurance variations
        if 'quality assurance' in extracted and 'quality assurance' in lookup:
            print("🔍 Testing Quality Assurance special handling...")
            # Remove "qa" and ":" from extracted
            extracted_clean = extracted.replace('qa', '').replace(':', '').strip()
            lookup_clean = lookup.replace('qa', '').replace(':', '').strip()
            
            # Clean up extra spaces
            extracted_clean = ' '.join(extracted_clean.split())
            lookup_clean = ' '.join(lookup_clean.split())
            
            print(f"Cleaned extracted: '{extracted_clean}'")
            print(f"Cleaned lookup: '{lookup_clean}'")
            
            if extracted_clean == lookup_clean:
                print("✅ Quality Assurance special match!")
                return True
        
        print("❌ No match found")
        return False
    
    # Test the function
    result = fuzzy_match_prequal(extracted_prequal, expected_lookup)
    print(f"\nFinal result: {result}")
    
    # Test with all Special Services categories
    print(f"\n🔍 TESTING WITH ALL SPECIAL SERVICES CATEGORIES:")
    special_services = [k for k in prequal_lookup.keys() if k.startswith('Special Services')]
    
    for category in special_services:
        if fuzzy_match_prequal(extracted_prequal, category):
            print(f"✅ MATCH FOUND: {category}")
            break
    else:
        print("❌ No match found in any Special Services category")

if __name__ == "__main__":
    test_fuzzy_matching()
