#!/usr/bin/env python3
"""
Comprehensive Data Verification
Analyze and cross-verify all data sources without making changes
"""

import json
import pandas as pd
import os
from collections import defaultdict
from datetime import datetime

class ComprehensiveDataVerifier:
    def __init__(self):
        self.data_dir = '../data'
        self.verification_results = {}
        
    def load_all_data_sources(self):
        """Load all data sources for verification"""
        print("🔄 Loading all data sources for verification...")
        
        # Load award data
        with open(f'{self.data_dir}/award_structure.json', 'r') as f:
            self.award_data = json.load(f)
        print(f"✅ Loaded {len(self.award_data)} award records")
        
        # Load firms data
        with open(f'{self.data_dir}/firms_data.json', 'r') as f:
            self.firms_data = json.load(f)
        print(f"✅ Loaded {len(self.firms_data)} firm records")
        
        # Load prequal lookup
        with open(f'{self.data_dir}/prequal_lookup.json', 'r') as f:
            self.prequal_lookup = json.load(f)
        print(f"✅ Loaded {len(self.prequal_lookup)} prequalification categories")
        
        # Load IDOT Excel
        self.idot_excel = pd.read_excel(f'{self.data_dir}/IDOTConsultantList.xlsx')
        print(f"✅ Loaded IDOT Excel: {self.idot_excel.shape}")
        
        # Load improved mapping results
        try:
            with open(f'{self.data_dir}/award_structure_improved_prequals_20250807_113751.json', 'r') as f:
                self.improved_award_data = json.load(f)
            print(f"✅ Loaded improved award data: {len(self.improved_award_data)} records")
        except FileNotFoundError:
            self.improved_award_data = None
            print("⚠️  Improved award data not found")
            
    def analyze_prequal_json_structure(self):
        """Analyze the prequal_json folder structure"""
        print("\n🔍 Analyzing Prequal JSON Structure...")
        
        prequal_json_dir = f'{self.data_dir}/prequal_json'
        json_files = []
        
        if os.path.exists(prequal_json_dir):
            for file in os.listdir(prequal_json_dir):
                if file.endswith('.json'):
                    json_files.append(file)
                    
        # Load summary.json
        summary_file = f'{prequal_json_dir}/summary.json'
        if os.path.exists(summary_file):
            with open(summary_file, 'r') as f:
                summary_data = json.load(f)
                
        prequal_json_analysis = {
            'total_files': len(json_files),
            'summary_total_files': summary_data.get('total_files_processed', 0) if 'summary_data' in locals() else 0,
            'summary_total_firms': summary_data.get('total_firms_found', 0) if 'summary_data' in locals() else 0,
            'files_list': json_files[:10]  # First 10 files
        }
        
        self.verification_results['prequal_json_analysis'] = prequal_json_analysis
        
        print(f"📊 JSON Files Found: {len(json_files)}")
        print(f"📊 Summary Total Files: {prequal_json_analysis['summary_total_files']}")
        print(f"📊 Summary Total Firms: {prequal_json_analysis['summary_total_firms']}")
        
    def analyze_pre_qual_d_structure(self):
        """Analyze the pre-qual_d folder structure"""
        print("\n🔍 Analyzing Pre-qual_d Structure...")
        
        pre_qual_d_dir = f'{self.data_dir}/pre-qual_d'
        txt_files = []
        
        if os.path.exists(pre_qual_d_dir):
            for file in os.listdir(pre_qual_d_dir):
                if file.endswith('.txt'):
                    txt_files.append(file)
                    
        pre_qual_d_analysis = {
            'total_files': len(txt_files),
            'files_list': txt_files[:10]  # First 10 files
        }
        
        self.verification_results['pre_qual_d_analysis'] = pre_qual_d_analysis
        
        print(f"📊 Text Files Found: {len(txt_files)}")
        
    def cross_verify_prequal_categories(self):
        """Cross-verify prequalification categories across all sources"""
        print("\n🔍 Cross-verifying Prequalification Categories...")
        
        # Get categories from different sources
        prequal_lookup_categories = set(self.prequal_lookup.keys())
        
        # Get categories from prequal_json files
        prequal_json_categories = set()
        prequal_json_dir = f'{self.data_dir}/prequal_json'
        if os.path.exists(prequal_json_dir):
            for file in os.listdir(prequal_json_dir):
                if file.endswith('.json') and file != 'summary.json':
                    # Convert filename to category name
                    category_name = file.replace('.json', '').replace('___', ' - ').replace('__', ' - ')
                    prequal_json_categories.add(category_name)
                    
        # Get categories from pre-qual_d files
        pre_qual_d_categories = set()
        pre_qual_d_dir = f'{self.data_dir}/pre-qual_d'
        if os.path.exists(pre_qual_d_dir):
            for file in os.listdir(pre_qual_d_dir):
                if file.endswith('.txt'):
                    category_name = file.replace('.txt', '')
                    pre_qual_d_categories.add(category_name)
                    
        # Get categories from improved mapping
        improved_categories = set()
        if self.improved_award_data:
            for record in self.improved_award_data:
                category = record.get('Prequalification_Category')
                if category and category != 'Unknown':
                    improved_categories.add(category)
                    
        category_verification = {
            'prequal_lookup_categories': len(prequal_lookup_categories),
            'prequal_json_categories': len(prequal_json_categories),
            'pre_qual_d_categories': len(pre_qual_d_categories),
            'improved_categories': len(improved_categories),
            'common_categories': len(prequal_lookup_categories.intersection(prequal_json_categories)),
            'mapping_success_rate': (len(improved_categories) / len(prequal_lookup_categories) * 100) if prequal_lookup_categories else 0
        }
        
        self.verification_results['category_verification'] = category_verification
        
        print(f"📊 Prequal Lookup Categories: {len(prequal_lookup_categories)}")
        print(f"📊 Prequal JSON Categories: {len(prequal_json_categories)}")
        print(f"📊 Pre-qual_d Categories: {len(pre_qual_d_categories)}")
        print(f"📊 Improved Mapping Categories: {len(improved_categories)}")
        print(f"📊 Common Categories: {category_verification['common_categories']}")
        print(f"📊 Mapping Success Rate: {category_verification['mapping_success_rate']:.1f}%")
        
    def analyze_firm_data_consistency(self):
        """Analyze firm data consistency across sources"""
        print("\n🔍 Analyzing Firm Data Consistency...")
        
        # Extract firm names from different sources
        firms_data_names = set()
        for firm in self.firms_data:
            if firm.get('firm_name'):
                firms_data_names.add(firm['firm_name'].strip().upper())
                
        award_data_names = set()
        for record in self.award_data:
            if record.get('SELECTED FIRM'):
                award_data_names.add(str(record['SELECTED FIRM']).strip().upper())
                
        idot_excel_names = set()
        for _, row in self.idot_excel.iterrows():
            if pd.notna(row.get('Unnamed: 1')) and isinstance(row['Unnamed: 1'], str):
                firm_name = row['Unnamed: 1'].strip()
                if firm_name and firm_name != 'FIRM' and not firm_name.startswith('#'):
                    idot_excel_names.add(firm_name.upper())
                    
        firm_consistency = {
            'firms_data_count': len(firms_data_names),
            'award_data_count': len(award_data_names),
            'idot_excel_count': len(idot_excel_names),
            'firms_award_common': len(firms_data_names.intersection(award_data_names)),
            'firms_idot_common': len(firms_data_names.intersection(idot_excel_names)),
            'award_idot_common': len(award_data_names.intersection(idot_excel_names)),
            'firms_award_match_rate': (len(firms_data_names.intersection(award_data_names)) / len(firms_data_names.union(award_data_names)) * 100) if firms_data_names.union(award_data_names) else 0,
            'firms_idot_match_rate': (len(firms_data_names.intersection(idot_excel_names)) / len(firms_data_names.union(idot_excel_names)) * 100) if firms_data_names.union(idot_excel_names) else 0
        }
        
        self.verification_results['firm_consistency'] = firm_consistency
        
        print(f"📊 Firms Data Count: {len(firms_data_names)}")
        print(f"📊 Award Data Count: {len(award_data_names)}")
        print(f"📊 IDOT Excel Count: {len(idot_excel_names)}")
        print(f"📊 Firms-Award Match Rate: {firm_consistency['firms_award_match_rate']:.1f}%")
        print(f"📊 Firms-IDOT Match Rate: {firm_consistency['firms_idot_match_rate']:.1f}%")
        
    def analyze_improved_mapping_quality(self):
        """Analyze the quality of improved mapping"""
        print("\n🔍 Analyzing Improved Mapping Quality...")
        
        if not self.improved_award_data:
            print("⚠️  No improved mapping data available")
            return
            
        # Analyze mapping results
        total_records = len(self.improved_award_data)
        mapped_records = sum(1 for record in self.improved_award_data if record.get('Prequalification_Category') != 'Unknown')
        unknown_records = total_records - mapped_records
        
        # Analyze category distribution
        category_counts = defaultdict(int)
        for record in self.improved_award_data:
            category = record.get('Prequalification_Category', 'Unknown')
            category_counts[category] += 1
            
        # Get top categories
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        top_categories = sorted_categories[:10]
        
        mapping_quality = {
            'total_records': total_records,
            'mapped_records': mapped_records,
            'unknown_records': unknown_records,
            'success_rate': (mapped_records / total_records * 100) if total_records > 0 else 0,
            'unique_categories': len(category_counts),
            'top_categories': dict(top_categories)
        }
        
        self.verification_results['mapping_quality'] = mapping_quality
        
        print(f"📊 Total Records: {total_records}")
        print(f"📊 Mapped Records: {mapped_records}")
        print(f"📊 Unknown Records: {unknown_records}")
        print(f"📊 Success Rate: {mapping_quality['success_rate']:.1f}%")
        print(f"📊 Unique Categories: {len(category_counts)}")
        
    def check_data_integrity_issues(self):
        """Check for data integrity issues"""
        print("\n🔍 Checking Data Integrity Issues...")
        
        integrity_issues = {
            'award_data_issues': [],
            'firms_data_issues': [],
            'prequal_lookup_issues': [],
            'idot_excel_issues': []
        }
        
        # Check award data
        missing_job_numbers = sum(1 for record in self.award_data if not record.get('Job #'))
        missing_firm_names = sum(1 for record in self.award_data if not record.get('SELECTED FIRM'))
        missing_descriptions = sum(1 for record in self.award_data if not record.get('Description'))
        
        integrity_issues['award_data_issues'] = [
            f"Missing Job Numbers: {missing_job_numbers}",
            f"Missing Firm Names: {missing_firm_names}",
            f"Missing Descriptions: {missing_descriptions}"
        ]
        
        # Check firms data
        missing_firm_codes = sum(1 for firm in self.firms_data if not firm.get('firm_code'))
        missing_firm_names = sum(1 for firm in self.firms_data if not firm.get('firm_name'))
        missing_locations = sum(1 for firm in self.firms_data if not firm.get('location'))
        
        integrity_issues['firms_data_issues'] = [
            f"Missing Firm Codes: {missing_firm_codes}",
            f"Missing Firm Names: {missing_firm_names}",
            f"Missing Locations: {missing_locations}"
        ]
        
        # Check prequal lookup
        empty_categories = sum(1 for category, firms in self.prequal_lookup.items() if not firms)
        
        integrity_issues['prequal_lookup_issues'] = [
            f"Empty Categories: {empty_categories}"
        ]
        
        # Check IDOT Excel
        missing_firm_names_excel = sum(1 for _, row in self.idot_excel.iterrows() if pd.isna(row.get('Unnamed: 1')))
        
        integrity_issues['idot_excel_issues'] = [
            f"Missing Firm Names: {missing_firm_names_excel}"
        ]
        
        self.verification_results['integrity_issues'] = integrity_issues
        
        print(f"📊 Award Data Issues: {len(integrity_issues['award_data_issues'])}")
        print(f"📊 Firms Data Issues: {len(integrity_issues['firms_data_issues'])}")
        print(f"📊 Prequal Lookup Issues: {len(integrity_issues['prequal_lookup_issues'])}")
        print(f"📊 IDOT Excel Issues: {len(integrity_issues['idot_excel_issues'])}")
        
    def generate_verification_report(self):
        """Generate comprehensive verification report"""
        print("\n📋 Generating Verification Report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'comprehensive_data_verification_report_{timestamp}.txt'
        
        with open(report_file, 'w') as f:
            f.write("COMPREHENSIVE DATA VERIFICATION REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("VERIFICATION SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Award Records: {len(self.award_data)}\n")
            f.write(f"Firm Records: {len(self.firms_data)}\n")
            f.write(f"Prequal Categories: {len(self.prequal_lookup)}\n")
            f.write(f"IDOT Excel Shape: {self.idot_excel.shape}\n\n")
            
            # Prequal JSON Analysis
            prequal_json = self.verification_results.get('prequal_json_analysis', {})
            f.write("Prequal JSON Analysis\n")
            f.write("-" * 25 + "\n")
            f.write(f"JSON Files: {prequal_json.get('total_files', 0)}\n")
            f.write(f"Summary Total Files: {prequal_json.get('summary_total_files', 0)}\n")
            f.write(f"Summary Total Firms: {prequal_json.get('summary_total_firms', 0)}\n\n")
            
            # Pre-qual_d Analysis
            pre_qual_d = self.verification_results.get('pre_qual_d_analysis', {})
            f.write("Pre-qual_d Analysis\n")
            f.write("-" * 20 + "\n")
            f.write(f"Text Files: {pre_qual_d.get('total_files', 0)}\n\n")
            
            # Category Verification
            category_verif = self.verification_results.get('category_verification', {})
            f.write("Category Verification\n")
            f.write("-" * 25 + "\n")
            f.write(f"Prequal Lookup Categories: {category_verif.get('prequal_lookup_categories', 0)}\n")
            f.write(f"Prequal JSON Categories: {category_verif.get('prequal_json_categories', 0)}\n")
            f.write(f"Pre-qual_d Categories: {category_verif.get('pre_qual_d_categories', 0)}\n")
            f.write(f"Improved Mapping Categories: {category_verif.get('improved_categories', 0)}\n")
            f.write(f"Mapping Success Rate: {category_verif.get('mapping_success_rate', 0):.1f}%\n\n")
            
            # Firm Consistency
            firm_consist = self.verification_results.get('firm_consistency', {})
            f.write("Firm Data Consistency\n")
            f.write("-" * 25 + "\n")
            f.write(f"Firms Data Count: {firm_consist.get('firms_data_count', 0)}\n")
            f.write(f"Award Data Count: {firm_consist.get('award_data_count', 0)}\n")
            f.write(f"IDOT Excel Count: {firm_consist.get('idot_excel_count', 0)}\n")
            f.write(f"Firms-Award Match Rate: {firm_consist.get('firms_award_match_rate', 0):.1f}%\n")
            f.write(f"Firms-IDOT Match Rate: {firm_consist.get('firms_idot_match_rate', 0):.1f}%\n\n")
            
            # Mapping Quality
            mapping_qual = self.verification_results.get('mapping_quality', {})
            if mapping_qual:
                f.write("Improved Mapping Quality\n")
                f.write("-" * 30 + "\n")
                f.write(f"Total Records: {mapping_qual.get('total_records', 0)}\n")
                f.write(f"Mapped Records: {mapping_qual.get('mapped_records', 0)}\n")
                f.write(f"Success Rate: {mapping_qual.get('success_rate', 0):.1f}%\n")
                f.write(f"Unique Categories: {mapping_qual.get('unique_categories', 0)}\n\n")
                
            # Integrity Issues
            integrity = self.verification_results.get('integrity_issues', {})
            f.write("Data Integrity Issues\n")
            f.write("-" * 25 + "\n")
            for source, issues in integrity.items():
                f.write(f"{source.replace('_', ' ').title()}:\n")
                for issue in issues:
                    f.write(f"  - {issue}\n")
                f.write("\n")
                
            f.write("CONCLUSION\n")
            f.write("-" * 10 + "\n")
            f.write("Data verification complete. Review findings above.\n")
            f.write("No changes were made during this analysis.\n")
            
        print(f"✅ Verification report saved: {report_file}")
        return report_file
        
    def run_comprehensive_verification(self):
        """Run complete data verification"""
        print("🚀 Starting Comprehensive Data Verification...")
        
        # Load all data sources
        self.load_all_data_sources()
        
        # Run all analyses
        self.analyze_prequal_json_structure()
        self.analyze_pre_qual_d_structure()
        self.cross_verify_prequal_categories()
        self.analyze_firm_data_consistency()
        self.analyze_improved_mapping_quality()
        self.check_data_integrity_issues()
        
        # Generate report
        report_file = self.generate_verification_report()
        
        print(f"\n✅ Comprehensive Verification Complete!")
        print(f"📄 Report: {report_file}")
        
        return self.verification_results

if __name__ == "__main__":
    verifier = ComprehensiveDataVerifier()
    results = verifier.run_comprehensive_verification()
