#!/usr/bin/env python3
"""
Prequalification Lookup Verification
Verify accuracy of prequal_lookup.json against IDOT Excel data
"""

import json
import pandas as pd
import os
from collections import defaultdict
from datetime import datetime

class PrequalLookupVerification:
    def __init__(self):
        self.data_dir = '../data'
        self.verification_results = {}
        
    def load_data_sources(self):
        """Load prequal_lookup.json and IDOT Excel data"""
        print("🔄 Loading data sources for prequalification verification...")
        
        # Load prequal_lookup.json
        with open(f'{self.data_dir}/prequal_lookup.json', 'r') as f:
            self.prequal_lookup = json.load(f)
        print(f"✅ Loaded prequal_lookup.json: {len(self.prequal_lookup)} categories")
        
        # Load IDOT Excel
        self.idot_excel = pd.read_excel(f'{self.data_dir}/IDOTConsultantList.xlsx', sheet_name='PrequalReport')
        print(f"✅ Loaded IDOT Excel PrequalReport: {self.idot_excel.shape}")
        
        # Extract prequalification data from IDOT Excel
        self.idot_prequals = defaultdict(set)
        for idx, row in self.idot_excel.iterrows():
            firm_name = row.get('Unnamed: 1')
            prequal_category = row.get('Unnamed: 3')
            
            if pd.notna(firm_name) and pd.notna(prequal_category):
                firm_name = str(firm_name).strip()
                prequal_category = str(prequal_category).strip()
                
                if firm_name and firm_name != 'FIRM' and prequal_category and prequal_category != 'PRE-QUAL CATEGORIES':
                    self.idot_prequals[prequal_category].add(firm_name)
                    
        print(f"✅ Extracted {len(self.idot_prequals)} prequalification categories from IDOT Excel")
        
    def test_1_category_count_verification(self):
        """Test 1: Verify category count matches"""
        print("\n🧪 Test 1: Category Count Verification")
        
        lookup_count = len(self.prequal_lookup)
        idot_count = len(self.idot_prequals)
        
        result = {
            'test_name': 'Category Count Verification',
            'lookup_count': lookup_count,
            'idot_count': idot_count,
            'match': lookup_count == idot_count,
            'accuracy': 100.0 if lookup_count == idot_count else 0.0,
            'details': f"Lookup: {lookup_count}, IDOT: {idot_count}"
        }
        
        print(f"📊 Lookup Categories: {lookup_count}")
        print(f"📊 IDOT Categories: {idot_count}")
        print(f"✅ Match: {result['match']}")
        
        return result
        
    def test_2_category_name_exact_match(self):
        """Test 2: Verify category names match exactly"""
        print("\n🧪 Test 2: Category Name Exact Match")
        
        lookup_categories = set(self.prequal_lookup.keys())
        idot_categories = set(self.idot_prequals.keys())
        
        exact_matches = lookup_categories.intersection(idot_categories)
        missing_in_lookup = idot_categories - lookup_categories
        missing_in_idot = lookup_categories - idot_categories
        
        accuracy = (len(exact_matches) / len(idot_categories)) * 100 if idot_categories else 0
        
        result = {
            'test_name': 'Category Name Exact Match',
            'lookup_categories': len(lookup_categories),
            'idot_categories': len(idot_categories),
            'exact_matches': len(exact_matches),
            'missing_in_lookup': list(missing_in_lookup)[:10],
            'missing_in_idot': list(missing_in_idot)[:10],
            'accuracy': accuracy,
            'match': len(missing_in_lookup) == 0 and len(missing_in_idot) == 0
        }
        
        print(f"📊 Lookup Categories: {len(lookup_categories)}")
        print(f"📊 IDOT Categories: {len(idot_categories)}")
        print(f"📊 Exact Matches: {len(exact_matches)}")
        print(f"📊 Missing in Lookup: {len(missing_in_lookup)}")
        print(f"📊 Missing in IDOT: {len(missing_in_idot)}")
        print(f"✅ Accuracy: {accuracy:.2f}%")
        
        return result
        
    def test_3_firm_count_verification(self):
        """Test 3: Verify firm counts per category"""
        print("\n🧪 Test 3: Firm Count Verification per Category")
        
        # Compare firm counts for matching categories
        matching_categories = set(self.prequal_lookup.keys()).intersection(set(self.idot_prequals.keys()))
        
        count_matches = 0
        count_discrepancies = []
        
        for category in matching_categories:
            # Extract firm names from prequal_lookup (list of dicts)
            lookup_firms = set()
            if isinstance(self.prequal_lookup[category], list):
                for firm_dict in self.prequal_lookup[category]:
                    if isinstance(firm_dict, dict) and 'firm_name' in firm_dict:
                        lookup_firms.add(firm_dict['firm_name'])
                        
            idot_firms = self.idot_prequals[category]
            
            if len(lookup_firms) == len(idot_firms):
                count_matches += 1
            else:
                count_discrepancies.append({
                    'category': category,
                    'lookup_count': len(lookup_firms),
                    'idot_count': len(idot_firms),
                    'difference': abs(len(lookup_firms) - len(idot_firms))
                })
                
        accuracy = (count_matches / len(matching_categories)) * 100 if matching_categories else 0
        
        result = {
            'test_name': 'Firm Count Verification per Category',
            'matching_categories': len(matching_categories),
            'count_matches': count_matches,
            'count_discrepancies': count_discrepancies[:10],  # Top 10 discrepancies
            'accuracy': accuracy
        }
        
        print(f"📊 Matching Categories: {len(matching_categories)}")
        print(f"📊 Count Matches: {count_matches}")
        print(f"📊 Count Discrepancies: {len(count_discrepancies)}")
        print(f"✅ Accuracy: {accuracy:.2f}%")
        
        return result
        
    def test_4_firm_name_verification(self):
        """Test 4: Verify firm names within categories"""
        print("\n🧪 Test 4: Firm Name Verification within Categories")
        
        # Sample 5 categories and verify firm names
        sample_categories = list(set(self.prequal_lookup.keys()).intersection(set(self.idot_prequals.keys())))[:5]
        
        verification_results = []
        total_firm_matches = 0
        total_firms_checked = 0
        
        for category in sample_categories:
            # Extract firm names from prequal_lookup (list of dicts)
            lookup_firms = set()
            if isinstance(self.prequal_lookup[category], list):
                for firm_dict in self.prequal_lookup[category]:
                    if isinstance(firm_dict, dict) and 'firm_name' in firm_dict:
                        lookup_firms.add(firm_dict['firm_name'])
                        
            idot_firms = self.idot_prequals[category]
            
            # Normalize firm names for comparison
            lookup_firms_normalized = {firm.strip().upper() for firm in lookup_firms}
            idot_firms_normalized = {firm.strip().upper() for firm in idot_firms}
            
            exact_matches = lookup_firms_normalized.intersection(idot_firms_normalized)
            missing_in_lookup = idot_firms_normalized - lookup_firms_normalized
            missing_in_idot = lookup_firms_normalized - idot_firms_normalized
            
            category_accuracy = (len(exact_matches) / len(idot_firms_normalized)) * 100 if idot_firms_normalized else 0
            
            verification_results.append({
                'category': category,
                'lookup_firms': len(lookup_firms),
                'idot_firms': len(idot_firms),
                'exact_matches': len(exact_matches),
                'missing_in_lookup': list(missing_in_lookup)[:5],
                'missing_in_idot': list(missing_in_idot)[:5],
                'accuracy': category_accuracy
            })
            
            total_firm_matches += len(exact_matches)
            total_firms_checked += len(idot_firms_normalized)
            
        overall_accuracy = (total_firm_matches / total_firms_checked) * 100 if total_firms_checked > 0 else 0
        
        result = {
            'test_name': 'Firm Name Verification within Categories',
            'sample_categories': len(sample_categories),
            'verification_results': verification_results,
            'total_firm_matches': total_firm_matches,
            'total_firms_checked': total_firms_checked,
            'accuracy': overall_accuracy
        }
        
        print(f"📊 Sample Categories: {len(sample_categories)}")
        print(f"📊 Total Firm Matches: {total_firm_matches}")
        print(f"📊 Total Firms Checked: {total_firms_checked}")
        print(f"✅ Overall Accuracy: {overall_accuracy:.2f}%")
        
        return result
        
    def test_5_specific_category_verification(self):
        """Test 5: Verify specific important categories"""
        print("\n🧪 Test 5: Specific Category Verification")
        
        # Test specific important categories
        important_categories = [
            'Highways - Roads and Streets',
            'Special Services - Construction Inspection',
            'Location Design Studies - Rehabilitation',
            'Special Studies - Traffic Studies',
            'Special Plans - Traffic Signals'
        ]
        
        verification_results = []
        verified_count = 0
        
        for category in important_categories:
            # Extract firm names from prequal_lookup (list of dicts)
            lookup_firms = set()
            if isinstance(self.prequal_lookup.get(category, []), list):
                for firm_dict in self.prequal_lookup[category]:
                    if isinstance(firm_dict, dict) and 'firm_name' in firm_dict:
                        lookup_firms.add(firm_dict['firm_name'])
                        
            idot_firms = self.idot_prequals.get(category, set())
            
            if lookup_firms and idot_firms:
                # Normalize for comparison
                lookup_firms_normalized = {firm.strip().upper() for firm in lookup_firms}
                idot_firms_normalized = {firm.strip().upper() for firm in idot_firms}
                
                exact_matches = lookup_firms_normalized.intersection(idot_firms_normalized)
                match_percentage = (len(exact_matches) / len(idot_firms_normalized)) * 100 if idot_firms_normalized else 0
                
                if match_percentage >= 80:  # Consider verified if 80%+ match
                    verified_count += 1
                    
                verification_results.append({
                    'category': category,
                    'lookup_firms': len(lookup_firms),
                    'idot_firms': len(idot_firms),
                    'exact_matches': len(exact_matches),
                    'match_percentage': match_percentage,
                    'verified': match_percentage >= 80
                })
            else:
                verification_results.append({
                    'category': category,
                    'lookup_firms': len(lookup_firms),
                    'idot_firms': len(idot_firms),
                    'exact_matches': 0,
                    'match_percentage': 0,
                    'verified': False
                })
                
        accuracy = (verified_count / len(important_categories)) * 100
        
        result = {
            'test_name': 'Specific Category Verification',
            'important_categories': important_categories,
            'verified_count': verified_count,
            'accuracy': accuracy,
            'verification_results': verification_results
        }
        
        print(f"📊 Important Categories: {len(important_categories)}")
        print(f"📊 Verified Categories: {verified_count}")
        print(f"✅ Accuracy: {accuracy:.2f}%")
        
        return result
        
    def test_6_data_structure_verification(self):
        """Test 6: Verify data structure integrity"""
        print("\n🧪 Test 6: Data Structure Verification")
        
        structure_issues = []
        
        # Check prequal_lookup structure
        for category, firms in self.prequal_lookup.items():
            if not isinstance(firms, list):
                structure_issues.append(f"Category '{category}' has non-list data: {type(firms)}")
                
        # Check for empty categories
        empty_categories = [cat for cat, firms in self.prequal_lookup.items() if not firms]
        if empty_categories:
            structure_issues.append(f"Empty categories found: {len(empty_categories)}")
            
        # Check for duplicate categories
        category_names = list(self.prequal_lookup.keys())
        duplicate_categories = [name for name in set(category_names) if category_names.count(name) > 1]
        if duplicate_categories:
            structure_issues.append(f"Duplicate categories found: {len(duplicate_categories)}")
            
        # Check for special characters in category names
        special_char_categories = [cat for cat in self.prequal_lookup.keys() if '?' in cat or '\\' in cat]
        if special_char_categories:
            structure_issues.append(f"Categories with special characters: {len(special_char_categories)}")
            
        structure_score = 100 - (len(structure_issues) * 10)
        structure_score = max(0, structure_score)
        
        result = {
            'test_name': 'Data Structure Verification',
            'structure_issues': structure_issues,
            'structure_score': structure_score,
            'empty_categories': len(empty_categories),
            'duplicate_categories': len(duplicate_categories),
            'special_char_categories': len(special_char_categories)
        }
        
        print(f"📊 Structure Issues: {len(structure_issues)}")
        print(f"📊 Empty Categories: {len(empty_categories)}")
        print(f"📊 Duplicate Categories: {len(duplicate_categories)}")
        print(f"✅ Structure Score: {structure_score:.2f}%")
        
        return result
        
    def test_7_completeness_verification(self):
        """Test 7: Verify completeness of prequalification data"""
        print("\n🧪 Test 7: Completeness Verification")
        
        # Get all unique firms from IDOT Excel
        all_idot_firms = set()
        for firms in self.idot_prequals.values():
            all_idot_firms.update(firms)
            
        # Get all unique firms from prequal_lookup
        all_lookup_firms = set()
        for category, firms_list in self.prequal_lookup.items():
            if isinstance(firms_list, list):
                for firm_dict in firms_list:
                    if isinstance(firm_dict, dict) and 'firm_name' in firm_dict:
                        all_lookup_firms.add(firm_dict['firm_name'])
                        
        # Normalize for comparison
        all_idot_firms_normalized = {firm.strip().upper() for firm in all_idot_firms}
        all_lookup_firms_normalized = {firm.strip().upper() for firm in all_lookup_firms}
        
        # Calculate coverage
        common_firms = all_idot_firms_normalized.intersection(all_lookup_firms_normalized)
        missing_in_lookup = all_idot_firms_normalized - all_lookup_firms_normalized
        missing_in_idot = all_lookup_firms_normalized - all_idot_firms_normalized
        
        idot_coverage = (len(common_firms) / len(all_idot_firms_normalized)) * 100 if all_idot_firms_normalized else 0
        lookup_coverage = (len(common_firms) / len(all_lookup_firms_normalized)) * 100 if all_lookup_firms_normalized else 0
        
        result = {
            'test_name': 'Completeness Verification',
            'all_idot_firms': len(all_idot_firms_normalized),
            'all_lookup_firms': len(all_lookup_firms_normalized),
            'common_firms': len(common_firms),
            'missing_in_lookup': len(missing_in_lookup),
            'missing_in_idot': len(missing_in_idot),
            'idot_coverage': idot_coverage,
            'lookup_coverage': lookup_coverage,
            'average_coverage': (idot_coverage + lookup_coverage) / 2
        }
        
        print(f"📊 IDOT Firms: {len(all_idot_firms_normalized)}")
        print(f"📊 Lookup Firms: {len(all_lookup_firms_normalized)}")
        print(f"📊 Common Firms: {len(common_firms)}")
        print(f"📊 IDOT Coverage: {idot_coverage:.2f}%")
        print(f"📊 Lookup Coverage: {lookup_coverage:.2f}%")
        print(f"✅ Average Coverage: {result['average_coverage']:.2f}%")
        
        return result
        
    def generate_comprehensive_report(self):
        """Generate comprehensive prequalification verification report"""
        print("\n📋 Generating Prequalification Verification Report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'prequal_lookup_verification_{timestamp}.txt'
        
        with open(report_file, 'w') as f:
            f.write("Prequalification Lookup Verification Report\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Purpose: Verify accuracy of prequal_lookup.json against IDOT Excel\n")
            f.write("Tests Conducted: 7 comprehensive verification tests\n\n")
            
            # Overall results
            accuracies = []
            for result in self.verification_results.values():
                if 'accuracy' in result:
                    accuracies.append(result['accuracy'])
                elif 'structure_score' in result:
                    accuracies.append(result['structure_score'])
                elif 'average_coverage' in result:
                    accuracies.append(result['average_coverage'])
                    
            overall_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
            
            f.write("OVERALL RESULTS\n")
            f.write("-" * 15 + "\n")
            f.write(f"Overall Accuracy: {overall_accuracy:.2f}%\n")
            f.write(f"Tests Completed: {len(self.verification_results)}/7\n\n")
            
            # Individual test results
            f.write("INDIVIDUAL TEST RESULTS\n")
            f.write("-" * 25 + "\n")
            
            for test_name, result in self.verification_results.items():
                f.write(f"{test_name}:\n")
                
                if 'accuracy' in result:
                    f.write(f"  Accuracy: {result['accuracy']:.2f}%\n")
                elif 'structure_score' in result:
                    f.write(f"  Structure Score: {result['structure_score']:.2f}%\n")
                elif 'average_coverage' in result:
                    f.write(f"  Average Coverage: {result['average_coverage']:.2f}%\n")
                    
                if 'match' in result:
                    f.write(f"  Match: {result['match']}\n")
                    
                f.write("\n")
                
            # Critical findings
            f.write("CRITICAL FINDINGS\n")
            f.write("-" * 18 + "\n")
            
            for test_name, result in self.verification_results.items():
                if test_name == 'Category Count Verification':
                    if result.get('match'):
                        f.write("✅ Category count matches between lookup and IDOT Excel\n")
                    else:
                        f.write("❌ Category count mismatch detected\n")
                        
                if test_name == 'Category Name Exact Match':
                    if result.get('match'):
                        f.write("✅ All category names match exactly between lookup and IDOT Excel\n")
                    else:
                        f.write("❌ Category name mismatches detected\n")
                        
            f.write("\nVERIFICATION CONCLUSION\n")
            f.write("-" * 25 + "\n")
            
            if overall_accuracy >= 95:
                f.write("🎉 EXCELLENT: Prequalification data accuracy is very high (95%+)\n")
                f.write("   prequal_lookup.json is highly reliable and matches IDOT Excel\n")
            elif overall_accuracy >= 80:
                f.write("✅ GOOD: Prequalification data accuracy is good (80%+)\n")
                f.write("   Minor issues detected but overall reliable\n")
            elif overall_accuracy >= 60:
                f.write("⚠️  FAIR: Prequalification data accuracy needs improvement (60%+)\n")
                f.write("   Several issues detected that need attention\n")
            else:
                f.write("❌ POOR: Prequalification data accuracy is low (<60%)\n")
                f.write("   Significant issues detected - data needs major fixes\n")
                
        print(f"✅ Prequalification verification report saved: {report_file}")
        return report_file
        
    def run_all_tests(self):
        """Run all prequalification verification tests"""
        print("🚀 Starting Prequalification Lookup Verification (7 Tests)...")
        
        # Load data
        self.load_data_sources()
        
        # Run all tests
        tests = [
            self.test_1_category_count_verification,
            self.test_2_category_name_exact_match,
            self.test_3_firm_count_verification,
            self.test_4_firm_name_verification,
            self.test_5_specific_category_verification,
            self.test_6_data_structure_verification,
            self.test_7_completeness_verification
        ]
        
        for i, test_func in enumerate(tests, 1):
            print(f"\n{'='*60}")
            print(f"🧪 RUNNING TEST {i}/7: {test_func.__name__.replace('_', ' ').title()}")
            print(f"{'='*60}")
            
            try:
                result = test_func()
                self.verification_results[result['test_name']] = result
                print(f"✅ Test {i} completed successfully")
            except Exception as e:
                print(f"❌ Test {i} failed: {str(e)}")
                self.verification_results[f"Test {i}"] = {
                    'test_name': test_func.__name__.replace('_', ' ').title(),
                    'error': str(e),
                    'accuracy': 0.0
                }
                
        # Generate comprehensive report
        self.generate_comprehensive_report()
        
        return self.verification_results

if __name__ == "__main__":
    verifier = PrequalLookupVerification()
    results = verifier.run_all_tests()
