#!/usr/bin/env python3
"""
Universal PTB Prequalification Extractor - Final Version
=======================================================
Combines regex patterns with master list matching for maximum accuracy.
"""

import json
import re
import os
from datetime import datetime
from docx import Document

class UniversalPTBExtractorFinal:
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
    
    def extract_prequalifications_final(self, project_text):
        """Final prequalification extraction combining multiple methods"""
        found_prequals = []
        
        # Method 1: Look for the specific pattern: "Firms must be prequalified in the following categories"
        categories_pattern = r'Firms must be prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|Statements of Interest|$)'
        categories_match = re.search(categories_pattern, project_text, re.IGNORECASE)
        
        if categories_match:
            categories_text = categories_match.group(1)
            print(f"📋 Found categories section: {categories_text[:100]}...")
            
            # Extract from the categories section using regex patterns
            section_prequals = self.extract_from_categories_section(categories_text)
            found_prequals.extend(section_prequals)
        
        # Method 2: Look for individual "prequalified in the" patterns
        individual_pattern = r'prequalified in the ([^)]*\([^)]*\)[^)]*) category'
        individual_matches = re.findall(individual_pattern, project_text, re.IGNORECASE)
        
        for match in individual_matches:
            match_clean = match.strip()
            # Try to find this in our master list
            matched_prequal = self.find_best_match(match_clean)
            if matched_prequal and matched_prequal not in found_prequals:
                found_prequals.append(matched_prequal)
                print(f"✅ Found individual: {matched_prequal}")
        
        # Method 3: Search for any prequalification from master list in the entire project text
        project_text_lower = project_text.lower()
        for prequal in self.master_prequals:
            prequal_lower = prequal.lower()
            if prequal_lower in project_text_lower and prequal not in found_prequals:
                # Additional check: make sure it's not just a substring of another found prequal
                is_substring = False
                for found_prequal in found_prequals:
                    if prequal_lower in found_prequal.lower() and prequal_lower != found_prequal.lower():
                        is_substring = True
                        break
                
                if not is_substring:
                    found_prequals.append(prequal)
                    print(f"✅ Found in text: {prequal}")
        
        return found_prequals
    
    def extract_from_categories_section(self, categories_text):
        """Extract prequalifications from the categories section using regex"""
        prequalifications = []
        
        # Split by lines and clean up
        lines = categories_text.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                # Look for complete prequalification patterns: "Category Name (Subcategory)"
                prequal_pattern = r'([A-Z][a-zA-Z\s&/]+)\s*\(([^)]+)\)'
                matches = re.findall(prequal_pattern, line)
                
                for category, subcategory in matches:
                    # Create the complete prequalification name
                    full_prequal = f"{category.strip()} ({subcategory.strip()})"
                    
                    # Try to find the best match in our master list
                    matched_prequal = self.find_best_match(full_prequal)
                    if matched_prequal:
                        prequalifications.append(matched_prequal)
                        print(f"✅ Extracted from categories: {matched_prequal}")
                    else:
                        # Keep original if no match found
                        prequalifications.append(full_prequal)
                        print(f"⚠️  No match found for: {full_prequal}")
        
        return prequalifications
    
    def find_best_match(self, extracted_prequal):
        """Find the best match for extracted prequalification in master list"""
        # Try exact match first
        if extracted_prequal in self.master_prequals:
            return extracted_prequal
        
        # Try fuzzy matching
        for prequal in self.master_prequals:
            if self.fuzzy_match_prequal(extracted_prequal, prequal):
                return prequal
        
        return None
    
    def fuzzy_match_prequal(self, extracted_prequal, lookup_prequal):
        """Fuzzy match for prequalifications"""
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
        
        # Special handling for Location/Design Studies
        if 'location' in extracted and 'design' in extracted and 'studies' in extracted:
            if 'location' in lookup and 'design' in lookup and 'studies' in lookup:
                # Check if the subcategory matches
                extracted_sub = extracted_prequal.split('(')[-1].split(')')[0] if '(' in extracted_prequal else ''
                lookup_sub = lookup_prequal.split('(')[-1].split(')')[0] if '(' in lookup_prequal else ''
                
                # Normalize subcategories
                extracted_sub_norm = extracted_sub.replace('/', ':').replace(':', ':').lower()
                lookup_sub_norm = lookup_sub.replace('/', ':').replace(':', ':').lower()
                
                if extracted_sub_norm == lookup_sub_norm:
                    return True
        
        return False
    
    def process_ptb_universal_final(self, ptb_number):
        """Process any PTB document using final universal extraction"""
        print(f"🔧 UNIVERSAL FINAL PTB{ptb_number} PROCESSING")
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
                
                # Extract prequalifications using final method
                prequalifications = self.extract_prequalifications_final(job_text)
                
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
        output_filename = f'ptb_processing_reports/ptb{ptb_number}_universal_final_enhanced_awards.json'
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
        
        report_filename = f'ptb_processing_reports/ptb{ptb_number}_universal_final_report.json'
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 UNIVERSAL FINAL PROCESSING RESULTS:")
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
    extractor = UniversalPTBExtractorFinal()
    
    # Test with PTB160
    print(f"🧪 TESTING UNIVERSAL FINAL WITH PTB160:")
    print("-" * 40)
    enhanced_awards = extractor.process_ptb_universal_final(160)
    
    # Show sample results
    if enhanced_awards:
        print(f"\n📋 SAMPLE UNIVERSAL FINAL EXTRACTION RESULTS:")
        print("-" * 50)
        for i, award in enumerate(enhanced_awards[:3]):
            print(f"Award {i+1}:")
            print(f"  Job: {award.get('Job #')}")
            print(f"  Firm: {award.get('SELECTED FIRM')}")
            print(f"  Prequals: {award.get('required_prequals')}")
            print()

if __name__ == "__main__":
    main()




