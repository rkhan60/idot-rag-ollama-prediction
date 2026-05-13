#!/usr/bin/env python3
"""
Final Corrected PTB Enrichment Processor
Uses sequential mapping between job numbers and Exhibit A sections
"""

import pandas as pd
import json
import os
import re
from datetime import datetime
from docx import Document
import numpy as np

class FinalCorrectedPTBProcessor:
    def __init__(self):
        self.award_file = '../data/award.xlsx'
        self.ptb_directory = '../data/'
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.output_file = '../data/award_final_enriched.xlsx'
        self.log_file = f"final_enrichment_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Load prequalification lookup for validation
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        # Load award data
        self.award_df = pd.read_excel(self.award_file)
        
        # Initialize tracking
        self.enrichment_stats = {
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
    
    def parse_ptb_with_sequential_mapping(self, ptb_text):
        """Parse PTB using sequential mapping between job numbers and Exhibit A sections"""
        projects = []
        
        # Find all job numbers in order
        job_numbers = re.findall(r'([A-Z]-\d{2}-\d{3}-\d{2})', ptb_text)
        
        # Find all Exhibit A sections
        exhibit_sections = ptb_text.split('Exhibit A')
        
        self.log_message(f"📋 Found {len(job_numbers)} job numbers and {len(exhibit_sections)-1} Exhibit A sections")
        
        # Map job numbers to Exhibit A sections sequentially
        for i, job_number in enumerate(job_numbers):
            exhibit_index = i  # Sequential mapping
            
            if exhibit_index < len(exhibit_sections) - 1:  # -1 because first section is empty
                exhibit_content = exhibit_sections[exhibit_index + 1]  # +1 because first section is empty
                
                # Extract prequalifications from this Exhibit A section
                prequalifications = self.extract_prequalifications_from_exhibit(exhibit_content)
                
                projects.append({
                    'job_number': job_number,
                    'exhibit_index': exhibit_index,
                    'prequalifications': prequalifications,
                    'exhibit_content_sample': exhibit_content[:200] + "..." if len(exhibit_content) > 200 else exhibit_content
                })
                
                self.log_message(f"📝 Job {job_number} → Exhibit A {exhibit_index} → {len(prequalifications)} prequals: {prequalifications}")
            else:
                self.log_message(f"⚠️ Job {job_number}: No corresponding Exhibit A section found")
        
        return projects
    
    def extract_prequalifications_from_exhibit(self, exhibit_content):
        """Extract prequalifications from Exhibit A content"""
        prequalifications = []
        
        # Look for "prequalified in the" pattern
        prequal_patterns = [
            r'prequalified in the ([^)]+) category',
            r'prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|$)',
        ]
        
        for pattern in prequal_patterns:
            matches = re.findall(pattern, exhibit_content, re.IGNORECASE)
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
            'location/design': 'location design',
            'location design': 'location/design',
        }
        
        if extracted in variations and variations[extracted] == lookup:
            return True
        if lookup in variations and variations[lookup] == extracted:
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
            self.enrichment_stats['missing_ptb_files'].append(ptb_number)
            return None
        
        # Extract text from PTB
        ptb_text = self.extract_text_from_docx(ptb_path)
        if not ptb_text:
            self.log_message(f"❌ PTB{ptb_number}: Failed to extract text")
            return None
        
        # Parse using sequential mapping
        projects = self.parse_ptb_with_sequential_mapping(ptb_text)
        
        # Update statistics
        self.enrichment_stats['processed_ptb_files'] += 1
        self.enrichment_stats['total_projects_found'] += len(projects)
        
        projects_with_prequals = sum(1 for p in projects if p['prequalifications'])
        self.enrichment_stats['projects_with_prequals'] += projects_with_prequals
        self.enrichment_stats['prequalifications_extracted'] += sum(len(p['prequalifications']) for p in projects)
        
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
                self.enrichment_stats['job_number_matches'] += 1
                self.log_message(f"✅ Match: PTB{ptb_number} Job {job_number} → {len(prequalifications)} prequals")
            else:
                self.log_message(f"❌ No match: PTB{ptb_number} Job {job_number}")
        
        return matches
    
    def format_prequalifications_for_award(self, prequalifications):
        """Format prequalifications in the required format for award.xlsx"""
        if not prequalifications:
            return ""
        
        formatted = []
        for i, prequal in enumerate(prequalifications, 1):
            formatted.append(f"{i}.{prequal}")
        
        return '\n'.join(formatted)
    
    def update_award_file(self, matches):
        """Update award.xlsx with extracted prequalifications"""
        self.log_message(f"📊 Updating award file with {len(matches)} matches...")
        
        # Create a copy of the award dataframe
        updated_df = self.award_df.copy()
        
        # Track updates
        updates_made = 0
        
        for match in matches:
            job_number = match['job_number']
            prequalifications = match['prequalifications']
            
            # Find rows with matching job number
            mask = updated_df['Job #'] == job_number
            matching_rows = updated_df[mask]
            
            if len(matching_rows) > 0:
                # Format prequalifications
                formatted_prequals = self.format_prequalifications_for_award(prequalifications)
                
                # Update Prequals column
                updated_df.loc[mask, 'Prequals'] = formatted_prequals
                updates_made += len(matching_rows)
                
                self.log_message(f"✅ Updated {len(matching_rows)} rows for Job {job_number}")
            else:
                self.log_message(f"❌ No rows found for Job {job_number}")
        
        self.log_message(f"📊 Total updates made: {updates_made}")
        
        # Save updated file
        updated_df.to_excel(self.output_file, index=False)
        self.log_message(f"💾 Updated award file saved: {self.output_file}")
        
        return updated_df
    
    def generate_enrichment_report(self, all_projects, matches, updated_df):
        """Generate comprehensive enrichment report"""
        self.log_message(f"📊 Generating enrichment report...")
        
        # Calculate statistics
        total_award_rows = len(self.award_df)
        rows_with_prequals_before = self.award_df['Prequals'].notna().sum()
        rows_with_prequals_after = updated_df['Prequals'].notna().sum()
        new_enrichments = rows_with_prequals_after - rows_with_prequals_before
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'enrichment_summary': {
                'total_ptb_files_available': 40,
                'processed_ptb_files': self.enrichment_stats['processed_ptb_files'],
                'total_projects_found': self.enrichment_stats['total_projects_found'],
                'projects_with_prequals': self.enrichment_stats['projects_with_prequals'],
                'job_number_matches': self.enrichment_stats['job_number_matches'],
                'prequalifications_extracted': self.enrichment_stats['prequalifications_extracted'],
                'validation_errors': self.enrichment_stats['validation_errors'],
                'missing_ptb_files': self.enrichment_stats['missing_ptb_files']
            },
            'award_file_impact': {
                'total_rows': total_award_rows,
                'rows_with_prequals_before': rows_with_prequals_before,
                'rows_with_prequals_after': rows_with_prequals_after,
                'new_enrichments': new_enrichments,
                'enrichment_percentage': (new_enrichments / total_award_rows) * 100
            },
            'project_results': all_projects,
            'job_matches': matches
        }
        
        # Save report
        report_filename = f"final_enrichment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.log_message(f"📄 Enrichment report saved: {report_filename}")
        
        # Print summary
        self.log_message(f"\n🎉 FINAL ENRICHMENT COMPLETE!")
        self.log_message(f"📊 SUMMARY:")
        self.log_message(f"  • PTB Files Processed: {self.enrichment_stats['processed_ptb_files']}/40")
        self.log_message(f"  • Total Projects Found: {self.enrichment_stats['total_projects_found']}")
        self.log_message(f"  • Projects with Prequals: {self.enrichment_stats['projects_with_prequals']}")
        self.log_message(f"  • Job Number Matches: {self.enrichment_stats['job_number_matches']}")
        self.log_message(f"  • Prequalifications Extracted: {self.enrichment_stats['prequalifications_extracted']}")
        self.log_message(f"  • New Enrichments: {new_enrichments}")
        self.log_message(f"  • Enrichment Rate: {(new_enrichments / total_award_rows) * 100:.1f}%")
        
        return report
    
    def run_complete_enrichment(self):
        """Run the complete final PTB enrichment process"""
        self.log_message("🚀 STARTING FINAL PTB ENRICHMENT PROCESS")
        self.log_message("=" * 80)
        
        # Process PTB files 160-200 (excluding 164)
        ptb_numbers = list(range(160, 201))
        ptb_numbers.remove(164)  # Remove missing PTB164
        
        self.enrichment_stats['total_ptb_files'] = len(ptb_numbers)
        
        # Process each PTB file
        all_projects = []
        for ptb_number in ptb_numbers:
            projects = self.process_single_ptb(ptb_number)
            if projects:
                # Add PTB number to each project
                for project in projects:
                    project['ptb_number'] = ptb_number
                all_projects.extend(projects)
        
        # Match job numbers to award data
        matches = self.match_job_numbers_to_award(all_projects)
        
        # Update award file
        updated_df = self.update_award_file(matches)
        
        # Generate report
        report = self.generate_enrichment_report(all_projects, matches, updated_df)
        
        self.log_message("🎯 FINAL ENRICHMENT PROCESS COMPLETE!")
        self.log_message("=" * 80)
        
        return report

def main():
    """Main execution function"""
    print("🚀 FINAL CORRECTED PTB ENRICHMENT PROCESSOR")
    print("=" * 80)
    
    processor = FinalCorrectedPTBProcessor()
    report = processor.run_complete_enrichment()
    
    print(f"\n✅ Final enrichment completed successfully!")
    print(f"📄 Check the log file: {processor.log_file}")
    print(f"📊 Check the enrichment report for detailed results.")

if __name__ == "__main__":
    main()





