#!/usr/bin/env python3
"""
Verify Prequalification Lookup Structure
Check number of sub-categories and verify uniqueness
"""

import json
from collections import defaultdict

class PrequalLookupVerifier:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        
        # Load data
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
    
    def count_sub_categories(self):
        """Count all sub-categories and their details"""
        total_sub_categories = 0
        sub_category_details = []
        all_prequal_names = []
        
        print("🔍 ANALYZING PREQUAL_LOOKUP.JSON STRUCTURE")
        print("=" * 80)
        
        for head_category, data in self.prequal_lookup.items():
            print(f"\n📋 Head Category: {head_category}")
            print(f"   Sub-categories: {len(data['sub_categories'])}")
            
            for sub_code, sub_data in data['sub_categories'].items():
                total_sub_categories += 1
                prequal_name = sub_data['full_prequal_name']
                firm_count = sub_data['firm_count']
                
                sub_category_details.append({
                    'head_category': head_category,
                    'sub_code': sub_code,
                    'prequal_name': prequal_name,
                    'firm_count': firm_count
                })
                
                all_prequal_names.append(prequal_name)
                
                print(f"     • {sub_code}: {prequal_name} ({firm_count} firms)")
        
        return total_sub_categories, sub_category_details, all_prequal_names
    
    def check_uniqueness(self, all_prequal_names):
        """Check if all prequalification names are unique"""
        print(f"\n🔍 CHECKING UNIQUENESS")
        print("=" * 80)
        
        # Count occurrences
        name_counts = defaultdict(int)
        for name in all_prequal_names:
            name_counts[name] += 1
        
        # Find duplicates
        duplicates = {name: count for name, count in name_counts.items() if count > 1}
        unique_names = {name: count for name, count in name_counts.items() if count == 1}
        
        print(f"Total prequalification names: {len(all_prequal_names)}")
        print(f"Unique names: {len(unique_names)}")
        print(f"Duplicate names: {len(duplicates)}")
        
        if duplicates:
            print(f"\n⚠️  DUPLICATE PREQUALIFICATION NAMES FOUND:")
            for name, count in duplicates.items():
                print(f"   • {name} (appears {count} times)")
        else:
            print(f"\n✅ ALL PREQUALIFICATION NAMES ARE UNIQUE!")
        
        return duplicates, unique_names
    
    def check_sub_codes(self, sub_category_details):
        """Check if sub-codes are unique"""
        print(f"\n🔍 CHECKING SUB-CODES")
        print("=" * 80)
        
        all_sub_codes = [detail['sub_code'] for detail in sub_category_details]
        sub_code_counts = defaultdict(int)
        
        for code in all_sub_codes:
            sub_code_counts[code] += 1
        
        duplicate_codes = {code: count for code, count in sub_code_counts.items() if count > 1}
        unique_codes = {code: count for code, count in sub_code_counts.items() if count == 1}
        
        print(f"Total sub-codes: {len(all_sub_codes)}")
        print(f"Unique sub-codes: {len(unique_codes)}")
        print(f"Duplicate sub-codes: {len(duplicate_codes)}")
        
        if duplicate_codes:
            print(f"\n⚠️  DUPLICATE SUB-CODES FOUND:")
            for code, count in duplicate_codes.items():
                print(f"   • {code} (appears {count} times)")
        else:
            print(f"\n✅ ALL SUB-CODES ARE UNIQUE!")
        
        return duplicate_codes, unique_codes
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("📊 COMPREHENSIVE STRUCTURE REPORT")
        print("=" * 80)
        
        # Count sub-categories
        total_sub_categories, sub_category_details, all_prequal_names = self.count_sub_categories()
        
        # Check uniqueness
        duplicate_names, unique_names = self.check_uniqueness(all_prequal_names)
        duplicate_codes, unique_codes = self.check_sub_codes(sub_category_details)
        
        # Summary
        print(f"\n📋 SUMMARY")
        print("=" * 80)
        print(f"Total head categories: {len(self.prequal_lookup)}")
        print(f"Total sub-categories: {total_sub_categories}")
        print(f"Total prequalification names: {len(all_prequal_names)}")
        print(f"Unique prequalification names: {len(unique_names)}")
        print(f"Duplicate prequalification names: {len(duplicate_names)}")
        print(f"Unique sub-codes: {len(unique_codes)}")
        print(f"Duplicate sub-codes: {len(duplicate_codes)}")
        
        # Head category breakdown
        print(f"\n📊 HEAD CATEGORY BREAKDOWN")
        print("=" * 80)
        for head_category, data in self.prequal_lookup.items():
            sub_count = len(data['sub_categories'])
            print(f"• {head_category}: {sub_count} sub-categories")
        
        # Expected count verification
        print(f"\n🎯 EXPECTED COUNT VERIFICATION")
        print("=" * 80)
        print(f"Expected sub-categories (from previous work): 62")
        print(f"Actual sub-categories found: {total_sub_categories}")
        
        if total_sub_categories == 62:
            print("✅ COUNT MATCHES EXPECTATION!")
        else:
            print(f"⚠️  COUNT MISMATCH! Expected 62, found {total_sub_categories}")
        
        # Data quality assessment
        print(f"\n🔍 DATA QUALITY ASSESSMENT")
        print("=" * 80)
        
        if len(duplicate_names) == 0 and len(duplicate_codes) == 0:
            print("✅ EXCELLENT: All names and codes are unique!")
        elif len(duplicate_names) == 0:
            print("✅ GOOD: All prequalification names are unique")
            print(f"⚠️  ISSUE: {len(duplicate_codes)} duplicate sub-codes found")
        elif len(duplicate_codes) == 0:
            print("✅ GOOD: All sub-codes are unique")
            print(f"⚠️  ISSUE: {len(duplicate_names)} duplicate prequalification names found")
        else:
            print(f"⚠️  ISSUES: {len(duplicate_names)} duplicate names and {len(duplicate_codes)} duplicate codes")
        
        return {
            'total_sub_categories': total_sub_categories,
            'total_head_categories': len(self.prequal_lookup),
            'duplicate_names': duplicate_names,
            'duplicate_codes': duplicate_codes,
            'sub_category_details': sub_category_details
        }

def main():
    verifier = PrequalLookupVerifier()
    results = verifier.generate_summary_report()
    
    print(f"\n✅ Verification complete!")

if __name__ == "__main__":
    main()





