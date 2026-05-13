#!/usr/bin/env python3
"""
Debug Prequalification Lookup Structure
Examine the actual structure of prequal_lookup.json
"""

import json

def debug_prequal_lookup():
    """Debug the prequal_lookup.json structure"""
    data_dir = '../data'
    
    print("🔍 Debugging Prequalification Lookup Structure...")
    
    # Load prequal_lookup.json
    with open(f'{data_dir}/prequal_lookup.json', 'r') as f:
        prequal_lookup = json.load(f)
    
    print(f"📊 Total categories: {len(prequal_lookup)}")
    print(f"📊 Keys: {list(prequal_lookup.keys())[:5]}...")
    
    print(f"\n📋 Sample category data:")
    for i, (category, data) in enumerate(prequal_lookup.items()):
        if i < 3:  # Show first 3 categories
            print(f"\nCategory: {category}")
            print(f"  Type: {type(data)}")
            print(f"  Content: {data}")
            
            if isinstance(data, list):
                print(f"  List length: {len(data)}")
                print(f"  Sample firms: {data[:3]}")
            elif isinstance(data, dict):
                print(f"  Dict keys: {list(data.keys())}")
                print(f"  Sample content: {list(data.items())[:3]}")
                
    print(f"\n🔍 Data type analysis:")
    type_counts = {}
    for category, data in prequal_lookup.items():
        data_type = type(data).__name__
        type_counts[data_type] = type_counts.get(data_type, 0) + 1
        
    for data_type, count in type_counts.items():
        print(f"  {data_type}: {count} categories")

if __name__ == "__main__":
    debug_prequal_lookup()
