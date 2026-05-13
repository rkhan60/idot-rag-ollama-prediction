#!/usr/bin/env python3
"""
Structured Award Processor
Creates new Excel file with specified columns and tests on PTB160
"""

import pandas as pd
import json
import os
import re
from datetime import datetime
from docx import Document
import numpy as np

class StructuredAwardProcessor:
    def __init__(self):
        self.award_file = '../data/award.xlsx'
        self.ptb_directory = '../data/'
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.output_file = '../data/structured_award_data.xlsx'
        self.log_file = f"structured_award_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Load prequalification lookup for validation
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        # Load award data
        self.award_df = pd.read_excel(self.award_file)
        
        # Initialize tracking
        self.processing_stats = {
            'total_ptb_files': 0,
            'processed_ptb_files': 0,
            'total_projects_found': 0,
            'projects_with_prequals': 0,
            'job_number_matches': 0,
            'prequalifications_extracted': 0,
            'validation_errors': 0,
            'missing_ptb_files': []
        }
        
    def log_message(self, message):
        """Log message to file and print"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')
    
    def extract_text_from_docx(self, filepath):
        """Extract text from .docx file"""
        try:
            doc = Document(filepath)
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            return '\n'.join(text)
        except Exception as e:
            self.log_message(f"❌ Error reading {filepath}: {str(e)}")
            return None
    
    def parse_projects_with_markers(self, ptb_text):
        """Parse projects using exact start and end markers"""
        projects = []
        
        # Project start pattern: "Job No. [JOB_NUMBER], [DESCRIPTION]"
        start_pattern = r'Job No\.\s*([A-Z]-\d{2}-\d{3}-\d{2}),\s*([^.]*?)\s*\.'
        
        # Project end pattern: "Statements of Interest, including resumes of the key people noted above, must be submitted electronically to the Central Bureau of Design and Environment at the following address: SOIPTB@dot.il.gov."
        end_pattern = r'Statements of Interest, including resumes of the key people noted above, must be submitted electronically to the Central Bureau of Design and Environment at the following address:\s*SOIPTB@dot\.il\.gov\.'
        
        # Find all project starts
        start_matches = list(re.finditer(start_pattern, ptb_text, re.IGNORECASE))
        
        self.log_message(f"📋 Found {len(start_matches)} project starts")
        
        # Find all project ends
        end_matches = list(re.finditer(end_pattern, ptb_text, re.IGNORECASE))
        
        self.log_message(f"📋 Found {len(end_matches)} project ends")
        
        # Match starts with ends
        for i, start_match in enumerate(start_matches):
            job_number = start_match.group(1)
            description = start_match.group(2)
            start_pos = start_match.start()
            
            # Find the next end marker after this start
            end_pos = len(ptb_text)  # Default to end of text
            for end_match in end_matches:
                if end_match.start() > start_pos:
                    end_pos = end_match.end()
                    break
            
            # Extract project text
            project_text = ptb_text[start_pos:end_pos].strip()
            
            # Extract prequalifications from this project
            prequalifications = self.extract_prequalifications_from_project(project_text)
            
            projects.append({
                'job_number': job_number,
                'description': description,
                'prequalifications': prequalifications,
                'project_text_sample': project_text[:200] + "..." if len(project_text) > 200 else project_text
            })
            
            self.log_message(f"📝 Job {job_number}: {len(prequalifications)} prequals: {prequalifications}")
        
        return projects
    
    def extract_prequalifications_from_project(self, project_text):
        """Extract prequalifications from project text"""
        prequalifications = []
        
        # Look for "prequalified in the" pattern
        prequal_patterns = [
            r'prequalified in the ([^)]*\([^)]*\)[^)]*) category',
            r'prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|$)',
        ]
        
        for pattern in prequal_patterns:
            matches = re.findall(pattern, project_text, re.IGNORECASE)
            if matches:
                for match in matches:
                    if '\n' in match:  # Multiple categories
                        # Split by newlines and clean up
                        categories = [cat.strip() for cat in match.split('\n') if cat.strip()]
                        for category in categories:
                            # Clean up the category name
                            clean_category = re.sub(r'^\s*[-•]\s*', '', category.strip())
                            if clean_category:
                                prequalifications.append(clean_category)
                    else:  # Single category
                        prequalifications.append(match.strip())
                break
        
        # Validate against prequal_lookup
        validated_prequals = []
        for prequal in prequalifications:
            # Try exact match first
            if prequal in self.prequal_lookup:
                validated_prequals.append(prequal)
            else:
                # Try fuzzy matching
                for lookup_category in self.prequal_lookup.keys():
                    if self.fuzzy_match_prequal(prequal, lookup_category):
                        validated_prequals.append(lookup_category)
                        break
        
        return list(set(validated_prequals))  # Remove duplicates
    
    def fuzzy_match_prequal(self, extracted_prequal, lookup_category):
        """Fuzzy match extracted prequalification to lookup category"""
        # Normalize both strings
        extracted = extracted_prequal.lower().replace(':', '').replace('-', ' ').strip()
        lookup = lookup_category.lower().replace(':', '').replace('-', ' ').strip()
        
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
        
        # Special handling for Quality Assurance variations
        if 'quality assurance' in extracted and 'quality assurance' in lookup:
            # Remove "qa" and ":" from extracted
            extracted_clean = extracted.replace('qa', '').replace(':', '').strip()
            lookup_clean = lookup.replace('qa', '').replace(':', '').strip()
            
            # Clean up extra spaces
            extracted_clean = ' '.join(extracted_clean.split())
            lookup_clean = ' '.join(lookup_clean.split())
            
            if extracted_clean == lookup_clean:
                return True
        
        # Special handling for Aerial Mapping variations
        if 'aerial mapping' in extracted and 'aerial mapping' in lookup:
            # Handle missing ": LiDAR" suffix - check if one has "lidar" and the other doesn't
            extracted_has_lidar = 'lidar' in extracted
            lookup_has_lidar = 'lidar' in lookup
            
            if extracted_has_lidar != lookup_has_lidar:
                # Remove "lidar" from both and compare
                extracted_clean = extracted.replace('lidar', '').strip()
                lookup_clean = lookup.replace('lidar', '').strip()
                
                # Clean up extra spaces and remove trailing spaces
                extracted_clean = ' '.join(extracted_clean.split()).strip()
                lookup_clean = ' '.join(lookup_clean.split()).strip()
                
                # Remove trailing spaces before closing parenthesis
                extracted_clean = extracted_clean.replace(' )', ')')
                lookup_clean = lookup_clean.replace(' )', ')')
                
                if extracted_clean == lookup_clean:
                    return True
        
        # Special handling for Structures variations
        if 'structures' in extracted and 'structures' in lookup:
            # Handle ":" vs "-" in "Advanced Typical"
            if 'advanced typical' in extracted and 'advanced typical' in lookup:
                # Normalize both by replacing ":" with "-" and clean up spaces
                extracted_clean = extracted.replace(':', '-')
                lookup_clean = lookup.replace(':', '-')
                
                # Clean up extra spaces
                extracted_clean = ' '.join(extracted_clean.split())
                lookup_clean = ' '.join(lookup_clean.split())
                
                if extracted_clean == lookup_clean:
                    return True
        
        return False
    
    def process_single_ptb(self, ptb_number):
        """Process a single PTB file"""
        self.log_message(f"🔍 Processing PTB{ptb_number}...")
        
        # Check if file exists
        ptb_file = f"ptb{ptb_number}.docx"
        ptb_path = os.path.join(self.ptb_directory, ptb_file)
        
        if not os.path.exists(ptb_path):
            self.log_message(f"❌ PTB{ptb_number}: File not found")
            self.processing_stats['missing_ptb_files'].append(ptb_number)
            return None
        
        # Extract text from PTB
        ptb_text = self.extract_text_from_docx(ptb_path)
        if not ptb_text:
            self.log_message(f"❌ PTB{ptb_number}: Failed to extract text")
            return None
        
        # Parse using markers
        projects = self.parse_projects_with_markers(ptb_text)
        
        # Update statistics
        self.processing_stats['processed_ptb_files'] += 1
        self.processing_stats['total_projects_found'] += len(projects)
        
        projects_with_prequals = sum(1 for p in projects if p['prequalifications'])
        self.processing_stats['projects_with_prequals'] += projects_with_prequals
        self.processing_stats['prequalifications_extracted'] += sum(len(p['prequalifications']) for p in projects)
        
        return projects
    
    def match_job_numbers_to_award(self, all_projects):
        """Match project job numbers to award.xlsx job numbers"""
        self.log_message(f"🔗 Matching job numbers to award data...")
        
        matches = []
        award_job_numbers = set(self.award_df['Job #'].dropna().astype(str))
        
        for project in all_projects:
            ptb_number = project.get('ptb_number', 'Unknown')
            job_number = project['job_number']
            prequalifications = project['prequalifications']
            
            if job_number in award_job_numbers:
                matches.append({
                    'ptb_number': ptb_number,
                    'job_number': job_number,
                    'prequalifications': prequalifications
                })
                self.processing_stats['job_number_matches'] += 1
                self.log_message(f"✅ Match: PTB{ptb_number} Job {job_number} → {len(prequalifications)} prequals")
            else:
                self.log_message(f"❌ No match: PTB{ptb_number} Job {job_number}")
        
        return matches
    
    def format_prequalifications_for_excel(self, prequalifications):
        """Format prequalifications for Excel column"""
        if not prequalifications:
            return ""
        
        formatted = []
        for i, prequal in enumerate(prequalifications, 1):
            formatted.append(f"{i}.{prequal}")
        
        return '\n'.join(formatted)
    
    def create_structured_excel(self, matches):
        """Create new Excel file with specified columns"""
        self.log_message(f"📊 Creating structured Excel file with {len(matches)} matches...")
        
        # Create new dataframe with specified columns
        structured_data = []
        
        for match in matches:
            job_number = match['job_number']
            prequalifications = match['prequalifications']
            
            # Find rows with matching job number in award.xlsx
            mask = self.award_df['Job #'] == job_number
            matching_rows = self.award_df[mask]
            
            if len(matching_rows) > 0:
                for idx, row in matching_rows.iterrows():
                    # Extract data from award.xlsx
                    item_number = row.get('ITEM#', '')
                    selected_firm = row.get('SELECTED FIRM', '')
                    subconsultants = row.get('SUBCONSULTANTS', '')
                    first_alternate = row.get('First Alternate', '')
                    second_alternate = row.get('Second Alternate', '')
                    district = row.get('District', '')
                    selection_date = row.get('selection date', '')
                    
                    # Format prequalifications
                    formatted_prequals = self.format_prequalifications_for_excel(prequalifications)
                    
                    # Create structured row
                    structured_row = {
                        'f': '',  # Empty column as requested
                        'ITEM#': item_number,
                        'SELECTED FIRM': selected_firm,
                        'SUBCONSULTANTS': subconsultants,
                        'First Alternate': first_alternate,
                        'Second Alternate': second_alternate,
                        'Job #': job_number,
                        'District': district,
                        'selection date': selection_date,
                        'prequals': formatted_prequals
                    }
                    
                    structured_data.append(structured_row)
                    
                    self.log_message(f"✅ Added row for Job {job_number}: {selected_firm}")
            else:
                self.log_message(f"❌ No rows found for Job {job_number}")
        
        # Create DataFrame
        structured_df = pd.DataFrame(structured_data)
        
        # Save to Excel
        structured_df.to_excel(self.output_file, index=False)
        self.log_message(f"💾 Structured Excel file saved: {self.output_file}")
        
        return structured_df
    
    def generate_processing_report(self, all_projects, matches, structured_df):
        """Generate comprehensive processing report"""
        self.log_message(f"📊 Generating processing report...")
        
        # Calculate statistics
        total_award_rows = len(self.award_df)
        rows_in_structured = len(structured_df)
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'processing_summary': {
                'total_ptb_files_available': 40,
                'processed_ptb_files': self.processing_stats['processed_ptb_files'],
                'total_projects_found': self.processing_stats['total_projects_found'],
                'projects_with_prequals': self.processing_stats['projects_with_prequals'],
                'job_number_matches': self.processing_stats['job_number_matches'],
                'prequalifications_extracted': self.processing_stats['prequalifications_extracted'],
                'validation_errors': self.processing_stats['validation_errors'],
                'missing_ptb_files': self.processing_stats['missing_ptb_files']
            },
            'excel_file_impact': {
                'total_award_rows': total_award_rows,
                'rows_in_structured': rows_in_structured,
                'enrichment_percentage': (rows_in_structured / total_award_rows) * 100 if total_award_rows > 0 else 0
            },
            'project_results': all_projects,
            'job_matches': matches,
            'excel_columns': list(structured_df.columns) if not structured_df.empty else []
        }
        
        # Save report
        report_filename = f"structured_award_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.log_message(f"📄 Processing report saved: {report_filename}")
        
        # Print summary
        self.log_message(f"\n🎉 STRUCTURED AWARD PROCESSING COMPLETE!")
        self.log_message(f"📊 SUMMARY:")
        self.log_message(f"  • PTB Files Processed: {self.processing_stats['processed_ptb_files']}/40")
        self.log_message(f"  • Total Projects Found: {self.processing_stats['total_projects_found']}")
        self.log_message(f"  • Projects with Prequals: {self.processing_stats['projects_with_prequals']}")
        self.log_message(f"  • Job Number Matches: {self.processing_stats['job_number_matches']}")
        self.log_message(f"  • Prequalifications Extracted: {self.processing_stats['prequalifications_extracted']}")
        self.log_message(f"  • Rows in Structured Excel: {rows_in_structured}")
        self.log_message(f"  • Excel Columns: {list(structured_df.columns) if not structured_df.empty else []}")
        
        return report
    
    def run_ptb160_test(self):
        """Run test on PTB160 specifically"""
        self.log_message("🚀 STARTING PTB160 STRUCTURED AWARD TEST")
        self.log_message("=" * 80)
        
        # Process PTB160
        projects = self.process_single_ptb(160)
        
        if projects:
            # Add PTB number to each project
            for project in projects:
                project['ptb_number'] = 160
            
            # Match job numbers to award data
            matches = self.match_job_numbers_to_award(projects)
            
            # Create structured Excel
            structured_df = self.create_structured_excel(matches)
            
            # Generate report
            report = self.generate_processing_report(projects, matches, structured_df)
            
            self.log_message("🎯 PTB160 STRUCTURED AWARD TEST COMPLETE!")
            self.log_message("=" * 80)
            
            return report, structured_df
        else:
            self.log_message("❌ Failed to process PTB160")
            return None, None

def main():
    """Main execution function"""
    print("🚀 STRUCTURED AWARD PROCESSOR - PTB160 TEST")
    print("=" * 80)
    
    processor = StructuredAwardProcessor()
    report, structured_df = processor.run_ptb160_test()
    
    if report and structured_df is not None:
        print(f"\n✅ PTB160 structured award processing completed successfully!")
        print(f"📄 Check the log file: {processor.log_file}")
        print(f"📊 Check the structured Excel file: {processor.output_file}")
        print(f"📋 Excel columns: {list(structured_df.columns)}")
        print(f"📈 Total rows: {len(structured_df)}")
    else:
        print(f"\n❌ PTB160 processing failed")

if __name__ == "__main__":
    main()
