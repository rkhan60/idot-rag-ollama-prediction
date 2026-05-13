#!/usr/bin/env python3
"""
Check Specific Firm
Verify firm "T" Engineering Service, Ltd. in both files
"""

import json

class SpecificFirmChecker:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.firms_data_file = '../data/firms_data.json'
        
        # Load data
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        with open(self.firms_data_file, 'r') as f:
            self.firms_data = json.load(f)
    
    def find_firm_in_firms_data(self, firm_name):
        """Find firm in firms_data.json"""
        print(f"🔍 SEARCHING IN FIRMS_DATA.JSON")
        print("=" * 80)
        
        for firm in self.firms_data:
            if firm['firm_name'] == firm_name:
                print(f"✅ FOUND: {firm['firm_name']}")
                print(f"   Firm Code: {firm['firm_code']}")
                print(f"   Email: {firm.get('email', 'N/A')}")
                print(f"   DBE Status: {firm.get('dbe_status', 'N/A')}")
                print(f"   Location: {firm.get('location', 'N/A')}")
                print(f"   District: {firm.get('district', 'N/A')}")
                print(f"   Prequalifications ({len(firm.get('prequalifications', []))}):")
                
                for prequal in firm.get('prequalifications', []):
                    print(f"     • {prequal}")
                
                return firm
        
        print(f"❌ NOT FOUND: {firm_name}")
        return None
    
    def find_firm_in_prequal_lookup(self, firm_name):
        """Find firm in prequal_lookup.json"""
        print(f"\n🔍 SEARCHING IN PREQUAL_LOOKUP.JSON")
        print("=" * 80)
        
        firm_found = False
        firm_appearances = []
        
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                prequal_name = sub_data['full_prequal_name']
                firms_list = sub_data['firms']
                
                for firm in firms_list:
                    if firm['firm_name'] == firm_name:
                        firm_found = True
                        firm_appearances.append({
                            'head_category': head_category,
                            'sub_code': sub_code,
                            'prequal_name': prequal_name,
                            'firm_code': firm['firm_code']
                        })
        
        if firm_found:
            print(f"✅ FOUND: {firm_name}")
            print(f"   Appears in {len(firm_appearances)} prequalification categories:")
            
            for appearance in firm_appearances:
                print(f"     • {appearance['prequal_name']}")
                print(f"       (Code: {appearance['sub_code']}, Category: {appearance['head_category']})")
        else:
            print(f"❌ NOT FOUND: {firm_name}")
        
        return firm_appearances
    
    def check_specific_prequals(self, firm_name, target_prequals):
        """Check specific prequalifications for the firm"""
        print(f"\n🔍 CHECKING SPECIFIC PREQUALIFICATIONS")
        print("=" * 80)
        print(f"Target prequalifications to verify:")
        for prequal in target_prequals:
            print(f"   • {prequal}")
        print()
        
        # Check in firms_data.json
        firm_data = self.find_firm_in_firms_data(firm_name)
        if firm_data:
            firm_prequals = firm_data.get('prequalifications', [])
            
            print(f"📋 COMPARISON WITH FIRMS_DATA.JSON:")
            for target_prequal in target_prequals:
                found = target_prequal in firm_prequals
                status = "✅ FOUND" if found else "❌ NOT FOUND"
                print(f"   {status}: {target_prequal}")
        
        # Check in prequal_lookup.json
        firm_appearances = self.find_firm_in_prequal_lookup(firm_name)
        if firm_appearances:
            lookup_prequals = [app['prequal_name'] for app in firm_appearances]
            
            print(f"\n📋 COMPARISON WITH PREQUAL_LOOKUP.JSON:")
            for target_prequal in target_prequals:
                found = target_prequal in lookup_prequals
                status = "✅ FOUND" if found else "❌ NOT FOUND"
                print(f"   {status}: {target_prequal}")
    
    def analyze_discrepancies(self, firm_name, target_prequals):
        """Analyze any discrepancies between the two files"""
        print(f"\n🔍 DISCREPANCY ANALYSIS")
        print("=" * 80)
        
        # Get firm data from both files
        firm_data = None
        for firm in self.firms_data:
            if firm['firm_name'] == firm_name:
                firm_data = firm
                break
        
        firm_appearances = []
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                for firm in sub_data['firms']:
                    if firm['firm_name'] == firm_name:
                        firm_appearances.append({
                            'prequal_name': sub_data['full_prequal_name'],
                            'sub_code': sub_code,
                            'head_category': head_category
                        })
        
        if firm_data and firm_appearances:
            firms_data_prequals = set(firm_data.get('prequalifications', []))
            lookup_prequals = set([app['prequal_name'] for app in firm_appearances])
            
            # Find differences
            only_in_firms_data = firms_data_prequals - lookup_prequals
            only_in_lookup = lookup_prequals - firms_data_prequals
            common = firms_data_prequals & lookup_prequals
            
            print(f"📊 COMPARISON RESULTS:")
            print(f"   Common prequalifications: {len(common)}")
            print(f"   Only in firms_data.json: {len(only_in_firms_data)}")
            print(f"   Only in prequal_lookup.json: {len(only_in_lookup)}")
            
            if only_in_firms_data:
                print(f"\n   Only in firms_data.json:")
                for prequal in only_in_firms_data:
                    print(f"     • {prequal}")
            
            if only_in_lookup:
                print(f"\n   Only in prequal_lookup.json:")
                for prequal in only_in_lookup:
                    print(f"     • {prequal}")
            
            if common:
                print(f"\n   Common in both files:")
                for prequal in common:
                    print(f"     • {prequal}")
    
    def run_complete_check(self, firm_name, target_prequals):
        """Run complete check for the firm"""
        print(f"🚀 COMPLETE FIRM CHECK: {firm_name}")
        print("=" * 80)
        
        # Check specific prequalifications
        self.check_specific_prequals(firm_name, target_prequals)
        
        # Analyze discrepancies
        self.analyze_discrepancies(firm_name, target_prequals)
        
        print(f"\n✅ Complete check finished!")

def main():
    checker = SpecificFirmChecker()
    
    firm_name = '"T" Engineering Service, Ltd.'
    target_prequals = [
        'Special Services - Specialty Firm',
        'Specialty Agents - Appraiser',
        'Specialty Agents - Review Appraiser'
    ]
    
    checker.run_complete_check(firm_name, target_prequals)

if __name__ == "__main__":
    main()





