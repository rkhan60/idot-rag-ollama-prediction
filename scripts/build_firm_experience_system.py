#!/usr/bin/env python3
"""
Build Firm Experience System
Create firm experience matrix based on award data and prequalifications
"""

import json
import pandas as pd
from datetime import datetime
from collections import defaultdict
import re

class FirmExperienceSystem:
    def __init__(self):
        self.data_dir = '../data'
        self.results = {}
        
    def load_all_data_sources(self):
        """Load all required data sources"""
        print("🔄 Loading all data sources...")
        
        # Load both award structure files for comparison
        with open(f'{self.data_dir}/award_structure.json', 'r') as f:
            self.original_award_data = json.load(f)
        print(f"✅ Loaded {len(self.original_award_data)} original award records")
        
        with open(f'{self.data_dir}/award_structure_standardized.json', 'r') as f:
            self.standardized_award_data = json.load(f)
        print(f"✅ Loaded {len(self.standardized_award_data)} standardized award records")
        
        # Load firms data
        with open(f'{self.data_dir}/firms_data_standardized.json', 'r') as f:
            self.firms_data = json.load(f)
        print(f"✅ Loaded {len(self.firms_data)} firm records")
        
        # Load prequal lookup
        with open(f'{self.data_dir}/prequal_lookup.json', 'r') as f:
            self.prequal_lookup = json.load(f)
        print(f"✅ Loaded {len(self.prequal_lookup)} prequalification categories")
        
        # Load prequal tree for mapping (optional)
        try:
            with open(f'{self.data_dir}/prequalification_tree.json', 'r') as f:
                self.prequal_tree = json.load(f)
            print(f"✅ Loaded prequalification tree")
        except FileNotFoundError:
            self.prequal_tree = {}
            print(f"⚠️  Prequalification tree not found, using empty dict")
        
    def compare_award_files(self):
        """Compare original vs standardized award files"""
        print("\n🔍 Comparing Award Files...")
        
        original_count = len(self.original_award_data)
        standardized_count = len(self.standardized_award_data)
        
        # Compare data quality
        original_missing_fields = 0
        standardized_missing_fields = 0
        
        for record in self.original_award_data:
            if not record.get('Job #') or not record.get('SELECTED FIRM'):
                original_missing_fields += 1
                
        for record in self.standardized_award_data:
            if not record.get('Job #') or not record.get('SELECTED FIRM'):
                standardized_missing_fields += 1
        
        comparison = {
            'original_records': original_count,
            'standardized_records': standardized_count,
            'original_missing_fields': original_missing_fields,
            'standardized_missing_fields': standardized_missing_fields,
            'original_quality_score': ((original_count - original_missing_fields) / original_count * 100) if original_count > 0 else 0,
            'standardized_quality_score': ((standardized_count - standardized_missing_fields) / standardized_count * 100) if standardized_count > 0 else 0
        }
        
        # Determine which file to use
        if comparison['standardized_quality_score'] > comparison['original_quality_score']:
            comparison['selected_file'] = 'standardized'
            self.selected_award_data = self.standardized_award_data
        else:
            comparison['selected_file'] = 'original'
            self.selected_award_data = self.original_award_data
            
        self.results['file_comparison'] = comparison
        
        print(f"📊 Original Quality: {comparison['original_quality_score']:.1f}%")
        print(f"📊 Standardized Quality: {comparison['standardized_quality_score']:.1f}%")
        print(f"📊 Selected File: {comparison['selected_file']}")
        
        return comparison
        
    def extract_prequal_from_description(self, description):
        """Extract prequalification category from project description"""
        if not description:
            return None
            
        description_lower = description.lower()
        
        # Map common keywords to prequalification categories
        keyword_mapping = {
            'highway': ['Highways - Freeways', 'Highways - Roads and Streets'],
            'bridge': ['Structures - Highway- Complex', 'Structures - Highway- Typical'],
            'traffic': ['Special Plans - Traffic Signals'],
            'environmental': ['Environmental Reports - Environmental Assessment', 'Environmental Reports - Environmental Impact Statement'],
            'geotechnical': ['Geotechnical Services - General Geotechnical Services', 'Geotechnical Services - Complex Geotech:Major Foundation'],
            'survey': ['Special Services - Surveying'],
            'aerial': ['Special Services - Aerial Mapping:LiDAR'],
            'construction inspection': ['Special Services - Construction Inspection'],
            'airport': ['Airports - Design', 'Airports - Construction Inspection'],
            'hydraulic': ['Hydraulic Reports - Waterways- Typical', 'Hydraulic Reports - Waterways- Complex'],
            'electrical': ['Special Services - Electrical Engineering'],
            'mechanical': ['Special Services - Mechanical'],
            'landscape': ['Special Services - Landscape Architecture'],
            'architecture': ['Special Services - Architecture']
        }
        
        # Find matching categories
        matched_categories = []
        for keyword, categories in keyword_mapping.items():
            if keyword in description_lower:
                matched_categories.extend(categories)
                
        return matched_categories[0] if matched_categories else None
        
    def add_prequal_categories_to_awards(self):
        """Add prequalification categories to award data"""
        print("\n🔧 Adding Prequalification Categories...")
        
        added_count = 0
        total_records = len(self.selected_award_data)
        
        for record in self.selected_award_data:
            description = record.get('Description', '')
            
            # Extract prequalification from description
            prequal_category = self.extract_prequal_from_description(description)
            
            if prequal_category:
                record['Prequalification_Category'] = prequal_category
                added_count += 1
            else:
                record['Prequalification_Category'] = 'Unknown'
                
        self.results['prequal_addition'] = {
            'total_records': total_records,
            'added_count': added_count,
            'success_rate': (added_count / total_records * 100) if total_records > 0 else 0
        }
        
        print(f"📊 Added prequal categories to {added_count}/{total_records} records")
        print(f"📊 Success rate: {self.results['prequal_addition']['success_rate']:.1f}%")
        
    def calculate_firm_experience_matrix(self):
        """Calculate firm experience matrix (Firms × Prequals)"""
        print("\n📊 Calculating Firm Experience Matrix...")
        
        # Initialize experience matrix
        firm_experience = defaultdict(lambda: defaultdict(float))
        
        # Process each award record
        for record in self.selected_award_data:
            prime_firm_raw = record.get('SELECTED FIRM')
            if prime_firm_raw is None:
                continue
            prime_firm = str(prime_firm_raw).strip()
            subconsultants = record.get('SUBCONSULTANTS', [])
            prequal_category = record.get('Prequalification_Category', 'Unknown')
            
            if not prime_firm or not prequal_category:
                continue
                
            # Add prime firm experience (1.0 point)
            firm_experience[prime_firm.upper()][prequal_category] += 1.0
            
            # Add subconsultant experience (0.5 points each)
            if isinstance(subconsultants, list):
                for sub in subconsultants:
                    if sub and isinstance(sub, str):
                        firm_experience[sub.strip().upper()][prequal_category] += 0.5
                        
        self.results['firm_experience'] = dict(firm_experience)
        
        # Calculate statistics
        total_firms = len(firm_experience)
        total_prequals = len(set([prequal for firm_data in firm_experience.values() for prequal in firm_data.keys()]))
        
        self.results['experience_statistics'] = {
            'total_firms': total_firms,
            'total_prequals': total_prequals,
            'total_experience_points': sum(sum(firm_data.values()) for firm_data in firm_experience.values())
        }
        
        print(f"📊 Total Firms with Experience: {total_firms}")
        print(f"📊 Total Prequal Categories: {total_prequals}")
        print(f"📊 Total Experience Points: {self.results['experience_statistics']['total_experience_points']:.1f}")
        
        return firm_experience
        
    def create_firm_experience_dataframe(self):
        """Create a pandas DataFrame for firm experience"""
        print("\n📋 Creating Firm Experience DataFrame...")
        
        firm_experience = self.results['firm_experience']
        
        # Get all unique prequalification categories
        all_prequals = set()
        for firm_data in firm_experience.values():
            all_prequals.update(firm_data.keys())
        all_prequals = sorted(list(all_prequals))
        
        # Create DataFrame
        df_data = []
        for firm_name, experience_data in firm_experience.items():
            row = {'Firm_Name': firm_name}
            for prequal in all_prequals:
                row[prequal] = experience_data.get(prequal, 0.0)
            df_data.append(row)
            
        self.firm_experience_df = pd.DataFrame(df_data)
        
        print(f"📊 DataFrame Shape: {self.firm_experience_df.shape}")
        print(f"📊 Columns: {len(self.firm_experience_df.columns)}")
        
        return self.firm_experience_df
        
    def calculate_5_year_experience(self):
        """Calculate experience for last 5 years (2020-2025)"""
        print("\n📅 Calculating 5-Year Experience (2020-2025)...")
        
        # Filter records for last 5 years
        five_year_records = []
        cutoff_date = datetime(2020, 1, 1)
        
        for record in self.selected_award_data:
            selection_date_str = record.get('Selection Date', '')
            if selection_date_str:
                try:
                    selection_date = datetime.strptime(selection_date_str.split()[0], '%Y-%m-%d')
                    if selection_date >= cutoff_date:
                        five_year_records.append(record)
                except:
                    continue
                    
        # Calculate 5-year experience matrix
        five_year_experience = defaultdict(lambda: defaultdict(float))
        
        for record in five_year_records:
            prime_firm_raw = record.get('SELECTED FIRM')
            if prime_firm_raw is None:
                continue
            prime_firm = str(prime_firm_raw).strip()
            subconsultants = record.get('SUBCONSULTANTS', [])
            prequal_category = record.get('Prequalification_Category', 'Unknown')
            
            if not prime_firm or not prequal_category:
                continue
                
            # Add prime firm experience (1.0 point)
            five_year_experience[prime_firm.upper()][prequal_category] += 1.0
            
            # Add subconsultant experience (0.5 points each)
            if isinstance(subconsultants, list):
                for sub in subconsultants:
                    if sub and isinstance(sub, str):
                        five_year_experience[sub.strip().upper()][prequal_category] += 0.5
                        
        self.results['five_year_experience'] = dict(five_year_experience)
        
        # Calculate 5-year statistics
        five_year_firms = len(five_year_experience)
        five_year_points = sum(sum(firm_data.values()) for firm_data in five_year_experience.values())
        
        self.results['five_year_statistics'] = {
            'five_year_records': len(five_year_records),
            'five_year_firms': five_year_firms,
            'five_year_points': five_year_points
        }
        
        print(f"📊 5-Year Records: {len(five_year_records)}")
        print(f"📊 5-Year Firms: {five_year_firms}")
        print(f"📊 5-Year Experience Points: {five_year_points:.1f}")
        
        return five_year_experience
        
    def save_experience_data(self):
        """Save all experience data to files"""
        print("\n💾 Saving Experience Data...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save complete experience matrix
        with open(f'{self.data_dir}/firm_experience_matrix_{timestamp}.json', 'w') as f:
            json.dump(self.results['firm_experience'], f, indent=2)
        print(f"✅ Saved complete experience matrix")
        
        # Save 5-year experience matrix
        with open(f'{self.data_dir}/firm_experience_5year_{timestamp}.json', 'w') as f:
            json.dump(self.results['five_year_experience'], f, indent=2)
        print(f"✅ Saved 5-year experience matrix")
        
        # Save enhanced award data with prequals
        with open(f'{self.data_dir}/award_structure_with_prequals_{timestamp}.json', 'w') as f:
            json.dump(self.selected_award_data, f, indent=2)
        print(f"✅ Saved award data with prequalifications")
        
        # Save DataFrame
        self.firm_experience_df.to_csv(f'{self.data_dir}/firm_experience_matrix_{timestamp}.csv', index=False)
        print(f"✅ Saved experience matrix as CSV")
        
        # Save results summary
        with open(f'firm_experience_system_results_{timestamp}.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"✅ Saved system results")
        
    def generate_experience_report(self):
        """Generate comprehensive experience system report"""
        print("\n📋 Generating Experience System Report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'firm_experience_system_report_{timestamp}.txt'
        
        with open(report_file, 'w') as f:
            f.write("FIRM EXPERIENCE SYSTEM REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("SYSTEM OVERVIEW\n")
            f.write("-" * 20 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Purpose: Build firm experience matrix for scoring\n")
            f.write("Scoring: Prime Firm = 1.0 point, Sub Consultant = 0.5 point\n\n")
            
            # File comparison
            comparison = self.results.get('file_comparison', {})
            f.write("AWARD FILE COMPARISON\n")
            f.write("-" * 25 + "\n")
            f.write(f"Original Quality: {comparison.get('original_quality_score', 0):.1f}%\n")
            f.write(f"Standardized Quality: {comparison.get('standardized_quality_score', 0):.1f}%\n")
            f.write(f"Selected File: {comparison.get('selected_file', 'Unknown')}\n\n")
            
            # Prequal addition
            prequal_add = self.results.get('prequal_addition', {})
            f.write("Prequalification Addition\n")
            f.write("-" * 25 + "\n")
            f.write(f"Total Records: {prequal_add.get('total_records', 0)}\n")
            f.write(f"Added Successfully: {prequal_add.get('added_count', 0)}\n")
            f.write(f"Success Rate: {prequal_add.get('success_rate', 0):.1f}%\n\n")
            
            # Experience statistics
            exp_stats = self.results.get('experience_statistics', {})
            f.write("COMPLETE EXPERIENCE STATISTICS\n")
            f.write("-" * 35 + "\n")
            f.write(f"Total Firms: {exp_stats.get('total_firms', 0)}\n")
            f.write(f"Total Prequals: {exp_stats.get('total_prequals', 0)}\n")
            f.write(f"Total Experience Points: {exp_stats.get('total_experience_points', 0):.1f}\n\n")
            
            # 5-year statistics
            five_year_stats = self.results.get('five_year_statistics', {})
            f.write("5-YEAR EXPERIENCE STATISTICS\n")
            f.write("-" * 35 + "\n")
            f.write(f"5-Year Records: {five_year_stats.get('five_year_records', 0)}\n")
            f.write(f"5-Year Firms: {five_year_stats.get('five_year_firms', 0)}\n")
            f.write(f"5-Year Experience Points: {five_year_stats.get('five_year_points', 0):.1f}\n\n")
            
            f.write("NEXT STEPS\n")
            f.write("-" * 10 + "\n")
            f.write("1. Use experience matrix for firm scoring\n")
            f.write("2. Integrate with prediction system\n")
            f.write("3. Test accuracy improvements\n")
            
        print(f"✅ Experience system report saved: {report_file}")
        return report_file
        
    def run_experience_system_build(self):
        """Run complete firm experience system build"""
        print("🚀 Starting Firm Experience System Build...")
        
        # Load all data sources
        self.load_all_data_sources()
        
        # Compare award files and select best one
        self.compare_award_files()
        
        # Add prequalification categories
        self.add_prequal_categories_to_awards()
        
        # Calculate complete experience matrix
        self.calculate_firm_experience_matrix()
        
        # Create DataFrame
        self.create_firm_experience_dataframe()
        
        # Calculate 5-year experience
        self.calculate_5_year_experience()
        
        # Save all data
        self.save_experience_data()
        
        # Generate report
        report_file = self.generate_experience_report()
        
        print(f"\n✅ Firm Experience System Build Complete!")
        print(f"📄 Report: {report_file}")
        
        return self.results

if __name__ == "__main__":
    builder = FirmExperienceSystem()
    results = builder.run_experience_system_build()
