#!/usr/bin/env python3
"""
Bulletin Format Changes - Exact Changes Needed
Identify exact bulletin format changes needed for 100% accuracy
"""

import json
import re
from docx import Document

class BulletinFormatChanges:
    def __init__(self):
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        
        # Load current lookup
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        # Key bulletin format differences found
        self.bulletin_format_changes = {
            # Missing categories that need to be added
            'missing_categories': [
                'Highways (Freeways)',  # Found in multiple PTBs
                'Location/Design Studies (Rehabilitation)',  # Found in PTB 165, 170
                'Special Studies [Signal Coordination & Timing (SCAT)]',  # Found in PTB 167
                'Special Services (Quality Assurance: QA PCC and Aggregate)',  # Found in PTB 167
                'Special Services: Electrical Engineering',  # Found in PTB 165
                'Structures: Highway (Simple)',  # Found in PTB 165
                'Highways: (Roads and Streets)',  # Found in PTB 163
                'Structures: (Highway: Typical)',  # Found in PTB 163
                'Location/ Design Studies (Reconstruction/Major Rehabilitation)',  # Found in PTB 169
                'Structures – (Highway: Typical)',  # Found in PTB 169
                'Location Studies – New Construction/Major Reconstruction',  # Found in PTB 169
                'Special Transportation Studies (Railway Engineering)',  # Found in PTB 169
                'Hydraulic Reports - Waterways: Typical',  # Found in PTB 169
                'Location/ Design Studies (Reconstruction/Major Rehabilitation)',  # Found in PTB 170
                'Structures (Highway:  Advanced Typical)',  # Found in PTB 170
            ],
            
            # Format variations that need fuzzy matching updates
            'format_variations': {
                'brackets_vs_parentheses': {
                    'bulletin': 'Special Studies [Signal Coordination & Timing (SCAT)]',
                    'lookup': 'Special Studies (Signal Coordination & Timing (SCAT))'
                },
                'slash_vs_space': {
                    'bulletin': 'Location/Design Studies (Rehabilitation)',
                    'lookup': 'Location Design Studies (Rehabilitation)'
                },
                'colon_vs_hyphen': {
                    'bulletin': 'Highways: (Roads and Streets)',
                    'lookup': 'Highways (Roads and Streets)'
                },
                'dash_vs_hyphen': {
                    'bulletin': 'Structures – (Highway: Typical)',
                    'lookup': 'Structures (Highway: Typical)'
                },
                'space_after_colon': {
                    'bulletin': 'Structures (Highway:  Advanced Typical)',
                    'lookup': 'Structures (Highway- Advanced Typical)'
                }
            }
        }
    
    def analyze_current_lookup(self):
        """Analyze current lookup structure"""
        print("📊 CURRENT LOOKUP ANALYSIS")
        print("=" * 60)
        print(f"Total categories: {len(self.prequal_lookup)}")
        
        # Check for existing similar categories
        print("\n🔍 CHECKING FOR SIMILAR EXISTING CATEGORIES:")
        for missing in self.bulletin_format_changes['missing_categories']:
            similar = self.find_similar_categories(missing)
            if similar:
                print(f"'{missing}' → Similar: {similar}")
            else:
                print(f"'{missing}' → No similar found")
    
    def find_similar_categories(self, target):
        """Find similar categories in current lookup"""
        target_lower = target.lower()
        similar = []
        
        for category in self.prequal_lookup.keys():
            category_lower = category.lower()
            
            # Check for key word matches
            target_words = set(target_lower.split())
            category_words = set(category_lower.split())
            
            # If more than 50% of words match
            common_words = target_words.intersection(category_words)
            if len(common_words) / max(len(target_words), len(category_words)) > 0.5:
                similar.append(category)
        
        return similar[:3]  # Return top 3 matches
    
    def propose_changes(self):
        """Propose exact changes needed"""
        print("\n📋 PROPOSED CHANGES FOR 100% ACCURACY")
        print("=" * 60)
        
        print("\n1️⃣ MISSING CATEGORIES TO ADD:")
        print("-" * 40)
        for i, category in enumerate(self.bulletin_format_changes['missing_categories'], 1):
            print(f"{i:2d}. '{category}'")
        
        print("\n2️⃣ FUZZY MATCHING UPDATES NEEDED:")
        print("-" * 40)
        for variation_type, variation in self.bulletin_format_changes['format_variations'].items():
            print(f"• {variation_type}:")
            print(f"  Bulletin: '{variation['bulletin']}'")
            print(f"  Lookup:   '{variation['lookup']}'")
            print()
        
        print("\n3️⃣ IMPLEMENTATION PLAN:")
        print("-" * 40)
        print("Step 1: Add missing categories to prequal_lookup.json")
        print("Step 2: Update fuzzy matching logic to handle format variations")
        print("Step 3: Test with PTB 160-170 to verify 100% accuracy")
        
        return self.bulletin_format_changes
    
    def generate_updated_lookup(self):
        """Generate updated lookup with missing categories"""
        print("\n🔄 GENERATING UPDATED LOOKUP")
        print("=" * 60)
        
        # Create backup of current lookup
        backup_file = '../data/prequal_lookup_backup_before_bulletin_fixes.json'
        with open(backup_file, 'w') as f:
            json.dump(self.prequal_lookup, f, indent=2)
        print(f"✅ Backup created: {backup_file}")
        
        # Add missing categories
        updated_lookup = self.prequal_lookup.copy()
        
        for category in self.bulletin_format_changes['missing_categories']:
            if category not in updated_lookup:
                # Add empty list for new category
                updated_lookup[category] = []
                print(f"➕ Added: '{category}'")
        
        # Save updated lookup
        updated_file = '../data/prequal_lookup_updated.json'
        with open(updated_file, 'w') as f:
            json.dump(updated_lookup, f, indent=2)
        print(f"✅ Updated lookup saved: {updated_file}")
        
        return updated_lookup
    
    def generate_fuzzy_matching_updates(self):
        """Generate updated fuzzy matching logic"""
        print("\n🔧 GENERATING FUZZY MATCHING UPDATES")
        print("=" * 60)
        
        fuzzy_updates = """
# Updated fuzzy_match_prequal function with bulletin format support

def fuzzy_match_prequal(extracted_prequal):
    \"\"\"Fuzzy match extracted prequalification to lookup category with bulletin format support\"\"\"
    extracted = extracted_prequal.lower().replace(':', '').replace('-', ' ').strip()
    
    for lookup_category in prequal_lookup.keys():
        lookup = lookup_category.lower().replace(':', '').replace('-', ' ').strip()
        
        # Direct match
        if extracted == lookup:
            return lookup_category
        
        # Partial match
        if extracted in lookup or lookup in extracted:
            return lookup_category
        
        # Handle common variations
        variations = {
            'roads & streets': 'roads and streets',
            'roads and streets': 'roads & streets',
            'quality assurance: qa': 'quality assurance',
            'quality assurance qa': 'quality assurance',
            'location/design': 'location design',
            'location design': 'location/design',
        }
        
        if extracted in variations and variations[extracted] == lookup:
            return lookup_category
        if lookup in variations and variations[lookup] == extracted:
            return lookup_category
        
        # NEW: Handle bulletin format variations
        # Brackets vs parentheses
        if '[' in extracted and '(' in lookup:
            extracted_clean = extracted.replace('[', '(').replace(']', ')')
            if extracted_clean == lookup:
                return lookup_category
        
        # Slash vs space
        if '/' in extracted and ' ' in lookup:
            extracted_clean = extracted.replace('/', ' ')
            if extracted_clean == lookup:
                return lookup_category
        
        # Colon vs hyphen
        if ':' in extracted and '-' in lookup:
            extracted_clean = extracted.replace(':', '-')
            if extracted_clean == lookup:
                return lookup_category
        
        # Dash vs hyphen
        if '–' in extracted and '-' in lookup:
            extracted_clean = extracted.replace('–', '-')
            if extracted_clean == lookup:
                return lookup_category
        
        # Space after colon
        if '  ' in extracted and ' ' in lookup:
            extracted_clean = ' '.join(extracted.split())
            lookup_clean = ' '.join(lookup.split())
            if extracted_clean == lookup_clean:
                return lookup_category
        
        # Special handling for Quality Assurance variations
        if 'quality assurance' in extracted and 'quality assurance' in lookup:
            extracted_clean = extracted.replace('qa', '').replace(':', '').strip()
            lookup_clean = lookup.replace('qa', '').replace(':', '').strip()
            extracted_clean = ' '.join(extracted_clean.split())
            lookup_clean = ' '.join(lookup_clean.split())
            if extracted_clean == lookup_clean:
                return lookup_category
        
        # Special handling for Aerial Mapping variations
        if 'aerial mapping' in extracted and 'aerial mapping' in lookup:
            extracted_has_lidar = 'lidar' in extracted
            lookup_has_lidar = 'lidar' in lookup
            
            if extracted_has_lidar != lookup_has_lidar:
                extracted_clean = extracted.replace('lidar', '').strip()
                lookup_clean = lookup.replace('lidar', '').strip()
                extracted_clean = ' '.join(extracted_clean.split()).strip()
                lookup_clean = ' '.join(lookup_clean.split()).strip()
                extracted_clean = extracted_clean.replace(' )', ')')
                lookup_clean = lookup_clean.replace(' )', ')')
                
                if extracted_clean == lookup_clean:
                    return lookup_category
        
        # Special handling for Structures variations
        if 'structures' in extracted and 'structures' in lookup:
            if 'advanced typical' in extracted and 'advanced typical' in lookup:
                extracted_clean = extracted.replace(':', '-')
                lookup_clean = lookup.replace(':', '-')
                extracted_clean = ' '.join(extracted_clean.split())
                lookup_clean = ' '.join(lookup_clean.split())
                
                if extracted_clean == lookup_clean:
                    return lookup_category
    
    return None
"""
        
        # Save fuzzy matching updates
        with open('fuzzy_matching_updates.py', 'w') as f:
            f.write(fuzzy_updates)
        print("✅ Fuzzy matching updates saved: fuzzy_matching_updates.py")
        
        return fuzzy_updates
    
    def run_analysis(self):
        """Run complete analysis and generate recommendations"""
        print("🚀 BULLETIN FORMAT CHANGES ANALYSIS")
        print("=" * 60)
        
        # Analyze current lookup
        self.analyze_current_lookup()
        
        # Propose changes
        changes = self.propose_changes()
        
        # Generate updated files
        updated_lookup = self.generate_updated_lookup()
        fuzzy_updates = self.generate_fuzzy_matching_updates()
        
        print(f"\n✅ ANALYSIS COMPLETE!")
        print(f"📋 {len(changes['missing_categories'])} missing categories identified")
        print(f"🔧 {len(changes['format_variations'])} format variations identified")
        print(f"\n📄 Generated files:")
        print(f"  • prequal_lookup_updated.json")
        print(f"  • fuzzy_matching_updates.py")
        print(f"  • prequal_lookup_backup_before_bulletin_fixes.json")
        
        return changes

def main():
    analyzer = BulletinFormatChanges()
    changes = analyzer.run_analysis()
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Review the proposed changes above")
    print("2. Approve the changes to implement")
    print("3. Test with PTB 160-170 to verify 100% accuracy")

if __name__ == "__main__":
    main()





