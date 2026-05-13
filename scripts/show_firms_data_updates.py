#!/usr/bin/env python3
"""
Show Firms Data Updates Needed
Analyze and show what changes are needed in firms_data.json to match bulletin format
"""

import json
from collections import defaultdict

class FirmsDataUpdateAnalyzer:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.firms_data_file = '../data/firms_data.json'
        
        # Load data
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        with open(self.firms_data_file, 'r') as f:
            self.firms_data = json.load(f)
        
        # Create mapping from old format to bulletin format
        self.format_mapping = self.create_format_mapping()
        
        # Analysis results
        self.analysis_results = {
            'total_firms': len(self.firms_data),
            'firms_needing_updates': 0,
            'total_prequals_to_update': 0,
            'format_changes': [],
            'firms_with_changes': []
        }
    
    def create_format_mapping(self):
        """Create mapping from firms_data format to prequal_lookup bulletin format"""
        mapping = {}
        
        # Extract all prequal names from prequal_lookup.json
        bulletin_formats = set()
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                bulletin_formats.add(sub_data['full_prequal_name'])
        
        # Create reverse mapping for common patterns
        reverse_mapping = {
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
        
        return reverse_mapping
    
    def analyze_firms_data_updates(self):
        """Analyze what updates are needed in firms_data.json"""
        print("🔍 ANALYZING FIRMS DATA UPDATES NEEDED")
        print("=" * 80)
        
        firms_with_changes = []
        total_prequals_to_update = 0
        
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
                    total_prequals_to_update += 1
                else:
                    updated_prequals.append(prequal)  # Keep as is
            
            if changes_made:
                firms_with_changes.append({
                    'firm_code': firm_code,
                    'firm_name': firm_name,
                    'current_prequals': current_prequals,
                    'updated_prequals': updated_prequals,
                    'changes': changes_made
                })
        
        self.analysis_results['firms_needing_updates'] = len(firms_with_changes)
        self.analysis_results['total_prequals_to_update'] = total_prequals_to_update
        self.analysis_results['firms_with_changes'] = firms_with_changes
        
        return firms_with_changes
    
    def show_summary(self):
        """Show summary of changes needed"""
        print(f"\n📊 SUMMARY OF CHANGES NEEDED")
        print("=" * 80)
        print(f"Total firms in firms_data.json: {self.analysis_results['total_firms']}")
        print(f"Firms needing updates: {self.analysis_results['firms_needing_updates']}")
        print(f"Total prequalifications to update: {self.analysis_results['total_prequals_to_update']}")
        print(f"Percentage of firms needing updates: {(self.analysis_results['firms_needing_updates']/self.analysis_results['total_firms'])*100:.1f}%")
    
    def show_format_mapping(self):
        """Show the format mapping that will be applied"""
        print(f"\n🔄 FORMAT MAPPING (Old → New)")
        print("=" * 80)
        print("The following format changes will be applied:")
        print()
        
        for old_format, new_format in self.format_mapping.items():
            print(f"• {old_format}")
            print(f"  → {new_format}")
            print()
    
    def show_sample_changes(self, max_samples=5):
        """Show sample changes that will be made"""
        print(f"\n📋 SAMPLE CHANGES (First {max_samples} firms)")
        print("=" * 80)
        
        if not self.analysis_results['firms_with_changes']:
            print("✅ No changes needed!")
            return
        
        for i, firm in enumerate(self.analysis_results['firms_with_changes'][:max_samples]):
            print(f"\n🏢 Firm: {firm['firm_code']} - {firm['firm_name']}")
            print("Changes:")
            for change in firm['changes']:
                print(f"  • {change['old']}")
                print(f"    → {change['new']}")
            print()
    
    def show_all_changes(self):
        """Show all changes that will be made"""
        print(f"\n📋 ALL CHANGES TO BE MADE")
        print("=" * 80)
        
        if not self.analysis_results['firms_with_changes']:
            print("✅ No changes needed!")
            return
        
        for firm in self.analysis_results['firms_with_changes']:
            print(f"\n🏢 Firm: {firm['firm_code']} - {firm['firm_name']}")
            print("Changes:")
            for change in firm['changes']:
                print(f"  • {change['old']}")
                print(f"    → {change['new']}")
            print()
    
    def run_analysis(self):
        """Run complete analysis"""
        print("🚀 FIRMS DATA UPDATE ANALYSIS")
        print("=" * 80)
        print("This analysis shows what changes are needed to update firms_data.json")
        print("to match the bulletin format in prequal_lookup.json")
        print()
        
        # Analyze changes needed
        firms_with_changes = self.analyze_firms_data_updates()
        
        # Show summary
        self.show_summary()
        
        # Show format mapping
        self.show_format_mapping()
        
        # Show sample changes
        self.show_sample_changes()
        
        # Ask if user wants to see all changes
        print(f"\n❓ Would you like to see ALL changes? (y/n): ", end="")
        response = input().lower().strip()
        
        if response in ['y', 'yes']:
            self.show_all_changes()
        
        print(f"\n✅ Analysis complete!")
        print(f"Ready to apply {self.analysis_results['total_prequals_to_update']} format updates to {self.analysis_results['firms_needing_updates']} firms.")
        
        return self.analysis_results

def main():
    analyzer = FirmsDataUpdateAnalyzer()
    results = analyzer.run_analysis()

if __name__ == "__main__":
    main()





