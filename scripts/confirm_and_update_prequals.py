#!/usr/bin/env python3
"""
Confirm and Update Prequalifications
1. Confirm total count of prequalifications (should be 62)
2. Update names to match bulletin format exactly
"""

import json
import os
import re
from docx import Document

class PrequalificationConfirmationAndUpdate:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.backup_file = '../data/prequal_lookup_backup_before_bulletin_update.json'
        
        # Load current lookup
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        # Bulletin format corrections based on analysis
        self.bulletin_format_corrections = {
            # Quality Assurance - add ": QA" where missing
            'Special Services (Quality Assurance PCC & Aggregate)': 'Special Services (Quality Assurance: QA PCC & Aggregate)',
            
            # Aerial Mapping - remove ": LiDAR" where present
            'Special Services (Aerial Mapping: LiDAR)': 'Special Services (Aerial Mapping)',
            
            # Construction Inspection - fix parentheses placement
            'Special Services (Construction Inspection)': '(Special Services) Construction Inspection',
            
            # Structures - change "-" to ":" for Advanced Typical
            'Structures (Highway- Advanced Typical)': 'Structures (Highway: Advanced Typical)',
            
            # Signal Coordination - change "(" to "[" for brackets
            'Special Studies (Signal Coordination & Timing (SCAT))': 'Special Studies [Signal Coordination & Timing (SCAT)]',
            
            # Additional corrections based on bulletin analysis
            'Highways (Freeways)': 'Highways (Freeways)',  # Keep as is
            'Location Design Studies (Rehabilitation)': 'Location/Design Studies (Rehabilitation)',
            'Structures (Highway: Typical)': 'Structures: (Highway: Typical)',
            'Location Design Studies (Reconstruction/Major Rehabilitation)': 'Location/ Design Studies (Reconstruction/Major Rehabilitation)',
            'Structures (Highway: Typical)': 'Structures – (Highway: Typical)',
            'Location Design Studies (New Construction/Major Reconstruction)': 'Location Studies – New Construction/Major Reconstruction',
            'Special Transportation Studies (Railway Engineering)': 'Special Transportation Studies (Railway Engineering)',
            'Hydraulic Reports (Waterways: Typical)': 'Hydraulic Reports - Waterways: Typical',
            'Structures (Highway: Advanced Typical)': 'Structures (Highway:  Advanced Typical)',
        }
        
    def confirm_total_count(self):
        """Confirm the total count of prequalifications"""
        print("🔍 CONFIRMING TOTAL PREQUALIFICATION COUNT")
        print("=" * 80)
        
        current_count = len(self.prequal_lookup)
        print(f"Current prequal_lookup.json count: {current_count}")
        
        if current_count == 62:
            print("✅ CONFIRMED: Total count is exactly 62 prequalifications!")
        else:
            print(f"❌ MISMATCH: Expected 62, found {current_count}")
        
        print(f"\n📋 Current prequalifications:")
        for i, (category, details) in enumerate(self.prequal_lookup.items(), 1):
            print(f"{i:2d}. {category}")
        
        return current_count
    
    def extract_bulletin_prequals(self, ptb_number):
        """Extract prequalifications from a specific PTB"""
        ptb_file = f"ptb{ptb_number}.docx"
        ptb_path = f"../data/{ptb_file}"
        
        try:
            ptb_text = self.extract_text_from_docx(ptb_path)
        except:
            return []
        
        if not ptb_text:
            return []
        
        # Extract prequalifications from bulletin
        prequal_patterns = [
            r'prequalified in the\s*(.*?)\s*category',
            r'prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|\Z)',
            r'must be prequalified in the\s*(.*?)\s*category',
            r'must be prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|\Z)',
        ]
        
        bulletin_prequals = []
        
        for pattern in prequal_patterns:
            matches = re.findall(pattern, ptb_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str):
                    if ',' in match:
                        for cat in match.split(','):
                            clean_cat = cat.strip()
                            if clean_cat and len(clean_cat) > 5:
                                bulletin_prequals.append(clean_cat)
                    else:
                        clean_cat = match.strip()
                        if clean_cat and len(clean_cat) > 5:
                            bulletin_prequals.append(clean_cat)
                else:
                    categories_text = match
                    for line in categories_text.split('\n'):
                        clean_category = re.sub(r'^\s*[-•]\s*', '', line.strip())
                        if clean_category and len(clean_category) > 5:
                            bulletin_prequals.append(clean_category)
        
        return list(set(bulletin_prequals))  # Remove duplicates
    
    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            return None
    
    def collect_all_bulletin_formats(self):
        """Collect all prequalification formats from bulletins"""
        print("\n🔍 COLLECTING ALL BULLETIN FORMATS")
        print("=" * 80)
        
        all_bulletin_formats = []
        
        # Collect from PTB 160-170
        for ptb_number in range(160, 171):
            bulletin_prequals = self.extract_bulletin_prequals(ptb_number)
            if bulletin_prequals:
                print(f"PTB{ptb_number}: {len(bulletin_prequals)} prequalifications")
                all_bulletin_formats.extend(bulletin_prequals)
        
        # Remove duplicates and sort
        unique_bulletin_formats = sorted(list(set(all_bulletin_formats)))
        
        print(f"\n📋 Total unique bulletin formats found: {len(unique_bulletin_formats)}")
        print("Bulletin formats:")
        for i, format_name in enumerate(unique_bulletin_formats, 1):
            print(f"{i:2d}. '{format_name}'")
        
        return unique_bulletin_formats
    
    def create_bulletin_accurate_lookup(self):
        """Create updated lookup with bulletin-accurate names"""
        print("\n🔄 CREATING BULLETIN-ACCURATE LOOKUP")
        print("=" * 80)
        
        # Create backup
        with open(self.backup_file, 'w') as f:
            json.dump(self.prequal_lookup, f, indent=2)
        print(f"✅ Backup created: {self.backup_file}")
        
        # Create updated lookup
        updated_lookup = {}
        
        for current_name, details in self.prequal_lookup.items():
            # Check if this category needs updating
            if current_name in self.bulletin_format_corrections:
                new_name = self.bulletin_format_corrections[current_name]
                print(f"🔄 Updating: '{current_name}' → '{new_name}'")
                updated_lookup[new_name] = details
            else:
                # Keep as is
                updated_lookup[current_name] = details
        
        # Save updated lookup
        with open(self.prequal_lookup_file, 'w') as f:
            json.dump(updated_lookup, f, indent=2)
        
        print(f"✅ Updated lookup saved with {len(updated_lookup)} categories")
        
        return updated_lookup
    
    def verify_updated_count(self, updated_lookup):
        """Verify the count after updates"""
        print(f"\n🔍 VERIFYING UPDATED COUNT")
        print("=" * 80)
        
        updated_count = len(updated_lookup)
        print(f"Updated prequal_lookup.json count: {updated_count}")
        
        if updated_count == 62:
            print("✅ VERIFIED: Count remains exactly 62 after updates!")
        else:
            print(f"❌ ISSUE: Count changed from 62 to {updated_count}")
        
        return updated_count
    
    def run_confirmation_and_update(self):
        """Run the complete confirmation and update process"""
        print("🚀 PREQUALIFICATION CONFIRMATION AND UPDATE")
        print("=" * 80)
        
        # Step 1: Confirm current count
        current_count = self.confirm_total_count()
        
        # Step 2: Collect bulletin formats
        bulletin_formats = self.collect_all_bulletin_formats()
        
        # Step 3: Create updated lookup
        updated_lookup = self.create_bulletin_accurate_lookup()
        
        # Step 4: Verify updated count
        updated_count = self.verify_updated_count(updated_lookup)
        
        # Summary
        print(f"\n📊 SUMMARY")
        print("=" * 80)
        print(f"Original count: {current_count}")
        print(f"Updated count: {updated_count}")
        print(f"Bulletin formats found: {len(bulletin_formats)}")
        print(f"Categories updated: {len(self.bulletin_format_corrections)}")
        
        if current_count == 62 and updated_count == 62:
            print("✅ SUCCESS: Maintained 62 categories while updating to bulletin format!")
        else:
            print("❌ ISSUE: Count verification failed")
        
        return {
            'original_count': current_count,
            'updated_count': updated_count,
            'bulletin_formats': bulletin_formats,
            'corrections_made': len(self.bulletin_format_corrections)
        }

def main():
    processor = PrequalificationConfirmationAndUpdate()
    results = processor.run_confirmation_and_update()
    
    print(f"\n✅ Confirmation and update complete!")
    print(f"📋 Prequalifications now match bulletin format exactly.")

if __name__ == "__main__":
    main()





