#!/usr/bin/env python3
"""
Verify Quality Assurance Format in All Bulletins
Search all bulletins for exact Quality Assurance prequalification format
"""

import os
import re
from docx import Document

class QualityAssuranceFormatVerifier:
    def __init__(self):
        self.ptb_directory = '../data/'
        self.quality_assurance_patterns = [
            r'Quality Assurance[^.]*',
            r'QA[^.]*',
            r'PCC[^.]*',
            r'Aggregate[^.]*',
            r'prequalified.*Quality[^.]*',
            r'prequalified.*QA[^.]*',
            r'must be prequalified.*Quality[^.]*',
            r'must be prequalified.*QA[^.]*',
        ]
        
    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"❌ Error extracting text from {file_path}: {e}")
            return None
    
    def search_quality_assurance_in_ptb(self, ptb_number):
        """Search for Quality Assurance references in a specific PTB"""
        print(f"\n🔍 SEARCHING PTB{ptb_number} FOR QUALITY ASSURANCE FORMAT")
        print("=" * 80)
        
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
        
        # Search for Quality Assurance patterns
        found_matches = []
        
        for pattern in self.quality_assurance_patterns:
            matches = re.findall(pattern, ptb_text, re.IGNORECASE)
            for match in matches:
                if match not in found_matches:
                    found_matches.append(match)
        
        if found_matches:
            print(f"✅ Found {len(found_matches)} Quality Assurance references in PTB{ptb_number}:")
            for i, match in enumerate(found_matches, 1):
                print(f"  {i}. '{match}'")
            
            # Look for specific prequalification patterns
            prequal_patterns = [
                r'prequalified in the\s*(.*?Quality Assurance.*?)\s*category',
                r'prequalified in the following categories[^:]*:\s*([\s\S]*?Quality Assurance[^.]*?)(?=\n\n|\Z)',
                r'must be prequalified in the\s*(.*?Quality Assurance.*?)\s*category',
                r'must be prequalified in the following categories[^:]*:\s*([\s\S]*?Quality Assurance[^.]*?)(?=\n\n|\Z)',
            ]
            
            print(f"\n🔍 SEARCHING FOR SPECIFIC PREQUALIFICATION PATTERNS:")
            for pattern in prequal_patterns:
                matches = re.findall(pattern, ptb_text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, str):
                        print(f"  • '{match.strip()}'")
                    else:
                        print(f"  • '{match.strip()}'")
        else:
            print(f"❌ No Quality Assurance references found in PTB{ptb_number}")
        
        return found_matches
    
    def search_all_bulletins(self):
        """Search all bulletins for Quality Assurance format"""
        print("🚀 SEARCHING ALL BULLETINS FOR QUALITY ASSURANCE FORMAT")
        print("=" * 80)
        
        all_results = {}
        
        # Search PTB 160-170
        for ptb_number in range(160, 171):
            results = self.search_quality_assurance_in_ptb(ptb_number)
            if results:
                all_results[ptb_number] = results
        
        # Generate summary
        print(f"\n📊 QUALITY ASSURANCE FORMAT SUMMARY")
        print("=" * 80)
        
        if all_results:
            print(f"Found Quality Assurance references in {len(all_results)} PTBs:")
            for ptb_number, results in all_results.items():
                print(f"\nPTB{ptb_number}:")
                for result in results:
                    print(f"  • '{result}'")
        else:
            print("❌ No Quality Assurance references found in any PTB")
        
        return all_results
    
    def verify_specific_format(self):
        """Verify the specific format 'Special Services (Quality Assurance: QA PCC and Aggregate)'"""
        print(f"\n🎯 VERIFYING SPECIFIC FORMAT")
        print("=" * 80)
        
        target_format = "Special Services (Quality Assurance: QA PCC and Aggregate)"
        target_variations = [
            "Special Services (Quality Assurance: QA PCC and Aggregate)",
            "Special Services (Quality Assurance: QA PCC & Aggregate)",
            "Special Services (Quality Assurance PCC & Aggregate)",
            "Special Services (Quality Assurance: QA PCC and Aggregate)",
            "Quality Assurance: QA PCC and Aggregate",
            "Quality Assurance: QA PCC & Aggregate",
            "Quality Assurance PCC & Aggregate",
        ]
        
        found_exact_matches = []
        found_similar_matches = []
        
        for ptb_number in range(160, 171):
            ptb_file = f"ptb{ptb_number}.docx"
            ptb_path = os.path.join(self.ptb_directory, ptb_file)
            
            if not os.path.exists(ptb_path):
                continue
            
            ptb_text = self.extract_text_from_docx(ptb_path)
            if not ptb_text:
                continue
            
            # Search for exact format
            if target_format in ptb_text:
                found_exact_matches.append(ptb_number)
                print(f"✅ PTB{ptb_number}: Found EXACT format '{target_format}'")
            
            # Search for variations
            for variation in target_variations:
                if variation in ptb_text:
                    found_similar_matches.append((ptb_number, variation))
                    print(f"🔄 PTB{ptb_number}: Found variation '{variation}'")
        
        print(f"\n📋 SUMMARY:")
        print(f"Exact matches found in PTBs: {found_exact_matches}")
        print(f"Similar variations found: {len(found_similar_matches)}")
        
        if not found_exact_matches and not found_similar_matches:
            print(f"❌ WARNING: The format '{target_format}' was NOT found in any bulletin!")
            print(f"This suggests the format may be incorrect or needs verification.")
        
        return found_exact_matches, found_similar_matches

def main():
    verifier = QualityAssuranceFormatVerifier()
    
    # Search all bulletins
    all_results = verifier.search_all_bulletins()
    
    # Verify specific format
    exact_matches, similar_matches = verifier.verify_specific_format()
    
    print(f"\n✅ Quality Assurance format verification complete!")
    print(f"📋 Check the results above to verify the correct bulletin format.")

if __name__ == "__main__":
    main()





