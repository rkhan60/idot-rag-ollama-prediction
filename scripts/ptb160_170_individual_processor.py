#!/usr/bin/env python3
"""
PTB 160-170 Individual Processor
Process each PTB file individually and analyze results for refinement
"""

import os
import json
import pandas as pd
from datetime import datetime
from docx import Document
import re

class PTB160170IndividualProcessor:
    def __init__(self):
        self.ptb_directory = '../data/'
        self.award_file = '../data/award.xlsx'
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.output_directory = '../data/ptb160_170_results/'
        
        # Create output directory
        os.makedirs(self.output_directory, exist_ok=True)
        
        # Load data
        self.award_df = pd.read_excel(self.award_file)
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        # Results tracking
        self.results = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
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
            start_pos = start_match.start()
            
            # Find the next end marker after this start
            end_pos = len(ptb_text)
            for end_match in end_matches:
                if end_match.start() > start_pos:
                    end_pos = end_match.end()
                    break
            
            # Extract project text
            project_text = ptb_text[start_pos:end_pos].strip()
            
            # Extract prequalifications
            prequalifications = self.extract_prequalifications_from_project(project_text)
            
            projects.append({
                'job_number': job_number,
                'project_description': project_description,
                'project_text': project_text,
                'prequalifications': prequalifications
            })
        
        return projects
    
    def extract_prequalifications_from_project(self, project_text):
        """Extract prequalifications from project text"""
        prequalifications = []
        
        # Pattern 1: Single category
        match_single = re.search(r'prequalified in the\s*(.*?)\s*category', project_text, re.IGNORECASE | re.DOTALL)
        if match_single:
            extracted_category = match_single.group(1).strip()
            if ',' in extracted_category:
                for cat in extracted_category.split(','):
                    prequalifications.append(cat.strip())
            else:
                prequalifications.append(extracted_category)
        
        # Pattern 2: Multiple categories
        match_multiple = re.search(r'prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|\Z)', project_text, re.IGNORECASE)
        if match_multiple:
            categories_text = match_multiple.group(1)
            for line in categories_text.split('\n'):
                clean_category = re.sub(r'^\s*[-•]\s*', '', line.strip())
                if clean_category:
                    prequalifications.append(clean_category)
        
        # Validate and match with lookup
        validated_prequals = []
        for prequal in prequalifications:
            matched = self.fuzzy_match_prequal(prequal)
            if matched:
                validated_prequals.append(matched)
        
        return list(set(validated_prequals))
    
    def fuzzy_match_prequal(self, extracted_prequal):
        """Fuzzy match extracted prequalification to lookup category"""
        # Normalize both strings
        extracted = extracted_prequal.lower().replace(':', '').replace('-', ' ').strip()
        
        # Direct match
        if extracted_prequal in self.prequal_lookup:
            return extracted_prequal
        
        # Try normalized match
        for lookup_category in self.prequal_lookup.keys():
            lookup = lookup_category.lower().replace(':', '').replace('-', ' ').strip()
            
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
        print(f"\n🔍 PROCESSING PTB{ptb_number}")
        print("=" * 60)
        
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
        
        print(f"📋 Found {len(projects)} projects")
        
        # Analyze each project
        project_results = []
        for i, project in enumerate(projects, 1):
            job_number = project['job_number']
            prequalifications = project['prequalifications']
            
            print(f"  {i}. Job {job_number}: {len(prequalifications)} prequals")
            if prequalifications:
                for prequal in prequalifications:
                    print(f"     • {prequal}")
            
            project_results.append({
                'job_number': job_number,
                'project_description': project['project_description'],
                'prequalifications': prequalifications,
                'prequal_count': len(prequalifications)
            })
        
        # Calculate statistics
        total_projects = len(projects)
        projects_with_prequals = sum(1 for p in projects if p['prequalifications'])
        total_prequals = sum(len(p['prequalifications']) for p in projects)
        
        # Match with award data
        award_matches = []
        award_job_numbers = set(self.award_df['Job #'].dropna().astype(str))
        
        for project in projects:
            job_number = project['job_number']
            if job_number in award_job_numbers:
                award_matches.append(project)
        
        # Store results
        ptb_result = {
            'ptb_number': ptb_number,
            'total_projects': total_projects,
            'projects_with_prequals': projects_with_prequals,
            'total_prequals': total_prequals,
            'award_matches': len(award_matches),
            'success_rate': (projects_with_prequals / total_projects * 100) if total_projects > 0 else 0,
            'projects': project_results
        }
        
        self.results[ptb_number] = ptb_result
        
        # Print summary
        print(f"\n📊 PTB{ptb_number} SUMMARY:")
        print(f"  • Total Projects: {total_projects}")
        print(f"  • Projects with Prequals: {projects_with_prequals}")
        print(f"  • Total Prequalifications: {total_prequals}")
        print(f"  • Award Matches: {len(award_matches)}")
        print(f"  • Success Rate: {ptb_result['success_rate']:.1f}%")
        
        return ptb_result
    
    def process_range(self, start=160, end=170):
        """Process PTB range"""
        print(f"🚀 PROCESSING PTB {start}-{end}")
        print("=" * 80)
        
        for ptb_number in range(start, end + 1):
            if ptb_number == 164:  # Skip missing PTB164
                print(f"\n⏭️  SKIPPING PTB{ptb_number} (missing)")
                continue
            
            result = self.process_single_ptb(ptb_number)
            if result:
                # Save individual result
                result_file = os.path.join(self.output_directory, f"ptb{ptb_number}_result.json")
                with open(result_file, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate summary report"""
        print(f"\n📊 GENERATING SUMMARY REPORT")
        print("=" * 80)
        
        summary = {
            'timestamp': self.timestamp,
            'total_ptbs_processed': len(self.results),
            'ptb_results': self.results,
            'overall_stats': {
                'total_projects': sum(r['total_projects'] for r in self.results.values()),
                'total_projects_with_prequals': sum(r['projects_with_prequals'] for r in self.results.values()),
                'total_prequalifications': sum(r['total_prequals'] for r in self.results.values()),
                'total_award_matches': sum(r['award_matches'] for r in self.results.values()),
                'average_success_rate': sum(r['success_rate'] for r in self.results.values()) / len(self.results) if self.results else 0
            }
        }
        
        # Save summary
        summary_file = os.path.join(self.output_directory, f"ptb160_170_summary_{self.timestamp}.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Print summary
        stats = summary['overall_stats']
        print(f"📈 OVERALL STATISTICS:")
        print(f"  • PTBs Processed: {summary['total_ptbs_processed']}")
        print(f"  • Total Projects: {stats['total_projects']}")
        print(f"  • Projects with Prequals: {stats['total_projects_with_prequals']}")
        print(f"  • Total Prequalifications: {stats['total_prequalifications']}")
        print(f"  • Award Matches: {stats['total_award_matches']}")
        print(f"  • Average Success Rate: {stats['average_success_rate']:.1f}%")
        
        # Identify issues for refinement
        self.identify_refinement_opportunities()
    
    def identify_refinement_opportunities(self):
        """Identify opportunities for refinement"""
        print(f"\n🔍 REFINEMENT OPPORTUNITIES:")
        print("=" * 80)
        
        issues = []
        
        for ptb_number, result in self.results.items():
            if result['success_rate'] < 100:
                issues.append({
                    'ptb_number': ptb_number,
                    'success_rate': result['success_rate'],
                    'total_projects': result['total_projects'],
                    'projects_with_prequals': result['projects_with_prequals']
                })
        
        if issues:
            print("❌ PTBs with < 100% success rate:")
            for issue in sorted(issues, key=lambda x: x['success_rate']):
                print(f"  • PTB{issue['ptb_number']}: {issue['success_rate']:.1f}% ({issue['projects_with_prequals']}/{issue['total_projects']})")
        else:
            print("✅ All PTBs achieved 100% success rate!")
        
        # Save issues for analysis
        if issues:
            issues_file = os.path.join(self.output_directory, f"refinement_issues_{self.timestamp}.json")
            with open(issues_file, 'w') as f:
                json.dump(issues, f, indent=2, default=str)

def main():
    processor = PTB160170IndividualProcessor()
    processor.process_range(160, 170)

if __name__ == "__main__":
    main()





