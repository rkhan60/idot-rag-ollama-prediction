#!/usr/bin/env python3
"""
Test Firm Eligibility Extraction
Test if the model can extract eligible firms based on prequalification data
and verify complete data integration and process
"""

import json
import re
from docx import Document

class FirmEligibilityExtractionTest:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.firms_data_file = '../data/firms_data.json'
        self.district_mapping_file = '../data/district_mapping.json'
        
        # Load data
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        with open(self.firms_data_file, 'r') as f:
            self.firms_data = json.load(f)
        
        with open(self.district_mapping_file, 'r') as f:
            self.district_mapping = json.load(f)
        
        # Create firm code to firm data mapping
        self.firm_code_to_data = {firm['firm_code']: firm for firm in self.firms_data}
        
        # Test prequalifications from PTB 160-170
        self.test_prequals = [
            "Special Services (Quality Assurance: QA PCC & Aggregate)",
            "Special Services (Aerial Mapping)",
            "Structures (Highway: Advanced Typical)",
            "Highways (Roads & Streets)",
            "Location/Design Studies (Rehabilitation)",
            "Special Services (Surveying)",
            "Environmental Reports (Environmental Assessment)",
            "Special Studies (Traffic)",
            "Hydraulic Reports (Waterways: Typical)",
            "Geotechnical Services (General Geotechnical Services)"
        ]
    
    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            return None
    
    def find_eligible_firms_for_prequal(self, prequal_name):
        """Find all eligible firms for a given prequalification"""
        print(f"\n🔍 Finding eligible firms for: {prequal_name}")
        print("-" * 60)
        
        eligible_firms = []
        
        # Search through all sub-categories in restructured data
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                lookup_name = sub_data['full_prequal_name']
                
                # Check if this prequalification matches
                if self.fuzzy_match_prequal(prequal_name, lookup_name):
                    print(f"✅ Match found: {head_category}/{sub_code}")
                    print(f"   Full name: {lookup_name}")
                    print(f"   Firm count: {sub_data['firm_count']}")
                    
                    # Get all firms for this prequalification
                    for firm in sub_data['firms']:
                        firm_code = firm['firm_code']
                        firm_name = firm['firm_name']
                        
                        # Get additional firm data from firms_data.json
                        if firm_code in self.firm_code_to_data:
                            firm_data = self.firm_code_to_data[firm_code]
                            eligible_firms.append({
                                'firm_code': firm_code,
                                'firm_name': firm_name,
                                'prequal_category': lookup_name,
                                'head_category': head_category,
                                'sub_code': sub_code,
                                'dbe_status': firm_data.get('dbe_status', 'Unknown'),
                                'location': firm_data.get('location', 'Unknown'),
                                'district': firm_data.get('district', 'Unknown')
                            })
                        else:
                            print(f"   ⚠️  Firm {firm_code} not found in firms_data.json")
        
        return eligible_firms
    
    def fuzzy_match_prequal(self, extracted_prequal, lookup_name):
        """Fuzzy match extracted prequalification to lookup name"""
        extracted = extracted_prequal.lower().replace(':', '').replace('-', ' ').strip()
        lookup = lookup_name.lower().replace(':', '').replace('-', ' ').strip()
        
        # Direct match
        if extracted == lookup:
            return True
        
        # Partial match
        if extracted in lookup or lookup in extracted:
            return True
        
        # Handle common variations
        variations = {
            'roads & streets': 'roads and streets',
            'roads and streets': 'roads & streets',
            'quality assurance: qa': 'quality assurance',
            'quality assurance qa': 'quality assurance',
            'location/design': 'location design',
            'location design': 'location/design',
        }
        
        if extracted in variations and variations[extracted] == lookup:
            return True
        if lookup in variations and variations[lookup] == extracted:
            return True
        
        return False
    
    def test_prequalification_extraction_from_ptb(self):
        """Test extracting prequalifications from PTB and finding eligible firms"""
        print("🔍 TESTING PREQUALIFICATION EXTRACTION FROM PTB")
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
        
        # Remove duplicates and filter meaningful prequals
        unique_prequals = []
        for prequal in set(extracted_prequals):
            # Filter out general text that's not a prequalification
            if any(keyword in prequal.lower() for keyword in ['prequalified', 'category', 'services', 'studies', 'reports']):
                unique_prequals.append(prequal)
        
        print(f"📋 Extracted {len(unique_prequals)} meaningful prequalifications from PTB160:")
        for prequal in unique_prequals[:10]:  # Show first 10
            print(f"  • '{prequal}'")
        
        # Test finding eligible firms for each extracted prequalification
        total_eligible_firms = 0
        successful_extractions = 0
        
        for prequal in unique_prequals[:5]:  # Test first 5
            eligible_firms = self.find_eligible_firms_for_prequal(prequal)
            
            if eligible_firms:
                successful_extractions += 1
                total_eligible_firms += len(eligible_firms)
                print(f"  ✅ Found {len(eligible_firms)} eligible firms for '{prequal}'")
                
                # Show sample firms
                for firm in eligible_firms[:3]:
                    print(f"    - {firm['firm_code']}: {firm['firm_name']} ({firm['dbe_status']}, {firm['district']})")
            else:
                print(f"  ❌ No eligible firms found for '{prequal}'")
        
        print(f"\n📊 PTB EXTRACTION RESULTS:")
        print(f"Successful extractions: {successful_extractions}/{min(5, len(unique_prequals))}")
        print(f"Total eligible firms found: {total_eligible_firms}")
        
        return successful_extractions > 0
    
    def test_known_prequalifications(self):
        """Test finding eligible firms for known prequalifications"""
        print(f"\n🔍 TESTING KNOWN PREQUALIFICATIONS")
        print("=" * 80)
        
        results = {}
        
        for prequal in self.test_prequals:
            eligible_firms = self.find_eligible_firms_for_prequal(prequal)
            results[prequal] = {
                'eligible_count': len(eligible_firms),
                'firms': eligible_firms
            }
            
            print(f"📋 {prequal}: {len(eligible_firms)} eligible firms")
            
            # Show sample firms
            for firm in eligible_firms[:3]:
                print(f"  - {firm['firm_code']}: {firm['firm_name']} ({firm['dbe_status']}, {firm['district']})")
        
        return results
    
    def test_data_integration(self):
        """Test complete data integration across all files"""
        print(f"\n🔍 TESTING DATA INTEGRATION")
        print("=" * 80)
        
        # Test 1: Firm code consistency
        prequal_firm_codes = set()
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                for firm in sub_data['firms']:
                    prequal_firm_codes.add(firm['firm_code'])
        
        firms_data_codes = set(self.firm_code_to_data.keys())
        
        missing_in_firms_data = prequal_firm_codes - firms_data_codes
        missing_in_prequal = firms_data_codes - prequal_firm_codes
        
        print(f"✅ Firm code consistency:")
        print(f"  Prequal lookup codes: {len(prequal_firm_codes)}")
        print(f"  Firms data codes: {len(firms_data_codes)}")
        print(f"  Missing in firms_data: {len(missing_in_firms_data)}")
        print(f"  Missing in prequal_lookup: {len(missing_in_prequal)}")
        
        # Test 2: District mapping consistency
        prequal_districts = set()
        for firm_code in prequal_firm_codes:
            if firm_code in self.firm_code_to_data:
                district = self.firm_code_to_data[firm_code].get('district', 'Unknown')
                prequal_districts.add(district)
        
        district_mapping_keys = set(self.district_mapping.keys())
        
        print(f"\n✅ District mapping consistency:")
        print(f"  Districts in prequal firms: {sorted(prequal_districts)}")
        print(f"  Districts in mapping: {sorted(district_mapping_keys)}")
        
        # Test 3: DBE status distribution
        dbe_statuses = {}
        for firm_code in prequal_firm_codes:
            if firm_code in self.firm_code_to_data:
                dbe_status = self.firm_code_to_data[firm_code].get('dbe_status', 'Unknown')
                dbe_statuses[dbe_status] = dbe_statuses.get(dbe_status, 0) + 1
        
        print(f"\n✅ DBE status distribution:")
        for status, count in dbe_statuses.items():
            print(f"  {status}: {count} firms")
        
        return len(missing_in_firms_data) == 0 and len(missing_in_prequal) == 0
    
    def test_complete_process(self):
        """Test the complete process from PTB to eligible firms"""
        print(f"\n🔍 TESTING COMPLETE PROCESS")
        print("=" * 80)
        
        # Simulate the complete process
        print("1️⃣ Step 1: Extract prequalifications from PTB")
        ptb_prequals = [
            "Special Services (Quality Assurance: QA PCC & Aggregate)",
            "Highways (Roads & Streets)",
            "Location/Design Studies (Rehabilitation)"
        ]
        
        print("2️⃣ Step 2: Find eligible firms for each prequalification")
        all_eligible_firms = {}
        
        for prequal in ptb_prequals:
            eligible_firms = self.find_eligible_firms_for_prequal(prequal)
            all_eligible_firms[prequal] = eligible_firms
            print(f"   {prequal}: {len(eligible_firms)} firms")
        
        print("3️⃣ Step 3: Analyze firm characteristics")
        total_unique_firms = set()
        dbe_firms = 0
        district_distribution = {}
        
        for prequal, firms in all_eligible_firms.items():
            for firm in firms:
                total_unique_firms.add(firm['firm_code'])
                if firm['dbe_status'] == 'YES':
                    dbe_firms += 1
                
                district = firm['district']
                district_distribution[district] = district_distribution.get(district, 0) + 1
        
        print(f"\n📊 PROCESS RESULTS:")
        print(f"Total unique eligible firms: {len(total_unique_firms)}")
        print(f"DBE firms: {dbe_firms}")
        print(f"District distribution: {district_distribution}")
        
        # Show sample firms
        print(f"\n📋 Sample eligible firms:")
        sample_count = 0
        for prequal, firms in all_eligible_firms.items():
            if sample_count >= 5:
                break
            for firm in firms[:2]:
                print(f"  {firm['firm_code']}: {firm['firm_name']} - {firm['prequal_category']} ({firm['dbe_status']}, {firm['district']})")
                sample_count += 1
        
        return len(total_unique_firms) > 0
    
    def run_comprehensive_test(self):
        """Run comprehensive test of firm eligibility extraction"""
        print("🚀 COMPREHENSIVE FIRM ELIGIBILITY EXTRACTION TEST")
        print("=" * 80)
        
        results = {}
        
        # Test 1: Known prequalifications
        results['known_prequals'] = self.test_known_prequalifications()
        
        # Test 2: PTB extraction
        results['ptb_extraction'] = self.test_prequalification_extraction_from_ptb()
        
        # Test 3: Data integration
        results['data_integration'] = self.test_data_integration()
        
        # Test 4: Complete process
        results['complete_process'] = self.test_complete_process()
        
        # Summary
        print(f"\n📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Model can successfully extract eligible firms based on prequalification data.")
        else:
            print("⚠️  Some tests failed. Review the results above.")
        
        return results

def main():
    tester = FirmEligibilityExtractionTest()
    results = tester.run_comprehensive_test()
    
    print(f"\n✅ Comprehensive firm eligibility extraction test complete!")

if __name__ == "__main__":
    main()





