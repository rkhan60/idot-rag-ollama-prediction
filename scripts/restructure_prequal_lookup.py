#!/usr/bin/env python3
"""
Restructure Prequalification Lookup
Reorganize prequal_lookup.json with:
1. Head categories in ascending order
2. Unique codes for prequal sub-categories
3. Firms with their firm codes
"""

import json
import re

class PrequalificationRestructure:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.backup_file = '../data/prequal_lookup_backup_before_restructure.json'
        self.output_file = '../data/prequal_lookup_restructured.json'
        
        # Load current lookup
        with open(self.prequal_lookup_file, 'r') as f:
            self.current_data = json.load(f)
        
        # Define head categories and their codes
        self.head_categories = {
            'Airports': 'A',
            'Environmental Reports': 'ER', 
            'Geotechnical Services': 'GS',
            'Highways': 'H',
            'Hydraulic Reports': 'HR',
            'Location Design Studies': 'LDS',
            'Location Studies': 'LS',
            'Special Plans': 'SP',
            'Special Services': 'SS',
            'Special Studies': 'ST',
            'Specialty Agents': 'SA',
            'Structures': 'S',
            'Transportation Studies': 'TS'
        }
        
    def extract_head_category(self, prequal_name):
        """Extract head category from prequalification name"""
        for head_cat in self.head_categories.keys():
            if prequal_name.startswith(head_cat):
                return head_cat
        return 'Other'  # Fallback
    
    def generate_unique_code(self, head_category, sub_category, index):
        """Generate unique code for prequal sub-category"""
        head_code = self.head_categories.get(head_category, 'O')
        
        # Clean sub-category name for code generation
        clean_sub = re.sub(r'[^\w\s]', '', sub_category)
        clean_sub = re.sub(r'\s+', '_', clean_sub).upper()
        
        # Create unique code: HEAD_CODE + SUB_CATEGORY + INDEX
        unique_code = f"{head_code}_{clean_sub}_{index:03d}"
        return unique_code
    
    def restructure_data(self):
        """Restructure the prequalification data"""
        print("🔄 RESTRUCTURING PREQUALIFICATION DATA")
        print("=" * 80)
        
        # Create backup
        with open(self.backup_file, 'w') as f:
            json.dump(self.current_data, f, indent=2)
        print(f"✅ Backup created: {self.backup_file}")
        
        # Group by head categories
        grouped_data = {}
        
        for prequal_name, firms in self.current_data.items():
            head_category = self.extract_head_category(prequal_name)
            
            if head_category not in grouped_data:
                grouped_data[head_category] = []
            
            grouped_data[head_category].append({
                'prequal_name': prequal_name,
                'firms': firms
            })
        
        # Sort head categories alphabetically
        sorted_head_categories = sorted(grouped_data.keys())
        
        # Create restructured data
        restructured_data = {}
        
        for head_category in sorted_head_categories:
            print(f"\n📋 Processing head category: {head_category}")
            
            # Sort sub-categories within head category
            sub_categories = sorted(grouped_data[head_category], 
                                  key=lambda x: x['prequal_name'])
            
            restructured_data[head_category] = {
                'head_category_code': self.head_categories.get(head_category, 'O'),
                'sub_categories': {}
            }
            
            for index, sub_cat_data in enumerate(sub_categories, 1):
                prequal_name = sub_cat_data['prequal_name']
                firms = sub_cat_data['firms']
                
                # Generate unique code
                unique_code = self.generate_unique_code(head_category, prequal_name, index)
                
                # Extract sub-category name (remove head category prefix)
                sub_category_name = prequal_name
                if prequal_name.startswith(head_category):
                    sub_category_name = prequal_name[len(head_category):].strip()
                    if sub_category_name.startswith('('):
                        sub_category_name = sub_category_name[1:]
                    if sub_category_name.endswith(')'):
                        sub_category_name = sub_category_name[:-1]
                
                restructured_data[head_category]['sub_categories'][unique_code] = {
                    'sub_category_name': sub_category_name,
                    'full_prequal_name': prequal_name,
                    'firms': firms,
                    'firm_count': len(firms)
                }
                
                print(f"  {unique_code}: {prequal_name} ({len(firms)} firms)")
        
        return restructured_data
    
    def save_restructured_data(self, restructured_data):
        """Save the restructured data"""
        print(f"\n💾 SAVING RESTRUCTURED DATA")
        print("=" * 80)
        
        with open(self.output_file, 'w') as f:
            json.dump(restructured_data, f, indent=2)
        
        print(f"✅ Restructured data saved: {self.output_file}")
        
        # Also update the original file
        with open(self.prequal_lookup_file, 'w') as f:
            json.dump(restructured_data, f, indent=2)
        
        print(f"✅ Original file updated: {self.prequal_lookup_file}")
    
    def verify_structure(self, restructured_data):
        """Verify the restructured data"""
        print(f"\n🔍 VERIFYING RESTRUCTURED DATA")
        print("=" * 80)
        
        total_head_categories = len(restructured_data)
        total_sub_categories = 0
        total_firms = 0
        
        print(f"Head Categories ({total_head_categories}):")
        for head_cat, data in restructured_data.items():
            sub_cat_count = len(data['sub_categories'])
            total_sub_categories += sub_cat_count
            
            head_firm_count = 0
            for sub_cat_code, sub_cat_data in data['sub_categories'].items():
                head_firm_count += sub_cat_data['firm_count']
                total_firms += sub_cat_data['firm_count']
            
            print(f"  {head_cat} ({data['head_category_code']}): {sub_cat_count} sub-categories, {head_firm_count} firms")
        
        print(f"\n📊 SUMMARY:")
        print(f"Total head categories: {total_head_categories}")
        print(f"Total sub-categories: {total_sub_categories}")
        print(f"Total firms: {total_firms}")
        
        return {
            'head_categories': total_head_categories,
            'sub_categories': total_sub_categories,
            'total_firms': total_firms
        }
    
    def run_restructure(self):
        """Run the complete restructure process"""
        print("🚀 PREQUALIFICATION LOOKUP RESTRUCTURE")
        print("=" * 80)
        
        # Step 1: Restructure data
        restructured_data = self.restructure_data()
        
        # Step 2: Save restructured data
        self.save_restructured_data(restructured_data)
        
        # Step 3: Verify structure
        verification = self.verify_structure(restructured_data)
        
        print(f"\n✅ RESTRUCTURE COMPLETE!")
        print(f"📋 Data now organized by head categories with unique codes.")
        
        return restructured_data

def main():
    restructure = PrequalificationRestructure()
    result = restructure.run_restructure()
    
    print(f"\n✅ Prequalification lookup restructured successfully!")

if __name__ == "__main__":
    main()





