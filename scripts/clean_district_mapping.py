#!/usr/bin/env python3
"""
Clean and Reassign District Mapping
Uses city_to_district.json to fix Unknown firms and standardize data
"""

import json
import csv
from collections import defaultdict
import re

def normalize_city(city):
    """Normalize city name: strip spaces, title-case"""
    if not city:
        return ""
    return city.strip().title()

def normalize_district(district):
    """Normalize district to 'District X' format"""
    if not district:
        return ""
    
    match = re.search(r'(\d+)', district)
    if match:
        number = match.group(1)
        return f"District {number}"
    
    return district

def clean_district_mapping():
    """Clean and reassign district mapping data"""
    
    print("🧹 CLEANING DISTRICT MAPPING DATA")
    print("="*50)
    
    # Load data files
    with open('../data/district_mapping.json', 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    with open('../data/city_to_district.json', 'r', encoding='utf-8') as f:
        city_lookup = json.load(f)
    
    print(f"✅ Loaded original data: {len(original_data)} groups")
    print(f"✅ Loaded city lookup: {len(city_lookup)} cities")
    
    # Initialize clean data structure
    clean_data = defaultdict(list)
    reassignment_log = []
    
    # Process all firms from all groups
    total_firms = 0
    fixed_count = 0
    unknown_count = 0
    
    for group_key, firms in original_data.items():
        print(f"📊 Processing {group_key}: {len(firms)} firms")
        
        for firm in firms:
            total_firms += 1
            
            # Extract firm data
            firm_code = firm.get('firm_code', '')
            firm_name = firm.get('firm_name', '')
            original_district = firm.get('district', '')
            city = firm.get('city', '')
            state = firm.get('state', '')
            
            # Normalize city
            normalized_city = normalize_city(city)
            
            # Determine new district and status
            new_district = None
            status = None
            old_group = group_key
            
            if group_key == "Out of State":
                # Keep out of state firms as is
                new_district = "Out of State"
                status = "OOS"
                
            elif group_key == "Unknown":
                # Try to assign district using city lookup
                if normalized_city in city_lookup:
                    new_district = city_lookup[normalized_city]
                    status = "FIXED"
                    fixed_count += 1
                    print(f"   ✅ FIXED: {firm_name} ({normalized_city}) → {new_district}")
                else:
                    new_district = "Unknown"
                    status = "UNKNOWN"
                    unknown_count += 1
                    
            else:
                # Already in a valid district
                new_district = normalize_district(group_key)
                status = "VALID"
            
            # Create clean firm record
            clean_firm = {
                'firm_code': firm_code,
                'firm_name': firm_name,
                'district': new_district,
                'city': normalized_city,
                'state': state,
                'status': status
            }
            
            # Add to clean data
            clean_data[new_district].append(clean_firm)
            
            # Log reassignment
            reassignment_log.append({
                'firm_code': firm_code,
                'old_group': old_group,
                'new_group': new_district,
                'city': normalized_city,
                'status': status
            })
    
    print(f"\n📊 PROCESSING SUMMARY:")
    print(f"   • Total firms processed: {total_firms}")
    print(f"   • Fixed from Unknown: {fixed_count}")
    print(f"   • Remaining Unknown: {unknown_count}")
    
    # Save clean district mapping
    with open('../data/district_mapping_clean.json', 'w', encoding='utf-8') as f:
        json.dump(dict(clean_data), f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved district_mapping_clean.json")
    
    # Save reassignment log
    with open('../data/reassignment_log.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['firm_code', 'old_group', 'new_group', 'city', 'status'])
        writer.writeheader()
        writer.writerows(reassignment_log)
    
    print(f"✅ Saved reassignment_log.csv")
    
    return clean_data, reassignment_log

def print_summary(clean_data, reassignment_log):
    """Print summary statistics"""
    
    print(f"\n{'='*60}")
    print(f"📊 FINAL SUMMARY")
    print(f"{'='*60}")
    
    # Per-district counts
    print(f"\n🏛️  PER-DISTRICT FIRM COUNTS:")
    print("-"*40)
    
    district_counts = {}
    for district, firms in clean_data.items():
        district_counts[district] = len(firms)
    
    # Sort by district number
    sorted_districts = sorted(district_counts.items(), 
                            key=lambda x: (x[0] != "Unknown", x[0] != "Out of State", x[0]))
    
    for district, count in sorted_districts:
        print(f"   {district}: {count} firms")
    
    # Status breakdown
    print(f"\n📋 STATUS BREAKDOWN:")
    print("-"*40)
    
    status_counts = defaultdict(int)
    for log in reassignment_log:
        status_counts[log['status']] += 1
    
    for status, count in sorted(status_counts.items()):
        print(f"   {status}: {count} firms")
    
    # Fixed vs Unknown
    fixed_count = status_counts.get('FIXED', 0)
    unknown_count = status_counts.get('UNKNOWN', 0)
    
    print(f"\n🎯 KEY METRICS:")
    print("-"*40)
    print(f"   • Firms FIXED from Unknown: {fixed_count}")
    print(f"   • Firms still Unknown: {unknown_count}")
    print(f"   • Improvement rate: {fixed_count/(fixed_count+unknown_count)*100:.1f}%" if (fixed_count+unknown_count) > 0 else "   • Improvement rate: N/A")
    
    return {
        'district_counts': dict(district_counts),
        'status_counts': dict(status_counts),
        'fixed_count': fixed_count,
        'unknown_count': unknown_count
    }

def main():
    """Main function"""
    print("🗺️  DISTRICT MAPPING CLEANER")
    print("="*60)
    
    try:
        # Clean and reassign data
        clean_data, reassignment_log = clean_district_mapping()
        
        # Print summary
        summary = print_summary(clean_data, reassignment_log)
        
        print(f"\n📁 OUTPUT FILES:")
        print(f"   • ../data/district_mapping_clean.json")
        print(f"   • ../data/reassignment_log.csv")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())




