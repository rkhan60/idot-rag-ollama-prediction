#!/usr/bin/env python3
"""
Fix Extra Firm Codes
Map firm names to correct codes from firms_data.json and fix prequal_lookup.json
"""

import json

class ExtraFirmCodeFixer:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.firms_data_file = '../data/firms_data.json'
        self.backup_file = '../data/prequal_lookup_backup_before_firm_code_fix.json'
        
        # Load data
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        with open(self.firms_data_file, 'r') as f:
            self.firms_data = json.load(f)
        
        # Create firm name to code mapping
        self.firm_name_to_code = {firm['firm_name']: firm['firm_code'] for firm in self.firms_data}
        
        # Extra firm names that need to be mapped
        self.extra_firm_names = [
            '"T" Engineering Service, Ltd.',
            '1st AEROW Valuation Group',
            'ABNA ENGINEERING, INC.',
            'AMERICAN SURVEYING & ENGINEERING, Ltd.',
            'CBRE, Inc',
            'CHICAGO METRO REALTY VALUATION CORP.',
            'CIVILTECH ENGINEERING, INC.',
            'CRAWFORD, MURPHY, & TILLY, INC.',
            'DECA Properties',
            'Elder Valuation Services',
            'HAMPTON, LENZINI AND RENWICK, INC.',
            'HANSON PROFESSIONAL SERVICES INC.',
            'Jay Heap & Associates, Ltd.',
            'JLL Valuation & Advisory Services LLC',
            'Planning & Valuation Consultants, Inc.',
            'Valu Pros',
            'Webster & Associates, Inc.'
        ]
    
    def create_backup(self):
        """Create backup of current prequal_lookup.json"""
        import shutil
        shutil.copy2(self.prequal_lookup_file, self.backup_file)
        print(f"✅ Backup created: {self.backup_file}")
    
    def map_extra_firm_codes(self):
        """Map extra firm names to their correct codes"""
        print("🔍 MAPPING EXTRA FIRM CODES")
        print("=" * 80)
        
        mappings = {}
        for firm_name in self.extra_firm_names:
            if firm_name in self.firm_name_to_code:
                correct_code = self.firm_name_to_code[firm_name]
                mappings[firm_name] = correct_code
                print(f"✅ {firm_name} → {correct_code}")
            else:
                print(f"❌ {firm_name} → NOT FOUND")
        
        return mappings
    
    def fix_prequal_lookup(self, mappings):
        """Fix the prequal_lookup.json by replacing incorrect firm codes"""
        print(f"\n🔧 FIXING PREQUAL_LOOKUP.JSON")
        print("=" * 80)
        
        changes_made = 0
        
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                for firm in sub_data['firms']:
                    firm_name = firm['firm_name']
                    current_code = firm['firm_code']
                    
                    # Check if this firm needs to be fixed
                    if firm_name in mappings:
                        correct_code = mappings[firm_name]
                        if current_code != correct_code:
                            print(f"🔄 {firm_name}: {current_code} → {correct_code}")
                            firm['firm_code'] = correct_code
                            changes_made += 1
        
        print(f"\n📊 FIX SUMMARY:")
        print(f"Total changes made: {changes_made}")
        
        return changes_made
    
    def verify_fix(self):
        """Verify that all firm codes now exist in firms_data.json"""
        print(f"\n🔍 VERIFYING FIX")
        print("=" * 80)
        
        valid_firm_codes = set(firm['firm_code'] for firm in self.firms_data)
        all_prequal_codes = set()
        
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                for firm in sub_data['firms']:
                    all_prequal_codes.add(firm['firm_code'])
        
        missing_codes = all_prequal_codes - valid_firm_codes
        
        if missing_codes:
            print(f"❌ Still missing codes: {sorted(missing_codes)}")
            return False
        else:
            print(f"✅ All firm codes are valid!")
            print(f"Total unique firm codes: {len(all_prequal_codes)}")
            return True
    
    def save_fixed_data(self):
        """Save the fixed prequal_lookup.json"""
        with open(self.prequal_lookup_file, 'w') as f:
            json.dump(self.prequal_lookup, f, indent=2)
        print(f"✅ Fixed data saved to: {self.prequal_lookup_file}")
    
    def run_fix(self):
        """Run the complete fix process"""
        print("🚀 EXTRA FIRM CODE FIX")
        print("=" * 80)
        
        # Create backup
        self.create_backup()
        
        # Map extra firm codes
        mappings = self.map_extra_firm_codes()
        
        if not mappings:
            print("❌ No mappings found. Cannot proceed.")
            return False
        
        # Fix prequal_lookup
        changes_made = self.fix_prequal_lookup(mappings)
        
        if changes_made == 0:
            print("❌ No changes were made.")
            return False
        
        # Save fixed data
        self.save_fixed_data()
        
        # Verify fix
        success = self.verify_fix()
        
        if success:
            print(f"\n🎉 SUCCESS! Fixed {changes_made} firm code mappings.")
        else:
            print(f"\n⚠️  Fix completed but verification failed.")
        
        return success

def main():
    fixer = ExtraFirmCodeFixer()
    success = fixer.run_fix()
    
    if success:
        print(f"\n✅ Firm code fix completed successfully!")
    else:
        print(f"\n❌ Firm code fix failed!")

if __name__ == "__main__":
    main()





