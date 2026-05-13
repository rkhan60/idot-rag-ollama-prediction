#!/usr/bin/env python3
"""
Update Firms Data Format
Update firms_data.json to match bulletin format in prequal_lookup.json
"""

import json
import os
from datetime import datetime

class FirmsDataFormatUpdater:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.firms_data_file = '../data/firms_data.json'
        self.backup_file = f'../data/firms_data_backup_before_format_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        # Load data
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        with open(self.firms_data_file, 'r') as f:
            self.firms_data = json.load(f)
        
        # Create format mapping
        self.format_mapping = self.create_format_mapping()
        
        # Results tracking
        self.update_results = {
            'total_firms': len(self.firms_data),
            'firms_updated': 0,
            'total_prequals_updated': 0,
            'firms_with_changes': []
        }
    
    def create_format_mapping(self):
        """Create mapping from firms_data format to prequal_lookup bulletin format"""
        return {
            'Airports - Construction Inspection': 'Airports (Construction Inspection)',
            'Airports - Construction Inspection: Complex Electrical': 'Airports (Construction Inspection: Complex Electrical)',
            'Airports - Design': 'Airports (Design)',
            'Airports - Design: Complex Electrical': 'Airports (Design: Complex Electrical)',
            'Airports - Master Planning/Airport Layout Plans (ALP)': 'Airports (Master Planning: Airport Layout Plans (ALP))',
            'Environmental Reports - Environmental Assessment': 'Environmental Reports (Environmental Assessment)',
            'Environmental Reports - Environmental Impact Statement': 'Environmental Reports (Environmental Impact Statement)',
            'Geotechnical Services - Complex Geotech/Major Foundation': 'Geotechnical Services (Complex Geotech: Major Foundation)',
            'Geotechnical Services - General Geotechnical Services': 'Geotechnical Services (General Geotechnical Services)',
            'Geotechnical Services - Structure Geotechnical Reports (SGR)': 'Geotechnical Services (Structure Geotechnical Reports (SGR))',
            'Geotechnical Services - Subsurface Explorations': 'Geotechnical Services (Subsurface Explorations)',
            'Highways - Freeways': 'Highways (Freeways)',
            'Highways - Roads and Streets': 'Highways (Roads & Streets)',
            'Hydraulic Reports - Pump Stations': 'Hydraulic Reports (Pump Stations)',
            'Hydraulic Reports - Waterways: Complex': 'Hydraulic Reports (Waterways: Complex)',
            'Hydraulic Reports - Waterways: Two-Dimensional Hydraulics (2D)': 'Hydraulic Reports (Waterways: Two-Dimensional Hydraulics (2D))',
            'Hydraulic Reports - Waterways: Typical': 'Hydraulic Reports (Waterways: Typical)',
            'Location Design Studies - New Construction: Major Reconstruction': 'Location/Design Studies (New Construction: Major Reconstruction)',
            'Location Design Studies - Reconstruction: Major Rehabilitation': 'Location/Design Studies (Reconstruction: Major Rehabilitation)',
            'Location Design Studies - Rehabilitation': 'Location/Design Studies (Rehabilitation)',
            'Special Plans - Lighting: Complex': 'Special Plans (Lighting: Complex)',
            'Special Plans - Lighting: Typical': 'Special Plans (Lighting: Typical)',
            'Special Plans - Pumping Stations': 'Special Plans (Pumping Stations)',
            'Special Plans - Traffic Signals': 'Special Plans (Traffic Signals)',
            'Special Services - Aerial Mapping: LiDAR': 'Special Services (Aerial Mapping: LiDAR)',
            'Special Services - Architecture': 'Special Services (Architecture)',
            'Special Services - Asbestos Abatement Surveys': 'Special Services (Asbestos Abatement Surveys)',
            'Special Services - Construction Inspection': 'Special Services (Construction Inspection)',
            'Special Services - Electrical Engineering': 'Special Services (Electrical Engineering)',
            'Special Services - Hazardous Waste: Advance': 'Special Services (Hazardous Waste: Advance)',
            'Special Services - Hazardous Waste: Simple': 'Special Services (Hazardous Waste: Simple)',
            'Special Services - Landscape Architecture': 'Special Services (Landscape Architecture)',
            'Special Services - Mechanical': 'Special Services (Mechanical)',
            'Special Services - Mobile LiDAR': 'Special Services (Mobile LiDAR)',
            'Special Services - Project Controls': 'Special Services (Project Controls)',
            'Special Services - Public Involvement': 'Special Services (Public Involvement)',
            'Special Services - Quality Assurance HMA & Aggregate': 'Special Services (Quality Assurance: QA HMA & Aggregate)',
            'Special Services - Quality Assurance PCC & Aggregate': 'Special Services (Quality Assurance: QA PCC & Aggregate)',
            'Special Services - Sanitary': 'Special Services (Sanitary)',
            'Special Services - Specialty Firm': 'Special Services (Specialty Firm)',
            'Special Services - Subsurface Utility Engineering': 'Special Services (Subsurface Utility Engineering)',
            'Special Services - Surveying': 'Special Services (Surveying)',
            'Special Studies - Feasibility': 'Special Studies (Feasibility)',
            'Special Studies - Pavement Analysis and Evaluation': 'Special Studies (Pavement Analysis and Evaluation)',
            'Special Studies - Safety': 'Special Studies (Safety)',
            'Special Studies - Signal Coordination & Timing (SCAT)': 'Special Studies (Signal Coordination & Timing (SCAT))',
            'Special Studies - Traffic Studies': 'Special Studies (Traffic Studies)',
            'Special Studies- Location Drainage': 'Special Studies (Location Drainage)',
            'Specialty Agents - Appraiser': 'Specialty Agents (Appraiser)',
            'Specialty Agents - Negotiator': 'Specialty Agents (Negotiator)',
            'Specialty Agents - Relocation Agent': 'Specialty Agents (Relocation Agent)',
            'Specialty Agents - Review Appraiser': 'Specialty Agents (Review Appraiser)',
            'Structures - Highway: Advanced Typical': 'Structures (Highway: Advanced Typical)',
            'Structures - Highway: Complex': 'Structures (Highway: Complex)',
            'Structures - Highway: Simple': 'Structures (Highway: Simple)',
            'Structures - Highway: Typical': 'Structures (Highway: Typical)',
            'Structures - Major River Bridges': 'Structures (Major River Bridges)',
            'Structures - Moveable': 'Structures (Moveable)',
            'Structures - Railroad': 'Structures (Railroad)',
            'Transportation Studies - Mass Transit': 'Transportation Studies (Mass Transit)',
            'Transportation Studies - Railway Engineering': 'Transportation Studies (Railway Engineering)',
            'Transportation Studies - Railway Planning': 'Transportation Studies (Railway Planning)',
        }
    
    def create_backup(self):
        """Create backup of original firms_data.json"""
        print(f"📦 Creating backup: {self.backup_file}")
        
        with open(self.backup_file, 'w') as f:
            json.dump(self.firms_data, f, indent=2)
        
        print(f"✅ Backup created successfully!")
    
    def update_firms_data(self):
        """Update firms_data.json with new format"""
        print("🔄 Updating firms_data.json format...")
        
        updated_firms = []
        firms_with_changes = []
        
        for firm in self.firms_data:
            firm_code = firm['firm_code']
            firm_name = firm['firm_name']
            current_prequals = firm.get('prequalifications', [])
            
            updated_prequals = []
            changes_made = []
            
            for prequal in current_prequals:
                if prequal in self.format_mapping:
                    new_prequal = self.format_mapping[prequal]
                    updated_prequals.append(new_prequal)
                    changes_made.append({
                        'old': prequal,
                        'new': new_prequal
                    })
                    self.update_results['total_prequals_updated'] += 1
                else:
                    updated_prequals.append(prequal)  # Keep as is
            
            # Create updated firm record
            updated_firm = firm.copy()
            updated_firm['prequalifications'] = updated_prequals
            updated_firms.append(updated_firm)
            
            if changes_made:
                firms_with_changes.append({
                    'firm_code': firm_code,
                    'firm_name': firm_name,
                    'changes': changes_made
                })
                self.update_results['firms_updated'] += 1
        
        self.update_results['firms_with_changes'] = firms_with_changes
        
        # Write updated data
        with open(self.firms_data_file, 'w') as f:
            json.dump(updated_firms, f, indent=2)
        
        print(f"✅ firms_data.json updated successfully!")
        return updated_firms
    
    def validate_update(self):
        """Validate the update by checking accuracy again"""
        print("🔍 Validating update...")
        
        # Load updated data
        with open(self.firms_data_file, 'r') as f:
            updated_firms_data = json.load(f)
        
        # Quick accuracy check
        correct_matches = 0
        total_checks = 0
        
        for firm in updated_firms_data:
            firm_code = firm['firm_code']
            firm_prequals = firm.get('prequalifications', [])
            
            for firm_prequal in firm_prequals:
                total_checks += 1
                
                # Check if this prequal exists in prequal_lookup.json
                found = False
                for head_category, data in self.prequal_lookup.items():
                    for sub_code, sub_data in data['sub_categories'].items():
                        if sub_data['full_prequal_name'] == firm_prequal:
                            found = True
                            correct_matches += 1
                            break
                    if found:
                        break
        
        accuracy = (correct_matches / total_checks * 100) if total_checks > 0 else 0
        
        print(f"📊 Validation Results:")
        print(f"  Total checks: {total_checks}")
        print(f"  Correct matches: {correct_matches}")
        print(f"  Accuracy: {accuracy:.1f}%")
        
        return accuracy
    
    def show_update_summary(self):
        """Show summary of updates made"""
        print(f"\n📊 UPDATE SUMMARY")
        print("=" * 80)
        print(f"Total firms processed: {self.update_results['total_firms']}")
        print(f"Firms updated: {self.update_results['firms_updated']}")
        print(f"Total prequalifications updated: {self.update_results['total_prequals_updated']}")
        print(f"Percentage of firms updated: {(self.update_results['firms_updated']/self.update_results['total_firms'])*100:.1f}%")
        
        print(f"\n📋 Sample changes made:")
        for i, firm in enumerate(self.update_results['firms_with_changes'][:3]):
            print(f"\n🏢 {firm['firm_code']} - {firm['firm_name']}")
            for change in firm['changes'][:2]:  # Show first 2 changes
                print(f"  • {change['old']}")
                print(f"    → {change['new']}")
            if len(firm['changes']) > 2:
                print(f"  ... and {len(firm['changes']) - 2} more changes")
    
    def run_update(self):
        """Run complete update process"""
        print("🚀 UPDATING FIRMS DATA FORMAT")
        print("=" * 80)
        print("Updating firms_data.json to match bulletin format in prequal_lookup.json")
        print()
        
        # Step 1: Create backup
        self.create_backup()
        print()
        
        # Step 2: Update firms data
        updated_firms = self.update_firms_data()
        print()
        
        # Step 3: Show summary
        self.show_update_summary()
        print()
        
        # Step 4: Validate update
        accuracy = self.validate_update()
        print()
        
        # Final status
        if accuracy >= 95:
            print("🎉 EXCELLENT! Update successful with high accuracy!")
        elif accuracy >= 90:
            print("✅ GOOD! Update successful with good accuracy!")
        else:
            print("⚠️  Update completed but accuracy needs review.")
        
        print(f"\n✅ Update process complete!")
        print(f"Backup saved as: {self.backup_file}")
        
        return self.update_results

def main():
    updater = FirmsDataFormatUpdater()
    results = updater.run_update()

if __name__ == "__main__":
    main()





