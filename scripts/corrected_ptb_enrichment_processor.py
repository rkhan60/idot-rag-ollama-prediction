#!/usr/bin/env python3
"""
Corrected PTB Enrichment Processor
Extract prequalifications from individual projects within PTB files
"""

import pandas as pd
import json
import os
import re
from datetime import datetime
from docx import Document
import numpy as np

class CorrectedPTBEnrichmentProcessor:
    def __init__(self):
        self.award_file = '../data/award.xlsx'
        self.ptb_directory = '../data/'
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.output_file = '../data/award_corrected_enriched.xlsx'
        self.log_file = f"corrected_enrichment_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
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
    
    def parse_individual_projects(self, ptb_text):
        """Parse individual projects from PTB text"""
        projects = []
        
        # Split by project patterns
        # Look for patterns like "1. Job No. D-91-516-11" or "Job No. D-91-516-11"
        project_patterns = [
            r'(\d+\.\s*Job\s*No\.\s*([A-Z]-\d{2}-\d{3}-\d{2})[^.]*?)(?=\d+\.\s*Job\s*No\.|$)',
            r'(Job\s*No\.\s*([A-Z]-\d{2}-\d{3}-\d{2})[^.]*?)(?=Job\s*No\.|$)',
        ]
        
        for pattern in project_patterns:
            matches = re.findall(pattern, ptb_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                project_text = match[0] if isinstance(match, tuple) else match
                job_number = match[1] if isinstance(match, tuple) else re.search(r'([A-Z]-\d{2}-\d{3}-\d{2})', match)
                if job_number:
                    job_number = job_number.group(1) if hasattr(job_number, 'group') else job_number
                    projects.append({
                        'job_number': job_number,
                        'project_text': project_text.strip()
                    })
        
        # If no structured projects found, try to extract from the entire text
        if not projects:
            # Look for job numbers in the text
            job_numbers = re.findall(r'([A-Z]-\d{2}-\d{3}-\d{2})', ptb_text)
            if job_numbers:
                # Split text by job numbers and create projects
                for i, job_number in enumerate(job_numbers):
                    start_idx = ptb_text.find(job_number)
                    if start_idx != -1:
                        # Find the end of this project (next job number or end of text)
                        end_idx = len(ptb_text)
                        for next_job in job_numbers[i+1:]:
                            next_idx = ptb_text.find(next_job, start_idx + 1)
                            if next_idx != -1:
                                end_idx = next_idx
                                break
                        
                        project_text = ptb_text[start_idx:end_idx].strip()
                        projects.append({
                            'job_number': job_number,
                            'project_text': project_text
                        })
        
        return projects
    
    def extract_prequalifications_from_project(self, project_text):
        """Extract prequalifications from a specific project text"""
        prequalifications = []
        
        # Look for Exhibit A section within this project
        exhibit_patterns = [
            r'Exhibit\s*A[:\s]*([\s\S]*?)(?=Exhibit\s*B|$)',
            r'Prequalification\s*Requirements[:\s]*([\s\S]*?)(?=\n\n|$)',
            r'Required\s*Prequalifications[:\s]*([\s\S]*?)(?=\n\n|$)',
        ]
        
        exhibit_text = ""
        for pattern in exhibit_patterns:
            matches = re.findall(pattern, project_text, re.IGNORECASE)
            if matches:
                exhibit_text = matches[0]
                break
        
        # If no Exhibit A found, look for prequalification keywords in project text
        if not exhibit_text:
            prequal_keywords = ['prequalification', 'qualification', 'required', 'must have']
            if any(keyword in project_text.lower() for keyword in prequal_keywords):
                exhibit_text = project_text
        
        # Extract prequalification categories from exhibit text
        if exhibit_text:
            # Match against prequal_lookup categories
            for category in self.prequal_lookup.keys():
                # Create flexible matching patterns
                category_patterns = [
                    re.escape(category),
                    re.escape(category.replace('(', ' (').replace(')', ') ')),
                    re.escape(category.replace(' - ', ' (').replace(':', ') ')),
                ]
                
                for pattern in category_patterns:
                    if re.search(pattern, exhibit_text, re.IGNORECASE):
                        prequalifications.append(category)
                        break
        
        return list(set(prequalifications))  # Remove duplicates
    
    def validate_prequalifications(self, prequalifications):
        """Validate extracted prequalifications against lookup"""
        validated = []
        errors = []
        
        for prequal in prequalifications:
            if prequal in self.prequal_lookup:
                validated.append(prequal)
            else:
                errors.append(prequal)
        
        return validated, errors
    
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
        
        # Parse individual projects
        projects = self.parse_individual_projects(ptb_text)
        self.log_message(f"📋 PTB{ptb_number}: Found {len(projects)} projects")
        
        # Process each project
        project_results = []
        for project in projects:
            job_number = project['job_number']
            project_text = project['project_text']
            
            # Extract prequalifications for this specific project
            prequalifications = self.extract_prequalifications_from_project(project_text)
            
            # Validate prequalifications
            validated_prequals, errors = self.validate_prequalifications(prequalifications)
            if errors:
                self.log_message(f"⚠️ PTB{ptb_number} Job {job_number}: Validation errors: {errors}")
                self.enrichment_stats['validation_errors'] += len(errors)
            
            project_results.append({
                'ptb_number': ptb_number,
                'job_number': job_number,
                'prequalifications': validated_prequals,
                'validation_errors': errors,
                'project_text_sample': project_text[:200] + "..." if len(project_text) > 200 else project_text
            })
            
            self.log_message(f"📝 PTB{ptb_number} Job {job_number}: {len(validated_prequals)} prequals: {validated_prequals}")
        
        # Update statistics
        self.enrichment_stats['processed_ptb_files'] += 1
        self.enrichment_stats['total_projects_found'] += len(projects)
        
        projects_with_prequals = sum(1 for p in project_results if p['prequalifications'])
        self.enrichment_stats['projects_with_prequals'] += projects_with_prequals
        self.enrichment_stats['prequalifications_extracted'] += sum(len(p['prequalifications']) for p in project_results)
        
        return project_results
    
    def match_job_numbers_to_award(self, all_project_results):
        """Match project job numbers to award.xlsx job numbers"""
        self.log_message(f"🔗 Matching job numbers to award data...")
        
        matches = []
        award_job_numbers = set(self.award_df['Job #'].dropna().astype(str))
        
        for project_result in all_project_results:
            ptb_number = project_result['ptb_number']
            job_number = project_result['job_number']
            prequalifications = project_result['prequalifications']
            
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
    
    def generate_enrichment_report(self, all_project_results, matches, updated_df):
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
            'project_results': all_project_results,
            'job_matches': matches
        }
        
        # Save report
        report_filename = f"corrected_enrichment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.log_message(f"📄 Enrichment report saved: {report_filename}")
        
        # Print summary
        self.log_message(f"\n🎉 CORRECTED ENRICHMENT COMPLETE!")
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
        """Run the complete corrected PTB enrichment process"""
        self.log_message("🚀 STARTING CORRECTED PTB ENRICHMENT PROCESS")
        self.log_message("=" * 80)
        
        # Process PTB files 160-200 (excluding 164)
        ptb_numbers = list(range(160, 201))
        ptb_numbers.remove(164)  # Remove missing PTB164
        
        self.enrichment_stats['total_ptb_files'] = len(ptb_numbers)
        
        # Process each PTB file
        all_project_results = []
        for ptb_number in ptb_numbers:
            project_results = self.process_single_ptb(ptb_number)
            if project_results:
                all_project_results.extend(project_results)
        
        # Match job numbers to award data
        matches = self.match_job_numbers_to_award(all_project_results)
        
        # Update award file
        updated_df = self.update_award_file(matches)
        
        # Generate report
        report = self.generate_enrichment_report(all_project_results, matches, updated_df)
        
        self.log_message("🎯 CORRECTED ENRICHMENT PROCESS COMPLETE!")
        self.log_message("=" * 80)
        
        return report

def main():
    """Main execution function"""
    print("🚀 CORRECTED PTB ENRICHMENT PROCESSOR")
    print("=" * 80)
    
    processor = CorrectedPTBEnrichmentProcessor()
    report = processor.run_complete_enrichment()
    
    print(f"\n✅ Corrected enrichment completed successfully!")
    print(f"📄 Check the log file: {processor.log_file}")
    print(f"📊 Check the enrichment report for detailed results.")

if __name__ == "__main__":
    main()





