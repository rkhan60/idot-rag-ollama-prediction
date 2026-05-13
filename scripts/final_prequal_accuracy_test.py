#!/usr/bin/env python3
"""
Final Prequalification Accuracy Test
Compare prequal_lookup.json with firms_data.json to verify accuracy
"""

import json
from collections import defaultdict

class FinalPrequalAccuracyTest:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.firms_data_file = '../data/firms_data.json'
        
        # Load data
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        with open(self.firms_data_file, 'r') as f:
            self.firms_data = json.load(f)
        
        # Create mappings
        self.firm_code_to_data = {firm['firm_code']: firm for firm in self.firms_data}
        
        # Results storage
        self.results = {
            'total_firms_checked': 0,
            'correct_assignments': 0,
            'missing_firms': 0,
            'incorrect_assignments': 0,
            'missing_prequals': 0,
            'extra_prequals': 0,
            'detailed_issues': []
        }
    
    def normalize_prequal_name(self, prequal_name):
        """Normalize prequalification name for comparison"""
        return prequal_name.lower().replace(':', '').replace('-', ' ').replace('_', ' ').strip()
    
    def fuzzy_match_prequal(self, prequal1, prequal2):
        """Fuzzy match two prequalification names"""
        norm1 = self.normalize_prequal_name(prequal1)
        norm2 = self.normalize_prequal_name(prequal2)
        
        # Direct match
        if norm1 == norm2:
            return True
        
        # Partial match
        if norm1 in norm2 or norm2 in norm1:
            return True
        
        # Handle common variations
        variations = {
            'roads & streets': 'roads and streets',
            'roads and streets': 'roads & streets',
            'quality assurance: qa': 'quality assurance',
            'quality assurance qa': 'quality assurance',
            'location/design': 'location design',
            'location design': 'location/design',
            'special services -': 'special services (',
            'special services(': 'special services (',
        }
        
        if norm1 in variations and variations[norm1] == norm2:
            return True
        if norm2 in variations and variations[norm2] == norm1:
            return True
        
        return False
    
    def test_prequal_lookup_to_firms_data(self):
        """Test: Check if firms in prequal_lookup.json have correct prequals in firms_data.json"""
        print("🔍 TESTING: Prequal Lookup → Firms Data")
        print("=" * 80)
        
        total_checked = 0
        correct_assignments = 0
        incorrect_assignments = 0
        missing_firms = 0
        
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                lookup_prequal_name = sub_data['full_prequal_name']
                
                for firm in sub_data['firms']:
                    firm_code = firm['firm_code']
                    firm_name = firm['firm_name']
                    total_checked += 1
                    
                    # Check if firm exists in firms_data.json
                    if firm_code not in self.firm_code_to_data:
                        missing_firms += 1
                        self.results['detailed_issues'].append({
                            'type': 'missing_firm',
                            'firm_code': firm_code,
                            'firm_name': firm_name,
                            'prequal_category': lookup_prequal_name,
                            'issue': f'Firm {firm_code} not found in firms_data.json'
                        })
                        continue
                    
                    # Get firm's prequalifications from firms_data.json
                    firm_data = self.firm_code_to_data[firm_code]
                    firm_prequals = firm_data.get('prequalifications', [])
                    
                    # Check if the firm has this prequalification
                    has_prequal = False
                    for firm_prequal in firm_prequals:
                        if self.fuzzy_match_prequal(lookup_prequal_name, firm_prequal):
                            has_prequal = True
                            break
                    
                    if has_prequal:
                        correct_assignments += 1
                    else:
                        incorrect_assignments += 1
                        self.results['detailed_issues'].append({
                            'type': 'incorrect_assignment',
                            'firm_code': firm_code,
                            'firm_name': firm_name,
                            'prequal_category': lookup_prequal_name,
                            'firm_prequals': firm_prequals,
                            'issue': f'Firm {firm_code} listed in {lookup_prequal_name} but has prequals: {firm_prequals}'
                        })
        
        print(f"📊 RESULTS:")
        print(f"Total firms checked: {total_checked}")
        print(f"Correct assignments: {correct_assignments}")
        print(f"Incorrect assignments: {incorrect_assignments}")
        print(f"Missing firms: {missing_firms}")
        print(f"Accuracy: {(correct_assignments/total_checked)*100:.1f}%" if total_checked > 0 else "N/A")
        
        self.results['total_firms_checked'] = total_checked
        self.results['correct_assignments'] = correct_assignments
        self.results['incorrect_assignments'] = incorrect_assignments
        self.results['missing_firms'] = missing_firms
        
        return correct_assignments, total_checked
    
    def test_firms_data_to_prequal_lookup(self):
        """Test: Check if firms in firms_data.json appear in correct categories in prequal_lookup.json"""
        print(f"\n🔍 TESTING: Firms Data → Prequal Lookup")
        print("=" * 80)
        
        total_checked = 0
        correct_assignments = 0
        missing_prequals = 0
        extra_prequals = 0
        
        # Create reverse mapping from prequal_lookup
        prequal_to_firms = defaultdict(set)
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                prequal_name = sub_data['full_prequal_name']
                for firm in sub_data['firms']:
                    prequal_to_firms[prequal_name].add(firm['firm_code'])
        
        for firm in self.firms_data:
            firm_code = firm['firm_code']
            firm_name = firm['firm_name']
            firm_prequals = firm.get('prequalifications', [])
            
            for firm_prequal in firm_prequals:
                total_checked += 1
                
                # Check if this firm appears in the corresponding prequal category
                found_in_lookup = False
                for lookup_prequal, firm_codes in prequal_to_firms.items():
                    if self.fuzzy_match_prequal(firm_prequal, lookup_prequal):
                        if firm_code in firm_codes:
                            found_in_lookup = True
                            correct_assignments += 1
                            break
                
                if not found_in_lookup:
                    missing_prequals += 1
                    self.results['detailed_issues'].append({
                        'type': 'missing_prequal',
                        'firm_code': firm_code,
                        'firm_name': firm_name,
                        'firm_prequal': firm_prequal,
                        'issue': f'Firm {firm_code} has prequal {firm_prequal} but not found in prequal_lookup.json'
                    })
        
        print(f"📊 RESULTS:")
        print(f"Total prequalifications checked: {total_checked}")
        print(f"Correct assignments: {correct_assignments}")
        print(f"Missing prequalifications: {missing_prequals}")
        print(f"Accuracy: {(correct_assignments/total_checked)*100:.1f}%" if total_checked > 0 else "N/A")
        
        self.results['missing_prequals'] = missing_prequals
        
        return correct_assignments, total_checked
    
    def analyze_prequalification_coverage(self):
        """Analyze prequalification coverage and distribution"""
        print(f"\n🔍 ANALYZING PREQUALIFICATION COVERAGE")
        print("=" * 80)
        
        # Count prequalifications in firms_data.json
        firms_data_prequals = defaultdict(int)
        for firm in self.firms_data:
            for prequal in firm.get('prequalifications', []):
                firms_data_prequals[prequal] += 1
        
        # Count prequalifications in prequal_lookup.json
        lookup_prequals = defaultdict(int)
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                prequal_name = sub_data['full_prequal_name']
                lookup_prequals[prequal_name] = sub_data['firm_count']
        
        print(f"📋 PREQUALIFICATION COMPARISON:")
        print(f"Prequalifications in firms_data.json: {len(firms_data_prequals)}")
        print(f"Prequalifications in prequal_lookup.json: {len(lookup_prequals)}")
        
        # Show top prequalifications
        print(f"\n📊 TOP PREQUALIFICATIONS (firms_data.json):")
        sorted_firms_data = sorted(firms_data_prequals.items(), key=lambda x: x[1], reverse=True)
        for prequal, count in sorted_firms_data[:10]:
            print(f"  {prequal}: {count} firms")
        
        print(f"\n📊 TOP PREQUALIFICATIONS (prequal_lookup.json):")
        sorted_lookup = sorted(lookup_prequals.items(), key=lambda x: x[1], reverse=True)
        for prequal, count in sorted_lookup[:10]:
            print(f"  {prequal}: {count} firms")
        
        # Find mismatches
        print(f"\n🔍 PREQUALIFICATION MISMATCHES:")
        firms_data_set = set(firms_data_prequals.keys())
        lookup_set = set(lookup_prequals.keys())
        
        only_in_firms_data = firms_data_set - lookup_set
        only_in_lookup = lookup_set - firms_data_set
        
        if only_in_firms_data:
            print(f"Only in firms_data.json ({len(only_in_firms_data)}):")
            for prequal in sorted(only_in_firms_data)[:5]:
                print(f"  • {prequal}")
        
        if only_in_lookup:
            print(f"Only in prequal_lookup.json ({len(only_in_lookup)}):")
            for prequal in sorted(only_in_lookup)[:5]:
                print(f"  • {prequal}")
    
    def generate_detailed_report(self):
        """Generate detailed report of issues found"""
        print(f"\n📋 DETAILED ISSUES REPORT")
        print("=" * 80)
        
        if not self.results['detailed_issues']:
            print("✅ No issues found!")
            return
        
        # Group issues by type
        issues_by_type = defaultdict(list)
        for issue in self.results['detailed_issues']:
            issues_by_type[issue['type']].append(issue)
        
        for issue_type, issues in issues_by_type.items():
            print(f"\n🔍 {issue_type.upper().replace('_', ' ')} ({len(issues)} issues):")
            for issue in issues[:5]:  # Show first 5
                print(f"  • {issue['issue']}")
            if len(issues) > 5:
                print(f"  ... and {len(issues) - 5} more")
    
    def run_comprehensive_test(self):
        """Run comprehensive accuracy test"""
        print("🚀 FINAL PREQUALIFICATION ACCURACY TEST")
        print("=" * 80)
        
        # Test 1: Prequal Lookup → Firms Data
        correct1, total1 = self.test_prequal_lookup_to_firms_data()
        
        # Test 2: Firms Data → Prequal Lookup
        correct2, total2 = self.test_firms_data_to_prequal_lookup()
        
        # Test 3: Coverage Analysis
        self.analyze_prequalification_coverage()
        
        # Generate detailed report
        self.generate_detailed_report()
        
        # Final summary
        print(f"\n📊 FINAL ACCURACY SUMMARY")
        print("=" * 80)
        
        total_correct = correct1 + correct2
        total_checked = total1 + total2
        
        print(f"Overall Accuracy: {(total_correct/total_checked)*100:.1f}%" if total_checked > 0 else "N/A")
        print(f"Total Correct Assignments: {total_correct}")
        print(f"Total Assignments Checked: {total_checked}")
        print(f"Total Issues Found: {len(self.results['detailed_issues'])}")
        
        if total_checked > 0 and (total_correct/total_checked) >= 0.95:
            print("🎉 EXCELLENT ACCURACY! Prequalification data is highly consistent.")
        elif total_checked > 0 and (total_correct/total_checked) >= 0.90:
            print("✅ GOOD ACCURACY! Prequalification data is mostly consistent.")
        else:
            print("⚠️  ACCURACY ISSUES DETECTED! Review the detailed report above.")
        
        return self.results

def main():
    tester = FinalPrequalAccuracyTest()
    results = tester.run_comprehensive_test()
    
    print(f"\n✅ Final prequalification accuracy test complete!")

if __name__ == "__main__":
    main()





