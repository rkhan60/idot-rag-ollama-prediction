#!/usr/bin/env python3
"""
Sync Firms Data with Prequalification Lookup
Update firms_data.json prequalifications to match prequal_lookup.json exactly
"""

import json
from datetime import datetime
from collections import defaultdict

class FirmsDataSyncUpdater:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.firms_data_file = '../data/firms_data.json'
        self.backup_file = f'../data/firms_data_backup_before_sync_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        # Load data
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        with open(self.firms_data_file, 'r') as f:
            self.firms_data = json.load(f)
        
        # Create lookup mappings
        self.firm_to_prequals = self.create_firm_prequal_mapping()
        
        # Results tracking
        self.sync_results = {
            'total_firms': len(self.firms_data),
            'firms_updated': 0,
            'firms_not_found_in_lookup': 0,
            'firms_with_changes': [],
            'firms_not_found': []
        }
    
    def create_firm_prequal_mapping(self):
        """Create mapping from firm to prequalifications from prequal_lookup.json"""
        firm_to_prequals = defaultdict(list)
        
        print("🔍 Creating firm to prequalification mapping from prequal_lookup.json...")
        
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                prequal_name = sub_data['full_prequal_name']
                
                for firm in sub_data['firms']:
                    firm_code = firm['firm_code']
                    firm_name = firm['firm_name']
                    
                    # Use both firm_code and firm_name as key for perfect matching
                    key = (firm_code, firm_name)
                    firm_to_prequals[key].append(prequal_name)
        
        print(f"✅ Mapping created for {len(firm_to_prequals)} firms")
        return firm_to_prequals
    
    def create_backup(self):
        """Create backup of original firms_data.json"""
        print(f"📦 Creating backup: {self.backup_file}")
        
        with open(self.backup_file, 'w') as f:
            json.dump(self.firms_data, f, indent=2)
        
        print(f"✅ Backup created successfully!")
    
    def sync_firms_data(self):
        """Sync firms_data.json with prequal_lookup.json"""
        print("🔄 Syncing firms_data.json with prequal_lookup.json...")
        
        updated_firms = []
        firms_with_changes = []
        firms_not_found = []
        
        for firm in self.firms_data:
            firm_code = firm['firm_code']
            firm_name = firm['firm_name']
            current_prequals = firm.get('prequalifications', [])
            
            # Create key for lookup
            lookup_key = (firm_code, firm_name)
            
            if lookup_key in self.firm_to_prequals:
                # Get prequalifications from lookup
                lookup_prequals = self.firm_to_prequals[lookup_key]
                
                # Check if there are changes
                current_set = set(current_prequals)
                lookup_set = set(lookup_prequals)
                
                if current_set != lookup_set:
                    # Changes needed
                    changes = {
                        'added': list(lookup_set - current_set),
                        'removed': list(current_set - lookup_set),
                        'unchanged': list(current_set & lookup_set)
                    }
                    
                    firms_with_changes.append({
                        'firm_code': firm_code,
                        'firm_name': firm_name,
                        'old_prequals': current_prequals,
                        'new_prequals': lookup_prequals,
                        'changes': changes
                    })
                    
                    self.sync_results['firms_updated'] += 1
                
                # Create updated firm record
                updated_firm = firm.copy()
                updated_firm['prequalifications'] = lookup_prequals
                updated_firms.append(updated_firm)
                
            else:
                # Firm not found in lookup
                firms_not_found.append({
                    'firm_code': firm_code,
                    'firm_name': firm_name,
                    'current_prequals': current_prequals
                })
                
                self.sync_results['firms_not_found_in_lookup'] += 1
                
                # Keep firm as is
                updated_firms.append(firm)
        
        self.sync_results['firms_with_changes'] = firms_with_changes
        self.sync_results['firms_not_found'] = firms_not_found
        
        # Write updated data
        with open(self.firms_data_file, 'w') as f:
            json.dump(updated_firms, f, indent=2)
        
        print(f"✅ firms_data.json updated successfully!")
        return updated_firms
    
    def show_sync_summary(self):
        """Show summary of sync results"""
        print(f"\n📊 SYNC SUMMARY")
        print("=" * 80)
        print(f"Total firms processed: {self.sync_results['total_firms']}")
        print(f"Firms updated: {self.sync_results['firms_updated']}")
        print(f"Firms not found in lookup: {self.sync_results['firms_not_found_in_lookup']}")
        print(f"Percentage of firms updated: {(self.sync_results['firms_updated']/self.sync_results['total_firms'])*100:.1f}%")
        
        if self.sync_results['firms_with_changes']:
            print(f"\n📋 Sample changes made:")
            for i, firm in enumerate(self.sync_results['firms_with_changes'][:3]):
                print(f"\n🏢 {firm['firm_code']} - {firm['firm_name']}")
                
                if firm['changes']['added']:
                    print(f"  Added:")
                    for prequal in firm['changes']['added']:
                        print(f"    + {prequal}")
                
                if firm['changes']['removed']:
                    print(f"  Removed:")
                    for prequal in firm['changes']['removed']:
                        print(f"    - {prequal}")
                
                if firm['changes']['unchanged']:
                    print(f"  Unchanged:")
                    for prequal in firm['changes']['unchanged']:
                        print(f"    = {prequal}")
        
        if self.sync_results['firms_not_found']:
            print(f"\n⚠️  Firms not found in prequal_lookup.json:")
            for firm in self.sync_results['firms_not_found'][:5]:
                print(f"  • {firm['firm_code']} - {firm['firm_name']}")
            if len(self.sync_results['firms_not_found']) > 5:
                print(f"  ... and {len(self.sync_results['firms_not_found']) - 5} more")
    
    def validate_sync(self):
        """Validate the sync by checking accuracy again"""
        print("🔍 Validating sync...")
        
        # Load updated data
        with open(self.firms_data_file, 'r') as f:
            updated_firms_data = json.load(f)
        
        # Quick accuracy check
        correct_matches = 0
        total_checks = 0
        
        for firm in updated_firms_data:
            firm_code = firm['firm_code']
            firm_name = firm['firm_name']
            firm_prequals = firm.get('prequalifications', [])
            
            # Check if this firm exists in lookup
            lookup_key = (firm_code, firm_name)
            if lookup_key in self.firm_to_prequals:
                lookup_prequals = self.firm_to_prequals[lookup_key]
                
                for firm_prequal in firm_prequals:
                    total_checks += 1
                    if firm_prequal in firm_prequals:
                        correct_matches += 1
        
        accuracy = (correct_matches / total_checks * 100) if total_checks > 0 else 0
        
        print(f"📊 Validation Results:")
        print(f"  Total checks: {total_checks}")
        print(f"  Correct matches: {correct_matches}")
        print(f"  Accuracy: {accuracy:.1f}%")
        
        return accuracy
    
    def run_complete_sync(self):
        """Run complete sync process"""
        print("🚀 SYNCING FIRMS_DATA.JSON WITH PREQUAL_LOOKUP.JSON")
        print("=" * 80)
        print("Using firm_code and firm_name for perfect matching")
        print("Updating only prequalification categories")
        print()
        
        # Step 1: Create backup
        self.create_backup()
        print()
        
        # Step 2: Sync firms data
        updated_firms = self.sync_firms_data()
        print()
        
        # Step 3: Show summary
        self.show_sync_summary()
        print()
        
        # Step 4: Validate sync
        accuracy = self.validate_sync()
        print()
        
        # Final status
        if accuracy >= 95:
            print("🎉 EXCELLENT! Sync successful with high accuracy!")
        elif accuracy >= 90:
            print("✅ GOOD! Sync successful with good accuracy!")
        else:
            print("⚠️  Sync completed but accuracy needs review.")
        
        print(f"\n✅ Sync process complete!")
        print(f"Backup saved as: {self.backup_file}")
        
        return self.sync_results

def main():
    syncer = FirmsDataSyncUpdater()
    results = syncer.run_complete_sync()

if __name__ == "__main__":
    main()





