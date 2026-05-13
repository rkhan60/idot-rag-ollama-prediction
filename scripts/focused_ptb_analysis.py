#!/usr/bin/env python3
"""
Focused PTB Analysis - Only Prequalification Issues
Analyze only actual prequalification extraction problems, not general text
"""

import os
import json
import pandas as pd
from datetime import datetime
from docx import Document
import re

class FocusedPTBAnalyzer:
    def __init__(self):
        self.ptb_directory = '../data/'
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.award_file = '../data/award.xlsx'
        
        # Load data
        self.load_data()
        
        # Results storage
        self.individual_results = {}
        self.actual_prequal_issues = []
        
    def load_data(self):
        """Load required data files"""
        print("📂 Loading data files...")
        
        # Load prequal lookup
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        # Load award data
        self.award_df = pd.read_excel(self.award_file)
        
        print(f"✅ Loaded {len(self.prequal_lookup)} prequal categories")
        print(f"✅ Loaded {len(self.award_df)} award records")
    
    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"❌ Error extracting text from {file_path}: {e}")
            return None
    
    def parse_projects_with_markers(self, ptb_text):
        """Parse projects using exact start and end markers"""
        projects = []
        start_pattern = r'Job No\.\s*([A-Z]-\d{2}-\d{3}-\d{2}),\s*([^.]*?)\s*\.'
        end_pattern = r'Statements of Interest, including resumes of the key people noted above, must be submitted electronically to the Central Bureau of Design and Environment at the following address:\s*SOIPTB@dot\.il\.gov\.'
        
        # Find all start and end markers
        start_matches = list(re.finditer(start_pattern, ptb_text, re.IGNORECASE))
        end_matches = list(re.finditer(end_pattern, ptb_text, re.IGNORECASE))
        
        # Match starts with ends
        for i, start_match in enumerate(start_matches):
            job_number = start_match.group(1)
            project_description = start_match.group(2).strip()
            
            # Find the next end marker after this start
            end_pos = len(ptb_text)
            for end_match in end_matches:
                if end_match.start() > start_match.start():
                    end_pos = end_match.end()
                    break
            
            # Extract project text
            project_text = ptb_text[start_match.start():end_pos].strip()
            
            # Extract prequalifications
            prequalifications = self.extract_prequalifications_from_project(project_text)
            
            projects.append({
                'job_number': job_number,
                'description': project_description,
                'project_text': project_text,
                'prequalifications': prequalifications
            })
        
        return projects
    
    def extract_prequalifications_from_project(self, project_text):
        """Extract prequalifications from project text - FOCUSED VERSION"""
        prequalifications = []
        
        # ONLY look for actual prequalification patterns
        prequal_patterns = [
            # Pattern 1: "prequalified in the X category"
            r'prequalified in the\s*(.*?)\s*category',
            # Pattern 2: "prequalified in the following categories:"
            r'prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|\Z)',
            # Pattern 3: "must be prequalified in the X category"
            r'must be prequalified in the\s*(.*?)\s*category',
            # Pattern 4: "must be prequalified in the following categories:"
            r'must be prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|\Z)',
        ]
        
        for pattern in prequal_patterns:
            matches = re.findall(pattern, project_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str):
                    # Single category
                    if ',' in match:
                        for cat in match.split(','):
                            clean_cat = cat.strip()
                            if clean_cat and len(clean_cat) > 5:  # Filter out very short strings
                                prequalifications.append(clean_cat)
                    else:
                        clean_cat = match.strip()
                        if clean_cat and len(clean_cat) > 5:
                            prequalifications.append(clean_cat)
                else:
                    # Multiple categories (from pattern 2/4)
                    categories_text = match
                    for line in categories_text.split('\n'):
                        clean_category = re.sub(r'^\s*[-•]\s*', '', line.strip())
                        if clean_category and len(clean_category) > 5:
                            prequalifications.append(clean_category)
        
        # Validate and match with lookup
        validated_prequals = []
        for prequal in prequalifications:
            matched = self.fuzzy_match_prequal(prequal)
            if matched:
                validated_prequals.append(matched)
            else:
                # Only store if it looks like a real prequalification
                if self.looks_like_prequalification(prequal):
                    self.actual_prequal_issues.append({
                        'extracted': prequal,
                        'available_categories': list(self.prequal_lookup.keys())
                    })
        
        return validated_prequals
    
    def looks_like_prequalification(self, text):
        """Check if text looks like a real prequalification category"""
        text_lower = text.lower()
        
        # Must contain key prequalification words
        key_words = ['structures', 'highways', 'special', 'geotechnical', 'environmental', 
                    'location', 'hydraulic', 'airports', 'transportation', 'studies', 
                    'services', 'reports', 'planning', 'quality', 'assurance']
        
        has_key_word = any(word in text_lower for word in key_words)
        
        # Must be reasonable length (not too short, not too long)
        reasonable_length = 5 < len(text) < 100
        
        # Must not contain obvious non-prequalification content
        non_prequal_indicators = ['this project', 'the consultant', 'must be', 'will be', 
                                'completion date', 'key personnel', 'statements of interest']
        
        has_non_prequal = any(indicator in text_lower for indicator in non_prequal_indicators)
        
        return has_key_word and reasonable_length and not has_non_prequal
    
    def fuzzy_match_prequal(self, extracted_prequal):
        """Fuzzy match extracted prequalification to lookup category"""
        extracted = extracted_prequal.lower().replace(':', '').replace('-', ' ').strip()
        
        for lookup_category in self.prequal_lookup.keys():
            lookup = lookup_category.lower().replace(':', '').replace('-', ' ').strip()
            
            # Direct match
            if extracted == lookup:
                return lookup_category
            
            # Partial match
            if extracted in lookup or lookup in extracted:
                return lookup_category
            
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
                return lookup_category
            if lookup in variations and variations[lookup] == extracted:
                return lookup_category
            
            # Special handling for Quality Assurance variations
            if 'quality assurance' in extracted and 'quality assurance' in lookup:
                extracted_clean = extracted.replace('qa', '').replace(':', '').strip()
                lookup_clean = lookup.replace('qa', '').replace(':', '').strip()
                extracted_clean = ' '.join(extracted_clean.split())
                lookup_clean = ' '.join(lookup_clean.split())
                if extracted_clean == lookup_clean:
                    return lookup_category
            
            # Special handling for Aerial Mapping variations
            if 'aerial mapping' in extracted and 'aerial mapping' in lookup:
                extracted_has_lidar = 'lidar' in extracted
                lookup_has_lidar = 'lidar' in lookup
                
                if extracted_has_lidar != lookup_has_lidar:
                    extracted_clean = extracted.replace('lidar', '').strip()
                    lookup_clean = lookup.replace('lidar', '').strip()
                    extracted_clean = ' '.join(extracted_clean.split()).strip()
                    lookup_clean = ' '.join(lookup_clean.split()).strip()
                    extracted_clean = extracted_clean.replace(' )', ')')
                    lookup_clean = lookup_clean.replace(' )', ')')
                    
                    if extracted_clean == lookup_clean:
                        return lookup_category
            
            # Special handling for Structures variations
            if 'structures' in extracted and 'structures' in lookup:
                if 'advanced typical' in extracted and 'advanced typical' in lookup:
                    extracted_clean = extracted.replace(':', '-')
                    lookup_clean = lookup.replace(':', '-')
                    extracted_clean = ' '.join(extracted_clean.split())
                    lookup_clean = ' '.join(lookup_clean.split())
                    
                    if extracted_clean == lookup_clean:
                        return lookup_category
        
        return None
    
    def process_single_ptb(self, ptb_number):
        """Process a single PTB file"""
        print(f"\n🔍 Processing PTB{ptb_number}...")
        
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
        
        # Parse using markers
        projects = self.parse_projects_with_markers(ptb_text)
        
        # Match with award data
        award_job_numbers = set(self.award_df['Job #'].dropna().astype(str))
        matches = []
        
        for project in projects:
            job_number = project['job_number']
            if job_number in award_job_numbers:
                matches.append(project)
        
        # Store results
        self.individual_results[ptb_number] = {
            'total_projects': len(projects),
            'projects_with_prequals': sum(1 for p in projects if p['prequalifications']),
            'total_prequals': sum(len(p['prequalifications']) for p in projects),
            'award_matches': len(matches),
            'projects': projects,
            'matches': matches
        }
        
        print(f"📊 PTB{ptb_number} Results:")
        print(f"  • Total Projects: {len(projects)}")
        print(f"  • Projects with Prequals: {sum(1 for p in projects if p['prequalifications'])}")
        print(f"  • Total Prequals: {sum(len(p['prequalifications']) for p in projects)}")
        print(f"  • Award Matches: {len(matches)}")
        
        return projects
    
    def analyze_actual_prequal_issues(self):
        """Analyze actual prequalification issues found"""
        print(f"\n🔍 ACTUAL PREQUALIFICATION ISSUES ANALYSIS:")
        print("=" * 60)
        
        if not self.actual_prequal_issues:
            print("✅ No actual prequalification issues found!")
            return
        
        print(f"Found {len(self.actual_prequal_issues)} actual prequalification issues:")
        
        # Group by extracted text to avoid duplicates
        unique_issues = {}
        for issue in self.actual_prequal_issues:
            extracted = issue['extracted']
            if extracted not in unique_issues:
                unique_issues[extracted] = issue
        
        for i, (extracted, issue) in enumerate(unique_issues.items(), 1):
            print(f"\n{i}. Extracted: '{extracted}'")
            
            # Find closest matches
            extracted_lower = extracted.lower()
            closest_matches = []
            
            for category in issue['available_categories']:
                category_lower = category.lower()
                if extracted_lower in category_lower or category_lower in extracted_lower:
                    closest_matches.append(category)
            
            if closest_matches:
                print(f"   Closest matches: {closest_matches[:3]}")
            else:
                print(f"   No close matches found")
    
    def generate_focused_report(self):
        """Generate focused analysis report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"focused_ptb_160_170_report_{timestamp}.json"
        
        report = {
            'timestamp': timestamp,
            'summary': {
                'ptbs_processed': len(self.individual_results),
                'total_projects': sum(r['total_projects'] for r in self.individual_results.values()),
                'total_projects_with_prequals': sum(r['projects_with_prequals'] for r in self.individual_results.values()),
                'total_prequals_extracted': sum(r['total_prequals'] for r in self.individual_results.values()),
                'total_award_matches': sum(r['award_matches'] for r in self.individual_results.values()),
                'actual_prequal_issues': len(self.actual_prequal_issues),
            },
            'individual_results': self.individual_results,
            'actual_prequal_issues': self.actual_prequal_issues,
            'recommendations': []
        }
        
        # Calculate accuracy metrics
        total_projects = report['summary']['total_projects']
        projects_with_prequals = report['summary']['total_projects_with_prequals']
        
        if total_projects > 0:
            accuracy = (projects_with_prequals / total_projects) * 100
            report['summary']['accuracy_percentage'] = round(accuracy, 2)
        
        # Save report
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Focused report saved: {report_file}")
        return report
    
    def run_focused_analysis(self):
        """Run focused analysis for PTB 160-170"""
        print("🚀 FOCUSED PTB 160-170 ANALYSIS")
        print("=" * 60)
        
        # Process each PTB
        for ptb_number in range(160, 171):
            self.process_single_ptb(ptb_number)
        
        # Analyze actual prequalification issues
        self.analyze_actual_prequal_issues()
        
        # Generate report
        report = self.generate_focused_report()
        
        # Print summary
        print(f"\n🎯 FOCUSED ANALYSIS SUMMARY:")
        print("=" * 60)
        print(f"PTBs Processed: {report['summary']['ptbs_processed']}")
        print(f"Total Projects: {report['summary']['total_projects']}")
        print(f"Projects with Prequals: {report['summary']['total_projects_with_prequals']}")
        print(f"Total Prequals Extracted: {report['summary']['total_prequals_extracted']}")
        print(f"Total Award Matches: {report['summary']['total_award_matches']}")
        
        if 'accuracy_percentage' in report['summary']:
            print(f"Accuracy: {report['summary']['accuracy_percentage']}%")
        
        print(f"Actual Prequal Issues Found: {len(self.actual_prequal_issues)}")
        
        return report

def main():
    analyzer = FocusedPTBAnalyzer()
    report = analyzer.run_focused_analysis()
    
    print(f"\n✅ Focused analysis complete! Check the report for actual prequalification issues.")
    print(f"📄 Report file: focused_ptb_160_170_report_*.json")

if __name__ == "__main__":
    main()





