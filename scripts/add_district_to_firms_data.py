#!/usr/bin/env python3
"""
Add District to Firms Data
Add district assignments to firms_data.json based on district_mapping.json
"""

import json
import os
from datetime import datetime

class DistrictAdder:
    def __init__(self):
        self.data_dir = '../data'
        self.backup_dir = '../data/backups'
        
    def add_district_to_firms_data(self):
        """Add district assignments to firms_data.json"""
        print("🚀 ADDING DISTRICT ASSIGNMENTS TO FIRMS_DATA.JSON")
        print("=" * 60)
        
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Load district_mapping.json
        print("📂 Loading district_mapping.json...")
        with open(f'{self.data_dir}/district_mapping.json', 'r') as f:
            district_mapping = json.load(f)
            
        print(f"✅ Loaded district mapping with {len(district_mapping)} districts")
        
        # Load firms_data.json
        print("📂 Loading firms_data.json...")
        with open(f'{self.data_dir}/firms_data.json', 'r') as f:
            firms_data = json.load(f)
            
        print(f"✅ Loaded {len(firms_data)} firms from firms_data.json")
        
        # Create backup of existing firms_data.json
        firms_data_path = f'{self.data_dir}/firms_data.json'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f'{self.backup_dir}/firms_data_backup_{timestamp}.json'
        
        print(f"📦 Creating backup: {backup_path}")
        with open(backup_path, 'w') as f:
            json.dump(firms_data, f, indent=2)
        print("✅ Backup created successfully")
        
        # Create a lookup dictionary for district assignments
        print("\n🔍 Creating district lookup...")
        district_lookup = {}
        for district, firms in district_mapping.items():
            for firm in firms:
                firm_name = firm.get('firm_name', '').strip()
                if firm_name:
                    district_lookup[firm_name] = district
                    
        print(f"✅ Created district lookup for {len(district_lookup)} firms")
        
        # Add district to each firm in firms_data.json
        print("\n🔍 Adding district assignments to firms...")
        updated_firms = []
        firms_with_district = 0
        firms_without_district = 0
        
        for firm in firms_data:
            firm_name = firm.get('firm_name', '').strip()
            
            # Create updated firm entry
            updated_firm = firm.copy()
            
            # Add district assignment
            if firm_name in district_lookup:
                updated_firm['district'] = district_lookup[firm_name]
                firms_with_district += 1
            else:
                updated_firm['district'] = 'Unknown'
                firms_without_district += 1
                
            updated_firms.append(updated_firm)
            
        # Print summary
        print(f"\n📊 DISTRICT ASSIGNMENT SUMMARY:")
        print(f"   Total Firms: {len(updated_firms)}")
        print(f"   Firms with District: {firms_with_district}")
        print(f"   Firms without District: {firms_without_district}")
        
        # Show district breakdown
        district_counts = {}
        for firm in updated_firms:
            district = firm.get('district', 'Unknown')
            district_counts[district] = district_counts.get(district, 0) + 1
            
        print(f"\n📋 DISTRICT BREAKDOWN:")
        for district, count in sorted(district_counts.items()):
            print(f"   {district}: {count} firms")
            
        # Save the updated firms_data.json
        print(f"\n💾 Saving updated firms_data.json...")
        with open(firms_data_path, 'w') as f:
            json.dump(updated_firms, f, indent=2)
            
        print("✅ firms_data.json updated successfully!")
        
        # Verify the update
        print(f"\n🔍 Verifying update...")
        with open(firms_data_path, 'r') as f:
            verification_data = json.load(f)
            
        verification_firms_with_district = sum(1 for firm in verification_data if firm.get('district'))
        print(f"   Verification: {verification_firms_with_district}/{len(verification_data)} firms have district")
        
        if verification_firms_with_district == len(verification_data):
            print("✅ Verification successful!")
        else:
            print("❌ Verification failed!")
            
        return updated_firms
        
    def show_sample_updated_firm(self, updated_firms):
        """Show a sample of the updated firm structure"""
        print(f"\n📋 SAMPLE UPDATED FIRM STRUCTURE:")
        print("=" * 50)
        
        if updated_firms:
            sample_firm = updated_firms[0]
            print(json.dumps(sample_firm, indent=2))
            
            print(f"\n📊 SAMPLE FIRM DETAILS:")
            print(f"   Firm Code: {sample_firm.get('firm_code', 'N/A')}")
            print(f"   Firm Name: {sample_firm.get('firm_name', 'N/A')}")
            print(f"   District: {sample_firm.get('district', 'N/A')}")
            print(f"   City: {sample_firm.get('city', 'N/A')}")
            print(f"   State: {sample_firm.get('state', 'N/A')}")
            print(f"   Prequalifications: {len(sample_firm.get('prequalifications', []))}")

def main():
    adder = DistrictAdder()
    
    # Add district to firms data
    updated_firms = adder.add_district_to_firms_data()
    
    # Show sample updated firm
    adder.show_sample_updated_firm(updated_firms)
    
    print(f"\n🎯 FINAL SUMMARY:")
    print(f"   Firms Data: UPDATED WITH DISTRICTS")
    print(f"   Total Firms: {len(updated_firms)}")
    print(f"   Firms with District: {sum(1 for firm in updated_firms if firm.get('district') != 'Unknown')}")
    print(f"   Firms without District: {sum(1 for firm in updated_firms if firm.get('district') == 'Unknown')}")
    print("✅ Ready for next verification step!")

if __name__ == "__main__":
    main()
