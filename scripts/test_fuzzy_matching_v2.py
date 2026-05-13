#!/usr/bin/env python3
"""
Test Fuzzy Matching V2 for Aerial Mapping and Advanced Typical
Test the fuzzy matching function directly for the new cases
"""

import json

def test_fuzzy_matching_v2():
    """Test fuzzy matching for new cases"""
    
    print("🔍 TESTING FUZZY MATCHING V2 FOR NEW CASES")
    print("=" * 80)
    
    # Load prequal_lookup.json
    with open('../data/prequal_lookup.json', 'r') as f:
        prequal_lookup = json.load(f)
    
    # Test cases
    test_cases = [
        {
            'name': 'P-95-052-11 Aerial Mapping',
            'extracted': 'Special Services (Aerial Mapping)',
            'expected': 'Special Services (Aerial Mapping: LiDAR)'
        },
        {
            'name': 'D-30-001-12 Advanced Typical',
            'extracted': 'Structures (Highway: Advanced Typical)',
            'expected': 'Structures (Highway- Advanced Typical)'
        }
    ]
    
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
        
        # Special handling for Aerial Mapping variations
        if 'aerial mapping' in extracted and 'aerial mapping' in lookup:
            print("🔍 Testing Aerial Mapping special handling...")
            # Handle missing ": LiDAR" suffix - check if one has "lidar" and the other doesn't
            extracted_has_lidar = 'lidar' in extracted
            lookup_has_lidar = 'lidar' in lookup
            
            if extracted_has_lidar != lookup_has_lidar:
                print("🔍 Testing LiDAR suffix handling...")
                # Remove "lidar" from both and compare
                extracted_clean = extracted.replace('lidar', '').strip()
                lookup_clean = lookup.replace('lidar', '').strip()
                
                # Clean up extra spaces
                extracted_clean = ' '.join(extracted_clean.split())
                lookup_clean = ' '.join(lookup_clean.split())
                
                print(f"LiDAR cleaned extracted: '{extracted_clean}'")
                print(f"LiDAR cleaned lookup: '{lookup_clean}'")
                
                if extracted_clean == lookup_clean:
                    print("✅ Aerial Mapping special match!")
                    return True
        
        # Special handling for Structures variations
        if 'structures' in extracted and 'structures' in lookup:
            print("🔍 Testing Structures special handling...")
            # Handle ":" vs "-" in "Advanced Typical"
            if 'advanced typical' in extracted and 'advanced typical' in lookup:
                print("🔍 Testing Advanced Typical special handling...")
                # Normalize both by replacing ":" with "-" and clean up spaces
                extracted_clean = extracted.replace(':', '-')
                lookup_clean = lookup.replace(':', '-')
                
                # Clean up extra spaces
                extracted_clean = ' '.join(extracted_clean.split())
                lookup_clean = ' '.join(lookup_clean.split())
                
                print(f"Advanced Typical extracted_clean: '{extracted_clean}'")
                print(f"Advanced Typical lookup_clean: '{lookup_clean}'")
                
                if extracted_clean == lookup_clean:
                    print("✅ Advanced Typical special match!")
                    return True
        
        print("❌ No match found")
        return False
    
    # Test each case
    for test_case in test_cases:
        print(f"\n🔍 TESTING: {test_case['name']}")
        print("-" * 50)
        print(f"Extracted: {test_case['extracted']}")
        print(f"Expected: {test_case['expected']}")
        print(f"Available in lookup: {test_case['expected'] in prequal_lookup.keys()}")
        print()
        
        result = fuzzy_match_prequal(test_case['extracted'], test_case['expected'])
        print(f"Final result: {result}")
        
        # Test with all categories
        print(f"\n🔍 TESTING WITH ALL CATEGORIES:")
        found_match = False
        for category in prequal_lookup.keys():
            if fuzzy_match_prequal(test_case['extracted'], category):
                print(f"✅ MATCH FOUND: {category}")
                found_match = True
                break
        
        if not found_match:
            print("❌ No match found in any category")

if __name__ == "__main__":
    test_fuzzy_matching_v2()
