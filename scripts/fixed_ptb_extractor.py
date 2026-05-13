#!/usr/bin/env python3
"""
Fixed PTB Extractor
==================
Fixed extraction system that properly captures all prequalifications.
"""

import re
import json
from datetime import datetime
from docx import Document

class FixedPTBExtractor:
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
    
    def extract_prequalifications_fixed(self, project_text):
        """Fixed prequalification extraction that captures all prequals"""
        prequalifications = []
        
        # Look for the specific pattern: "Firms must be prequalified in the following categories"
        categories_pattern = r'Firms must be prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|Statements of Interest|$)'
        categories_match = re.search(categories_pattern, project_text, re.IGNORECASE)
        
        if categories_match:
            categories_text = categories_match.group(1)
            print(f"📋 Found categories text: {categories_text[:200]}...")
            
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
                        print(f"✅ Extracted: {full_prequal}")
        
        # Also look for individual "prequalified in the" patterns
        individual_pattern = r'prequalified in the ([^)]*\([^)]*\)[^)]*) category'
        individual_matches = re.findall(individual_pattern, project_text, re.IGNORECASE)
        
        for match in individual_matches:
            if match not in prequalifications:
                prequalifications.append(match.strip())
                print(f"✅ Extracted individual: {match.strip()}")
        
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
                extracted_sub = extracted.split('(')[-1].split(')')[0] if '(' in extracted else ''
                lookup_sub = lookup.split('(')[-1].split(')')[0] if '(' in lookup else ''
                
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
    
    def process_ptb160_fixed(self):
        """Process PTB160 with fixed extraction"""
        print("🔧 PROCESSING PTB160 WITH FIXED EXTRACTION")
        print("=" * 50)
        
        # Load PTB160 document
        doc_path = '../../ptb160.docx'
        ptb_text = self.extract_text_from_docx(doc_path)
        
        if not ptb_text:
            print("❌ Could not load PTB160 document")
            return
        
        # Find P-30-006-12 section
        job_pattern = r'Job No\.\s*P-30-006-12[^.]*\.(.*?)(?=Job No\.|$)'
        job_match = re.search(job_pattern, ptb_text, re.DOTALL | re.IGNORECASE)
        
        if job_match:
            job_text = job_match.group(1)
            print("📄 PROCESSING P-30-006-12:")
            print("-" * 30)
            
            # Extract prequalifications with fixed method
            prequalifications = self.extract_prequalifications_fixed(job_text)
            
            print(f"\n📊 EXTRACTION RESULTS:")
            print("-" * 30)
            print(f"Total prequalifications found: {len(prequalifications)}")
            for i, prequal in enumerate(prequalifications, 1):
                print(f"{i}. {prequal}")
            
            # Check if we found the missing one
            missing_prequal = "Location/Design Studies (New Construction/Major Reconstruction)"
            if missing_prequal in prequalifications:
                print(f"\n✅ SUCCESS: Found missing prequalification '{missing_prequal}'")
            else:
                print(f"\n❌ STILL MISSING: '{missing_prequal}'")
                
        else:
            print("❌ P-30-006-12 not found in PTB160")

def main():
    """Main function"""
    extractor = FixedPTBExtractor()
    extractor.process_ptb160_fixed()

if __name__ == "__main__":
    main()
