#!/usr/bin/env python3
"""
Fix Bulletin Mismatches
Fix specific mismatches between bulletin examples and standardized lookup
"""

import json
import os
from datetime import datetime

class BulletinMismatchFixer:
    def __init__(self):
        self.data_dir = '../data'
        self.backup_dir = '../data/backups'
        
    def fix_bulletin_mismatches(self):
        """Fix specific mismatches between bulletin and lookup"""
        print("🔧 FIXING BULLETIN MISMATCHES")
        print("=" * 50)
        
        # Load standardized prequal_lookup.json
        print("📂 Loading standardized prequal_lookup.json...")
        with open(f'{self.data_dir}/prequal_lookup.json', 'r') as f:
            prequal_lookup = json.load(f)
            
        print(f"✅ Loaded {len(prequal_lookup)} categories")
        
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f'{self.backup_dir}/prequal_lookup_before_fix_{timestamp}.json'
        
        print(f"📦 Creating backup: {backup_path}")
        with open(backup_path, 'w') as f:
            json.dump(prequal_lookup, f, indent=2)
        print("✅ Backup created successfully")
        
        # Define specific fixes needed
        fixes = {
            # Bulletin: "Special Studies (Traffic)" vs Lookup: "Special Studies (Traffic Studies)"
            "Special Studies (Traffic Studies)": "Special Studies (Traffic)",
            
            # Bulletin: "Highways (Roads & Streets)" vs Lookup: "Highways (Roads and Streets)"
            "Highways (Roads and Streets)": "Highways (Roads & Streets)",
            
            # Bulletin: "Structures (Highway: Typical)" vs Lookup: "Structures (Highway- Typical)"
            "Structures (Highway- Typical)": "Structures (Highway: Typical)",
            
            # Bulletin: "Location Design Studies (Reconstruction/Major Rehabilitation)" vs Lookup: "Location Design Studies (Reconstruction:Major Rehabilitation)"
            "Location Design Studies (Reconstruction:Major Rehabilitation)": "Location Design Studies (Reconstruction/Major Rehabilitation)",
            
            # Bulletin: "Structures (Highway: Complex)" vs Lookup: "Structures (Highway- Complex)"
            "Structures (Highway- Complex)": "Structures (Highway: Complex)",
            
            # Additional fixes for other variations
            "Airports (Design- Complex Electrical)": "Airports (Design: Complex Electrical)",
            "Airports (Construction Inspection- Complex Electrical)": "Airports (Construction Inspection: Complex Electrical)",
            "Special Services (Hazardous Waste- Advance)": "Special Services (Hazardous Waste: Advance)",
            "Special Services (Hazardous Waste- Simple)": "Special Services (Hazardous Waste: Simple)",
            "Special Plans (Lighting- Complex)": "Special Plans (Lighting: Complex)",
            "Special Plans (Lighting- Typical)": "Special Plans (Lighting: Typical)",
            "Hydraulic Reports (Waterways- Typical)": "Hydraulic Reports (Waterways: Typical)",
            "Hydraulic Reports (Waterways- Complex)": "Hydraulic Reports (Waterways: Complex)",
            "Hydraulic Reports (Waterways- Two-Dimensional Hydraulics (2D))": "Hydraulic Reports (Waterways: Two-Dimensional Hydraulics (2D))",
            "Geotechnical Services (Complex Geotech:Major Foundation)": "Geotechnical Services (Complex Geotech: Major Foundation)",
            "Special Studies (Signal Coordination & Timing (SCAT))": "Special Studies (Signal Coordination & Timing (SCAT))",
            "Special Studies (Location Drainage)": "Special Studies (Location Drainage)",
            "Special Services (Aerial Mapping:LiDAR)": "Special Services (Aerial Mapping: LiDAR)",
            "Special Services (Mobile LiDAR)": "Special Services (Mobile LiDAR)",
            "Special Services (Quality Assurance HMA & Aggregate)": "Special Services (Quality Assurance HMA & Aggregate)",
            "Special Services (Quality Assurance PCC & Aggregate)": "Special Services (Quality Assurance PCC & Aggregate)",
            "Special Services (Subsurface Utility Engineering)": "Special Services (Subsurface Utility Engineering)",
            "Special Services (Construction Inspection)": "Special Services (Construction Inspection)",
            "Special Services (Surveying)": "Special Services (Surveying)",
            "Special Services (Architecture)": "Special Services (Architecture)",
            "Special Services (Electrical Engineering)": "Special Services (Electrical Engineering)",
            "Special Services (Mechanical)": "Special Services (Mechanical)",
            "Special Services (Landscape Architecture)": "Special Services (Landscape Architecture)",
            "Special Services (Project Controls)": "Special Services (Project Controls)",
            "Special Services (Public Involvement)": "Special Services (Public Involvement)",
            "Special Services (Quality Assurance HMA & Aggregate)": "Special Services (Quality Assurance HMA & Aggregate)",
            "Special Services (Quality Assurance PCC & Aggregate)": "Special Services (Quality Assurance PCC & Aggregate)",
            "Special Services (Sanitary)": "Special Services (Sanitary)",
            "Special Services (Specialty Firm)": "Special Services (Specialty Firm)",
            "Special Services (Asbestos Abatement Surveys)": "Special Services (Asbestos Abatement Surveys)",
            "Special Plans (Lighting: Complex)": "Special Plans (Lighting: Complex)",
            "Special Plans (Lighting: Typical)": "Special Plans (Lighting: Typical)",
            "Special Plans (Pumping Stations)": "Special Plans (Pumping Stations)",
            "Special Plans (Traffic Signals)": "Special Plans (Traffic Signals)",
            "Structures (Highway: Advanced Typical)": "Structures (Highway: Advanced Typical)",
            "Structures (Highway: Simple)": "Structures (Highway: Simple)",
            "Structures (Highway: Typical)": "Structures (Highway: Typical)",
            "Structures (Highway: Complex)": "Structures (Highway: Complex)",
            "Structures (Major River Bridges)": "Structures (Major River Bridges)",
            "Structures (Moveable)": "Structures (Moveable)",
            "Structures (Railroad)": "Structures (Railroad)",
            "Airports (Construction Inspection)": "Airports (Construction Inspection)",
            "Airports (Construction Inspection: Complex Electrical)": "Airports (Construction Inspection: Complex Electrical)",
            "Airports (Design)": "Airports (Design)",
            "Airports (Design: Complex Electrical)": "Airports (Design: Complex Electrical)",
            "Airports (Master Planning: Airport Layout Plans (ALP))": "Airports (Master Planning: Airport Layout Plans (ALP))",
            "Environmental Reports (Environmental Assessment)": "Environmental Reports (Environmental Assessment)",
            "Environmental Reports (Environmental Impact Statement)": "Environmental Reports (Environmental Impact Statement)",
            "Geotechnical Services (Complex Geotech: Major Foundation)": "Geotechnical Services (Complex Geotech: Major Foundation)",
            "Geotechnical Services (General Geotechnical Services)": "Geotechnical Services (General Geotechnical Services)",
            "Geotechnical Services (Structure Geotechnical Reports (SGR))": "Geotechnical Services (Structure Geotechnical Reports (SGR))",
            "Geotechnical Services (Subsurface Explorations)": "Geotechnical Services (Subsurface Explorations)",
            "Highways (Freeways)": "Highways (Freeways)",
            "Highways (Roads & Streets)": "Highways (Roads & Streets)",
            "Hydraulic Reports (Pump Stations)": "Hydraulic Reports (Pump Stations)",
            "Hydraulic Reports (Waterways: Complex)": "Hydraulic Reports (Waterways: Complex)",
            "Hydraulic Reports (Waterways: Typical)": "Hydraulic Reports (Waterways: Typical)",
            "Hydraulic Reports (Waterways: Two-Dimensional Hydraulics (2D))": "Hydraulic Reports (Waterways: Two-Dimensional Hydraulics (2D))",
            "Location Design Studies (New Construction: Major Reconstruction)": "Location Design Studies (New Construction: Major Reconstruction)",
            "Location Design Studies (Reconstruction: Major Rehabilitation)": "Location Design Studies (Reconstruction: Major Rehabilitation)",
            "Location Design Studies (Reconstruction/Major Rehabilitation)": "Location Design Studies (Reconstruction/Major Rehabilitation)",
            "Location Design Studies (Rehabilitation)": "Location Design Studies (Rehabilitation)",
            "Special Studies (Feasibility)": "Special Studies (Feasibility)",
            "Special Studies (Location Drainage)": "Special Studies (Location Drainage)",
            "Special Studies (Pavement Analysis and Evaluation)": "Special Studies (Pavement Analysis and Evaluation)",
            "Special Studies (Safety)": "Special Studies (Safety)",
            "Special Studies (Signal Coordination & Timing (SCAT))": "Special Studies (Signal Coordination & Timing (SCAT))",
            "Special Studies (Traffic)": "Special Studies (Traffic)",
            "Special Studies (Traffic Studies)": "Special Studies (Traffic Studies)",
            "Specialty Agents (Appraiser)": "Specialty Agents (Appraiser)",
            "Specialty Agents (Negotiator)": "Specialty Agents (Negotiator)",
            "Specialty Agents (Relocation Agent)": "Specialty Agents (Relocation Agent)",
            "Specialty Agents (Review Appraiser)": "Specialty Agents (Review Appraiser)",
            "Transportation Studies (Mass Transit)": "Transportation Studies (Mass Transit)",
            "Transportation Studies (Railway Engineering)": "Transportation Studies (Railway Engineering)",
            "Transportation Studies (Railway Planning)": "Transportation Studies (Railway Planning)"
        }
        
        # Apply fixes
        print("\n🔧 Applying fixes...")
        fixed_lookup = {}
        fixes_applied = 0
        
        for old_category, firms in prequal_lookup.items():
            if old_category in fixes:
                new_category = fixes[old_category]
                fixed_lookup[new_category] = firms
                print(f"  FIXED: {old_category} → {new_category}")
                fixes_applied += 1
            else:
                fixed_lookup[old_category] = firms
                
        print(f"\n📊 FIXES APPLIED: {fixes_applied}")
        
        # Save fixed prequal_lookup.json
        print(f"\n💾 Saving fixed prequal_lookup.json...")
        with open(f'{self.data_dir}/prequal_lookup.json', 'w') as f:
            json.dump(fixed_lookup, f, indent=2)
            
        print("✅ prequal_lookup.json fixed successfully!")
        
        # Test bulletin mapping again
        accuracy = self.test_bulletin_mapping(fixed_lookup)
        
        return fixed_lookup, accuracy
        
    def test_bulletin_mapping(self, fixed_lookup):
        """Test mapping with bulletin examples"""
        print(f"\n🧪 TESTING BULLETIN MAPPING AFTER FIXES")
        print("=" * 60)
        
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
            if bulletin_example in fixed_lookup:
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
    fixer = BulletinMismatchFixer()
    
    # Fix bulletin mismatches
    fixed_lookup, accuracy = fixer.fix_bulletin_mismatches()
    
    print(f"\n🎯 FINAL SUMMARY:")
    print(f"   Mismatches Fixed: COMPLETED")
    print(f"   Bulletin Mapping Accuracy: {accuracy:.2f}%")
    
    if accuracy >= 70:
        print("✅ Ready for final verification!")
    else:
        print("⚠️  Still need improvements")

if __name__ == "__main__":
    main()
