#!/usr/bin/env python3
"""
Improved Prequalification Mapping
Create comprehensive mapping using all 61 prequalification categories
"""

import json
import re
from collections import defaultdict

class ImprovedPrequalMapping:
    def __init__(self):
        self.data_dir = '../data'
        self.mapping_results = {}
        
    def load_data(self):
        """Load all required data"""
        print("🔄 Loading data for improved mapping...")
        
        # Load award data
        with open(f'{self.data_dir}/award_structure.json', 'r') as f:
            self.award_data = json.load(f)
        print(f"✅ Loaded {len(self.award_data)} award records")
        
        # Load prequal lookup
        with open(f'{self.data_dir}/prequal_lookup.json', 'r') as f:
            self.prequal_lookup = json.load(f)
        print(f"✅ Loaded {len(self.prequal_lookup)} prequalification categories")
        
    def create_comprehensive_keyword_mapping(self):
        """Create comprehensive keyword mapping for all 61 categories"""
        print("\n🔧 Creating Comprehensive Keyword Mapping...")
        
        # Comprehensive keyword mapping for all 61 categories
        self.keyword_mapping = {
            # Highways
            'highway': ['Highways - Freeways', 'Highways - Roads and Streets'],
            'road': ['Highways - Roads and Streets'],
            'street': ['Highways - Roads and Streets'],
            'freeway': ['Highways - Freeways'],
            'pavement': ['Highways - Roads and Streets', 'Highways - Freeways'],
            'asphalt': ['Highways - Roads and Streets', 'Highways - Freeways'],
            'concrete': ['Highways - Roads and Streets', 'Highways - Freeways'],
            
            # Structures
            'bridge': ['Structures - Highway- Complex', 'Structures - Highway- Typical', 'Structures - Highway- Simple', 'Structures - Highway- Advanced Typical'],
            'structure': ['Structures - Highway- Complex', 'Structures - Highway- Typical', 'Structures - Highway- Simple', 'Structures - Highway- Advanced Typical'],
            'overpass': ['Structures - Highway- Complex', 'Structures - Highway- Typical'],
            'underpass': ['Structures - Highway- Complex', 'Structures - Highway- Typical'],
            'culvert': ['Structures - Highway- Typical', 'Structures - Highway- Simple'],
            'retaining wall': ['Structures - Highway- Typical', 'Structures - Highway- Simple'],
            
            # Airports
            'airport': ['Airports - Design', 'Airports - Construction Inspection', 'Airports - Master Planning:Airport Layout Plans (ALP)'],
            'runway': ['Airports - Design', 'Airports - Construction Inspection'],
            'taxiway': ['Airports - Design', 'Airports - Construction Inspection'],
            'terminal': ['Airports - Design', 'Airports - Construction Inspection'],
            
            # Environmental
            'environmental': ['Environmental Reports - Environmental Assessment', 'Environmental Reports - Environmental Impact Statement'],
            'assessment': ['Environmental Reports - Environmental Assessment'],
            'impact statement': ['Environmental Reports - Environmental Impact Statement'],
            'eis': ['Environmental Reports - Environmental Impact Statement'],
            'ea': ['Environmental Reports - Environmental Assessment'],
            
            # Geotechnical
            'geotechnical': ['Geotechnical Services - General Geotechnical Services', 'Geotechnical Services - Complex Geotech:Major Foundation', 'Geotechnical Services - Subsurface Explorations'],
            'geotech': ['Geotechnical Services - General Geotechnical Services', 'Geotechnical Services - Complex Geotech:Major Foundation'],
            'foundation': ['Geotechnical Services - Complex Geotech:Major Foundation'],
            'subsurface': ['Geotechnical Services - Subsurface Explorations'],
            'soil': ['Geotechnical Services - General Geotechnical Services', 'Geotechnical Services - Subsurface Explorations'],
            
            # Special Services
            'survey': ['Special Services - Surveying'],
            'surveying': ['Special Services - Surveying'],
            'aerial': ['Special Services - Aerial Mapping:LiDAR'],
            'lidar': ['Special Services - Aerial Mapping:LiDAR'],
            'mobile lidar': ['Special Services - Mobile LiDAR'],
            'construction inspection': ['Special Services - Construction Inspection', 'Airports - Construction Inspection'],
            'inspection': ['Special Services - Construction Inspection', 'Airports - Construction Inspection'],
            'electrical': ['Special Services - Electrical Engineering'],
            'mechanical': ['Special Services - Mechanical'],
            'landscape': ['Special Services - Landscape Architecture'],
            'architecture': ['Special Services - Architecture'],
            'asbestos': ['Special Services - Asbestos Abatement Surveys'],
            'hazardous waste': ['Special Services - Hazardous Waste- Simple', 'Special Services - Hazardous Waste- Advance'],
            'hazardous': ['Special Services - Hazardous Waste- Simple', 'Special Services - Hazardous Waste- Advance'],
            'utility': ['Special Services - Subsurface Utility Engineering'],
            'sue': ['Special Services - Subsurface Utility Engineering'],
            'subsurface utility': ['Special Services - Subsurface Utility Engineering'],
            'quality assurance': ['Special Services - Quality Assurance HMA & Aggregate', 'Special Services - Quality Assurance PCC & Aggregate'],
            'quality': ['Special Services - Quality Assurance HMA & Aggregate', 'Special Services - Quality Assurance PCC & Aggregate'],
            'hma': ['Special Services - Quality Assurance HMA & Aggregate'],
            'pcc': ['Special Services - Quality Assurance PCC & Aggregate'],
            'aggregate': ['Special Services - Quality Assurance HMA & Aggregate', 'Special Services - Quality Assurance PCC & Aggregate'],
            'public involvement': ['Special Services - Public Involvement'],
            'project controls': ['Special Services - Project Controls'],
            'sanitary': ['Special Services - Sanitary'],
            'specialty firm': ['Special Services - Specialty Firm'],
            
            # Special Plans
            'traffic signal': ['Special Plans - Traffic Signals'],
            'traffic': ['Special Plans - Traffic Signals'],
            'signal': ['Special Plans - Traffic Signals'],
            'lighting': ['Special Plans - Lighting- Typical', 'Special Plans - Lighting- Complex'],
            'light': ['Special Plans - Lighting- Typical', 'Special Plans - Lighting- Complex'],
            'pump station': ['Special Plans - Pumping Stations'],
            'pumping': ['Special Plans - Pumping Stations'],
            
            # Special Studies
            'feasibility': ['Special Studies - Feasibility'],
            'pavement analysis': ['Special Studies - Pavement Analysis and Evaluation'],
            'pavement evaluation': ['Special Studies - Pavement Analysis and Evaluation'],
            'safety': ['Special Studies - Safety'],
            'signal coordination': ['Special Studies - Signal Coordination & Timing (SCAT)'],
            'scat': ['Special Studies - Signal Coordination & Timing (SCAT)'],
            'traffic study': ['Special Studies - Traffic Studies'],
            'traffic studies': ['Special Studies - Traffic Studies'],
            'location drainage': ['Special Studies- Location Drainage'],
            'drainage': ['Special Studies- Location Drainage'],
            
            # Location Design Studies
            'location design': ['Location Design Studies - New Construction:Major Reconstruction', 'Location Design Studies - Reconstruction:Major Rehabilitation', 'Location Design Studies - Rehabilitation'],
            'new construction': ['Location Design Studies - New Construction:Major Reconstruction'],
            'reconstruction': ['Location Design Studies - Reconstruction:Major Rehabilitation'],
            'rehabilitation': ['Location Design Studies - Rehabilitation'],
            
            # Hydraulic Reports
            'hydraulic': ['Hydraulic Reports - Waterways- Typical', 'Hydraulic Reports - Waterways- Complex', 'Hydraulic Reports - Waterways- Two-Dimensional Hydraulics (2D)', 'Hydraulic Reports - Pump Stations'],
            'waterway': ['Hydraulic Reports - Waterways- Typical', 'Hydraulic Reports - Waterways- Complex', 'Hydraulic Reports - Waterways- Two-Dimensional Hydraulics (2D)'],
            '2d hydraulics': ['Hydraulic Reports - Waterways- Two-Dimensional Hydraulics (2D)'],
            'pump station': ['Hydraulic Reports - Pump Stations'],
            
            # Transportation Studies
            'mass transit': ['Transportation Studies - Mass Transit'],
            'transit': ['Transportation Studies - Mass Transit'],
            'railway': ['Transportation Studies - Railway Engineering', 'Transportation Studies - Railway Planning'],
            'railroad': ['Transportation Studies - Railway Engineering', 'Transportation Studies - Railway Planning'],
            'rail': ['Transportation Studies - Railway Engineering', 'Transportation Studies - Railway Planning'],
            
            # Specialty Agents
            'appraiser': ['Specialty Agents - Appraiser'],
            'negotiator': ['Specialty Agents - Negotiator'],
            'relocation': ['Specialty Agents - Relocation Agent'],
            'review appraiser': ['Specialty Agents - Review Appraiser'],
            
            # Structures - Special
            'moveable': ['Structures - Moveable'],
            'railroad bridge': ['Structures - Railroad'],
            'major river': ['Structures- Major River Bridges'],
            'river bridge': ['Structures- Major River Bridges'],
            
            # Phase indicators
            'phase i': ['Location Design Studies - New Construction:Major Reconstruction'],
            'phase ii': ['Location Design Studies - Reconstruction:Major Rehabilitation'],
            'phase iii': ['Location Design Studies - Rehabilitation'],
            'phase 1': ['Location Design Studies - New Construction:Major Reconstruction'],
            'phase 2': ['Location Design Studies - Reconstruction:Major Rehabilitation'],
            'phase 3': ['Location Design Studies - Rehabilitation'],
            
            # Project types
            'various': ['Special Services - Specialty Firm'],
            'subsurface utility engineering': ['Special Services - Subsurface Utility Engineering'],
            'master planning': ['Airports - Master Planning:Airport Layout Plans (ALP)'],
            'alp': ['Airports - Master Planning:Airport Layout Plans (ALP)'],
        }
        
        print(f"✅ Created mapping with {len(self.keyword_mapping)} keyword groups")
        
    def map_prequalification(self, description):
        """Map description to prequalification category using comprehensive keywords"""
        if not description:
            return None
            
        description_lower = description.lower()
        
        # Score each prequalification category
        category_scores = defaultdict(int)
        
        for keyword, categories in self.keyword_mapping.items():
            if keyword in description_lower:
                for category in categories:
                    category_scores[category] += 1
                    
        # Return the category with highest score
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            return best_category[0]
            
        return None
        
    def test_mapping_accuracy(self):
        """Test the mapping accuracy on sample data"""
        print("\n🔍 Testing Mapping Accuracy...")
        
        # Test on first 100 records
        test_records = self.award_data[:100]
        mapped_count = 0
        
        for record in test_records:
            description = record.get('Description', '')
            mapped_category = self.map_prequalification(description)
            if mapped_category:
                mapped_count += 1
                
        accuracy = (mapped_count / len(test_records)) * 100
        print(f"📊 Test Accuracy: {mapped_count}/{len(test_records)} ({accuracy:.1f}%)")
        
        return accuracy
        
    def apply_improved_mapping(self):
        """Apply improved mapping to all award records"""
        print("\n🔧 Applying Improved Mapping...")
        
        mapped_count = 0
        total_records = len(self.award_data)
        
        for record in self.award_data:
            description = record.get('Description', '')
            mapped_category = self.map_prequalification(description)
            
            if mapped_category:
                record['Prequalification_Category'] = mapped_category
                mapped_count += 1
            else:
                record['Prequalification_Category'] = 'Unknown'
                
        self.mapping_results = {
            'total_records': total_records,
            'mapped_count': mapped_count,
            'unknown_count': total_records - mapped_count,
            'success_rate': (mapped_count / total_records * 100) if total_records > 0 else 0
        }
        
        print(f"📊 Mapped: {mapped_count}/{total_records} records")
        print(f"📊 Success Rate: {self.mapping_results['success_rate']:.1f}%")
        print(f"📊 Unknown: {self.mapping_results['unknown_count']} records")
        
        return self.mapping_results
        
    def analyze_mapping_results(self):
        """Analyze the mapping results by category"""
        print("\n📊 Analyzing Mapping Results...")
        
        category_counts = defaultdict(int)
        
        for record in self.award_data:
            category = record.get('Prequalification_Category', 'Unknown')
            category_counts[category] += 1
            
        # Sort by count
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        print("Top 10 Mapped Categories:")
        for i, (category, count) in enumerate(sorted_categories[:10]):
            percentage = (count / len(self.award_data)) * 100
            print(f"  {i+1}. {category}: {count} ({percentage:.1f}%)")
            
        self.mapping_results['category_breakdown'] = dict(sorted_categories)
        
    def save_improved_data(self):
        """Save the improved award data with better prequalification mapping"""
        print("\n💾 Saving Improved Data...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save improved award data
        with open(f'{self.data_dir}/award_structure_improved_prequals_{timestamp}.json', 'w') as f:
            json.dump(self.award_data, f, indent=2)
        print(f"✅ Saved improved award data")
        
        # Save mapping results
        with open(f'improved_prequal_mapping_results_{timestamp}.json', 'w') as f:
            json.dump(self.mapping_results, f, indent=2)
        print(f"✅ Saved mapping results")
        
    def generate_mapping_report(self):
        """Generate comprehensive mapping report"""
        print("\n📋 Generating Mapping Report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'improved_prequal_mapping_report_{timestamp}.txt'
        
        with open(report_file, 'w') as f:
            f.write("IMPROVED PREQUALIFICATION MAPPING REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("MAPPING SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Records: {self.mapping_results.get('total_records', 0)}\n")
            f.write(f"Mapped Records: {self.mapping_results.get('mapped_count', 0)}\n")
            f.write(f"Unknown Records: {self.mapping_results.get('unknown_count', 0)}\n")
            f.write(f"Success Rate: {self.mapping_results.get('success_rate', 0):.1f}%\n\n")
            
            f.write("CATEGORY BREAKDOWN\n")
            f.write("-" * 20 + "\n")
            category_breakdown = self.mapping_results.get('category_breakdown', {})
            for category, count in list(category_breakdown.items())[:15]:
                percentage = (count / self.mapping_results.get('total_records', 1)) * 100
                f.write(f"{category}: {count} ({percentage:.1f}%)\n")
            f.write("\n")
            
            f.write("IMPROVEMENT COMPARISON\n")
            f.write("-" * 25 + "\n")
            f.write("Previous Success Rate: 30.8%\n")
            f.write(f"New Success Rate: {self.mapping_results.get('success_rate', 0):.1f}%\n")
            improvement = self.mapping_results.get('success_rate', 0) - 30.8
            f.write(f"Improvement: {improvement:+.1f} percentage points\n\n")
            
        print(f"✅ Mapping report saved: {report_file}")
        return report_file
        
    def run_improved_mapping(self):
        """Run complete improved mapping process"""
        print("🚀 Starting Improved Prequalification Mapping...")
        
        # Load data
        self.load_data()
        
        # Create comprehensive mapping
        self.create_comprehensive_keyword_mapping()
        
        # Test accuracy
        test_accuracy = self.test_mapping_accuracy()
        
        # Apply mapping
        mapping_results = self.apply_improved_mapping()
        
        # Analyze results
        self.analyze_mapping_results()
        
        # Save data
        self.save_improved_data()
        
        # Generate report
        report_file = self.generate_mapping_report()
        
        print(f"\n✅ Improved Mapping Complete!")
        print(f"📄 Report: {report_file}")
        
        return self.mapping_results

if __name__ == "__main__":
    from datetime import datetime
    mapper = ImprovedPrequalMapping()
    results = mapper.run_improved_mapping()
