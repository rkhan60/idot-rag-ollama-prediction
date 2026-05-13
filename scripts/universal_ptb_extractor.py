#!/usr/bin/env python3
"""
Universal PTB Prequalification Extractor
========================================
Extract prequalifications from any PTB document using master prequalification list.
"""

import json
import re
import os
from datetime import datetime
from docx import Document

class UniversalPTBExtractor:
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
        
        # Remove duplicates and sort
        return sorted(list(set(master_list)))
    
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
    
    def extract_prequalifications_universal(self, project_text):
        """Universal prequalification extraction using master list"""
        found_prequals = []
        
        # Convert project text to lowercase for case-insensitive matching
        project_text_lower = project_text.lower()
        
        # Search for each prequalification in the master list
        for prequal in self.master_prequals:
            # Convert prequal to lowercase for matching
            prequal_lower = prequal.lower()
            
            # Check if this prequalification appears in the project text
            if prequal_lower in project_text_lower:
                found_prequals.append(prequal)
                print(f"✅ Found: {prequal}")
        
        return found_prequals
    
    def process_ptb_universal(self, ptb_number):
        """Process any PTB document using universal extraction"""
        print(f"🔧 UNIVERSAL PTB{ptb_number} PROCESSING")
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
                
                # Extract prequalifications using universal method
                prequalifications = self.extract_prequalifications_universal(job_text)
                
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
        output_filename = f'ptb_processing_reports/ptb{ptb_number}_universal_enhanced_awards.json'
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
        
        report_filename = f'ptb_processing_reports/ptb{ptb_number}_universal_report.json'
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 UNIVERSAL PROCESSING RESULTS:")
        print("-" * 40)
        print(f"   Total awards: {len(enhanced_awards)}")
        print(f"   ✅ Successful matches: {successful_matches}")
        print(f"   ❌ Missing PTB data: {missing_matches}")
        print(f"   📈 Success rate: {(successful_matches/len(enhanced_awards)*100):.1f}%" if enhanced_awards else "0%")
        print(f"   💾 Enhanced awards saved: {output_filename}")
        print(f"   📋 Report saved: {report_filename}")
        
        return enhanced_awards
    
    def show_master_prequal_list(self, limit=20):
        """Show sample of master prequalification list"""
        print(f"\n📋 MASTER PREQUALIFICATION LIST (showing first {limit}):")
        print("-" * 50)
        for i, prequal in enumerate(self.master_prequals[:limit]):
            print(f"{i+1:2d}. {prequal}")
        if len(self.master_prequals) > limit:
            print(f"... and {len(self.master_prequals) - limit} more")

def main():
    """Main function"""
    extractor = UniversalPTBExtractor()
    
    # Show master list
    extractor.show_master_prequal_list()
    
    # Test with PTB160
    print(f"\n🧪 TESTING WITH PTB160:")
    print("-" * 30)
    enhanced_awards = extractor.process_ptb_universal(160)
    
    # Show sample results
    if enhanced_awards:
        print(f"\n📋 SAMPLE UNIVERSAL EXTRACTION RESULTS:")
        print("-" * 50)
        for i, award in enumerate(enhanced_awards[:3]):
            print(f"Award {i+1}:")
            print(f"  Job: {award.get('Job #')}")
            print(f"  Firm: {award.get('SELECTED FIRM')}")
            print(f"  Prequals: {award.get('required_prequals')}")
            print()

if __name__ == "__main__":
    main()




