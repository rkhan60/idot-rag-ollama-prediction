#!/usr/bin/env python3
"""
Complete PTB160 Processor - Fixed Extraction
===========================================
Process PTB160 with complete prequalification extraction.
"""

import json
import re
import os
from datetime import datetime
from docx import Document

class CompletePTB160Processor:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        
        # Load prequalification lookup for validation
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
    
    def extract_text_from_docx(self, filepath):
        """Extract text from .docx file"""
        try:
            doc = Document(filepath)
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            return '\n'.join(text)
        except Exception as e:
            print(f"❌ Error reading {filepath}: {str(e)}")
            return None
    
    def extract_prequalifications_complete(self, project_text):
        """Complete prequalification extraction that captures all prequals"""
        prequalifications = []
        
        # Look for the specific pattern: "Firms must be prequalified in the following categories"
        categories_pattern = r'Firms must be prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|Statements of Interest|$)'
        categories_match = re.search(categories_pattern, project_text, re.IGNORECASE)
        
        if categories_match:
            categories_text = categories_match.group(1)
            
            # Split by lines and clean up
            lines = categories_text.split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    # Look for prequalification patterns in this line
                    # Pattern: "Category Name (Subcategory)"
                    prequal_pattern = r'([A-Z][a-zA-Z\s&/]+)\s*\(([^)]+)\)'
                    matches = re.findall(prequal_pattern, line)
                    
                    for category, subcategory in matches:
                        full_prequal = f"{category.strip()} ({subcategory.strip()})"
                        prequalifications.append(full_prequal)
        
        # Also look for individual "prequalified in the" patterns
        individual_pattern = r'prequalified in the ([^)]*\([^)]*\)[^)]*) category'
        individual_matches = re.findall(individual_pattern, project_text, re.IGNORECASE)
        
        for match in individual_matches:
            if match not in prequalifications:
                prequalifications.append(match.strip())
        
        # Validate against prequal_lookup
        validated_prequals = []
        for prequal in prequalifications:
            # Try exact match first
            if prequal in self.prequal_lookup:
                validated_prequals.append(prequal)
            else:
                # Try fuzzy matching against main categories and subcategories
                matched = False
                for lookup_category in self.prequal_lookup.keys():
                    if self.fuzzy_match_prequal(prequal, lookup_category):
                        validated_prequals.append(lookup_category)
                        matched = True
                        break
                    
                    # Also check subcategories
                    if lookup_category in self.prequal_lookup:
                        subcategories = self.prequal_lookup[lookup_category].get('sub_categories', {})
                        for subcat_key, subcat_data in subcategories.items():
                            full_prequal_name = subcat_data.get('full_prequal_name', '')
                            if self.fuzzy_match_prequal(prequal, full_prequal_name):
                                validated_prequals.append(full_prequal_name)
                                matched = True
                                break
                        if matched:
                            break
                
                # If no match found, keep the original
                if not matched:
                    validated_prequals.append(prequal)
        
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
        
        # Special handling for Location/Design Studies
        if 'location' in extracted and 'design' in extracted and 'studies' in extracted:
            if 'location' in lookup and 'design' in lookup and 'studies' in lookup:
                # Check if the subcategory matches
                extracted_sub = extracted_prequal.split('(')[-1].split(')')[0] if '(' in extracted_prequal else ''
                lookup_sub = lookup_category.split('(')[-1].split(')')[0] if '(' in lookup_category else ''
                
                # Normalize subcategories
                extracted_sub_norm = extracted_sub.replace('/', ':').replace(':', ':').lower()
                lookup_sub_norm = lookup_sub.replace('/', ':').replace(':', ':').lower()
                
                if extracted_sub_norm == lookup_sub_norm:
                    return True
        
        # Handle common variations
        variations = {
            'roads & streets': 'roads and streets',
            'roads and streets': 'roads & streets',
            'quality assurance: qa': 'quality assurance',
            'quality assurance qa': 'quality assurance',
            'location/design': 'location design',
            'location design': 'location/design',
            'new construction/major reconstruction': 'new construction:major reconstruction',
            'new construction:major reconstruction': 'new construction/major reconstruction',
        }
        
        if extracted in variations and variations[extracted] == lookup:
            return True
        if lookup in variations and variations[lookup] == extracted:
            return True
        
        return False
    
    def process_ptb160_complete(self):
        """Process PTB160 with complete extraction"""
        print("🔧 COMPLETE PTB160 PROCESSING")
        print("=" * 50)
        
        # Load PTB160 document
        doc_path = '../../ptb160.docx'
        ptb_text = self.extract_text_from_docx(doc_path)
        
        if not ptb_text:
            print("❌ Could not load PTB160 document")
            return
        
        # Load award data
        with open('../data/award_structure.json', 'r') as f:
            award_data = json.load(f)
        
        # Get PTB160 awards
        ptb160_awards = [a for a in award_data if a.get('f') == '160']
        print(f"📊 Found {len(ptb160_awards)} PTB160 awards")
        
        # Process each award
        enhanced_awards = []
        successful_matches = 0
        missing_matches = 0
        
        for award in ptb160_awards:
            job_number = award.get('Job #')
            
            # Find this job in PTB160 document
            job_pattern = rf'Job No\.\s*{re.escape(job_number)}[^.]*\.(.*?)(?=Job No\.|$)'
            job_match = re.search(job_pattern, ptb_text, re.DOTALL | re.IGNORECASE)
            
            if job_match:
                job_text = job_match.group(1)
                
                # Extract prequalifications with complete method
                prequalifications = self.extract_prequalifications_complete(job_text)
                
                # Create enhanced award
                enhanced_award = award.copy()
                enhanced_award['required_prequals'] = prequalifications
                enhanced_award['ptb_match_status'] = 'SUCCESS'
                
                enhanced_awards.append(enhanced_award)
                successful_matches += 1
                
                print(f"✅ {job_number}: {len(prequalifications)} prequals → {award.get('SELECTED FIRM')}")
            else:
                # No match found
                enhanced_award = award.copy()
                enhanced_award['required_prequals'] = []
                enhanced_award['ptb_match_status'] = 'NO_PTB_DATA'
                
                enhanced_awards.append(enhanced_award)
                missing_matches += 1
                
                print(f"❌ {job_number}: No PTB data → {award.get('SELECTED FIRM')}")
        
        # Save results
        output_filename = 'ptb_processing_reports/ptb160_complete_enhanced_awards.json'
        with open(output_filename, 'w') as f:
            json.dump(enhanced_awards, f, indent=2)
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'ptb_number': 160,
            'summary': {
                'total_awards': len(enhanced_awards),
                'successful_matches': successful_matches,
                'missing_ptb_data': missing_matches,
                'success_rate': f"{(successful_matches/len(enhanced_awards)*100):.1f}%" if enhanced_awards else "0%"
            },
            'sample_enhanced_awards': enhanced_awards[:3] if enhanced_awards else []
        }
        
        report_filename = 'ptb_processing_reports/ptb160_complete_report.json'
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 COMPLETE PROCESSING RESULTS:")
        print("-" * 40)
        print(f"   Total awards: {len(enhanced_awards)}")
        print(f"   ✅ Successful matches: {successful_matches}")
        print(f"   ❌ Missing PTB data: {missing_matches}")
        print(f"   📈 Success rate: {(successful_matches/len(enhanced_awards)*100):.1f}%" if enhanced_awards else "0%")
        print(f"   💾 Enhanced awards saved: {output_filename}")
        print(f"   📋 Report saved: {report_filename}")
        
        # Show sample with prequalifications
        print(f"\n📋 SAMPLE ENHANCED AWARDS:")
        print("-" * 40)
        for i, award in enumerate(enhanced_awards[:3]):
            print(f"Award {i+1}:")
            print(f"  Job: {award.get('Job #')}")
            print(f"  Firm: {award.get('SELECTED FIRM')}")
            print(f"  Prequals: {award.get('required_prequals')}")
            print()

def main():
    """Main function"""
    processor = CompletePTB160Processor()
    processor.process_ptb160_complete()

if __name__ == "__main__":
    main()




