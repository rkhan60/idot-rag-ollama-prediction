#!/usr/bin/env python3
"""
Fix Final Mismatch
Fix the final mismatch: Special Studies (Traffic) vs Special Studies (Traffic Studies)
"""

import json
import os
from datetime import datetime

def fix_final_mismatch():
    """Fix the final mismatch"""
    print("🔧 FIXING FINAL MISMATCH")
    print("=" * 40)
    
    # Load prequal_lookup.json
    print("📂 Loading prequal_lookup.json...")
    with open('../data/prequal_lookup.json', 'r') as f:
        prequal_lookup = json.load(f)
        
    print(f"✅ Loaded {len(prequal_lookup)} categories")
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f'../data/backups/prequal_lookup_final_fix_{timestamp}.json'
    
    print(f"📦 Creating backup: {backup_path}")
    with open(backup_path, 'w') as f:
        json.dump(prequal_lookup, f, indent=2)
    print("✅ Backup created successfully")
    
    # Fix the final mismatch
    print("\n🔧 Applying final fix...")
    fixed_lookup = {}
    
    for category, firms in prequal_lookup.items():
        if category == "Special Studies (Traffic Studies)":
            new_category = "Special Studies (Traffic)"
            fixed_lookup[new_category] = firms
            print(f"  FIXED: {category} → {new_category}")
        else:
            fixed_lookup[category] = firms
            
    # Save fixed prequal_lookup.json
    print(f"\n💾 Saving fixed prequal_lookup.json...")
    with open('../data/prequal_lookup.json', 'w') as f:
        json.dump(fixed_lookup, f, indent=2)
        
    print("✅ prequal_lookup.json fixed successfully!")
    
    # Test bulletin mapping
    print(f"\n🧪 TESTING FINAL BULLETIN MAPPING")
    print("=" * 50)
    
    bulletin_examples = [
        "Special Services (Subsurface Utility Engineering)",
        "Special Services (Construction Inspection)",
        "Special Studies (Traffic)",
        "Highways (Roads & Streets)",
        "Structures (Highway: Typical)",
        "Location Design Studies (Reconstruction/Major Rehabilitation)",
        "Structures (Highway: Complex)"
    ]
    
    matches = 0
    total = len(bulletin_examples)
    
    for bulletin_example in bulletin_examples:
        if bulletin_example in fixed_lookup:
            print(f"✅ MATCH: {bulletin_example}")
            matches += 1
        else:
            print(f"❌ NO MATCH: {bulletin_example}")
            
    accuracy = (matches / total) * 100 if total > 0 else 0
    
    print(f"\n📊 FINAL MAPPING ACCURACY:")
    print(f"   Matches: {matches}/{total}")
    print(f"   Accuracy: {accuracy:.2f}%")
    
    if accuracy == 100:
        print("🎉 PERFECT MAPPING ACCURACY!")
    else:
        print("⚠️  Still need improvements")
        
    return accuracy

if __name__ == "__main__":
    accuracy = fix_final_mismatch()
    
    print(f"\n🎯 FINAL SUMMARY:")
    print(f"   Final Fix: COMPLETED")
    print(f"   Bulletin Mapping Accuracy: {accuracy:.2f}%")
    
    if accuracy == 100:
        print("✅ PERFECT! Ready for final verification!")
    else:
        print("⚠️  Still need improvements")
