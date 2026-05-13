#!/usr/bin/env python3
"""
Investigate Remaining Accuracy Issues
Comprehensive analysis of remaining prequalification mismatches
"""

import json
from collections import defaultdict

class RemainingIssuesInvestigator:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.firms_data_file = '../data/firms_data.json'
        
        # Load data
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        with open(self.firms_data_file, 'r') as f:
            self.firms_data = json.load(f)
        
        # Analysis results
        self.analysis = {
            'missing_in_lookup': [],
            'missing_in_firms_data': [],
            'format_differences': [],
            'firms_affected': defaultdict(list),
            'recommendations': []
        }
    
    def extract_all_prequal_names(self):
        """Extract all prequalification names from both files"""
        # From prequal_lookup.json
        lookup_prequals = set()
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                lookup_prequals.add(sub_data['full_prequal_name'])
        
        # From firms_data.json
        firms_data_prequals = set()
        for firm in self.firms_data:
            for prequal in firm.get('prequalifications', []):
                firms_data_prequals.add(prequal)
        
        return lookup_prequals, firms_data_prequals
    
    def normalize_for_comparison(self, text):
        """Normalize text for comparison"""
        return text.lower().replace(':', '').replace('-', ' ').replace('_', ' ').replace('(', '').replace(')', '').strip()
    
    def find_missing_categories(self):
        """Find categories missing in each file"""
        lookup_prequals, firms_data_prequals = self.extract_all_prequal_names()
        
        # Categories in firms_data.json but not in prequal_lookup.json
        missing_in_lookup = firms_data_prequals - lookup_prequals
        
        # Categories in prequal_lookup.json but not in firms_data.json
        missing_in_firms_data = lookup_prequals - firms_data_prequals
        
        self.analysis['missing_in_lookup'] = sorted(missing_in_lookup)
        self.analysis['missing_in_firms_data'] = sorted(missing_in_firms_data)
        
        return missing_in_lookup, missing_in_firms_data
    
    def find_format_differences(self):
        """Find format differences between similar categories"""
        lookup_prequals, firms_data_prequals = self.extract_all_prequal_names()
        
        format_differences = []
        
        # Create normalized mappings
        lookup_normalized = {self.normalize_for_comparison(p): p for p in lookup_prequals}
        firms_normalized = {self.normalize_for_comparison(p): p for p in firms_data_prequals}
        
        # Find similar categories with different formats
        for firms_normal, firms_original in firms_normalized.items():
            for lookup_normal, lookup_original in lookup_normalized.items():
                if firms_normal == lookup_normal and firms_original != lookup_original:
                    format_differences.append({
                        'firms_data_format': firms_original,
                        'lookup_format': lookup_original,
                        'normalized': firms_normal
                    })
        
        self.analysis['format_differences'] = format_differences
        return format_differences
    
    def analyze_firms_affected(self):
        """Analyze which firms are affected by missing categories"""
        missing_in_lookup, _ = self.find_missing_categories()
        
        for firm in self.firms_data:
            firm_code = firm['firm_code']
            firm_name = firm['firm_name']
            firm_prequals = firm.get('prequalifications', [])
            
            affected_prequals = []
            for prequal in firm_prequals:
                if prequal in missing_in_lookup:
                    affected_prequals.append(prequal)
            
            if affected_prequals:
                self.analysis['firms_affected']['missing_in_lookup'].append({
                    'firm_code': firm_code,
                    'firm_name': firm_name,
                    'affected_prequals': affected_prequals
                })
    
    def generate_recommendations(self):
        """Generate recommendations for fixing the issues"""
        recommendations = []
        
        # Recommendation 1: Add missing categories to prequal_lookup.json
        if self.analysis['missing_in_lookup']:
            recommendations.append({
                'type': 'add_to_lookup',
                'title': 'Add Missing Categories to prequal_lookup.json',
                'description': f'Add {len(self.analysis["missing_in_lookup"])} categories that exist in firms_data.json but not in prequal_lookup.json',
                'categories': self.analysis['missing_in_lookup'],
                'impact': f'Affects {len(self.analysis["firms_affected"]["missing_in_lookup"])} firms'
            })
        
        # Recommendation 2: Add missing categories to firms_data.json
        if self.analysis['missing_in_firms_data']:
            recommendations.append({
                'type': 'add_to_firms_data',
                'title': 'Add Missing Categories to firms_data.json',
                'description': f'Add {len(self.analysis["missing_in_firms_data"])} categories that exist in prequal_lookup.json but not in firms_data.json',
                'categories': self.analysis['missing_in_firms_data'],
                'impact': 'Would provide complete coverage of all bulletin categories'
            })
        
        # Recommendation 3: Fix format differences
        if self.analysis['format_differences']:
            recommendations.append({
                'type': 'fix_formats',
                'title': 'Standardize Format Differences',
                'description': f'Fix {len(self.analysis["format_differences"])} format differences between similar categories',
                'differences': self.analysis['format_differences'],
                'impact': 'Would improve matching accuracy'
            })
        
        self.analysis['recommendations'] = recommendations
        return recommendations
    
    def generate_detailed_report(self):
        """Generate comprehensive report"""
        print("🔍 COMPREHENSIVE INVESTIGATION REPORT")
        print("=" * 80)
        
        # Find all issues
        missing_in_lookup, missing_in_firms_data = self.find_missing_categories()
        format_differences = self.find_format_differences()
        self.analyze_firms_affected()
        recommendations = self.generate_recommendations()
        
        # Summary
        print(f"📊 SUMMARY")
        print(f"Categories missing in prequal_lookup.json: {len(missing_in_lookup)}")
        print(f"Categories missing in firms_data.json: {len(missing_in_firms_data)}")
        print(f"Format differences found: {len(format_differences)}")
        print(f"Firms affected by missing categories: {len(self.analysis['firms_affected']['missing_in_lookup'])}")
        print()
        
        # Missing in prequal_lookup.json
        if missing_in_lookup:
            print(f"🔍 CATEGORIES MISSING IN PREQUAL_LOOKUP.JSON ({len(missing_in_lookup)})")
            print("-" * 60)
            for category in missing_in_lookup:
                print(f"• {category}")
            print()
        
        # Missing in firms_data.json
        if missing_in_firms_data:
            print(f"🔍 CATEGORIES MISSING IN FIRMS_DATA.JSON ({len(missing_in_firms_data)})")
            print("-" * 60)
            for category in missing_in_firms_data:
                print(f"• {category}")
            print()
        
        # Format differences
        if format_differences:
            print(f"🔍 FORMAT DIFFERENCES ({len(format_differences)})")
            print("-" * 60)
            for diff in format_differences:
                print(f"• Firms Data: {diff['firms_data_format']}")
                print(f"  Lookup:     {diff['lookup_format']}")
                print()
        
        # Firms affected
        if self.analysis['firms_affected']['missing_in_lookup']:
            print(f"🔍 FIRMS AFFECTED BY MISSING CATEGORIES ({len(self.analysis['firms_affected']['missing_in_lookup'])})")
            print("-" * 60)
            for firm in self.analysis['firms_affected']['missing_in_lookup'][:10]:  # Show first 10
                print(f"• {firm['firm_code']} - {firm['firm_name']}")
                for prequal in firm['affected_prequals']:
                    print(f"  - {prequal}")
            if len(self.analysis['firms_affected']['missing_in_lookup']) > 10:
                print(f"  ... and {len(self.analysis['firms_affected']['missing_in_lookup']) - 10} more firms")
            print()
        
        # Recommendations
        print(f"💡 RECOMMENDATIONS ({len(recommendations)})")
        print("-" * 60)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['title']}")
            print(f"   {rec['description']}")
            print(f"   Impact: {rec['impact']}")
            print()
        
        # Priority analysis
        print(f"🎯 PRIORITY ANALYSIS")
        print("-" * 60)
        
        if missing_in_lookup:
            print(f"🔴 HIGH PRIORITY: Add {len(missing_in_lookup)} categories to prequal_lookup.json")
            print(f"   This will fix {len(self.analysis['firms_affected']['missing_in_lookup'])} firms with missing prequalifications")
        
        if missing_in_firms_data:
            print(f"🟡 MEDIUM PRIORITY: Add {len(missing_in_firms_data)} categories to firms_data.json")
            print(f"   This will provide complete coverage of all bulletin categories")
        
        if format_differences:
            print(f"🟢 LOW PRIORITY: Fix {len(format_differences)} format differences")
            print(f"   This will improve matching accuracy for similar categories")
        
        print()
        print("✅ Investigation complete!")
        
        return self.analysis
    
    def save_report_to_file(self, filename='investigation_report.json'):
        """Save detailed report to JSON file"""
        report_data = {
            'summary': {
                'missing_in_lookup_count': len(self.analysis['missing_in_lookup']),
                'missing_in_firms_data_count': len(self.analysis['missing_in_firms_data']),
                'format_differences_count': len(self.analysis['format_differences']),
                'firms_affected_count': len(self.analysis['firms_affected']['missing_in_lookup'])
            },
            'missing_in_lookup': self.analysis['missing_in_lookup'],
            'missing_in_firms_data': self.analysis['missing_in_firms_data'],
            'format_differences': self.analysis['format_differences'],
            'firms_affected': self.analysis['firms_affected'],
            'recommendations': self.analysis['recommendations']
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 Detailed report saved to: {filename}")

def main():
    investigator = RemainingIssuesInvestigator()
    analysis = investigator.generate_detailed_report()
    investigator.save_report_to_file()

if __name__ == "__main__":
    main()





