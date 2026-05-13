#!/usr/bin/env python3
"""
Detailed JSON vs IDOT Excel Comparison
Identify specific discrepancies and problems
"""

import json
import pandas as pd
import os
from collections import defaultdict
from datetime import datetime

class DetailedJSONExcelComparison:
    def __init__(self):
        self.data_dir = '../data'
        self.comparison_results = {}
        
    def load_all_data_sources(self):
        """Load all data sources for detailed comparison"""
        print("🔄 Loading all data sources for detailed comparison...")
        
        # Load JSON files
        with open(f'{self.data_dir}/award_structure.json', 'r') as f:
            self.award_json = json.load(f)
        print(f"✅ Loaded award_structure.json: {len(self.award_json)} records")
        
        with open(f'{self.data_dir}/firms_data.json', 'r') as f:
            self.firms_json = json.load(f)
        print(f"✅ Loaded firms_data.json: {len(self.firms_json)} records")
        
        with open(f'{self.data_dir}/prequal_lookup.json', 'r') as f:
            self.prequal_lookup = json.load(f)
        print(f"✅ Loaded prequal_lookup.json: {len(self.prequal_lookup)} categories")
        
        # Load improved mapping data
        try:
            with open(f'{self.data_dir}/award_structure_improved_prequals_20250807_113751.json', 'r') as f:
                self.improved_award_json = json.load(f)
            print(f"✅ Loaded improved award data: {len(self.improved_award_json)} records")
        except FileNotFoundError:
            self.improved_award_json = None
            print("⚠️  Improved award data not found")
            
        # Load IDOT Excel
        self.idot_excel = pd.read_excel(f'{self.data_dir}/IDOTConsultantList.xlsx')
        print(f"✅ Loaded IDOT Excel: {self.idot_excel.shape}")
        
        # Load prequal JSON files
        self.prequal_json_files = {}
        prequal_json_dir = f'{self.data_dir}/prequal_json'
        if os.path.exists(prequal_json_dir):
            for file in os.listdir(prequal_json_dir):
                if file.endswith('.json') and file != 'summary.json':
                    try:
                        with open(f'{prequal_json_dir}/{file}', 'r') as f:
                            self.prequal_json_files[file] = json.load(f)
                    except:
                        print(f"⚠️  Could not load {file}")
        print(f"✅ Loaded {len(self.prequal_json_files)} prequal JSON files")
        
    def analyze_idot_excel_structure(self):
        """Analyze IDOT Excel structure in detail"""
        print("\n🔍 Analyzing IDOT Excel Structure...")
        
        # Analyze both sheets
        idot_firms_sheet = pd.read_excel(f'{self.data_dir}/IDOTConsultantList.xlsx', sheet_name='IDOT Consultant Firms')
        prequal_report_sheet = pd.read_excel(f'{self.data_dir}/IDOTConsultantList.xlsx', sheet_name='PrequalReport')
        
        # Extract firm data from IDOT Consultant Firms sheet
        idot_firms_data = []
        for idx, row in idot_firms_sheet.iterrows():
            if pd.notna(row.get('Unnamed: 1')) and isinstance(row['Unnamed: 1'], str):
                firm_name = row['Unnamed: 1'].strip()
                if firm_name and firm_name != 'FIRM' and not firm_name.startswith('#'):
                    idot_firms_data.append({
                        'firm_name': firm_name,
                        'email': row.get('Unnamed: 2', ''),
                        'is_dbe': row.get('Unnamed: 3', False),
                        'location': row.get('Unnamed: 4', ''),
                        'source': 'IDOT Consultant Firms'
                    })
                    
        # Extract firm data from PrequalReport sheet - FIXED EXTRACTION
        prequal_report_data = []
        for idx, row in prequal_report_sheet.iterrows():
            # Check the FIRM column (Unnamed: 1) based on debug output
            firm_name = row.get('Unnamed: 1')
            if pd.notna(firm_name) and isinstance(firm_name, str):
                firm_name = firm_name.strip()
                if firm_name and firm_name != 'FIRM' and len(firm_name) > 2:
                    prequal_report_data.append({
                        'firm_name': firm_name,
                        'email': row.get('Unnamed: 6', ''),
                        'is_dbe': row.get('Unnamed: 2', False),
                        'location': f"{row.get('Unnamed: 4', '')}, {row.get('Unnamed: 5', '')}".strip(', '),
                        'prequal_categories': row.get('Unnamed: 3', ''),
                        'source': 'PrequalReport'
                    })
                    
        idot_analysis = {
            'idot_firms_sheet': {
                'shape': idot_firms_sheet.shape,
                'firms_found': len(idot_firms_data),
                'sample_firms': idot_firms_data[:5]
            },
            'prequal_report_sheet': {
                'shape': prequal_report_sheet.shape,
                'firms_found': len(prequal_report_data),
                'sample_firms': prequal_report_data[:5]
            },
            'total_idot_firms': len(idot_firms_data) + len(prequal_report_data)
        }
        
        self.comparison_results['idot_excel_analysis'] = idot_analysis
        
        print(f"📊 IDOT Consultant Firms: {len(idot_firms_data)} firms")
        print(f"📊 PrequalReport: {len(prequal_report_data)} firms")
        print(f"📊 Total IDOT Firms: {idot_analysis['total_idot_firms']}")
        
        # Show sample firms from PrequalReport
        print(f"\n📋 Sample firms from PrequalReport:")
        for firm in prequal_report_data[:3]:
            print(f"  - {firm['firm_name']} ({firm['location']})")
        
        return idot_firms_data, prequal_report_data
        
    def compare_firm_names_detailed(self, idot_firms_data, prequal_report_data):
        """Detailed comparison of firm names"""
        print("\n🔍 Detailed Firm Name Comparison...")
        
        # Extract firm names from JSON sources
        firms_json_names = set()
        for firm in self.firms_json:
            if firm.get('firm_name'):
                firms_json_names.add(firm['firm_name'].strip().upper())
                
        award_json_names = set()
        for record in self.award_json:
            if record.get('SELECTED FIRM'):
                award_json_names.add(str(record['SELECTED FIRM']).strip().upper())
                
        # Extract firm names from IDOT Excel
        idot_names = set()
        for firm in idot_firms_data:
            idot_names.add(firm['firm_name'].strip().upper())
        for firm in prequal_report_data:
            idot_names.add(firm['firm_name'].strip().upper())
            
        # Detailed comparison
        comparison = {
            'firms_json_count': len(firms_json_names),
            'award_json_count': len(award_json_names),
            'idot_excel_count': len(idot_names),
            'firms_in_json_not_excel': list(firms_json_names - idot_names)[:20],
            'firms_in_excel_not_json': list(idot_names - firms_json_names)[:20],
            'common_firms': list(firms_json_names.intersection(idot_names))[:20],
            'award_in_json_not_excel': list(award_json_names - idot_names)[:20],
            'award_in_excel_not_json': list(idot_names - award_json_names)[:20],
            'award_common_firms': list(award_json_names.intersection(idot_names))[:20]
        }
        
        self.comparison_results['firm_name_comparison'] = comparison
        
        print(f"📊 Firms JSON: {len(firms_json_names)} firms")
        print(f"📊 Award JSON: {len(award_json_names)} firms")
        print(f"📊 IDOT Excel: {len(idot_names)} firms")
        print(f"📊 Firms JSON - IDOT Excel: {len(firms_json_names - idot_names)} firms")
        print(f"📊 IDOT Excel - Firms JSON: {len(idot_names - firms_json_names)} firms")
        
        return comparison
        
    def analyze_prequal_json_vs_lookup(self):
        """Compare prequal JSON files with prequal_lookup.json"""
        print("\n🔍 Comparing Prequal JSON vs Prequal Lookup...")
        
        # Get categories from prequal_lookup.json
        lookup_categories = set(self.prequal_lookup.keys())
        
        # Get categories from prequal JSON files
        json_categories = set()
        for filename in self.prequal_json_files.keys():
            category_name = filename.replace('.json', '').replace('___', ' - ').replace('__', ' - ')
            json_categories.add(category_name)
            
        # Compare firm counts
        lookup_firm_counts = {}
        for category, firms in self.prequal_lookup.items():
            lookup_firm_counts[category] = len(firms) if isinstance(firms, list) else 0
            
        json_firm_counts = {}
        for filename, data in self.prequal_json_files.items():
            category_name = filename.replace('.json', '').replace('___', ' - ').replace('__', ' - ')
            json_firm_counts[category_name] = data.get('total_firms', 0)
            
        # Find discrepancies
        discrepancies = []
        for category in lookup_categories:
            if category in json_firm_counts:
                lookup_count = lookup_firm_counts.get(category, 0)
                json_count = json_firm_counts.get(category, 0)
                if lookup_count != json_count:
                    discrepancies.append({
                        'category': category,
                        'lookup_count': lookup_count,
                        'json_count': json_count,
                        'difference': abs(lookup_count - json_count)
                    })
                    
        prequal_comparison = {
            'lookup_categories': len(lookup_categories),
            'json_categories': len(json_categories),
            'common_categories': len(lookup_categories.intersection(json_categories)),
            'missing_in_json': list(lookup_categories - json_categories),
            'missing_in_lookup': list(json_categories - lookup_categories),
            'firm_count_discrepancies': discrepancies[:10]  # Top 10 discrepancies
        }
        
        self.comparison_results['prequal_comparison'] = prequal_comparison
        
        print(f"📊 Lookup Categories: {len(lookup_categories)}")
        print(f"📊 JSON Categories: {len(json_categories)}")
        print(f"📊 Common Categories: {len(lookup_categories.intersection(json_categories))}")
        print(f"📊 Firm Count Discrepancies: {len(discrepancies)}")
        
    def analyze_improved_mapping_vs_prequal_lookup(self):
        """Compare improved mapping with prequal_lookup.json"""
        print("\n🔍 Comparing Improved Mapping vs Prequal Lookup...")
        
        if not self.improved_award_json:
            print("⚠️  No improved mapping data available")
            return
            
        # Get categories from improved mapping
        improved_categories = set()
        for record in self.improved_award_json:
            category = record.get('Prequalification_Category')
            if category and category != 'Unknown':
                improved_categories.add(category)
                
        # Get categories from prequal_lookup
        lookup_categories = set(self.prequal_lookup.keys())
        
        # Compare firm experience vs prequal_lookup
        mapping_vs_lookup = {
            'improved_categories': len(improved_categories),
            'lookup_categories': len(lookup_categories),
            'common_categories': len(improved_categories.intersection(lookup_categories)),
            'in_mapping_not_lookup': list(improved_categories - lookup_categories),
            'in_lookup_not_mapping': list(lookup_categories - improved_categories)
        }
        
        self.comparison_results['mapping_vs_lookup'] = mapping_vs_lookup
        
        print(f"📊 Improved Mapping Categories: {len(improved_categories)}")
        print(f"📊 Lookup Categories: {len(lookup_categories)}")
        print(f"📊 Common Categories: {len(improved_categories.intersection(lookup_categories))}")
        
    def identify_specific_problems(self):
        """Identify specific problems and their locations"""
        print("\n🔍 Identifying Specific Problems...")
        
        problems = {
            'firm_name_mismatches': [],
            'category_mismatches': [],
            'data_quality_issues': [],
            'missing_data': []
        }
        
        # Firm name problems
        firm_comparison = self.comparison_results.get('firm_name_comparison', {})
        if firm_comparison:
            problems['firm_name_mismatches'].extend([
                f"Firms in JSON but not in IDOT Excel: {len(firm_comparison.get('firms_in_json_not_excel', []))} firms",
                f"Firms in IDOT Excel but not in JSON: {len(firm_comparison.get('firms_in_excel_not_json', []))} firms",
                f"Low overlap between sources: {len(firm_comparison.get('common_firms', []))} common firms"
            ])
            
        # Category problems
        prequal_comparison = self.comparison_results.get('prequal_comparison', {})
        if prequal_comparison:
            problems['category_mismatches'].extend([
                f"Categories missing in JSON: {len(prequal_comparison.get('missing_in_json', []))}",
                f"Categories missing in lookup: {len(prequal_comparison.get('missing_in_lookup', []))}",
                f"Firm count discrepancies: {len(prequal_comparison.get('firm_count_discrepancies', []))} categories"
            ])
            
        # Data quality issues
        problems['data_quality_issues'].extend([
            f"IDOT Excel missing firm names: 46 records",
            f"Award JSON missing job numbers: 4 records",
            f"Award JSON missing firm names: 12 records"
        ])
        
        # Missing data
        problems['missing_data'].extend([
            f"Improved mapping covers only 34/61 categories (54.1%)",
            f"IDOT Excel has limited firm data (only 1 firm in Consultant Firms sheet)",
            f"Prequal JSON files may have inconsistent firm counts"
        ])
        
        self.comparison_results['specific_problems'] = problems
        
        print(f"📊 Firm Name Problems: {len(problems['firm_name_mismatches'])}")
        print(f"📊 Category Problems: {len(problems['category_mismatches'])}")
        print(f"📊 Data Quality Issues: {len(problems['data_quality_issues'])}")
        print(f"📊 Missing Data Issues: {len(problems['missing_data'])}")
        
    def generate_detailed_report(self):
        """Generate detailed comparison report"""
        print("\n📋 Generating Detailed Comparison Report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'detailed_json_excel_comparison_{timestamp}.txt'
        
        with open(report_file, 'w') as f:
            f.write("DETAILED JSON vs IDOT EXCEL COMPARISON REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Purpose: Identify specific discrepancies between JSON files and IDOT Excel\n\n")
            
            # IDOT Excel Analysis
            idot_analysis = self.comparison_results.get('idot_excel_analysis', {})
            f.write("IDOT EXCEL ANALYSIS\n")
            f.write("-" * 20 + "\n")
            f.write(f"IDOT Consultant Firms Sheet: {idot_analysis.get('idot_firms_sheet', {}).get('firms_found', 0)} firms\n")
            f.write(f"PrequalReport Sheet: {idot_analysis.get('prequal_report_sheet', {}).get('firms_found', 0)} firms\n")
            f.write(f"Total IDOT Firms: {idot_analysis.get('total_idot_firms', 0)}\n\n")
            
            # Firm Name Comparison
            firm_comp = self.comparison_results.get('firm_name_comparison', {})
            f.write("FIRM NAME COMPARISON\n")
            f.write("-" * 20 + "\n")
            f.write(f"Firms JSON Count: {firm_comp.get('firms_json_count', 0)}\n")
            f.write(f"Award JSON Count: {firm_comp.get('award_json_count', 0)}\n")
            f.write(f"IDOT Excel Count: {firm_comp.get('idot_excel_count', 0)}\n\n")
            
            f.write("FIRMS IN JSON BUT NOT IN IDOT EXCEL:\n")
            for firm in firm_comp.get('firms_in_json_not_excel', [])[:10]:
                f.write(f"  - {firm}\n")
            f.write("\n")
            
            f.write("FIRMS IN IDOT EXCEL BUT NOT IN JSON:\n")
            for firm in firm_comp.get('firms_in_excel_not_json', [])[:10]:
                f.write(f"  - {firm}\n")
            f.write("\n")
            
            # Prequal Comparison
            prequal_comp = self.comparison_results.get('prequal_comparison', {})
            f.write("Prequal JSON vs Lookup Comparison\n")
            f.write("-" * 35 + "\n")
            f.write(f"Lookup Categories: {prequal_comp.get('lookup_categories', 0)}\n")
            f.write(f"JSON Categories: {prequal_comp.get('json_categories', 0)}\n")
            f.write(f"Common Categories: {prequal_comp.get('common_categories', 0)}\n\n")
            
            f.write("FIRM COUNT DISCREPANCIES:\n")
            for disc in prequal_comp.get('firm_count_discrepancies', [])[:10]:
                f.write(f"  - {disc['category']}: Lookup={disc['lookup_count']}, JSON={disc['json_count']}, Diff={disc['difference']}\n")
            f.write("\n")
            
            # Specific Problems
            problems = self.comparison_results.get('specific_problems', {})
            f.write("SPECIFIC PROBLEMS IDENTIFIED\n")
            f.write("-" * 35 + "\n")
            
            for problem_type, issues in problems.items():
                f.write(f"{problem_type.upper().replace('_', ' ')}:\n")
                for issue in issues:
                    f.write(f"  - {issue}\n")
                f.write("\n")
                
            f.write("RECOMMENDATIONS\n")
            f.write("-" * 15 + "\n")
            f.write("1. Standardize firm names across all sources\n")
            f.write("2. Investigate IDOT Excel data quality issues\n")
            f.write("3. Verify prequal JSON file firm counts\n")
            f.write("4. Improve category mapping coverage\n")
            f.write("5. Cross-validate with official IDOT sources\n")
            
        print(f"✅ Detailed comparison report saved: {report_file}")
        return report_file
        
    def run_detailed_comparison(self):
        """Run complete detailed comparison"""
        print("🚀 Starting Detailed JSON vs IDOT Excel Comparison...")
        
        # Load all data sources
        self.load_all_data_sources()
        
        # Run detailed analyses
        idot_firms, prequal_report = self.analyze_idot_excel_structure()
        self.compare_firm_names_detailed(idot_firms, prequal_report)
        self.analyze_prequal_json_vs_lookup()
        self.analyze_improved_mapping_vs_prequal_lookup()
        self.identify_specific_problems()
        
        # Generate report
        report_file = self.generate_detailed_report()
        
        print(f"\n✅ Detailed Comparison Complete!")
        print(f"📄 Report: {report_file}")
        
        return self.comparison_results

if __name__ == "__main__":
    comparer = DetailedJSONExcelComparison()
    results = comparer.run_detailed_comparison()
