#!/usr/bin/env python3
"""
Comprehensive Accuracy Verification
Run 10 detailed tests to ensure 100% accuracy between JSON and IDOT Excel
"""

import json
import pandas as pd
import os
from collections import defaultdict
from datetime import datetime
import random

class ComprehensiveAccuracyVerification:
    def __init__(self):
        self.data_dir = '../data'
        self.test_results = []
        self.verification_results = {}
        
    def load_all_data_sources(self):
        """Load all data sources for verification"""
        print("🔄 Loading all data sources for comprehensive verification...")
        
        # Load JSON files
        with open(f'{self.data_dir}/firms_data.json', 'r') as f:
            self.firms_json = json.load(f)
        print(f"✅ Loaded firms_data.json: {len(self.firms_json)} records")
        
        with open(f'{self.data_dir}/prequal_lookup.json', 'r') as f:
            self.prequal_lookup = json.load(f)
        print(f"✅ Loaded prequal_lookup.json: {len(self.prequal_lookup)} categories")
        
        # Load IDOT Excel
        self.idot_excel = pd.read_excel(f'{self.data_dir}/IDOTConsultantList.xlsx', sheet_name='PrequalReport')
        print(f"✅ Loaded IDOT Excel PrequalReport: {self.idot_excel.shape}")
        
        # Extract firm data from IDOT Excel
        self.idot_firms = []
        for idx, row in self.idot_excel.iterrows():
            # Column 1 (Unnamed: 1) for firm names
            firm_name = row.get('Unnamed: 1')
            if pd.notna(firm_name) and isinstance(firm_name, str):
                firm_name = firm_name.strip()
                if firm_name and firm_name != 'FIRM' and len(firm_name) > 2:
                    # Column 3 (Unnamed: 3) for prequals
                    prequal_categories = row.get('Unnamed: 3')
                    
                    self.idot_firms.append({
                        'firm_name': firm_name,
                        'email': row.get('Unnamed: 6', ''),
                        'is_dbe': row.get('Unnamed: 2', False),
                        'location': f"{row.get('Unnamed: 4', '')}, {row.get('Unnamed: 5', '')}".strip(', '),
                        'prequal_categories': str(prequal_categories) if pd.notna(prequal_categories) else '',
                        'source': 'IDOT Excel'
                    })
        
        print(f"✅ Extracted {len(self.idot_firms)} firms from IDOT Excel")
        
    def test_1_firm_count_verification(self):
        """Test 1: Verify firm count matches exactly"""
        print("\n🧪 Test 1: Firm Count Verification")
        
        json_count = len(self.firms_json)
        idot_count = len(self.idot_firms)
        
        result = {
            'test_name': 'Firm Count Verification',
            'json_count': json_count,
            'idot_count': idot_count,
            'match': json_count == idot_count,
            'accuracy': 100.0 if json_count == idot_count else 0.0,
            'details': f"JSON: {json_count}, IDOT: {idot_count}"
        }
        
        print(f"📊 JSON Firms: {json_count}")
        print(f"📊 IDOT Firms: {idot_count}")
        print(f"✅ Match: {result['match']}")
        
        return result
        
    def test_2_firm_name_exact_match(self):
        """Test 2: Verify every firm name matches exactly"""
        print("\n🧪 Test 2: Firm Name Exact Match")
        
        json_names = set()
        for firm in self.firms_json:
            if firm.get('firm_name'):
                json_names.add(firm['firm_name'].strip().upper())
                
        idot_names = set()
        for firm in self.idot_firms:
            idot_names.add(firm['firm_name'].strip().upper())
            
        exact_matches = json_names.intersection(idot_names)
        missing_in_json = idot_names - json_names
        missing_in_idot = json_names - idot_names
        
        accuracy = (len(exact_matches) / len(idot_names)) * 100 if idot_names else 0
        
        result = {
            'test_name': 'Firm Name Exact Match',
            'json_names': len(json_names),
            'idot_names': len(idot_names),
            'exact_matches': len(exact_matches),
            'missing_in_json': list(missing_in_json)[:5],
            'missing_in_idot': list(missing_in_idot)[:5],
            'accuracy': accuracy,
            'match': len(missing_in_json) == 0 and len(missing_in_idot) == 0
        }
        
        print(f"📊 JSON Names: {len(json_names)}")
        print(f"📊 IDOT Names: {len(idot_names)}")
        print(f"📊 Exact Matches: {len(exact_matches)}")
        print(f"📊 Missing in JSON: {len(missing_in_json)}")
        print(f"📊 Missing in IDOT: {len(missing_in_idot)}")
        print(f"✅ Accuracy: {accuracy:.2f}%")
        
        return result
        
    def test_3_random_sample_verification(self):
        """Test 3: Verify random sample of firms"""
        print("\n🧪 Test 3: Random Sample Verification")
        
        # Take random sample of 20 firms
        sample_size = min(20, len(self.idot_firms))
        random_sample = random.sample(self.idot_firms, sample_size)
        
        verified_count = 0
        verification_details = []
        
        for idot_firm in random_sample:
            idot_name = idot_firm['firm_name'].strip().upper()
            
            # Find matching firm in JSON
            json_firm = None
            for firm in self.firms_json:
                if firm.get('firm_name') and firm['firm_name'].strip().upper() == idot_name:
                    json_firm = firm
                    break
                    
            if json_firm:
                verified_count += 1
                verification_details.append({
                    'firm_name': idot_firm['firm_name'],
                    'found_in_json': True,
                    'idot_prequals': idot_firm['prequal_categories'],
                    'json_prequals': json_firm.get('prequalifications', [])
                })
            else:
                verification_details.append({
                    'firm_name': idot_firm['firm_name'],
                    'found_in_json': False,
                    'idot_prequals': idot_firm['prequal_categories'],
                    'json_prequals': None
                })
                
        accuracy = (verified_count / sample_size) * 100
        
        result = {
            'test_name': 'Random Sample Verification',
            'sample_size': sample_size,
            'verified_count': verified_count,
            'accuracy': accuracy,
            'verification_details': verification_details[:5]  # Show first 5
        }
        
        print(f"📊 Sample Size: {sample_size}")
        print(f"📊 Verified: {verified_count}")
        print(f"✅ Accuracy: {accuracy:.2f}%")
        
        return result
        
    def test_4_prequalification_coverage(self):
        """Test 4: Verify prequalification coverage"""
        print("\n🧪 Test 4: Prequalification Coverage")
        
        # Get all prequal categories from IDOT Excel
        idot_prequals = set()
        for firm in self.idot_firms:
            if firm['prequal_categories']:
                idot_prequals.add(firm['prequal_categories'].strip())
                
        # Get all prequal categories from JSON lookup
        json_prequals = set(self.prequal_lookup.keys())
        
        # Get prequal categories from firms JSON
        firms_json_prequals = set()
        for firm in self.firms_json:
            if firm.get('prequalifications'):
                for prequal in firm['prequalifications']:
                    firms_json_prequals.add(prequal.strip())
                    
        coverage_analysis = {
            'idot_prequals': len(idot_prequals),
            'json_lookup_prequals': len(json_prequals),
            'firms_json_prequals': len(firms_json_prequals),
            'idot_in_lookup': len(idot_prequals.intersection(json_prequals)),
            'idot_in_firms_json': len(idot_prequals.intersection(firms_json_prequals)),
            'lookup_in_firms_json': len(json_prequals.intersection(firms_json_prequals))
        }
        
        # Calculate coverage accuracy
        idot_lookup_coverage = (coverage_analysis['idot_in_lookup'] / len(idot_prequals)) * 100 if idot_prequals else 0
        idot_firms_coverage = (coverage_analysis['idot_in_firms_json'] / len(idot_prequals)) * 100 if idot_prequals else 0
        
        result = {
            'test_name': 'Prequalification Coverage',
            'coverage_analysis': coverage_analysis,
            'idot_lookup_coverage': idot_lookup_coverage,
            'idot_firms_coverage': idot_firms_coverage,
            'average_coverage': (idot_lookup_coverage + idot_firms_coverage) / 2
        }
        
        print(f"📊 IDOT Prequals: {len(idot_prequals)}")
        print(f"📊 JSON Lookup Prequals: {len(json_prequals)}")
        print(f"📊 Firms JSON Prequals: {len(firms_json_prequals)}")
        print(f"📊 IDOT-Lookup Coverage: {idot_lookup_coverage:.2f}%")
        print(f"📊 IDOT-Firms Coverage: {idot_firms_coverage:.2f}%")
        print(f"✅ Average Coverage: {result['average_coverage']:.2f}%")
        
        return result
        
    def test_5_specific_firm_verification(self):
        """Test 5: Verify specific known firms (including CBB)"""
        print("\n🧪 Test 5: Specific Firm Verification")
        
        # Test specific firms including CBB
        test_firms = ['CBB', 'WSP USA Inc.', '"T" Engineering Service, Ltd.']
        
        verification_results = []
        verified_count = 0
        
        for test_firm in test_firms:
            # Find in IDOT Excel
            idot_firm = None
            for firm in self.idot_firms:
                if firm['firm_name'].strip().upper() == test_firm.upper():
                    idot_firm = firm
                    break
                    
            # Find in JSON
            json_firm = None
            for firm in self.firms_json:
                if firm.get('firm_name') and firm['firm_name'].strip().upper() == test_firm.upper():
                    json_firm = firm
                    break
                    
            if idot_firm and json_firm:
                verified_count += 1
                verification_results.append({
                    'firm_name': test_firm,
                    'found_in_both': True,
                    'idot_prequals': idot_firm['prequal_categories'],
                    'json_prequals': json_firm.get('prequalifications', [])
                })
            else:
                verification_results.append({
                    'firm_name': test_firm,
                    'found_in_both': False,
                    'found_in_idot': idot_firm is not None,
                    'found_in_json': json_firm is not None
                })
                
        accuracy = (verified_count / len(test_firms)) * 100
        
        result = {
            'test_name': 'Specific Firm Verification',
            'test_firms': test_firms,
            'verified_count': verified_count,
            'accuracy': accuracy,
            'verification_results': verification_results
        }
        
        print(f"📊 Test Firms: {len(test_firms)}")
        print(f"📊 Verified: {verified_count}")
        print(f"✅ Accuracy: {accuracy:.2f}%")
        
        return result
        
    def test_6_data_consistency_check(self):
        """Test 6: Check data consistency across sources"""
        print("\n🧪 Test 6: Data Consistency Check")
        
        consistency_issues = []
        
        # Check for duplicate firm names
        json_names = [firm['firm_name'].strip().upper() for firm in self.firms_json if firm.get('firm_name')]
        idot_names = [firm['firm_name'].strip().upper() for firm in self.idot_firms]
        
        json_duplicates = [name for name in set(json_names) if json_names.count(name) > 1]
        idot_duplicates = [name for name in set(idot_names) if idot_names.count(name) > 1]
        
        if json_duplicates:
            consistency_issues.append(f"JSON has {len(json_duplicates)} duplicate firm names")
        if idot_duplicates:
            consistency_issues.append(f"IDOT has {len(idot_duplicates)} duplicate firm names")
            
        # Check for empty/null values
        json_empty_names = sum(1 for firm in self.firms_json if not firm.get('firm_name'))
        idot_empty_names = sum(1 for firm in self.idot_firms if not firm['firm_name'])
        
        if json_empty_names > 0:
            consistency_issues.append(f"JSON has {json_empty_names} empty firm names")
        if idot_empty_names > 0:
            consistency_issues.append(f"IDOT has {idot_empty_names} empty firm names")
            
        # Check for special characters or formatting issues
        json_special_chars = sum(1 for firm in self.firms_json if firm.get('firm_name') and '?' in firm['firm_name'])
        idot_special_chars = sum(1 for firm in self.idot_firms if '?' in firm['firm_name'])
        
        if json_special_chars > 0:
            consistency_issues.append(f"JSON has {json_special_chars} firms with special characters")
        if idot_special_chars > 0:
            consistency_issues.append(f"IDOT has {idot_special_chars} firms with special characters")
            
        consistency_score = 100 - (len(consistency_issues) * 10)  # Deduct 10 points per issue
        consistency_score = max(0, consistency_score)
        
        result = {
            'test_name': 'Data Consistency Check',
            'consistency_issues': consistency_issues,
            'consistency_score': consistency_score,
            'json_duplicates': len(json_duplicates),
            'idot_duplicates': len(idot_duplicates),
            'json_empty_names': json_empty_names,
            'idot_empty_names': idot_empty_names
        }
        
        print(f"📊 Consistency Issues: {len(consistency_issues)}")
        print(f"📊 JSON Duplicates: {len(json_duplicates)}")
        print(f"📊 IDOT Duplicates: {len(idot_duplicates)}")
        print(f"✅ Consistency Score: {consistency_score:.2f}%")
        
        return result
        
    def test_7_prequalification_mapping_accuracy(self):
        """Test 7: Verify prequalification mapping accuracy"""
        print("\n🧪 Test 7: Prequalification Mapping Accuracy")
        
        # Sample 10 firms and check their prequalifications
        sample_size = min(10, len(self.idot_firms))
        sample_firms = random.sample(self.idot_firms, sample_size)
        
        mapping_accuracy = 0
        mapping_details = []
        
        for idot_firm in sample_firms:
            idot_name = idot_firm['firm_name'].strip().upper()
            idot_prequals = idot_firm['prequal_categories'].strip() if idot_firm['prequal_categories'] else ''
            
            # Find in JSON
            json_firm = None
            for firm in self.firms_json:
                if firm.get('firm_name') and firm['firm_name'].strip().upper() == idot_name:
                    json_firm = firm
                    break
                    
            if json_firm:
                json_prequals = json_firm.get('prequalifications', [])
                
                # Check if IDOT prequal is in JSON prequals
                if idot_prequals and json_prequals:
                    if idot_prequals in [p.strip() for p in json_prequals]:
                        mapping_accuracy += 1
                        
                mapping_details.append({
                    'firm_name': idot_firm['firm_name'],
                    'idot_prequal': idot_prequals,
                    'json_prequals': json_prequals,
                    'mapped': idot_prequals in [p.strip() for p in json_prequals] if idot_prequals and json_prequals else False
                })
            else:
                mapping_details.append({
                    'firm_name': idot_firm['firm_name'],
                    'idot_prequal': idot_prequals,
                    'json_prequals': None,
                    'mapped': False
                })
                
        accuracy = (mapping_accuracy / sample_size) * 100
        
        result = {
            'test_name': 'Prequalification Mapping Accuracy',
            'sample_size': sample_size,
            'mapping_accuracy': mapping_accuracy,
            'accuracy': accuracy,
            'mapping_details': mapping_details[:5]  # Show first 5
        }
        
        print(f"📊 Sample Size: {sample_size}")
        print(f"📊 Accurate Mappings: {mapping_accuracy}")
        print(f"✅ Accuracy: {accuracy:.2f}%")
        
        return result
        
    def test_8_complete_firm_list_verification(self):
        """Test 8: Verify complete firm list"""
        print("\n🧪 Test 8: Complete Firm List Verification")
        
        # Create complete lists
        json_firm_list = []
        for firm in self.firms_json:
            if firm.get('firm_name'):
                json_firm_list.append(firm['firm_name'].strip().upper())
                
        idot_firm_list = []
        for firm in self.idot_firms:
            idot_firm_list.append(firm['firm_name'].strip().upper())
            
        # Sort for comparison
        json_firm_list.sort()
        idot_firm_list.sort()
        
        # Check if lists are identical
        lists_match = json_firm_list == idot_firm_list
        
        # Find differences
        json_only = set(json_firm_list) - set(idot_firm_list)
        idot_only = set(idot_firm_list) - set(json_firm_list)
        
        accuracy = 100.0 if lists_match else 0.0
        
        result = {
            'test_name': 'Complete Firm List Verification',
            'lists_match': lists_match,
            'json_only': list(json_only)[:5],
            'idot_only': list(idot_only)[:5],
            'accuracy': accuracy,
            'json_count': len(json_firm_list),
            'idot_count': len(idot_firm_list)
        }
        
        print(f"📊 JSON Firms: {len(json_firm_list)}")
        print(f"📊 IDOT Firms: {len(idot_firm_list)}")
        print(f"📊 Lists Match: {lists_match}")
        print(f"📊 JSON Only: {len(json_only)}")
        print(f"📊 IDOT Only: {len(idot_only)}")
        print(f"✅ Accuracy: {accuracy:.2f}%")
        
        return result
        
    def test_9_data_format_verification(self):
        """Test 9: Verify data format consistency"""
        print("\n🧪 Test 9: Data Format Verification")
        
        format_issues = []
        
        # Check JSON format
        for firm in self.firms_json:
            if not isinstance(firm, dict):
                format_issues.append("JSON contains non-dictionary entries")
                break
            if 'firm_name' not in firm:
                format_issues.append("JSON missing firm_name field")
                break
                
        # Check IDOT format
        for firm in self.idot_firms:
            if not isinstance(firm, dict):
                format_issues.append("IDOT contains non-dictionary entries")
                break
            if 'firm_name' not in firm:
                format_issues.append("IDOT missing firm_name field")
                break
                
        # Check for required fields
        json_required_fields = ['firm_name']
        idot_required_fields = ['firm_name', 'email', 'is_dbe', 'location', 'prequal_categories']
        
        for field in json_required_fields:
            missing_count = sum(1 for firm in self.firms_json if field not in firm)
            if missing_count > 0:
                format_issues.append(f"JSON missing {field} in {missing_count} records")
                
        for field in idot_required_fields:
            missing_count = sum(1 for firm in self.idot_firms if field not in firm)
            if missing_count > 0:
                format_issues.append(f"IDOT missing {field} in {missing_count} records")
                
        format_score = 100 - (len(format_issues) * 10)
        format_score = max(0, format_score)
        
        result = {
            'test_name': 'Data Format Verification',
            'format_issues': format_issues,
            'format_score': format_score,
            'json_format_valid': len([i for i in format_issues if 'JSON' in i]) == 0,
            'idot_format_valid': len([i for i in format_issues if 'IDOT' in i]) == 0
        }
        
        print(f"📊 Format Issues: {len(format_issues)}")
        print(f"📊 JSON Format Valid: {result['json_format_valid']}")
        print(f"📊 IDOT Format Valid: {result['idot_format_valid']}")
        print(f"✅ Format Score: {format_score:.2f}%")
        
        return result
        
    def test_10_final_comprehensive_verification(self):
        """Test 10: Final comprehensive verification"""
        print("\n🧪 Test 10: Final Comprehensive Verification")
        
        # Run all previous tests and calculate overall accuracy
        all_tests = [
            self.test_1_firm_count_verification(),
            self.test_2_firm_name_exact_match(),
            self.test_3_random_sample_verification(),
            self.test_4_prequalification_coverage(),
            self.test_5_specific_firm_verification(),
            self.test_6_data_consistency_check(),
            self.test_7_prequalification_mapping_accuracy(),
            self.test_8_complete_firm_list_verification(),
            self.test_9_data_format_verification()
        ]
        
        # Calculate overall accuracy
        accuracies = []
        for test in all_tests:
            if 'accuracy' in test:
                accuracies.append(test['accuracy'])
            elif 'consistency_score' in test:
                accuracies.append(test['consistency_score'])
            elif 'format_score' in test:
                accuracies.append(test['format_score'])
            elif 'average_coverage' in test:
                accuracies.append(test['average_coverage'])
                
        overall_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
        
        # Check if all critical tests pass
        critical_tests = [
            all_tests[0]['match'],  # Firm count
            all_tests[1]['match'],  # Firm names
            all_tests[7]['lists_match'],  # Complete list
            all_tests[8]['json_format_valid'],  # JSON format
            all_tests[8]['idot_format_valid']   # IDOT format
        ]
        
        all_critical_passed = all(critical_tests)
        
        result = {
            'test_name': 'Final Comprehensive Verification',
            'overall_accuracy': overall_accuracy,
            'all_critical_passed': all_critical_passed,
            'individual_test_results': all_tests,
            'critical_tests_passed': sum(critical_tests),
            'total_critical_tests': len(critical_tests)
        }
        
        print(f"📊 Overall Accuracy: {overall_accuracy:.2f}%")
        print(f"📊 Critical Tests Passed: {sum(critical_tests)}/{len(critical_tests)}")
        print(f"✅ All Critical Tests Pass: {all_critical_passed}")
        
        return result
        
    def run_all_tests(self):
        """Run all 10 verification tests"""
        print("🚀 Starting Comprehensive Accuracy Verification (10 Tests)...")
        
        # Load data
        self.load_all_data_sources()
        
        # Run all tests
        tests = [
            self.test_1_firm_count_verification,
            self.test_2_firm_name_exact_match,
            self.test_3_random_sample_verification,
            self.test_4_prequalification_coverage,
            self.test_5_specific_firm_verification,
            self.test_6_data_consistency_check,
            self.test_7_prequalification_mapping_accuracy,
            self.test_8_complete_firm_list_verification,
            self.test_9_data_format_verification,
            self.test_10_final_comprehensive_verification
        ]
        
        for i, test_func in enumerate(tests, 1):
            print(f"\n{'='*60}")
            print(f"🧪 RUNNING TEST {i}/10: {test_func.__name__.replace('_', ' ').title()}")
            print(f"{'='*60}")
            
            try:
                result = test_func()
                self.test_results.append(result)
                print(f"✅ Test {i} completed successfully")
            except Exception as e:
                print(f"❌ Test {i} failed: {str(e)}")
                self.test_results.append({
                    'test_name': test_func.__name__.replace('_', ' ').title(),
                    'error': str(e),
                    'accuracy': 0.0
                })
                
        # Generate comprehensive report
        self.generate_comprehensive_report()
        
        return self.test_results
        
    def generate_comprehensive_report(self):
        """Generate comprehensive verification report"""
        print("\n📋 Generating Comprehensive Verification Report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'comprehensive_accuracy_verification_{timestamp}.txt'
        
        with open(report_file, 'w') as f:
            f.write("COMPREHENSIVE ACCURACY VERIFICATION REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Purpose: Verify 100% accuracy between JSON and IDOT Excel data\n")
            f.write("Tests Conducted: 10 comprehensive verification tests\n\n")
            
            # Overall results
            accuracies = []
            for result in self.test_results:
                if 'accuracy' in result:
                    accuracies.append(result['accuracy'])
                elif 'consistency_score' in result:
                    accuracies.append(result['consistency_score'])
                elif 'format_score' in result:
                    accuracies.append(result['format_score'])
                elif 'average_coverage' in result:
                    accuracies.append(result['average_coverage'])
                    
            overall_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
            
            f.write("OVERALL RESULTS\n")
            f.write("-" * 15 + "\n")
            f.write(f"Overall Accuracy: {overall_accuracy:.2f}%\n")
            f.write(f"Tests Completed: {len(self.test_results)}/10\n")
            f.write(f"Critical Tests Passed: {sum(1 for r in self.test_results if r.get('match', False))}\n\n")
            
            # Individual test results
            f.write("INDIVIDUAL TEST RESULTS\n")
            f.write("-" * 25 + "\n")
            
            for i, result in enumerate(self.test_results, 1):
                f.write(f"Test {i}: {result.get('test_name', 'Unknown Test')}\n")
                
                if 'accuracy' in result:
                    f.write(f"  Accuracy: {result['accuracy']:.2f}%\n")
                elif 'consistency_score' in result:
                    f.write(f"  Consistency Score: {result['consistency_score']:.2f}%\n")
                elif 'format_score' in result:
                    f.write(f"  Format Score: {result['format_score']:.2f}%\n")
                elif 'average_coverage' in result:
                    f.write(f"  Average Coverage: {result['average_coverage']:.2f}%\n")
                    
                if 'match' in result:
                    f.write(f"  Match: {result['match']}\n")
                if 'lists_match' in result:
                    f.write(f"  Lists Match: {result['lists_match']}\n")
                    
                f.write("\n")
                
            # Critical findings
            f.write("CRITICAL FINDINGS\n")
            f.write("-" * 18 + "\n")
            
            for result in self.test_results:
                if result.get('test_name') == 'Firm Count Verification':
                    if result.get('match'):
                        f.write("✅ Firm count matches exactly between JSON and IDOT Excel\n")
                    else:
                        f.write("❌ Firm count mismatch detected\n")
                        
                if result.get('test_name') == 'Firm Name Exact Match':
                    if result.get('match'):
                        f.write("✅ All firm names match exactly between JSON and IDOT Excel\n")
                    else:
                        f.write("❌ Firm name mismatches detected\n")
                        
                if result.get('test_name') == 'Complete Firm List Verification':
                    if result.get('lists_match'):
                        f.write("✅ Complete firm lists are identical\n")
                    else:
                        f.write("❌ Firm list differences detected\n")
                        
            f.write("\nVERIFICATION CONCLUSION\n")
            f.write("-" * 25 + "\n")
            
            if overall_accuracy >= 95:
                f.write("🎉 EXCELLENT: Data accuracy is very high (95%+)\n")
                f.write("   JSON data is highly reliable and matches IDOT Excel\n")
            elif overall_accuracy >= 80:
                f.write("✅ GOOD: Data accuracy is good (80%+)\n")
                f.write("   Minor issues detected but overall reliable\n")
            elif overall_accuracy >= 60:
                f.write("⚠️  FAIR: Data accuracy needs improvement (60%+)\n")
                f.write("   Several issues detected that need attention\n")
            else:
                f.write("❌ POOR: Data accuracy is low (<60%)\n")
                f.write("   Significant issues detected - data needs major fixes\n")
                
        print(f"✅ Comprehensive verification report saved: {report_file}")
        return report_file

if __name__ == "__main__":
    verifier = ComprehensiveAccuracyVerification()
    results = verifier.run_all_tests()
