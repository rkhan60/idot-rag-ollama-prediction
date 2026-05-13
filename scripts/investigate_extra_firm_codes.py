#!/usr/bin/env python3
"""
Investigate Extra Firm Codes
Find where F416-F433 firm codes are coming from in prequal_lookup.json
"""

import json

class ExtraFirmCodeInvestigator:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.firms_data_file = '../data/firms_data.json'
        
        # Load data
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        with open(self.firms_data_file, 'r') as f:
            self.firms_data = json.load(f)
        
        # Get valid firm codes
        self.valid_firm_codes = set(firm['firm_code'] for firm in self.firms_data)
        
    def find_extra_firm_codes(self):
        """Find all firm codes in prequal_lookup that don't exist in firms_data"""
        print("🔍 INVESTIGATING EXTRA FIRM CODES")
        print("=" * 80)
        
        extra_codes = []
        code_locations = {}
        
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                for firm in sub_data['firms']:
                    firm_code = firm['firm_code']
                    if firm_code not in self.valid_firm_codes:
                        extra_codes.append(firm_code)
                        if firm_code not in code_locations:
                            code_locations[firm_code] = []
                        code_locations[firm_code].append({
                            'head_category': head_category,
                            'sub_code': sub_code,
                            'firm_name': firm['firm_name']
                        })
        
        print(f"📊 ANALYSIS RESULTS:")
        print(f"Valid firm codes in firms_data: {len(self.valid_firm_codes)} (F001-F415)")
        print(f"Extra firm codes found: {len(extra_codes)}")
        print(f"Extra codes: {sorted(extra_codes)}")
        
        print(f"\n📍 LOCATIONS OF EXTRA CODES:")
        for code in sorted(extra_codes):
            locations = code_locations[code]
            print(f"\n🔍 {code}:")
            for loc in locations:
                print(f"  • {loc['head_category']}/{loc['sub_code']}: {loc['firm_name']}")
        
        return extra_codes, code_locations
    
    def check_backup_files(self):
        """Check if there are backup files that might contain the original data"""
        import os
        
        backup_files = [
            '../data/prequal_lookup_backup_before_restructure.json',
            '../data/prequal_lookup_backup_before_bulletin_update.json',
            '../data/prequal_lookup_backup_before_bulletin_fixes.json'
        ]
        
        print(f"\n🔍 CHECKING BACKUP FILES")
        print("=" * 80)
        
        for backup_file in backup_files:
            if os.path.exists(backup_file):
                print(f"📁 Found backup: {backup_file}")
                try:
                    with open(backup_file, 'r') as f:
                        backup_data = json.load(f)
                    
                    # Check if this backup has the extra codes
                    backup_codes = set()
                    if isinstance(backup_data, dict):
                        # Old format
                        for category, firms in backup_data.items():
                            backup_codes.update(firms)
                    else:
                        # New format
                        for head_category, data in backup_data.items():
                            for sub_code, sub_data in data['sub_categories'].items():
                                for firm in sub_data['firms']:
                                    backup_codes.add(firm['firm_code'])
                    
                    extra_in_backup = backup_codes - self.valid_firm_codes
                    print(f"  Extra codes in backup: {len(extra_in_backup)}")
                    if extra_in_backup:
                        print(f"  Codes: {sorted(extra_in_backup)}")
                except Exception as e:
                    print(f"  Error reading backup: {e}")
            else:
                print(f"❌ Not found: {backup_file}")
    
    def analyze_firm_code_pattern(self):
        """Analyze the pattern of firm codes to understand the issue"""
        print(f"\n🔍 ANALYZING FIRM CODE PATTERN")
        print("=" * 80)
        
        # Get all firm codes from prequal_lookup
        all_prequal_codes = set()
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                for firm in sub_data['firms']:
                    all_prequal_codes.add(firm['firm_code'])
        
        # Analyze the pattern
        prequal_codes_list = sorted(all_prequal_codes)
        firms_data_codes_list = sorted(self.valid_firm_codes)
        
        print(f"Firms data codes: {len(firms_data_codes_list)}")
        print(f"Prequal lookup codes: {len(prequal_codes_list)}")
        
        # Check if there's a pattern in the extra codes
        extra_codes = sorted(all_prequal_codes - self.valid_firm_codes)
        print(f"\nExtra codes pattern analysis:")
        print(f"Extra codes: {extra_codes}")
        
        # Check if they're sequential
        if extra_codes:
            first_extra = int(extra_codes[0][1:])
            last_extra = int(extra_codes[-1][1:])
            expected_sequence = [f"F{i:03d}" for i in range(first_extra, last_extra + 1)]
            
            if extra_codes == expected_sequence:
                print(f"✅ Extra codes are sequential: F{first_extra:03d} to F{last_extra:03d}")
            else:
                print(f"❌ Extra codes are NOT sequential")
                print(f"Expected: {expected_sequence}")
                print(f"Actual: {extra_codes}")
    
    def suggest_fix(self):
        """Suggest how to fix the extra firm codes issue"""
        print(f"\n🔧 SUGGESTED FIX")
        print("=" * 80)
        
        extra_codes, code_locations = self.find_extra_firm_codes()
        
        if not extra_codes:
            print("✅ No extra firm codes found!")
            return
        
        print(f"❌ ISSUE: Found {len(extra_codes)} extra firm codes (F416-F433)")
        print(f"These codes don't exist in firms_data.json")
        
        print(f"\n🔧 POSSIBLE SOLUTIONS:")
        print(f"1. Remove extra firm codes from prequal_lookup.json")
        print(f"2. Add missing firms to firms_data.json")
        print(f"3. Re-run the restructuring process with correct data")
        
        print(f"\n📋 AFFECTED CATEGORIES:")
        affected_categories = set()
        for code in extra_codes:
            for loc in code_locations[code]:
                affected_categories.add(f"{loc['head_category']}/{loc['sub_code']}")
        
        for category in sorted(affected_categories):
            print(f"  • {category}")
        
        print(f"\n💡 RECOMMENDATION:")
        print(f"Remove the extra firm codes (F416-F433) from prequal_lookup.json")
        print(f"since they don't exist in the source firms_data.json")
    
    def run_investigation(self):
        """Run complete investigation"""
        print("🚀 EXTRA FIRM CODE INVESTIGATION")
        print("=" * 80)
        
        # Find extra codes
        extra_codes, code_locations = self.find_extra_firm_codes()
        
        # Check backup files
        self.check_backup_files()
        
        # Analyze pattern
        self.analyze_firm_code_pattern()
        
        # Suggest fix
        self.suggest_fix()
        
        return extra_codes, code_locations

def main():
    investigator = ExtraFirmCodeInvestigator()
    extra_codes, code_locations = investigator.run_investigation()
    
    print(f"\n✅ Investigation complete!")
    print(f"Found {len(extra_codes)} extra firm codes that need to be addressed.")

if __name__ == "__main__":
    main()





