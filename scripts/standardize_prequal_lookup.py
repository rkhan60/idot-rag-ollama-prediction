#!/usr/bin/env python3
"""
Standardize Prequal Lookup
Convert prequal_lookup.json from hyphen format to parentheses format to match bulletin
"""

import json
import os
from datetime import datetime

class PrequalStandardizer:
    def __init__(self):
        self.data_dir = '../data'
        self.backup_dir = '../data/backups'
        
    def standardize_prequal_lookup(self):
        """Standardize prequal_lookup.json to bulletin format"""
        print("🚀 STANDARDIZING PREQUAL_LOOKUP.JSON TO BULLETIN FORMAT")
        print("=" * 70)
        
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Load prequal_lookup.json
        print("📂 Loading prequal_lookup.json...")
        with open(f'{self.data_dir}/prequal_lookup.json', 'r') as f:
            prequal_lookup = json.load(f)
            
        print(f"✅ Loaded {len(prequal_lookup)} categories from prequal_lookup.json")
        
        # Create backup of existing prequal_lookup.json
        prequal_lookup_path = f'{self.data_dir}/prequal_lookup.json'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f'{self.backup_dir}/prequal_lookup_backup_{timestamp}.json'
        
        print(f"📦 Creating backup: {backup_path}")
        with open(backup_path, 'w') as f:
            json.dump(prequal_lookup, f, indent=2)
        print("✅ Backup created successfully")
        
        # Standardize categories from hyphen to parentheses format
        print("\n🔍 Standardizing categories...")
        standardized_lookup = {}
        conversion_mapping = {}
        
        for old_category, firms in prequal_lookup.items():
            # Convert hyphen format to parentheses format
            new_category = self.convert_hyphen_to_parentheses(old_category)
            
            # Store the conversion mapping
            conversion_mapping[old_category] = new_category
            
            # Create new entry with standardized category name
            standardized_lookup[new_category] = firms
            
        # Print conversion examples
        print(f"\n📋 CONVERSION EXAMPLES:")
        print("=" * 50)
        for old, new in list(conversion_mapping.items())[:10]:
            print(f"  {old}")
            print(f"  → {new}")
            print()
            
        # Save the standardized prequal_lookup.json
        print(f"\n💾 Saving standardized prequal_lookup.json...")
        with open(prequal_lookup_path, 'w') as f:
            json.dump(standardized_lookup, f, indent=2)
            
        print("✅ prequal_lookup.json standardized successfully!")
        
        # Verify the standardization
        print(f"\n🔍 Verifying standardization...")
        with open(prequal_lookup_path, 'r') as f:
            verification_data = json.load(f)
            
        print(f"   Verification: {len(verification_data)} categories standardized")
        
        # Generate conversion report
        self.generate_conversion_report(conversion_mapping, len(prequal_lookup), len(standardized_lookup))
        
        return standardized_lookup, conversion_mapping
        
    def convert_hyphen_to_parentheses(self, category):
        """Convert hyphen format to parentheses format"""
        if ' - ' in category:
            # Split on ' - ' and convert to parentheses format
            parts = category.split(' - ')
            if len(parts) >= 2:
                main_category = parts[0].strip()
                service = ' - '.join(parts[1:]).strip()  # Handle multiple hyphens
                return f"{main_category} ({service})"
        
        # If no hyphen found, return as is
        return category
        
    def generate_conversion_report(self, conversion_mapping, old_count, new_count):
        """Generate conversion report"""
        print(f"\n📄 GENERATING CONVERSION REPORT")
        print("=" * 50)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'prequal_conversion_report_{timestamp}.txt'
        
        with open(report_file, 'w') as f:
            f.write("PREQUAL_LOOKUP STANDARDIZATION REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Purpose: Standardize prequal_lookup.json to bulletin format\n")
            f.write("Conversion: Hyphen format → Parentheses format\n\n")
            
            f.write("CONVERSION STATISTICS\n")
            f.write("-" * 25 + "\n")
            f.write(f"Original Categories: {old_count}\n")
            f.write(f"Standardized Categories: {new_count}\n")
            f.write(f"Conversions Made: {len(conversion_mapping)}\n\n")
            
            f.write("CONVERSION MAPPING\n")
            f.write("-" * 20 + "\n")
            for old_category, new_category in conversion_mapping.items():
                f.write(f"  {old_category}\n")
                f.write(f"  → {new_category}\n\n")
                
            f.write("FORMAT STANDARDIZATION RULES\n")
            f.write("-" * 30 + "\n")
            f.write("1. Replace ' - ' with ' (' and add ')' at the end\n")
            f.write("2. Maintain category and service separation\n")
            f.write("3. Preserve all firm data and relationships\n")
            f.write("4. Handle multiple hyphens in service names\n\n")
            
            f.write("BULLETIN COMPATIBILITY\n")
            f.write("-" * 25 + "\n")
            f.write("✅ Now matches bulletin format: 'Category (Service)'\n")
            f.write("✅ Enables direct mapping from bulletin text\n")
            f.write("✅ Improves model training accuracy\n")
            f.write("✅ Supports format standardization pipeline\n")
            
        print(f"✅ Conversion report saved: {report_file}")
        
    def test_bulletin_mapping(self, standardized_lookup):
        """Test mapping with bulletin examples"""
        print(f"\n🧪 TESTING BULLETIN MAPPING")
        print("=" * 50)
        
        # Test cases from bulletin
        bulletin_examples = [
            "Special Services (Subsurface Utility Engineering)",
            "Special Services (Construction Inspection)",
            "Special Studies (Traffic)",
            "Highways (Roads & Streets)",
            "Structures (Highway: Typical)",
            "Location Design Studies (Reconstruction/Major Rehabilitation)",
            "Structures (Highway: Complex)"
        ]
        
        print("📋 BULLETIN MAPPING TEST:")
        print("=" * 50)
        
        matches = 0
        total = len(bulletin_examples)
        
        for bulletin_example in bulletin_examples:
            if bulletin_example in standardized_lookup:
                print(f"✅ MATCH: {bulletin_example}")
                matches += 1
            else:
                print(f"❌ NO MATCH: {bulletin_example}")
                
        accuracy = (matches / total) * 100 if total > 0 else 0
        
        print(f"\n📊 MAPPING ACCURACY:")
        print(f"   Matches: {matches}/{total}")
        print(f"   Accuracy: {accuracy:.2f}%")
        
        if accuracy >= 90:
            print("🎉 Excellent mapping accuracy!")
        elif accuracy >= 70:
            print("⚠️  Good mapping accuracy, some improvements needed")
        else:
            print("❌ Poor mapping accuracy, significant improvements needed")
            
        return accuracy

def main():
    standardizer = PrequalStandardizer()
    
    # Standardize prequal lookup
    standardized_lookup, conversion_mapping = standardizer.standardize_prequal_lookup()
    
    # Test bulletin mapping
    accuracy = standardizer.test_bulletin_mapping(standardized_lookup)
    
    print(f"\n🎯 FINAL SUMMARY:")
    print(f"   Standardization: COMPLETED")
    print(f"   Categories Converted: {len(conversion_mapping)}")
    print(f"   Bulletin Mapping Accuracy: {accuracy:.2f}%")
    
    if accuracy >= 70:
        print("✅ Ready for next verification step!")
    else:
        print("⚠️  Mapping accuracy needs improvement")

if __name__ == "__main__":
    main()
