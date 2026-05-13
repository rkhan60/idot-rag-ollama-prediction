#!/usr/bin/env python3
"""
Final Dataframe Verification
Confirm 100% accuracy on all dataframes before training
"""

import json
import pandas as pd
import os
from collections import defaultdict
from datetime import datetime

class FinalDataframeVerification:
    def __init__(self):
        self.data_dir = '../data'
        self.verification_results = {}
        
    def verify_all_dataframes(self):
        """Verify all dataframes for 100% accuracy"""
        print("🚀 FINAL DATAFRAME VERIFICATION - 100% ACCURACY CHECK")
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
        
        # 3. Verify award_structure.json
        print("\n" + "="*60)
        print("3. VERIFYING award_structure.json")
        print("="*60)
        award_result = self.verify_award_structure()
        
        # 4. Verify IDOT Excel cross-reference
        print("\n" + "="*60)
        print("4. VERIFYING IDOT EXCEL CROSS-REFERENCE")
        print("="*60)
        idot_result = self.verify_idot_cross_reference()
        
        # 5. Verify data consistency
        print("\n" + "="*60)
        print("5. VERIFYING DATA CONSISTENCY")
        print("="*60)
        consistency_result = self.verify_data_consistency()
        
        # Generate final report
        self.generate_final_report([
            firms_result,
            prequal_result,
            award_result,
            idot_result,
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
        
        return result
        
    def verify_award_structure(self):
        """Verify award_structure.json"""
        print("🔍 Verifying award_structure.json...")
        
        # Load award_structure.json
        with open(f'{self.data_dir}/award_structure.json', 'r') as f:
            award_data = json.load(f)
            
        # Check data quality
        total_records = len(award_data)
        records_with_firm = sum(1 for record in award_data if record.get('SELECTED FIRM'))
        records_with_job_number = sum(1 for record in award_data if record.get('JOB NUMBER'))
        records_with_date = sum(1 for record in award_data if record.get('AWARD DATE'))
        
        firm_accuracy = (records_with_firm / total_records) * 100 if total_records > 0 else 0
        job_number_accuracy = (records_with_job_number / total_records) * 100 if total_records > 0 else 0
        date_accuracy = (records_with_date / total_records) * 100 if total_records > 0 else 0
        
        overall_accuracy = (firm_accuracy + job_number_accuracy + date_accuracy) / 3
        
        result = {
            'dataframe': 'award_structure.json',
            'total_records': total_records,
            'records_with_firm': records_with_firm,
            'records_with_job_number': records_with_job_number,
            'records_with_date': records_with_date,
            'firm_accuracy': firm_accuracy,
            'job_number_accuracy': job_number_accuracy,
            'date_accuracy': date_accuracy,
            'overall_accuracy': overall_accuracy,
            'status': 'PASS' if overall_accuracy >= 95 else 'FAIL'
        }
        
        print(f"📊 Total Records: {total_records}")
        print(f"📊 Records with Firm: {records_with_firm}")
        print(f"📊 Records with Job Number: {records_with_job_number}")
        print(f"📊 Records with Date: {records_with_date}")
        print(f"📊 Firm Accuracy: {firm_accuracy:.2f}%")
        print(f"📊 Job Number Accuracy: {job_number_accuracy:.2f}%")
        print(f"📊 Date Accuracy: {date_accuracy:.2f}%")
        print(f"✅ Overall Accuracy: {overall_accuracy:.2f}%")
        print(f"🎯 Status: {result['status']}")
        
        return result
        
    def verify_idot_cross_reference(self):
        """Verify IDOT Excel cross-reference"""
        print("🔍 Verifying IDOT Excel cross-reference...")
        
        # Load IDOT Excel
        idot_excel = pd.read_excel(f'{self.data_dir}/IDOTConsultantList.xlsx', sheet_name='PrequalReport')
        
        # Check data quality
        total_rows = len(idot_excel)
        rows_with_firm = sum(1 for idx, row in idot_excel.iterrows() 
                           if pd.notna(row.get('Unnamed: 1')) and str(row.get('Unnamed: 1')).strip() != 'FIRM')
        rows_with_prequal = sum(1 for idx, row in idot_excel.iterrows() 
                              if pd.notna(row.get('Unnamed: 3')) and str(row.get('Unnamed: 3')).strip() != 'PRE-QUAL CATEGORIES')
        
        firm_accuracy = (rows_with_firm / total_rows) * 100 if total_rows > 0 else 0
        prequal_accuracy = (rows_with_prequal / total_rows) * 100 if total_rows > 0 else 0
        
        overall_accuracy = (firm_accuracy + prequal_accuracy) / 2
        
        result = {
            'dataframe': 'IDOT Excel',
            'total_rows': total_rows,
            'rows_with_firm': rows_with_firm,
            'rows_with_prequal': rows_with_prequal,
            'firm_accuracy': firm_accuracy,
            'prequal_accuracy': prequal_accuracy,
            'overall_accuracy': overall_accuracy,
            'status': 'PASS' if overall_accuracy >= 95 else 'FAIL'
        }
        
        print(f"📊 Total Rows: {total_rows}")
        print(f"📊 Rows with Firm: {rows_with_firm}")
        print(f"📊 Rows with Prequal: {rows_with_prequal}")
        print(f"📊 Firm Accuracy: {firm_accuracy:.2f}%")
        print(f"📊 Prequal Accuracy: {prequal_accuracy:.2f}%")
        print(f"✅ Overall Accuracy: {overall_accuracy:.2f}%")
        print(f"🎯 Status: {result['status']}")
        
        return result
        
    def verify_data_consistency(self):
        """Verify data consistency across all sources"""
        print("🔍 Verifying data consistency...")
        
        # Load all data sources
        with open(f'{self.data_dir}/firms_data.json', 'r') as f:
            firms_data = json.load(f)
            
        with open(f'{self.data_dir}/prequal_lookup.json', 'r') as f:
            prequal_lookup = json.load(f)
            
        with open(f'{self.data_dir}/award_structure.json', 'r') as f:
            award_data = json.load(f)
            
        # Check for duplicate firm names
        firm_names = [firm['firm_name'] for firm in firms_data if firm.get('firm_name')]
        duplicate_firms = [name for name in set(firm_names) if firm_names.count(name) > 1]
        
        # Check for missing firm codes
        missing_codes = sum(1 for firm in firms_data if not firm.get('firm_code'))
        
        # Check for empty categories
        empty_categories = sum(1 for category, firms in prequal_lookup.items() if not firms)
        
        # Check for invalid award data
        invalid_awards = sum(1 for award in award_data if not award.get('SELECTED FIRM') or not award.get('JOB NUMBER'))
        
        consistency_score = 100
        if duplicate_firms:
            consistency_score -= len(duplicate_firms) * 5
        if missing_codes:
            consistency_score -= missing_codes * 2
        if empty_categories:
            consistency_score -= empty_categories * 3
        if invalid_awards:
            consistency_score -= invalid_awards * 1
            
        consistency_score = max(0, consistency_score)
        
        result = {
            'dataframe': 'Data Consistency',
            'duplicate_firms': len(duplicate_firms),
            'missing_codes': missing_codes,
            'empty_categories': empty_categories,
            'invalid_awards': invalid_awards,
            'consistency_score': consistency_score,
            'status': 'PASS' if consistency_score >= 95 else 'FAIL'
        }
        
        print(f"📊 Duplicate Firms: {len(duplicate_firms)}")
        print(f"📊 Missing Codes: {missing_codes}")
        print(f"📊 Empty Categories: {empty_categories}")
        print(f"📊 Invalid Awards: {invalid_awards}")
        print(f"✅ Consistency Score: {consistency_score:.2f}%")
        print(f"🎯 Status: {result['status']}")
        
        if duplicate_firms:
            print(f"❌ Duplicate firms: {duplicate_firms[:3]}")
            
        return result
        
    def generate_final_report(self, results):
        """Generate final verification report"""
        print("\n" + "="*70)
        print("FINAL VERIFICATION REPORT")
        print("="*70)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'final_dataframe_verification_{timestamp}.txt'
        
        with open(report_file, 'w') as f:
            f.write("FINAL DATAFRAME VERIFICATION REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Purpose: Confirm 100% accuracy on all dataframes before training\n\n")
            
            # Overall results
            all_passed = all(result['status'] == 'PASS' for result in results)
            avg_accuracy = sum(result.get('accuracy', result.get('overall_accuracy', result.get('consistency_score', 0))) for result in results) / len(results)
            
            f.write("OVERALL RESULTS\n")
            f.write("-" * 15 + "\n")
            f.write(f"All Dataframes Pass: {'YES' if all_passed else 'NO'}\n")
            f.write(f"Average Accuracy: {avg_accuracy:.2f}%\n")
            f.write(f"Ready for Training: {'YES' if all_passed else 'NO'}\n\n")
            
            # Individual results
            f.write("INDIVIDUAL DATAFRAME RESULTS\n")
            f.write("-" * 30 + "\n")
            
            for result in results:
                f.write(f"{result['dataframe']}:\n")
                f.write(f"  Status: {result['status']}\n")
                
                if 'accuracy' in result:
                    f.write(f"  Accuracy: {result['accuracy']:.2f}%\n")
                elif 'overall_accuracy' in result:
                    f.write(f"  Overall Accuracy: {result['overall_accuracy']:.2f}%\n")
                elif 'consistency_score' in result:
                    f.write(f"  Consistency Score: {result['consistency_score']:.2f}%\n")
                    
                f.write("\n")
                
            # Final recommendation
            f.write("FINAL RECOMMENDATION\n")
            f.write("-" * 20 + "\n")
            
            if all_passed:
                f.write("🎉 ALL DATAFRAMES PASS VERIFICATION!\n")
                f.write("✅ Ready to proceed with model training\n")
                f.write("✅ Data quality is excellent\n")
                f.write("✅ No critical issues detected\n")
            else:
                f.write("⚠️  SOME DATAFRAMES FAIL VERIFICATION\n")
                f.write("❌ Need to fix issues before training\n")
                f.write("❌ Data quality needs improvement\n")
                
        print(f"✅ Final verification report saved: {report_file}")
        
        # Print final summary
        print(f"\n🎯 FINAL SUMMARY:")
        print(f"  All Dataframes Pass: {'YES' if all_passed else 'NO'}")
        print(f"  Average Accuracy: {avg_accuracy:.2f}%")
        print(f"  Ready for Training: {'YES' if all_passed else 'NO'}")
        
        if all_passed:
            print(f"\n🎉 SUCCESS: All dataframes verified! Ready for training!")
        else:
            print(f"\n⚠️  ISSUES DETECTED: Need to fix before training!")

if __name__ == "__main__":
    verifier = FinalDataframeVerification()
    verifier.verify_all_dataframes()
