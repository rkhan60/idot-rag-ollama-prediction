#!/usr/bin/env python3
"""
Precise Spelling Analysis
Identify exact spelling differences between bulletin format and lookup format
"""

import json
import re
from docx import Document

class PreciseSpellingAnalysis:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        
        # Load current lookup
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        # Results storage
        self.spelling_differences = []
        self.actual_missing = []
        
    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"❌ Error extracting text from {file_path}: {e}")
            return None
    
    def find_exact_spelling_matches(self, bulletin_text, lookup_categories):
        """Find exact spelling matches between bulletin text and lookup categories"""
        matches = []
        
        for lookup_category in lookup_categories:
            if bulletin_text == lookup_category:
                matches.append(lookup_category)
            elif bulletin_text.lower() == lookup_category.lower():
                matches.append(lookup_category)
        
        return matches
    
    def find_similar_spelling_matches(self, bulletin_text, lookup_categories):
        """Find similar spelling matches (minor differences)"""
        similar_matches = []
        
        bulletin_lower = bulletin_text.lower()
        
        for lookup_category in lookup_categories:
            lookup_lower = lookup_category.lower()
            
            # Check for minor differences
            if self.is_similar_spelling(bulletin_lower, lookup_lower):
                similar_matches.append(lookup_category)
        
        return similar_matches
    
    def is_similar_spelling(self, text1, text2):
        """Check if two texts are similar with minor spelling differences"""
        # Remove common punctuation and normalize
        text1_clean = re.sub(r'[^\w\s]', '', text1).strip()
        text2_clean = re.sub(r'[^\w\s]', '', text2).strip()
        
        # Direct match after cleaning
        if text1_clean == text2_clean:
            return True
        
        # Check for common variations
        variations = {
            'roads & streets': 'roads and streets',
            'roads and streets': 'roads & streets',
            'location/design': 'location design',
            'location design': 'location/design',
            'highways freeways': 'highways (freeways)',
            'highways (freeways)': 'highways freeways',
            'structures highway': 'structures (highway',
            'structures (highway': 'structures highway',
        }
        
        if text1_clean in variations and variations[text1_clean] == text2_clean:
            return True
        if text2_clean in variations and variations[text2_clean] == text1_clean:
            return True
        
        # Check for word-by-word similarity (90%+ match)
        words1 = set(text1_clean.split())
        words2 = set(text2_clean.split())
        
        if len(words1) > 0 and len(words2) > 0:
            common_words = words1.intersection(words2)
            similarity = len(common_words) / max(len(words1), len(words2))
            if similarity >= 0.8:  # 80% word similarity
                return True
        
        return False
    
    def analyze_bulletin_prequals(self, ptb_number):
        """Analyze prequalifications in a specific PTB for spelling differences"""
        print(f"\n🔍 ANALYZING PTB{ptb_number} FOR SPELLING DIFFERENCES")
        print("=" * 80)
        
        # Check if file exists
        ptb_file = f"ptb{ptb_number}.docx"
        ptb_path = f"../data/{ptb_file}"
        
        try:
            ptb_text = self.extract_text_from_docx(ptb_path)
        except:
            print(f"❌ PTB{ptb_number}: File not found")
            return []
        
        if not ptb_text:
            print(f"❌ PTB{ptb_number}: Failed to extract text")
            return []
        
        # Extract prequalifications from bulletin
        prequal_patterns = [
            r'prequalified in the\s*(.*?)\s*category',
            r'prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|\Z)',
            r'must be prequalified in the\s*(.*?)\s*category',
            r'must be prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|\Z)',
        ]
        
        bulletin_prequals = []
        
        for pattern in prequal_patterns:
            matches = re.findall(pattern, ptb_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str):
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
                    categories_text = match
                    for line in categories_text.split('\n'):
                        clean_category = re.sub(r'^\s*[-•]\s*', '', line.strip())
                        if clean_category and len(clean_category) > 5:
                            bulletin_prequals.append(clean_category)
        
        # Remove duplicates
        unique_bulletin_prequals = []
        for prequal in bulletin_prequals:
            if prequal not in unique_bulletin_prequals:
                unique_bulletin_prequals.append(prequal)
        
        print(f"📋 Found {len(unique_bulletin_prequals)} unique prequalifications in PTB{ptb_number}")
        
        # Analyze each prequalification
        for bulletin_prequal in unique_bulletin_prequals:
            print(f"\n🔍 Analyzing: '{bulletin_prequal}'")
            
            # Check for exact matches
            exact_matches = self.find_exact_spelling_matches(bulletin_prequal, self.prequal_lookup.keys())
            if exact_matches:
                print(f"  ✅ Exact match: {exact_matches}")
                continue
            
            # Check for similar matches
            similar_matches = self.find_similar_spelling_matches(bulletin_prequal, self.prequal_lookup.keys())
            if similar_matches:
                print(f"  🔄 Similar matches: {similar_matches}")
                self.spelling_differences.append({
                    'ptb': ptb_number,
                    'bulletin_format': bulletin_prequal,
                    'lookup_matches': similar_matches,
                    'type': 'spelling_difference'
                })
            else:
                print(f"  ❌ No matches found")
                self.actual_missing.append({
                    'ptb': ptb_number,
                    'bulletin_format': bulletin_prequal,
                    'type': 'actually_missing'
                })
        
        return unique_bulletin_prequals
    
    def run_precise_analysis(self):
        """Run precise spelling analysis on all PTBs"""
        print("🚀 PRECISE SPELLING ANALYSIS")
        print("=" * 80)
        
        all_bulletin_prequals = []
        
        # Analyze PTB 160-170
        for ptb_number in range(160, 171):
            bulletin_prequals = self.analyze_bulletin_prequals(ptb_number)
            if bulletin_prequals:
                all_bulletin_prequals.extend(bulletin_prequals)
        
        # Generate summary
        print(f"\n📊 PRECISE ANALYSIS SUMMARY")
        print("=" * 80)
        
        print(f"Total bulletin prequalifications found: {len(all_bulletin_prequals)}")
        print(f"Spelling differences found: {len(self.spelling_differences)}")
        print(f"Actually missing categories: {len(self.actual_missing)}")
        
        print(f"\n🔍 SPELLING DIFFERENCES ({len(self.spelling_differences)}):")
        for diff in self.spelling_differences:
            print(f"PTB{diff['ptb']}: '{diff['bulletin_format']}' → {diff['lookup_matches']}")
        
        print(f"\n❌ ACTUALLY MISSING ({len(self.actual_missing)}):")
        for missing in self.actual_missing:
            print(f"PTB{missing['ptb']}: '{missing['bulletin_format']}'")
        
        # Group spelling differences by type
        print(f"\n📋 SPELLING DIFFERENCE TYPES:")
        difference_types = {}
        for diff in self.spelling_differences:
            bulletin = diff['bulletin_format']
            lookup = diff['lookup_matches'][0] if diff['lookup_matches'] else 'None'
            
            # Identify the type of difference
            if '[' in bulletin and '(' in lookup:
                diff_type = 'brackets_vs_parentheses'
            elif '/' in bulletin and ' ' in lookup:
                diff_type = 'slash_vs_space'
            elif ':' in bulletin and '-' in lookup:
                diff_type = 'colon_vs_hyphen'
            elif '–' in bulletin and '-' in lookup:
                diff_type = 'dash_vs_hyphen'
            elif '  ' in bulletin and ' ' in lookup:
                diff_type = 'extra_spaces'
            elif '&' in bulletin and 'and' in lookup:
                diff_type = 'ampersand_vs_and'
            else:
                diff_type = 'other'
            
            if diff_type not in difference_types:
                difference_types[diff_type] = []
            difference_types[diff_type].append((bulletin, lookup))
        
        for diff_type, examples in difference_types.items():
            print(f"\n• {diff_type} ({len(examples)} examples):")
            for bulletin, lookup in examples[:3]:  # Show first 3 examples
                print(f"  '{bulletin}' vs '{lookup}'")
        
        return {
            'spelling_differences': self.spelling_differences,
            'actual_missing': self.actual_missing,
            'difference_types': difference_types
        }

def main():
    analyzer = PreciseSpellingAnalysis()
    results = analyzer.run_precise_analysis()
    
    print(f"\n✅ Precise spelling analysis complete!")
    print(f"📋 Focus on spelling differences rather than missing categories.")

if __name__ == "__main__":
    main()





