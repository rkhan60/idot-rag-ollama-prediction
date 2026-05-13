#!/usr/bin/env python3
"""
Bulletin vs Prequalification Mapping Analysis
Analyze format differences between bulletin text and prequal_lookup.json
"""

import json
import pandas as pd
from collections import defaultdict

def analyze_bulletin_prequal_mapping():
    """Analyze mapping between bulletin format and prequalification format"""
    data_dir = '../data'
    
    print("🔍 Analyzing Bulletin vs Prequalification Mapping...")
    
    # Load prequal_lookup.json
    with open(f'{data_dir}/prequal_lookup.json', 'r') as f:
        prequal_lookup = json.load(f)
    print(f"✅ Loaded prequal_lookup.json: {len(prequal_lookup)} categories")
    
    # Example bulletin formats (as you provided)
    bulletin_examples = [
        "Special Services (Quality Assurance HMA & Aggregate)",
        "Special Services (Quality Assurance PCC & Aggregate)", 
        "Special Services (Construction Inspection)"
    ]
    
    print(f"\n📋 BULLETIN FORMAT EXAMPLES:")
    for example in bulletin_examples:
        print(f"  - {example}")
        
    # Find corresponding prequal_lookup categories
    print(f"\n🔍 CORRESPONDING PREQUAL_LOOKUP CATEGORIES:")
    
    mapping_results = []
    
    for bulletin_format in bulletin_examples:
        # Clean the bulletin format for comparison
        cleaned_bulletin = bulletin_format.strip()
        
        # Try to find exact matches first
        exact_matches = []
        partial_matches = []
        
        for lookup_category in prequal_lookup.keys():
            # Normalize both for comparison
            lookup_normalized = lookup_category.lower().replace('-', ' ').replace(':', ' ').replace('/', ' ')
            bulletin_normalized = cleaned_bulletin.lower().replace('(', ' ').replace(')', ' ').replace('-', ' ')
            
            # Remove extra spaces
            lookup_normalized = ' '.join(lookup_normalized.split())
            bulletin_normalized = ' '.join(bulletin_normalized.split())
            
            if lookup_normalized == bulletin_normalized:
                exact_matches.append(lookup_category)
            elif any(word in lookup_normalized for word in bulletin_normalized.split() if len(word) > 3):
                partial_matches.append(lookup_category)
                
        mapping_results.append({
            'bulletin_format': bulletin_format,
            'exact_matches': exact_matches,
            'partial_matches': partial_matches[:5]  # Top 5 partial matches
        })
        
        print(f"\n📊 Bulletin: '{bulletin_format}'")
        if exact_matches:
            print(f"  ✅ Exact Matches:")
            for match in exact_matches:
                print(f"    - {match}")
        else:
            print(f"  ❌ No exact matches found")
            
        if partial_matches:
            print(f"  🔍 Partial Matches:")
            for match in partial_matches[:3]:
                print(f"    - {match}")
                
    # Analyze the format differences
    print(f"\n" + "="*60)
    print("FORMAT DIFFERENCE ANALYSIS")
    print("="*60)
    
    print(f"\n📋 BULLETIN FORMAT PATTERNS:")
    print(f"  - Uses parentheses: (Quality Assurance HMA & Aggregate)")
    print(f"  - Uses 'Special Services' as main category")
    print(f"  - Specific service in parentheses")
    
    print(f"\n📋 PREQUAL_LOOKUP FORMAT PATTERNS:")
    print(f"  - Uses hyphens: Special Services - Quality Assurance HMA & Aggregate")
    print(f"  - Uses 'Special Services' as main category")
    print(f"  - Specific service after hyphen")
    
    # Show examples of format differences
    print(f"\n📊 FORMAT COMPARISON EXAMPLES:")
    
    format_comparisons = [
        {
            'bulletin': 'Special Services (Quality Assurance HMA & Aggregate)',
            'lookup': 'Special Services - Quality Assurance HMA & Aggregate'
        },
        {
            'bulletin': 'Special Services (Quality Assurance PCC & Aggregate)',
            'lookup': 'Special Services - Quality Assurance PCC & Aggregate'
        },
        {
            'bulletin': 'Special Services (Construction Inspection)',
            'lookup': 'Special Services - Construction Inspection'
        }
    ]
    
    for comp in format_comparisons:
        print(f"\n  Bulletin: {comp['bulletin']}")
        print(f"  Lookup:   {comp['lookup']}")
        print(f"  Difference: Parentheses vs Hyphens")
        
    # Create mapping rules
    print(f"\n" + "="*60)
    print("MAPPING RULES FOR MODEL")
    print("="*60)
    
    print(f"\n🔧 MAPPING RULES:")
    print(f"  1. Replace parentheses with hyphens")
    print(f"     '(Quality Assurance HMA & Aggregate)' → '- Quality Assurance HMA & Aggregate'")
    print(f"  2. Remove extra spaces")
    print(f"     'Special Services (' → 'Special Services -'")
    print(f"  3. Handle special characters")
    print(f"     '&' remains '&'")
    print(f"     '/' becomes ' ' or '-'")
    print(f"  4. Case insensitive matching")
    print(f"     'special services' matches 'Special Services'")
    
    # Create a mapping function example
    print(f"\n💻 EXAMPLE MAPPING FUNCTION:")
    print(f"""
def map_bulletin_to_prequal(bulletin_text):
    # 1. Clean the bulletin text
    cleaned = bulletin_text.strip()
    
    # 2. Replace parentheses with hyphens
    mapped = cleaned.replace('(', ' - ').replace(')', '')
    
    # 3. Remove extra spaces
    mapped = ' '.join(mapped.split())
    
    # 4. Find in prequal_lookup
    for category in prequal_lookup.keys():
        if mapped.lower() == category.lower():
            return category
            
    # 5. Try partial matching if exact fails
    for category in prequal_lookup.keys():
        if mapped.lower() in category.lower() or category.lower() in mapped.lower():
            return category
            
    return None
""")
    
    # Test the mapping with examples
    print(f"\n🧪 TESTING MAPPING WITH EXAMPLES:")
    
    for bulletin_format in bulletin_examples:
        # Apply mapping rules
        mapped = bulletin_format.strip()
        mapped = mapped.replace('(', ' - ').replace(')', '')
        mapped = ' '.join(mapped.split())
        
        # Find in prequal_lookup
        found = None
        for category in prequal_lookup.keys():
            if mapped.lower() == category.lower():
                found = category
                break
                
        print(f"\n  Bulletin: '{bulletin_format}'")
        print(f"  Mapped:   '{mapped}'")
        if found:
            print(f"  ✅ Found:  '{found}'")
        else:
            print(f"  ❌ Not found in prequal_lookup")
            
    # Summary
    print(f"\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    print(f"\n📊 KEY INSIGHTS:")
    print(f"  1. Bulletin uses parentheses, prequal_lookup uses hyphens")
    print(f"  2. Model needs to understand this format difference")
    print(f"  3. Mapping rules are consistent and predictable")
    print(f"  4. Case-insensitive matching is important")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    print(f"  1. Implement mapping function in the model")
    print(f"  2. Train model on format differences")
    print(f"  3. Use fuzzy matching for variations")
    print(f"  4. Create a prequalification mapping dictionary")
    
    return mapping_results

if __name__ == "__main__":
    analyze_bulletin_prequal_mapping()
