#!/usr/bin/env python3
"""
Populate District Mapping
Populate district_mapping.json using firms_data.json
"""

import json
import os
from collections import defaultdict
from datetime import datetime

class DistrictMappingPopulator:
    def __init__(self):
        self.data_dir = '../data'
        self.backup_dir = '../data/backups'
        
    def populate_district_mapping(self):
        """Populate district_mapping.json using firms_data.json"""
        print("🚀 POPULATING DISTRICT MAPPING")
        print("=" * 50)
        
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Load firms_data.json
        print("📂 Loading firms_data.json...")
        with open(f'{self.data_dir}/firms_data.json', 'r') as f:
            firms_data = json.load(f)
            
        print(f"✅ Loaded {len(firms_data)} firms from firms_data.json")
        
        # Create backup of existing district_mapping.json if it exists
        district_mapping_path = f'{self.data_dir}/district_mapping.json'
        if os.path.exists(district_mapping_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f'{self.backup_dir}/district_mapping_backup_{timestamp}.json'
            
            print(f"📦 Creating backup: {backup_path}")
            with open(district_mapping_path, 'r') as f:
                existing_data = json.load(f)
            with open(backup_path, 'w') as f:
                json.dump(existing_data, f, indent=2)
            print("✅ Backup created successfully")
        
        # Extract district information from firms_data
        print("\n🔍 Extracting district information...")
        district_mapping = defaultdict(list)
        
        for firm in firms_data:
            firm_name = firm.get('firm_name', '').strip()
            if not firm_name:
                continue
                
            # Extract district information
            district = firm.get('district', '')
            if not district:
                # If no district info, assign to 'Unknown' district
                district = 'Unknown'
                
            # Create firm entry
            firm_entry = {
                'firm_code': firm.get('firm_code', ''),
                'firm_name': firm_name,
                'district': district
            }
            
            # Add to district mapping
            district_mapping[district].append(firm_entry)
            
        # Convert defaultdict to regular dict
        district_mapping = dict(district_mapping)
        
        # Print summary
        print(f"\n📊 DISTRICT MAPPING SUMMARY:")
        print(f"   Total Districts: {len(district_mapping)}")
        total_firms = sum(len(firms) for firms in district_mapping.values())
        print(f"   Total Firms: {total_firms}")
        
        # Show district breakdown
        print(f"\n📋 DISTRICT BREAKDOWN:")
        for district, firms in sorted(district_mapping.items()):
            print(f"   {district}: {len(firms)} firms")
            
        # Save the populated district_mapping.json
        print(f"\n💾 Saving district_mapping.json...")
        with open(district_mapping_path, 'w') as f:
            json.dump(district_mapping, f, indent=2)
            
        print("✅ district_mapping.json populated successfully!")
        
        # Verify the populated file
        print(f"\n🔍 Verifying populated file...")
        with open(district_mapping_path, 'r') as f:
            verification_data = json.load(f)
            
        verification_firms = sum(len(firms) for firms in verification_data.values())
        print(f"   Verification: {verification_firms} firms in {len(verification_data)} districts")
        
        if verification_firms == total_firms:
            print("✅ Verification successful!")
        else:
            print("❌ Verification failed!")
            
        return district_mapping
        
    def analyze_district_data_quality(self, district_mapping):
        """Analyze the quality of district data"""
        print(f"\n🔍 ANALYZING DISTRICT DATA QUALITY")
        print("=" * 50)
        
        # Count firms by district
        district_counts = {district: len(firms) for district, firms in district_mapping.items()}
        
        # Find districts with most firms
        sorted_districts = sorted(district_counts.items(), key=lambda x: x[1], reverse=True)
        
        print(f"📊 TOP 10 DISTRICTS BY FIRM COUNT:")
        for i, (district, count) in enumerate(sorted_districts[:10], 1):
            print(f"   {i:2d}. {district}: {count} firms")
            
        # Check for unknown districts
        unknown_districts = [district for district in district_mapping.keys() if 'unknown' in district.lower()]
        if unknown_districts:
            print(f"\n⚠️  UNKNOWN DISTRICTS FOUND:")
            for district in unknown_districts:
                print(f"   - {district}: {len(district_mapping[district])} firms")
                
        # Check for empty districts
        empty_districts = [district for district, firms in district_mapping.items() if len(firms) == 0]
        if empty_districts:
            print(f"\n❌ EMPTY DISTRICTS FOUND:")
            for district in empty_districts:
                print(f"   - {district}")
                
        # Overall quality assessment
        total_firms = sum(district_counts.values())
        unknown_firms = sum(len(district_mapping[district]) for district in unknown_districts)
        quality_score = ((total_firms - unknown_firms) / total_firms) * 100 if total_firms > 0 else 0
        
        print(f"\n📈 DATA QUALITY ASSESSMENT:")
        print(f"   Total Firms: {total_firms}")
        print(f"   Firms with Known Districts: {total_firms - unknown_firms}")
        print(f"   Firms with Unknown Districts: {unknown_firms}")
        print(f"   Quality Score: {quality_score:.2f}%")
        
        if quality_score >= 90:
            print("✅ Excellent data quality!")
        elif quality_score >= 75:
            print("⚠️  Good data quality, some improvements needed")
        else:
            print("❌ Poor data quality, significant improvements needed")
            
        return quality_score

def main():
    populator = DistrictMappingPopulator()
    
    # Populate district mapping
    district_mapping = populator.populate_district_mapping()
    
    # Analyze data quality
    quality_score = populator.analyze_district_data_quality(district_mapping)
    
    print(f"\n🎯 FINAL SUMMARY:")
    print(f"   District Mapping: POPULATED")
    print(f"   Total Firms: {sum(len(firms) for firms in district_mapping.values())}")
    print(f"   Total Districts: {len(district_mapping)}")
    print(f"   Data Quality: {quality_score:.2f}%")
    
    if quality_score >= 75:
        print("✅ Ready for next verification step!")
    else:
        print("⚠️  Data quality needs improvement before proceeding")

if __name__ == "__main__":
    main()
