#!/usr/bin/env python3
"""
Build City to District Lookup
Creates a clean city→district mapping from district_mapping.json
"""

import json
import csv
from collections import defaultdict, Counter
import re

def normalize_city(city):
    """Normalize city name: strip spaces, title-case"""
    if not city:
        return ""
    # Strip spaces and title-case
    normalized = city.strip().title()
    return normalized

def normalize_district(district):
    """Normalize district to 'District X' format"""
    if not district:
        return ""
    
    # Extract number from various formats
    match = re.search(r'(\d+)', district)
    if match:
        number = match.group(1)
        return f"District {number}"
    
    return district

def build_city_district_lookup():
    """Build city→district lookup from district_mapping.json"""
    
    print("🏗️  BUILDING CITY TO DISTRICT LOOKUP")
    print("="*50)
    
    # Load district mapping data
    with open('../data/district_mapping.json', 'r', encoding='utf-8') as f:
        district_data = json.load(f)
    
    print(f"✅ Loaded district mapping with {len(district_data)} district groups")
    
    # Build city→district mapping (excluding Unknown and Out of State)
    city_district_map = defaultdict(set)
    city_counts = Counter()
    
    valid_districts = [key for key in district_data.keys() 
                      if key not in ["Unknown", "Out of State"]]
    
    print(f"📊 Processing {len(valid_districts)} valid districts: {valid_districts}")
    
    # Process each valid district
    for district_key in valid_districts:
        firms = district_data[district_key]
        normalized_district = normalize_district(district_key)
        
        print(f"   Processing {district_key} ({len(firms)} firms) → {normalized_district}")
        
        for firm in firms:
            city = firm.get('city', '')
            if city:
                normalized_city = normalize_city(city)
                city_district_map[normalized_city].add(normalized_district)
                city_counts[normalized_city] += 1
    
    print(f"✅ Processed {len(city_district_map)} unique cities")
    
    # Separate unambiguous and ambiguous cities
    unambiguous_cities = {}
    ambiguous_cities = []
    
    for city, districts in city_district_map.items():
        if len(districts) == 1:
            # Unambiguous - single district
            unambiguous_cities[city] = list(districts)[0]
        else:
            # Ambiguous - multiple districts
            district_list = list(districts)
            district_counts = {}
            
            # Count occurrences per district
            for district in district_list:
                count = sum(1 for firm_list in district_data.values() 
                           for firm in firm_list 
                           if normalize_city(firm.get('city', '')) == city and 
                           normalize_district(firm.get('district', '')) == district)
                district_counts[district] = count
            
            ambiguous_cities.append({
                'city': city,
                'districts_seen': ', '.join(district_list),
                'count_per_district': ', '.join([f"{d}:{c}" for d, c in district_counts.items()])
            })
    
    print(f"📊 Results:")
    print(f"   • Unambiguous cities: {len(unambiguous_cities)}")
    print(f"   • Ambiguous cities: {len(ambiguous_cities)}")
    print(f"   • Total unique cities: {len(city_district_map)}")
    
    # Save unambiguous city→district mapping
    with open('../data/city_to_district.json', 'w', encoding='utf-8') as f:
        json.dump(unambiguous_cities, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved city_to_district.json with {len(unambiguous_cities)} mappings")
    
    # Save ambiguous cities to CSV
    if ambiguous_cities:
        with open('../data/city_lookup_ambiguities.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['city', 'districts_seen', 'count_per_district'])
            writer.writeheader()
            writer.writerows(ambiguous_cities)
        
        print(f"✅ Saved city_lookup_ambiguities.csv with {len(ambiguous_cities)} ambiguous cities")
    else:
        print("✅ No ambiguous cities found")
    
    # Print sample of unambiguous mappings
    print(f"\n📋 SAMPLE UNAMBIGUOUS MAPPINGS:")
    print("-"*40)
    sample_cities = list(unambiguous_cities.items())[:10]
    for city, district in sample_cities:
        print(f"   {city} → {district}")
    
    # Print ambiguous cities if any
    if ambiguous_cities:
        print(f"\n⚠️  AMBIGUOUS CITIES (excluded from lookup):")
        print("-"*40)
        for item in ambiguous_cities[:5]:  # Show first 5
            print(f"   {item['city']} → {item['districts_seen']}")
        if len(ambiguous_cities) > 5:
            print(f"   ... and {len(ambiguous_cities) - 5} more")
    
    return {
        'unambiguous_count': len(unambiguous_cities),
        'ambiguous_count': len(ambiguous_cities),
        'total_cities': len(city_district_map)
    }

def main():
    """Main function"""
    print("🗺️  CITY TO DISTRICT LOOKUP BUILDER")
    print("="*60)
    
    try:
        results = build_city_district_lookup()
        
        print(f"\n{'='*60}")
        print(f"📊 FINAL SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Total unique cities learned: {results['total_cities']}")
        print(f"✅ Unambiguous cities: {results['unambiguous_count']}")
        print(f"⚠️  Ambiguous cities: {results['ambiguous_count']}")
        print(f"📁 Output files:")
        print(f"   • ../data/city_to_district.json")
        print(f"   • ../data/city_lookup_ambiguities.csv")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())




