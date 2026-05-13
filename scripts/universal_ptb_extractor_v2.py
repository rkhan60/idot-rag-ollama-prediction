#!/usr/bin/env python3
"""
Universal PTB Prequalification Extractor V2 - Precise Matching
==============================================================
Extract prequalifications from any PTB document using precise matching.
"""

import json
import re
import os
from datetime import datetime
from docx import Document

class UniversalPTBExtractorV2:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        
        # Load prequalification lookup and build master list
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        # Build master prequalification list
        self.master_prequals = self.build_master_prequal_list()
        print(f"📋 Built master list with {len(self.master_prequals)} prequalifications")
    
    def build_master_prequal_list(self):
        """Build a master list of all prequalification names"""
        master_list = []
        
        # Add main categories
        for category in self.prequal_lookup.keys():
            master_list.append(category)
        
        # Add all subcategories
        for category in self.prequal_lookup.keys():
            if category in self.prequal_lookup:
                subcategories = self.prequal_lookup[category].get('sub_categories', {})
                for subcat_key, subcat_data in subcategories.items():
                    full_prequal_name = subcat_data.get('full_prequal_name', '')
                    if full_prequal_name:
                        master_list.append(full_prequal_name)
        
        # Remove duplicates and sort by length (longest first to avoid substring issues)
        unique_list = list(set(master_list))
        return sorted(unique_list, key=len, reverse=True)
    
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
    
    def extract_prequalifications_precise(self, project_text):
        """Precise prequalification extraction using master list"""
        found_prequals = []
        project_text_lower = project_text.lower()
        
        # Sort prequals by length (longest first) to avoid substring issues
        sorted_prequals = sorted(self.master_prequals, key=len, reverse=True)
        
        # Track used text to avoid double-counting
        used_text_positions = set()
        
        for prequal in sorted_prequals:
            prequal_lower = prequal.lower()
            
            # Find all occurrences of this prequalification
            start_pos = 0
            while True:
                pos = project_text_lower.find(prequal_lower, start_pos)
                if pos == -1:
                    break
                
                # Check if this position overlaps with already used text
                overlap = False
                for used_start, used_end in used_text_positions:
                    if pos < used_end and pos + len(prequal_lower) > used_start:
                        overlap = True
                        break
                
                if not overlap:
                    # Mark this text as used
                    used_text_positions.add((pos, pos + len(prequal_lower)))
                    found_prequals.append(prequal)
                    print(f"✅ Found: {prequal}")
                    break  # Only take the first occurrence of each prequal
                
                start_pos = pos + 1
        
        return found_prequals
    
    def extract_prequalifications_smart(self, project_text):
        """Smart prequalification extraction with context awareness"""
        found_prequals = []
        
        # First, look for the specific pattern: "Firms must be prequalified in the following categories"
        categories_pattern = r'Firms must be prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|Statements of Interest|$)'
        categories_match = re.search(categories_pattern, project_text, re.IGNORECASE)
        
        if categories_match:
            categories_text = categories_match.group(1)
            print(f"📋 Found categories section: {categories_text[:100]}...")
            
            # Extract from the categories section using precise matching
            section_prequals = self.extract_prequalifications_precise(categories_text)
            found_prequals.extend(section_prequals)
        
        # Also look for individual "prequalified in the" patterns
        individual_pattern = r'prequalified in the ([^)]*\([^)]*\)[^)]*) category'
        individual_matches = re.findall(individual_pattern, project_text, re.IGNORECASE)
        
        for match in individual_matches:
            match_clean = match.strip()
            # Try to find this in our master list
            for prequal in self.master_prequals:
                if self.fuzzy_match_prequal(match_clean, prequal):
                    if prequal not in found_prequals:
                        found_prequals.append(prequal)
                        print(f"✅ Found individual: {prequal}")
                    break
        
        return found_prequals
    
    def fuzzy_match_prequal(self, extracted_prequal, lookup_prequal):
        """Fuzzy match for individual prequalifications"""
        # Normalize both strings
        extracted = extracted_prequal.lower().replace(':', '').replace('-', ' ').strip()
        lookup = lookup_prequal.lower().replace(':', '').replace('-', ' ').strip()
        
        # Direct match
        if extracted == lookup:
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
    
    def process_ptb_universal_v2(self, ptb_number):
        """Process any PTB document using smart universal extraction"""
        print(f"🔧 UNIVERSAL V2 PTB{ptb_number} PROCESSING")
        print("=" * 50)
        
        # Load PTB document
        doc_path = f'../../ptb{ptb_number}.docx'
        ptb_text = self.extract_text_from_docx(doc_path)
        
        if not ptb_text:
            print(f"❌ Could not load PTB{ptb_number} document")
            return
        
        # Load award data
        with open('../data/award_structure.json', 'r') as f:
            award_data = json.load(f)
        
        # Get PTB awards
        ptb_awards = [a for a in award_data if a.get('f') == str(ptb_number)]
        print(f"📊 Found {len(ptb_awards)} PTB{ptb_number} awards")
        
        # Process each award
        enhanced_awards = []
        successful_matches = 0
        missing_matches = 0
        
        for award in ptb_awards:
            job_number = award.get('Job #')
            
            # Find this job in PTB document
            job_pattern = rf'Job No\.\s*{re.escape(job_number)}[^.]*\.(.*?)(?=Job No\.|$)'
            job_match = re.search(job_pattern, ptb_text, re.DOTALL | re.IGNORECASE)
            
            if job_match:
                job_text = job_match.group(1)
                
                # Extract prequalifications using smart method
                prequalifications = self.extract_prequalifications_smart(job_text)
                
                # Create enhanced award
                enhanced_award = award.copy()
                enhanced_award['required_prequals'] = prequalifications
                enhanced_award['ptb_match_status'] = 'SUCCESS'
                
                enhanced_awards.append(enhanced_award)
                successful_matches += 1
                
                print(f"✅ {job_number}: {len(prequalifications)} prequals → {award.get('SELECTED FIRM')}")
                if prequalifications:
                    for prequal in prequalifications:
                        print(f"   - {prequal}")
            else:
                # No match found
                enhanced_award = award.copy()
                enhanced_award['required_prequals'] = []
                enhanced_award['ptb_match_status'] = 'NO_PTB_DATA'
                
                enhanced_awards.append(enhanced_award)
                missing_matches += 1
                
                print(f"❌ {job_number}: No PTB data → {award.get('SELECTED FIRM')}")
        
        # Save results
        output_filename = f'ptb_processing_reports/ptb{ptb_number}_universal_v2_enhanced_awards.json'
        with open(output_filename, 'w') as f:
            json.dump(enhanced_awards, f, indent=2)
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'ptb_number': ptb_number,
            'summary': {
                'total_awards': len(enhanced_awards),
                'successful_matches': successful_matches,
                'missing_ptb_data': missing_matches,
                'success_rate': f"{(successful_matches/len(enhanced_awards)*100):.1f}%" if enhanced_awards else "0%"
            },
            'sample_enhanced_awards': enhanced_awards[:3] if enhanced_awards else []
        }
        
        report_filename = f'ptb_processing_reports/ptb{ptb_number}_universal_v2_report.json'
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 UNIVERSAL V2 PROCESSING RESULTS:")
        print("-" * 40)
        print(f"   Total awards: {len(enhanced_awards)}")
        print(f"   ✅ Successful matches: {successful_matches}")
        print(f"   ❌ Missing PTB data: {missing_matches}")
        print(f"   📈 Success rate: {(successful_matches/len(enhanced_awards)*100):.1f}%" if enhanced_awards else "0%")
        print(f"   💾 Enhanced awards saved: {output_filename}")
        print(f"   📋 Report saved: {report_filename}")
        
        return enhanced_awards

def main():
    """Main function"""
    extractor = UniversalPTBExtractorV2()
    
    # Test with PTB160
    print(f"🧪 TESTING UNIVERSAL V2 WITH PTB160:")
    print("-" * 40)
    enhanced_awards = extractor.process_ptb_universal_v2(160)
    
    # Show sample results
    if enhanced_awards:
        print(f"\n📋 SAMPLE UNIVERSAL V2 EXTRACTION RESULTS:")
        print("-" * 50)
        for i, award in enumerate(enhanced_awards[:3]):
            print(f"Award {i+1}:")
            print(f"  Job: {award.get('Job #')}")
            print(f"  Firm: {award.get('SELECTED FIRM')}")
            print(f"  Prequals: {award.get('required_prequals')}")
            print()

if __name__ == "__main__":
    main()




