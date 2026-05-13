#!/usr/bin/env python3
"""
Critical Files Verification
Verify the 3 critical files that should match:
1. district_mapping.json
2. firms_data.json
3. prequal_lookup.json
"""

import json
import pandas as pd
import os
from collections import defaultdict
from datetime import datetime

class CriticalFilesVerification:
    def __init__(self):
        self.data_dir = '../data'
        self.verification_results = {}
        
    def verify_critical_files(self):
        """Verify the 3 critical files for 100% accuracy"""
        print("🚀 CRITICAL FILES VERIFICATION - 100% ACCURACY CHECK")
        print("=" * 70)
        print("Focusing on the 3 files that should match:")
        print("1. district_mapping.json")
        print("2. firms_data.json") 
        print("3. prequal_lookup.json")
        print("=" * 70)
        
        # 1. Verify firms_data.json
        print("\n" + "="*60)
        print("1. VERIFYING firms_data.json")
        print("="*60)
        firms_result = self.verify_firms_data()
        
        # 2. Verify prequal_lookup.json
        print("\n" + "="*60)
        print("2. VERIFYING prequal_lookup.json")
        print("="*60)
        prequal_result = self.verify_prequal_lookup()
        
        # 3. Verify district_mapping.json
        print("\n" + "="*60)
        print("3. VERIFYING district_mapping.json")
        print("="*60)
        district_result = self.verify_district_mapping()
        
        # 4. Verify cross-file consistency
        print("\n" + "="*60)
        print("4. VERIFYING CROSS-FILE CONSISTENCY")
        print("="*60)
        consistency_result = self.verify_cross_file_consistency()
        
        # Generate final report
        self.generate_final_report([
            firms_result,
            prequal_result,
            district_result,
            consistency_result
        ])
        
    def verify_firms_data(self):
        """Verify firms_data.json"""
        print("🔍 Verifying firms_data.json...")
        
        # Load firms_data.json
        with open(f'{self.data_dir}/firms_data.json', 'r') as f:
            firms_data = json.load(f)
            
        # Load IDOT Excel for comparison
        idot_excel = pd.read_excel(f'{self.data_dir}/IDOTConsultantList.xlsx', sheet_name='PrequalReport')
        
        # Extract unique firms from IDOT Excel
        idot_firms = set()
        for idx, row in idot_excel.iterrows():
            firm_name = row.get('Unnamed: 1')
            if pd.notna(firm_name) and isinstance(firm_name, str):
                firm_name = firm_name.strip()
                if firm_name and firm_name != 'FIRM' and len(firm_name) > 2:
                    idot_firms.add(firm_name)
                    
        # Extract firms from JSON
        json_firms = set()
        for firm in firms_data:
            if firm.get('firm_name'):
                json_firms.add(firm['firm_name'].strip())
                
        # Compare
        exact_matches = json_firms.intersection(idot_firms)
        missing_in_json = idot_firms - json_firms
        missing_in_idot = json_firms - idot_firms
        
        accuracy = (len(exact_matches) / len(idot_firms)) * 100 if idot_firms else 0
        
        result = {
            'dataframe': 'firms_data.json',
            'json_count': len(json_firms),
            'idot_count': len(idot_firms),
            'exact_matches': len(exact_matches),
            'missing_in_json': len(missing_in_json),
            'missing_in_idot': len(missing_in_idot),
            'accuracy': accuracy,
            'status': 'PASS' if accuracy >= 99.5 else 'FAIL'
        }
        
        print(f"📊 JSON Firms: {len(json_firms)}")
        print(f"📊 IDOT Firms: {len(idot_firms)}")
        print(f"📊 Exact Matches: {len(exact_matches)}")
        print(f"📊 Missing in JSON: {len(missing_in_json)}")
        print(f"📊 Missing in IDOT: {len(missing_in_idot)}")
        print(f"✅ Accuracy: {accuracy:.2f}%")
        print(f"🎯 Status: {result['status']}")
        
        if missing_in_json:
            print(f"❌ Missing in JSON: {list(missing_in_json)[:3]}")
            
        return result
        
    def verify_prequal_lookup(self):
        """Verify prequal_lookup.json"""
        print("🔍 Verifying prequal_lookup.json...")
        
        # Load prequal_lookup.json
        with open(f'{self.data_dir}/prequal_lookup.json', 'r') as f:
            prequal_lookup = json.load(f)
            
        # Load IDOT Excel for comparison
        idot_excel = pd.read_excel(f'{self.data_dir}/IDOTConsultantList.xlsx', sheet_name='PrequalReport')
        
        # Extract prequalifications from IDOT Excel
        idot_prequals = defaultdict(set)
        for idx, row in idot_excel.iterrows():
            firm_name = row.get('Unnamed: 1')
            prequal_category = row.get('Unnamed: 3')
            
            if pd.notna(firm_name) and pd.notna(prequal_category):
                firm_name = str(firm_name).strip()
                prequal_category = str(prequal_category).strip()
                
                if firm_name and firm_name != 'FIRM' and prequal_category and prequal_category != 'PRE-QUAL CATEGORIES':
                    idot_prequals[prequal_category].add(firm_name)
                    
        # Compare categories
        lookup_categories = set(prequal_lookup.keys())
        idot_categories = set(idot_prequals.keys())
        
        exact_matches = lookup_categories.intersection(idot_categories)
        missing_in_lookup = idot_categories - lookup_categories
        missing_in_idot = lookup_categories - idot_categories
        
        category_accuracy = (len(exact_matches) / len(idot_categories)) * 100 if idot_categories else 0
        
        # Compare firm counts for matching categories
        firm_count_matches = 0
        total_matching_categories = 0
        
        for category in exact_matches:
            total_matching_categories += 1
            lookup_firms = set()
            if isinstance(prequal_lookup[category], list):
                for firm_dict in prequal_lookup[category]:
                    if isinstance(firm_dict, dict) and 'firm_name' in firm_dict:
                        lookup_firms.add(firm_dict['firm_name'])
                        
            idot_firms = idot_prequals[category]
            
            if len(lookup_firms) == len(idot_firms):
                firm_count_matches += 1
                
        firm_count_accuracy = (firm_count_matches / total_matching_categories) * 100 if total_matching_categories > 0 else 0
        
        overall_accuracy = (category_accuracy + firm_count_accuracy) / 2
        
        result = {
            'dataframe': 'prequal_lookup.json',
            'lookup_categories': len(lookup_categories),
            'idot_categories': len(idot_categories),
            'exact_matches': len(exact_matches),
            'missing_in_lookup': len(missing_in_lookup),
            'missing_in_idot': len(missing_in_idot),
            'firm_count_matches': firm_count_matches,
            'total_matching_categories': total_matching_categories,
            'category_accuracy': category_accuracy,
            'firm_count_accuracy': firm_count_accuracy,
            'overall_accuracy': overall_accuracy,
            'status': 'PASS' if overall_accuracy >= 95 else 'FAIL'
        }
        
        print(f"📊 Lookup Categories: {len(lookup_categories)}")
        print(f"📊 IDOT Categories: {len(idot_categories)}")
        print(f"📊 Exact Matches: {len(exact_matches)}")
        print(f"📊 Firm Count Matches: {firm_count_matches}/{total_matching_categories}")
        print(f"📊 Category Accuracy: {category_accuracy:.2f}%")
        print(f"📊 Firm Count Accuracy: {firm_count_accuracy:.2f}%")
        print(f"✅ Overall Accuracy: {overall_accuracy:.2f}%")
        print(f"🎯 Status: {result['status']}")
        
        if missing_in_lookup:
            print(f"❌ Missing in Lookup: {list(missing_in_lookup)[:3]}")
        if missing_in_idot:
            print(f"❌ Missing in IDOT: {list(missing_in_idot)[:3]}")
            
        return result
        
    def verify_district_mapping(self):
        """Verify district_mapping.json"""
        print("🔍 Verifying district_mapping.json...")
        
        # Load district_mapping.json
        with open(f'{self.data_dir}/district_mapping.json', 'r') as f:
            district_mapping = json.load(f)
            
        # Load firms_data.json for comparison
        with open(f'{self.data_dir}/firms_data.json', 'r') as f:
            firms_data = json.load(f)
            
        # Extract firms from district mapping
        district_firms = set()
        for district, firms in district_mapping.items():
            if isinstance(firms, list):
                for firm in firms:
                    if isinstance(firm, dict) and firm.get('firm_name'):
                        district_firms.add(firm['firm_name'].strip())
                    elif isinstance(firm, str):
                        district_firms.add(firm.strip())
                        
        # Extract firms from firms_data
        firms_data_names = set()
        for firm in firms_data:
            if firm.get('firm_name'):
                firms_data_names.add(firm['firm_name'].strip())
                
        # Compare
        exact_matches = district_firms.intersection(firms_data_names)
        missing_in_district = firms_data_names - district_firms
        missing_in_firms = district_firms - firms_data_names
        
        accuracy = (len(exact_matches) / len(firms_data_names)) * 100 if firms_data_names else 0
        
        result = {
            'dataframe': 'district_mapping.json',
            'district_firms': len(district_firms),
            'firms_data_firms': len(firms_data_names),
            'exact_matches': len(exact_matches),
            'missing_in_district': len(missing_in_district),
            'missing_in_firms': len(missing_in_firms),
            'accuracy': accuracy,
            'status': 'PASS' if accuracy >= 95 else 'FAIL'
        }
        
        print(f"📊 District Firms: {len(district_firms)}")
        print(f"📊 Firms Data Firms: {len(firms_data_names)}")
        print(f"📊 Exact Matches: {len(exact_matches)}")
        print(f"📊 Missing in District: {len(missing_in_district)}")
        print(f"📊 Missing in Firms Data: {len(missing_in_firms)}")
        print(f"✅ Accuracy: {accuracy:.2f}%")
        print(f"🎯 Status: {result['status']}")
        
        if missing_in_district:
            print(f"❌ Missing in District: {list(missing_in_district)[:3]}")
        if missing_in_firms:
            print(f"❌ Missing in Firms Data: {list(missing_in_firms)[:3]}")
            
        return result
        
    def verify_cross_file_consistency(self):
        """Verify consistency across all 3 critical files"""
        print("🔍 Verifying cross-file consistency...")
        
        # Load all critical files
        with open(f'{self.data_dir}/firms_data.json', 'r') as f:
            firms_data = json.load(f)
            
        with open(f'{self.data_dir}/prequal_lookup.json', 'r') as f:
            prequal_lookup = json.load(f)
            
        with open(f'{self.data_dir}/district_mapping.json', 'r') as f:
            district_mapping = json.load(f)
            
        # Extract all firm names from each file
        firms_data_names = set()
        for firm in firms_data:
            if firm.get('firm_name'):
                firms_data_names.add(firm['firm_name'].strip())
                
        prequal_firms = set()
        for category, firms in prequal_lookup.items():
            if isinstance(firms, list):
                for firm_dict in firms:
                    if isinstance(firm_dict, dict) and firm_dict.get('firm_name'):
                        prequal_firms.add(firm_dict['firm_name'].strip())
                        
        district_firms = set()
        for district, firms in district_mapping.items():
            if isinstance(firms, list):
                for firm in firms:
                    if isinstance(firm, dict) and firm.get('firm_name'):
                        district_firms.add(firm['firm_name'].strip())
                    elif isinstance(firm, str):
                        district_firms.add(firm.strip())
                        
        # Find common firms across all 3 files
        common_firms = firms_data_names.intersection(prequal_firms).intersection(district_firms)
        
        # Calculate consistency scores
        firms_data_consistency = (len(common_firms) / len(firms_data_names)) * 100 if firms_data_names else 0
        prequal_consistency = (len(common_firms) / len(prequal_firms)) * 100 if prequal_firms else 0
        district_consistency = (len(common_firms) / len(district_firms)) * 100 if district_firms else 0
        
        overall_consistency = (firms_data_consistency + prequal_consistency + district_consistency) / 3
        
        # Find missing firms in each file
        missing_in_prequal = firms_data_names - prequal_firms
        missing_in_district = firms_data_names - district_firms
        missing_in_firms_data = prequal_firms - firms_data_names
        
        result = {
            'dataframe': 'Cross-File Consistency',
            'firms_data_firms': len(firms_data_names),
            'prequal_firms': len(prequal_firms),
            'district_firms': len(district_firms),
            'common_firms': len(common_firms),
            'missing_in_prequal': len(missing_in_prequal),
            'missing_in_district': len(missing_in_district),
            'missing_in_firms_data': len(missing_in_firms_data),
            'firms_data_consistency': firms_data_consistency,
            'prequal_consistency': prequal_consistency,
            'district_consistency': district_consistency,
            'overall_consistency': overall_consistency,
            'status': 'PASS' if overall_consistency >= 95 else 'FAIL'
        }
        
        print(f"📊 Firms Data Firms: {len(firms_data_names)}")
        print(f"📊 Prequal Firms: {len(prequal_firms)}")
        print(f"📊 District Firms: {len(district_firms)}")
        print(f"📊 Common Firms: {len(common_firms)}")
        print(f"📊 Missing in Prequal: {len(missing_in_prequal)}")
        print(f"📊 Missing in District: {len(missing_in_district)}")
        print(f"📊 Missing in Firms Data: {len(missing_in_firms_data)}")
        print(f"📊 Firms Data Consistency: {firms_data_consistency:.2f}%")
        print(f"📊 Prequal Consistency: {prequal_consistency:.2f}%")
        print(f"📊 District Consistency: {district_consistency:.2f}%")
        print(f"✅ Overall Consistency: {overall_consistency:.2f}%")
        print(f"🎯 Status: {result['status']}")
        
        if missing_in_prequal:
            print(f"❌ Missing in Prequal: {list(missing_in_prequal)[:3]}")
        if missing_in_district:
            print(f"❌ Missing in District: {list(missing_in_district)[:3]}")
            
        return result
        
    def generate_final_report(self, results):
        """Generate final verification report"""
        print("\n" + "="*70)
        print("CRITICAL FILES VERIFICATION REPORT")
        print("="*70)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'critical_files_verification_{timestamp}.txt'
        
        with open(report_file, 'w') as f:
            f.write("CRITICAL FILES VERIFICATION REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Purpose: Verify 3 critical files that should match\n")
            f.write("Files: district_mapping.json, firms_data.json, prequal_lookup.json\n\n")
            
            # Overall results
            all_passed = all(result['status'] == 'PASS' for result in results)
            avg_accuracy = sum(result.get('accuracy', result.get('overall_accuracy', result.get('overall_consistency', 0))) for result in results) / len(results)
            
            f.write("OVERALL RESULTS\n")
            f.write("-" * 15 + "\n")
            f.write(f"All Critical Files Pass: {'YES' if all_passed else 'NO'}\n")
            f.write(f"Average Accuracy: {avg_accuracy:.2f}%\n")
            f.write(f"Ready for Training: {'YES' if all_passed else 'NO'}\n\n")
            
            # Individual results
            f.write("INDIVIDUAL FILE RESULTS\n")
            f.write("-" * 25 + "\n")
            
            for result in results:
                f.write(f"{result['dataframe']}:\n")
                f.write(f"  Status: {result['status']}\n")
                
                if 'accuracy' in result:
                    f.write(f"  Accuracy: {result['accuracy']:.2f}%\n")
                elif 'overall_accuracy' in result:
                    f.write(f"  Overall Accuracy: {result['overall_accuracy']:.2f}%\n")
                elif 'overall_consistency' in result:
                    f.write(f"  Overall Consistency: {result['overall_consistency']:.2f}%\n")
                    
                f.write("\n")
                
            # Final recommendation
            f.write("FINAL RECOMMENDATION\n")
            f.write("-" * 20 + "\n")
            
            if all_passed:
                f.write("🎉 ALL CRITICAL FILES PASS VERIFICATION!\n")
                f.write("✅ Ready to proceed with model training\n")
                f.write("✅ Data quality is excellent\n")
                f.write("✅ No critical issues detected\n")
            else:
                f.write("⚠️  SOME CRITICAL FILES FAIL VERIFICATION\n")
                f.write("❌ Need to fix issues before training\n")
                f.write("❌ Data quality needs improvement\n")
                
        print(f"✅ Critical files verification report saved: {report_file}")
        
        # Print final summary
        print(f"\n🎯 FINAL SUMMARY:")
        print(f"  All Critical Files Pass: {'YES' if all_passed else 'NO'}")
        print(f"  Average Accuracy: {avg_accuracy:.2f}%")
        print(f"  Ready for Training: {'YES' if all_passed else 'NO'}")
        
        if all_passed:
            print(f"\n🎉 SUCCESS: All critical files verified! Ready for training!")
        else:
            print(f"\n⚠️  ISSUES DETECTED: Need to fix before training!")

if __name__ == "__main__":
    verifier = CriticalFilesVerification()
    verifier.verify_critical_files()
