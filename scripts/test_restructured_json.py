#!/usr/bin/env python3
"""
Test Restructured JSON Files
Test if the model can properly use the restructured prequal_lookup.json
"""

import json
import re
from docx import Document

class RestructuredJSONTest:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.firms_data_file = '../data/firms_data.json'
        self.district_mapping_file = '../data/district_mapping.json'
        
        # Load restructured data
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        with open(self.firms_data_file, 'r') as f:
            self.firms_data = json.load(f)
        
        with open(self.district_mapping_file, 'r') as f:
            self.district_mapping = json.load(f)
        
        # Test cases from PTB 160-170
        self.test_cases = [
            "Special Services (Quality Assurance: QA PCC & Aggregate)",
            "Special Services (Aerial Mapping)",
            "(Special Services) Construction Inspection",
            "Structures (Highway: Advanced Typical)",
            "Special Studies [Signal Coordination & Timing (SCAT)]",
            "Highways (Freeways)",
            "Location/Design Studies (Rehabilitation)",
            "Structures – (Highway: Typical)",
            "Hydraulic Reports - Waterways: Typical",
            "Location/ Design Studies (Reconstruction/Major Rehabilitation)"
        ]
    
    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            return None
    
    def test_restructured_lookup_access(self):
        """Test accessing data from restructured lookup"""
        print("🔍 TESTING RESTRUCTURED LOOKUP ACCESS")
        print("=" * 80)
        
        success_count = 0
        total_tests = 0
        
        for head_category, data in self.prequal_lookup.items():
            print(f"\n📋 Testing head category: {head_category} ({data['head_category_code']})")
            
            for sub_code, sub_data in data['sub_categories'].items():
                total_tests += 1
                
                # Test accessing sub-category data
                sub_name = sub_data['sub_category_name']
                full_name = sub_data['full_prequal_name']
                firms = sub_data['firms']
                firm_count = sub_data['firm_count']
                
                print(f"  ✅ {sub_code}: {full_name} ({firm_count} firms)")
                
                # Verify firm data structure
                if firms and len(firms) > 0:
                    first_firm = firms[0]
                    if 'firm_code' in first_firm and 'firm_name' in first_firm:
                        success_count += 1
                    else:
                        print(f"    ❌ Invalid firm data structure: {first_firm}")
                else:
                    print(f"    ⚠️  No firms found for {sub_code}")
        
        print(f"\n📊 LOOKUP ACCESS RESULTS:")
        print(f"Successful tests: {success_count}/{total_tests}")
        print(f"Success rate: {(success_count/total_tests)*100:.1f}%")
        
        return success_count == total_tests
    
    def test_fuzzy_matching_with_restructured_data(self):
        """Test fuzzy matching with restructured data"""
        print(f"\n🔍 TESTING FUZZY MATCHING WITH RESTRUCTURED DATA")
        print("=" * 80)
        
        def fuzzy_match_prequal(extracted_prequal):
            """Fuzzy match extracted prequalification to restructured lookup"""
            extracted = extracted_prequal.lower().replace(':', '').replace('-', ' ').strip()
            
            # Search through all sub-categories in restructured data
            for head_category, data in self.prequal_lookup.items():
                for sub_code, sub_data in data['sub_categories'].items():
                    lookup_name = sub_data['full_prequal_name'].lower().replace(':', '').replace('-', ' ').strip()
                    
                    # Direct match
                    if extracted == lookup_name:
                        return {
                            'matched': True,
                            'head_category': head_category,
                            'sub_code': sub_code,
                            'full_name': sub_data['full_prequal_name'],
                            'firm_count': sub_data['firm_count']
                        }
                    
                    # Partial match
                    if extracted in lookup_name or lookup_name in extracted:
                        return {
                            'matched': True,
                            'head_category': head_category,
                            'sub_code': sub_code,
                            'full_name': sub_data['full_prequal_name'],
                            'firm_count': sub_data['firm_count']
                        }
                    
                    # Handle common variations
                    variations = {
                        'roads & streets': 'roads and streets',
                        'roads and streets': 'roads & streets',
                        'quality assurance: qa': 'quality assurance',
                        'quality assurance qa': 'quality assurance',
                        'location/design': 'location design',
                        'location design': 'location/design',
                    }
                    
                    if extracted in variations and variations[extracted] == lookup_name:
                        return {
                            'matched': True,
                            'head_category': head_category,
                            'sub_code': sub_code,
                            'full_name': sub_data['full_prequal_name'],
                            'firm_count': sub_data['firm_count']
                        }
            
            return {'matched': False, 'extracted': extracted_prequal}
        
        # Test each case
        success_count = 0
        total_tests = len(self.test_cases)
        
        for test_case in self.test_cases:
            result = fuzzy_match_prequal(test_case)
            
            if result['matched']:
                print(f"✅ '{test_case}' → {result['head_category']}/{result['sub_code']} ({result['firm_count']} firms)")
                success_count += 1
            else:
                print(f"❌ '{test_case}' → No match found")
        
        print(f"\n📊 FUZZY MATCHING RESULTS:")
        print(f"Successful matches: {success_count}/{total_tests}")
        print(f"Success rate: {(success_count/total_tests)*100:.1f}%")
        
        return success_count == total_tests
    
    def test_ptb_extraction_with_restructured_data(self):
        """Test PTB extraction with restructured data"""
        print(f"\n🔍 TESTING PTB EXTRACTION WITH RESTRUCTURED DATA")
        print("=" * 80)
        
        # Test with PTB160
        ptb_file = "../data/ptb160.docx"
        ptb_text = self.extract_text_from_docx(ptb_file)
        
        if not ptb_text:
            print("❌ Could not extract text from PTB160")
            return False
        
        # Extract prequalifications from PTB
        prequal_patterns = [
            r'prequalified in the\s*(.*?)\s*category',
            r'prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|\Z)',
            r'must be prequalified in the\s*(.*?)\s*category',
            r'must be prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|\Z)',
        ]
        
        extracted_prequals = []
        
        for pattern in prequal_patterns:
            matches = re.findall(pattern, ptb_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str):
                    if ',' in match:
                        for cat in match.split(','):
                            clean_cat = cat.strip()
                            if clean_cat and len(clean_cat) > 5:
                                extracted_prequals.append(clean_cat)
                    else:
                        clean_cat = match.strip()
                        if clean_cat and len(clean_cat) > 5:
                            extracted_prequals.append(clean_cat)
        
        # Remove duplicates
        unique_prequals = list(set(extracted_prequals))
        
        print(f"📋 Extracted {len(unique_prequals)} unique prequalifications from PTB160:")
        for prequal in unique_prequals:
            print(f"  • '{prequal}'")
        
        # Test matching with restructured data
        def match_extracted_prequal(extracted_prequal):
            extracted = extracted_prequal.lower().replace(':', '').replace('-', ' ').strip()
            
            for head_category, data in self.prequal_lookup.items():
                for sub_code, sub_data in data['sub_categories'].items():
                    lookup_name = sub_data['full_prequal_name'].lower().replace(':', '').replace('-', ' ').strip()
                    
                    if extracted == lookup_name or extracted in lookup_name or lookup_name in extracted:
                        return {
                            'matched': True,
                            'head_category': head_category,
                            'sub_code': sub_code,
                            'full_name': sub_data['full_prequal_name'],
                            'firm_count': sub_data['firm_count']
                        }
            
            return {'matched': False, 'extracted': extracted_prequal}
        
        # Test each extracted prequal
        ptb_success_count = 0
        ptb_total_tests = len(unique_prequals)
        
        print(f"\n🔍 Matching extracted prequals with restructured data:")
        for prequal in unique_prequals:
            result = match_extracted_prequal(prequal)
            
            if result['matched']:
                print(f"✅ '{prequal}' → {result['head_category']}/{result['sub_code']} ({result['firm_count']} firms)")
                ptb_success_count += 1
            else:
                print(f"❌ '{prequal}' → No match found")
        
        print(f"\n📊 PTB EXTRACTION RESULTS:")
        print(f"Successful matches: {ptb_success_count}/{ptb_total_tests}")
        print(f"Success rate: {(ptb_success_count/ptb_total_tests)*100:.1f}%")
        
        return ptb_success_count > 0
    
    def test_data_integrity(self):
        """Test data integrity across all JSON files"""
        print(f"\n🔍 TESTING DATA INTEGRITY")
        print("=" * 80)
        
        # Test firms_data.json
        firms_count = len(self.firms_data)
        print(f"✅ firms_data.json: {firms_count} firms")
        
        # Test district_mapping.json
        districts_count = len(self.district_mapping)
        print(f"✅ district_mapping.json: {districts_count} districts")
        
        # Test prequal_lookup.json structure
        head_categories = len(self.prequal_lookup)
        total_sub_categories = sum(len(data['sub_categories']) for data in self.prequal_lookup.values())
        total_firms = sum(sum(sub_data['firm_count'] for sub_data in data['sub_categories'].values()) 
                         for data in self.prequal_lookup.values())
        
        print(f"✅ prequal_lookup.json: {head_categories} head categories, {total_sub_categories} sub-categories, {total_firms} total firms")
        
        # Verify firm codes consistency
        all_firm_codes = set()
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                for firm in sub_data['firms']:
                    all_firm_codes.add(firm['firm_code'])
        
        print(f"✅ Unique firm codes in prequal_lookup: {len(all_firm_codes)}")
        
        # Check if all firm codes exist in firms_data (firms_data is a list of dicts)
        firms_data_codes = set(firm['firm_code'] for firm in self.firms_data)
        missing_codes = all_firm_codes - firms_data_codes
        
        if missing_codes:
            print(f"❌ Missing firm codes in firms_data: {len(missing_codes)}")
            print(f"   Examples: {list(missing_codes)[:5]}")
        else:
            print(f"✅ All firm codes in prequal_lookup exist in firms_data")
        
        return len(missing_codes) == 0
    
    def run_comprehensive_test(self):
        """Run comprehensive test of restructured JSON files"""
        print("🚀 COMPREHENSIVE TEST OF RESTRUCTURED JSON FILES")
        print("=" * 80)
        
        results = {}
        
        # Test 1: Restructured lookup access
        results['lookup_access'] = self.test_restructured_lookup_access()
        
        # Test 2: Fuzzy matching
        results['fuzzy_matching'] = self.test_fuzzy_matching_with_restructured_data()
        
        # Test 3: PTB extraction
        results['ptb_extraction'] = self.test_ptb_extraction_with_restructured_data()
        
        # Test 4: Data integrity
        results['data_integrity'] = self.test_data_integrity()
        
        # Summary
        print(f"\n📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        passed_tests = sum(results.values())
        total_tests = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Model can properly use restructured JSON files.")
        else:
            print("⚠️  Some tests failed. Review the results above.")
        
        return results

def main():
    tester = RestructuredJSONTest()
    results = tester.run_comprehensive_test()
    
    print(f"\n✅ Comprehensive test complete!")

if __name__ == "__main__":
    main()
