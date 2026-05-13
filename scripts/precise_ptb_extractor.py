#!/usr/bin/env python3
"""
Precise PTB Extractor - Clean Output Structure
==============================================
Extract prequalifications and district from PTB documents with clean output structure.
"""

import json
import re
from docx import Document
import os

class PrecisePTBExtractor:
    def __init__(self):
        self.load_prequal_lookup()
        self.build_master_prequals()
        
    def load_prequal_lookup(self):
        """Load prequalification lookup data"""
        with open('../data/prequal_lookup.json', 'r') as f:
            self.prequal_lookup = json.load(f)
    
    def build_master_prequals(self):
        """Build master list of all prequalifications, sorted by length (longest first)"""
        self.master_prequals = []
        
        # Add all main categories and subcategories
        for main_cat, subcats in self.prequal_lookup.items():
            # Add main category
            self.master_prequals.append(main_cat)
            # Add subcategories
            for subcat in subcats:
                self.master_prequals.append(subcat)
        
        # Sort by length (longest first) to prevent partial matches
        self.master_prequals.sort(key=len, reverse=True)
    
    def extract_district_from_ptb(self, ptb_text):
        """Extract district from PTB text"""
        # Look for district patterns
        district_patterns = [
            r'District\s+(\d+)',
            r'DISTRICT\s+(\d+)',
            r'District\s*(\d+)',
            r'DISTRICT\s*(\d+)'
        ]
        
        for pattern in district_patterns:
            match = re.search(pattern, ptb_text, re.IGNORECASE)
            if match:
                return f"District {match.group(1)}"
        
        return None
    
    def extract_prequalifications_final(self, project_text):
        """Extract prequalifications with precise matching - FOCUS ON WORKING PATTERNS"""
        found_prequals = []
        
        # Method 1: Look for individual "prequalified in the" patterns (THIS IS WORKING)
        individual_pattern = r'prequalified in the ([^)]*\([^)]*\)[^)]*) category'
        individual_matches = re.findall(individual_pattern, project_text, re.IGNORECASE)
        
        for match in individual_matches:
            match_clean = match.strip()
            # Try to find this in our master list
            matched_prequal = self.find_best_match(match_clean)
            if matched_prequal and matched_prequal not in found_prequals:
                found_prequals.append(matched_prequal)
        
        # Method 2: Look for the specific pattern: "Firms must be prequalified in the following categories"
        categories_pattern = r'Firms must be prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|Statements of Interest|$)'
        categories_match = re.search(categories_pattern, project_text, re.IGNORECASE)
        
        if categories_match:
            categories_text = categories_match.group(1)
            # Extract from the categories section using regex patterns
            section_prequals = self.extract_from_categories_section(categories_text)
            found_prequals.extend(section_prequals)
        
        return found_prequals
    
    def extract_from_categories_section(self, categories_text):
        """Extract prequalifications from the categories section"""
        found_prequals = []
        
        # Split by lines and process each line
        lines = categories_text.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                # Try to match the line against our master prequal list
                matched_prequal = self.find_best_match(line)
                if matched_prequal:
                    found_prequals.append(matched_prequal)
        
        return found_prequals
    
    def find_best_match(self, text):
        """Find the best match for extracted prequalification in master list"""
        text_clean = text.strip()
        
        # Try exact match first against full_prequal_name
        for main_cat, subcats_data in self.prequal_lookup.items():
            if 'sub_categories' in subcats_data:
                for subcat_key, subcat_info in subcats_data['sub_categories'].items():
                    full_prequal_name = subcat_info.get('full_prequal_name', '')
                    if full_prequal_name.lower() == text_clean.lower():
                        return full_prequal_name
        
        # Try fuzzy matching with variations
        text_variations = [
            text_clean,
            text_clean.replace('&', 'and'),
            text_clean.replace('and', '&'),
            text_clean.replace('/', ':'),
            text_clean.replace(':', '/')
        ]
        
        for variation in text_variations:
            for main_cat, subcats_data in self.prequal_lookup.items():
                if 'sub_categories' in subcats_data:
                    for subcat_key, subcat_info in subcats_data['sub_categories'].items():
                        full_prequal_name = subcat_info.get('full_prequal_name', '')
                        if full_prequal_name.lower() == variation.lower():
                            return full_prequal_name
        
        # Special handling for Location/Design Studies
        if 'location' in text_clean.lower() and 'design' in text_clean.lower() and 'studies' in text_clean.lower():
            for main_cat, subcats_data in self.prequal_lookup.items():
                if 'sub_categories' in subcats_data:
                    for subcat_key, subcat_info in subcats_data['sub_categories'].items():
                        full_prequal_name = subcat_info.get('full_prequal_name', '')
                        if 'location' in full_prequal_name.lower() and 'design' in full_prequal_name.lower() and 'studies' in full_prequal_name.lower():
                            return full_prequal_name
        
        return None
    
    def extract_ptb_data(self, ptb_file):
        """Extract data from PTB document"""
        doc = Document(ptb_file)
        full_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        
        # Extract district
        district = self.extract_district_from_ptb(full_text)
        
        # Extract projects and their prequalifications
        projects = []
        
        # Split by project sections (look for job numbers)
        project_sections = re.split(r'(?=Job #|D-\d+|C-\d+|P-\d+)', full_text)
        
        for section in project_sections:
            if section.strip():
                # Extract job number
                job_match = re.search(r'(?:Job #\s*)?([DCP]-\d+-\d+-\d+)', section)
                if job_match:
                    job_number = job_match.group(1)
                    
                    # Extract prequalifications for this project
                    prequals = self.extract_prequalifications_final(section)
                    
                    projects.append({
                        'job_number': job_number,
                        'prequals': prequals,
                        'district': district
                    })
        
        return projects
    
    def process_ptb160(self):
        """Process PTB160 with clean output structure"""
        print("🧪 TESTING PRECISE EXTRACTION WITH PTB160:")
        print("-" * 50)
        
        # Load award data
        with open('../data/award_structure.json', 'r') as f:
            awards = json.load(f)
        
        # Filter PTB160 awards
        ptb160_awards = [a for a in awards if a.get('f') == '160']
        print(f"🔧 PRECISE PTB160 PROCESSING")
        print("=" * 50)
        print(f"📊 Found {len(ptb160_awards)} PTB160 awards")
        
        # Extract PTB data
        ptb_file = '../../ptb160.docx'
        ptb_data = self.extract_ptb_data(ptb_file)
        
        # Create lookup for PTB data
        ptb_lookup = {p['job_number']: p for p in ptb_data}
        
        # Process each award
        enhanced_awards = []
        
        for award in ptb160_awards:
            job_number = award.get('Job #')
            ptb_project = ptb_lookup.get(job_number)
            
            # Create clean output structure
            enhanced_award = {
                "f": award.get('f'),
                "ITEM#": award.get('ITEM#'),
                "SELECTED FIRM": award.get('SELECTED FIRM'),
                "SUBCONSULTANTS": award.get('SUBCONSULTANTS'),
                "First Alternate": award.get('First Alternate'),
                "Second Alternate": award.get('Second Alternate'),
                "Job #": award.get('Job #'),
                "Description": award.get('Description'),
                "Region/District": ptb_project.get('district') if ptb_project else award.get('Region/District'),
                "Fee Estimate": award.get('Fee Estimate'),
                "Eligible": award.get('Eligible'),
                "Selection Date": award.get('Selection Date'),
                "required_prequals": ptb_project.get('prequals', []) if ptb_project else [],
                "ptb_match_status": "SUCCESS" if ptb_project else "NO_PTB_DATA"
            }
            
            enhanced_awards.append(enhanced_award)
            
            # Print status
            if ptb_project:
                print(f"✅ {job_number}: {len(ptb_project.get('prequals', []))} prequals → {award.get('SELECTED FIRM')}")
                for prequal in ptb_project.get('prequals', []):
                    print(f"   - {prequal}")
            else:
                print(f"❌ {job_number}: No PTB data → {award.get('SELECTED FIRM')}")
        
        # Save results
        os.makedirs('ptb_processing_reports', exist_ok=True)
        
        with open('ptb_processing_reports/ptb160_clean_enhanced_awards.json', 'w') as f:
            json.dump(enhanced_awards, f, indent=2)
        
        # Create summary report
        successful_matches = len([a for a in enhanced_awards if a['ptb_match_status'] == 'SUCCESS'])
        total_awards = len(enhanced_awards)
        
        summary = {
            'ptb_number': '160',
            'total_awards': total_awards,
            'successful_matches': successful_matches,
            'success_rate': (successful_matches / total_awards * 100) if total_awards > 0 else 0,
            'awards_with_prequals': len([a for a in enhanced_awards if a.get('required_prequals')]),
            'unique_prequals_found': list(set([p for a in enhanced_awards for p in a.get('required_prequals', [])]))
        }
        
        with open('ptb_processing_reports/ptb160_clean_report.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 CLEAN PROCESSING RESULTS:")
        print("-" * 40)
        print(f"   Total awards: {total_awards}")
        print(f"   ✅ Successful matches: {successful_matches}")
        print(f"   📈 Success rate: {summary['success_rate']:.1f}%")
        print(f"   💾 Enhanced awards saved: ptb_processing_reports/ptb160_clean_enhanced_awards.json")
        print(f"   📋 Report saved: ptb_processing_reports/ptb160_clean_report.json")
        
        return enhanced_awards

def main():
    extractor = PrecisePTBExtractor()
    results = extractor.process_ptb160()
    
    # Show sample output
    print(f"\n📋 SAMPLE CLEAN OUTPUT STRUCTURE:")
    print("-" * 50)
    if results:
        sample = results[0]
        print(json.dumps(sample, indent=2))

if __name__ == "__main__":
    main()

