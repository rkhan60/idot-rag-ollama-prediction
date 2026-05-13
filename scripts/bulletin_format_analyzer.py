#!/usr/bin/env python3
"""
Bulletin Format Analyzer
Extract exact prequalification text from bulletins and compare with current lookup
"""

import os
import json
import re
from docx import Document

class BulletinFormatAnalyzer:
    def __init__(self):
        self.ptb_directory = '../data/'
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        
        # Load current lookup
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        # Results storage
        self.bulletin_prequals = {}
        self.format_differences = []
        self.missing_from_lookup = []
        
    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"❌ Error extracting text from {file_path}: {e}")
            return None
    
    def extract_bulletin_prequals(self, ptb_text, ptb_number):
        """Extract exact prequalification text from bulletin"""
        print(f"\n🔍 Extracting exact prequalifications from PTB{ptb_number}...")
        
        # Find all prequalification patterns in bulletin
        prequal_patterns = [
            # "prequalified in the X category"
            r'prequalified in the\s*(.*?)\s*category',
            # "prequalified in the following categories:"
            r'prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|\Z)',
            # "must be prequalified in the X category"
            r'must be prequalified in the\s*(.*?)\s*category',
            # "must be prequalified in the following categories:"
            r'must be prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|\Z)',
        ]
        
        bulletin_prequals = []
        
        for pattern in prequal_patterns:
            matches = re.findall(pattern, ptb_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str):
                    # Single category
                    if ',' in match:
                        for cat in match.split(','):
                            clean_cat = cat.strip()
                            if clean_cat and len(clean_cat) > 5:
                                bulletin_prequals.append(clean_cat)
                    else:
                        clean_cat = match.strip()
                        if clean_cat and len(clean_cat) > 5:
                            bulletin_prequals.append(clean_cat)
                else:
                    # Multiple categories
                    categories_text = match
                    for line in categories_text.split('\n'):
                        clean_category = re.sub(r'^\s*[-•]\s*', '', line.strip())
                        if clean_category and len(clean_category) > 5:
                            bulletin_prequals.append(clean_category)
        
        # Remove duplicates while preserving order
        unique_prequals = []
        for prequal in bulletin_prequals:
            if prequal not in unique_prequals:
                unique_prequals.append(prequal)
        
        self.bulletin_prequals[ptb_number] = unique_prequals
        
        print(f"📋 Found {len(unique_prequals)} unique prequalifications in PTB{ptb_number}")
        for i, prequal in enumerate(unique_prequals, 1):
            print(f"  {i}. '{prequal}'")
        
        return unique_prequals
    
    def compare_with_lookup(self, ptb_number, bulletin_prequals):
        """Compare bulletin prequalifications with current lookup"""
        print(f"\n🔍 Comparing PTB{ptb_number} with current lookup...")
        
        for bulletin_prequal in bulletin_prequals:
            # Check if exact match exists
            if bulletin_prequal in self.prequal_lookup:
                print(f"✅ Exact match: '{bulletin_prequal}'")
                continue
            
            # Check for fuzzy matches
            fuzzy_matches = []
            for lookup_category in self.prequal_lookup.keys():
                if self.fuzzy_compare(bulletin_prequal, lookup_category):
                    fuzzy_matches.append(lookup_category)
            
            if fuzzy_matches:
                print(f"🔄 Fuzzy match: '{bulletin_prequal}' → {fuzzy_matches}")
                self.format_differences.append({
                    'ptb': ptb_number,
                    'bulletin_format': bulletin_prequal,
                    'lookup_matches': fuzzy_matches
                })
            else:
                print(f"❌ No match: '{bulletin_prequal}'")
                self.missing_from_lookup.append({
                    'ptb': ptb_number,
                    'bulletin_format': bulletin_prequal
                })
    
    def fuzzy_compare(self, bulletin_text, lookup_text):
        """Fuzzy compare bulletin text with lookup text"""
        bulletin_lower = bulletin_text.lower().replace(':', '').replace('-', ' ').strip()
        lookup_lower = lookup_text.lower().replace(':', '').replace('-', ' ').strip()
        
        # Direct match
        if bulletin_lower == lookup_lower:
            return True
        
        # Partial match
        if bulletin_lower in lookup_lower or lookup_lower in bulletin_lower:
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
        
        if bulletin_lower in variations and variations[bulletin_lower] == lookup_lower:
            return True
        if lookup_lower in variations and variations[lookup_lower] == bulletin_lower:
            return True
        
        return False
    
    def analyze_ptb(self, ptb_number):
        """Analyze a single PTB for bulletin format"""
        print(f"\n🔍 ANALYZING PTB{ptb_number} BULLETIN FORMAT")
        print("=" * 80)
        
        # Check if file exists
        ptb_file = f"ptb{ptb_number}.docx"
        ptb_path = os.path.join(self.ptb_directory, ptb_file)
        
        if not os.path.exists(ptb_path):
            print(f"❌ PTB{ptb_number}: File not found")
            return None
        
        # Extract text from PTB
        ptb_text = self.extract_text_from_docx(ptb_path)
        if not ptb_text:
            print(f"❌ PTB{ptb_number}: Failed to extract text")
            return None
        
        # Extract bulletin prequalifications
        bulletin_prequals = self.extract_bulletin_prequals(ptb_text, ptb_number)
        
        # Compare with lookup
        self.compare_with_lookup(ptb_number, bulletin_prequals)
        
        return bulletin_prequals
    
    def generate_bulletin_analysis_report(self):
        """Generate analysis report"""
        print(f"\n📊 BULLETIN FORMAT ANALYSIS SUMMARY")
        print("=" * 80)
        
        print(f"PTBs Analyzed: {len(self.bulletin_prequals)}")
        
        total_bulletin_prequals = sum(len(prequals) for prequals in self.bulletin_prequals.values())
        print(f"Total Bulletin Prequals Found: {total_bulletin_prequals}")
        
        print(f"\n🔍 FORMAT DIFFERENCES ({len(self.format_differences)}):")
        for diff in self.format_differences:
            print(f"PTB{diff['ptb']}: '{diff['bulletin_format']}' → {diff['lookup_matches']}")
        
        print(f"\n❌ MISSING FROM LOOKUP ({len(self.missing_from_lookup)}):")
        for missing in self.missing_from_lookup:
            print(f"PTB{missing['ptb']}: '{missing['bulletin_format']}'")
        
        # Generate recommendations
        print(f"\n📋 RECOMMENDATIONS:")
        print("=" * 80)
        
        # Group missing prequalifications by similarity
        missing_groups = {}
        for missing in self.missing_from_lookup:
            prequal = missing['bulletin_format']
            # Create a key based on first few words
            key = ' '.join(prequal.split()[:3]).lower()
            if key not in missing_groups:
                missing_groups[key] = []
            missing_groups[key].append(prequal)
        
        print("Missing categories to add to prequal_lookup.json:")
        for key, prequals in missing_groups.items():
            # Use the most common format
            most_common = max(set(prequals), key=prequals.count)
            print(f"  • '{most_common}'")
        
        print(f"\nFormat variations to handle in fuzzy matching:")
        for diff in self.format_differences:
            print(f"  • '{diff['bulletin_format']}' vs '{diff['lookup_matches'][0]}'")
    
    def run_bulletin_analysis(self):
        """Run complete bulletin format analysis"""
        print("🚀 BULLETIN FORMAT ANALYSIS")
        print("=" * 80)
        
        # Analyze PTB 160-170
        for ptb_number in range(160, 171):
            self.analyze_ptb(ptb_number)
        
        # Generate report
        self.generate_bulletin_analysis_report()
        
        return {
            'bulletin_prequals': self.bulletin_prequals,
            'format_differences': self.format_differences,
            'missing_from_lookup': self.missing_from_lookup
        }

def main():
    analyzer = BulletinFormatAnalyzer()
    results = analyzer.run_bulletin_analysis()
    
    print(f"\n✅ Bulletin format analysis complete!")
    print(f"📋 Check the recommendations above for exact bulletin format changes.")

if __name__ == "__main__":
    main()





