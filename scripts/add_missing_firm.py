#!/usr/bin/env python3
"""
Add Missing Firm to Prequalification Lookup
Find prequalifications for "T" ENGINEERING SERVICE, LTD. and add to prequal_lookup.json
"""

import json
import pandas as pd
from collections import defaultdict

def add_missing_firm():
    """Add missing firm to prequal_lookup.json"""
    data_dir = '../data'
    
    print("🔍 Finding prequalifications for missing firm...")
    
    # Load IDOT Excel to find firm's prequalifications
    idot_excel = pd.read_excel(f'{data_dir}/IDOTConsultantList.xlsx', sheet_name='PrequalReport')
    print(f"✅ Loaded IDOT Excel PrequalReport: {idot_excel.shape}")
    
    # Find all prequalifications for "T" ENGINEERING SERVICE, LTD.
    target_firm = '"T" Engineering Service, Ltd.'
    firm_prequals = []
    
    for idx, row in idot_excel.iterrows():
        firm_name = row.get('Unnamed: 1')
        prequal_category = row.get('Unnamed: 3')
        
        if pd.notna(firm_name) and pd.notna(prequal_category):
            firm_name = str(firm_name).strip()
            prequal_category = str(prequal_category).strip()
            
            if firm_name == target_firm and prequal_category and prequal_category != 'PRE-QUAL CATEGORIES':
                firm_prequals.append(prequal_category)
                
    print(f"📊 Found {len(firm_prequals)} prequalifications for '{target_firm}':")
    for prequal in firm_prequals:
        print(f"  - {prequal}")
        
    # Load current prequal_lookup.json
    with open(f'{data_dir}/prequal_lookup.json', 'r') as f:
        prequal_lookup = json.load(f)
    print(f"✅ Loaded prequal_lookup.json: {len(prequal_lookup)} categories")
    
    # Find the firm code for "T" ENGINEERING SERVICE, LTD.
    firm_code = None
    for category, firms_list in prequal_lookup.items():
        if isinstance(firms_list, list):
            for firm_dict in firms_list:
                if isinstance(firm_dict, dict) and 'firm_name' in firm_dict:
                    if firm_dict['firm_name'] == target_firm:
                        firm_code = firm_dict['firm_code']
                        break
            if firm_code:
                break
                
    if not firm_code:
        # If not found, we need to find the next available firm code
        existing_codes = set()
        for category, firms_list in prequal_lookup.items():
            if isinstance(firms_list, list):
                for firm_dict in firms_list:
                    if isinstance(firm_dict, dict) and 'firm_code' in firm_dict:
                        existing_codes.add(firm_dict['firm_code'])
                        
        # Find the highest firm code number
        max_code_num = 0
        for code in existing_codes:
            if code.startswith('F') and code[1:].isdigit():
                max_code_num = max(max_code_num, int(code[1:]))
                
        firm_code = f"F{max_code_num + 1:03d}"
        print(f"📊 Generated new firm code: {firm_code}")
    else:
        print(f"📊 Found existing firm code: {firm_code}")
        
    # Create firm entry
    firm_entry = {
        'firm_code': firm_code,
        'firm_name': target_firm
    }
    
    # Add firm to each prequalification category
    added_categories = []
    skipped_categories = []
    
    for prequal_category in firm_prequals:
        # Check if category exists in prequal_lookup
        if prequal_category in prequal_lookup:
            # Check if firm is already in this category
            firm_exists = False
            for firm_dict in prequal_lookup[prequal_category]:
                if isinstance(firm_dict, dict) and firm_dict.get('firm_name') == target_firm:
                    firm_exists = True
                    break
                    
            if not firm_exists:
                prequal_lookup[prequal_category].append(firm_entry)
                added_categories.append(prequal_category)
            else:
                skipped_categories.append(prequal_category)
        else:
            # Category doesn't exist, create it
            prequal_lookup[prequal_category] = [firm_entry]
            added_categories.append(prequal_category)
            
    print(f"\n📊 ADDITION RESULTS:")
    print(f"  - Added to {len(added_categories)} categories")
    print(f"  - Skipped {len(skipped_categories)} categories (already present)")
    
    if added_categories:
        print(f"\n✅ ADDED TO CATEGORIES:")
        for cat in added_categories:
            print(f"  - {cat}")
            
    if skipped_categories:
        print(f"\n⚠️  SKIPPED CATEGORIES (already present):")
        for cat in skipped_categories:
            print(f"  - {cat}")
            
    # Save updated prequal_lookup.json
    backup_file = f'{data_dir}/prequal_lookup_backup_before_adding_firm.json'
    with open(backup_file, 'w') as f:
        json.dump(prequal_lookup, f, indent=2)
    print(f"\n💾 Created backup: {backup_file}")
    
    # Save updated file
    with open(f'{data_dir}/prequal_lookup.json', 'w') as f:
        json.dump(prequal_lookup, f, indent=2)
    print(f"✅ Updated prequal_lookup.json")
    
    # Verify the addition
    print(f"\n🔍 VERIFICATION:")
    total_firms_after = 0
    for category, firms_list in prequal_lookup.items():
        if isinstance(firms_list, list):
            total_firms_after += len(firms_list)
            
    print(f"  - Total firm entries after update: {total_firms_after}")
    print(f"  - Categories in lookup: {len(prequal_lookup)}")
    
    # Check if firm is now in all its prequalifications
    firm_found_in = 0
    for prequal_category in firm_prequals:
        if prequal_category in prequal_lookup:
            for firm_dict in prequal_lookup[prequal_category]:
                if isinstance(firm_dict, dict) and firm_dict.get('firm_name') == target_firm:
                    firm_found_in += 1
                    break
                    
    print(f"  - Firm found in {firm_found_in}/{len(firm_prequals)} prequalifications")
    
    if firm_found_in == len(firm_prequals):
        print(f"✅ SUCCESS: Firm added to all prequalifications!")
    else:
        print(f"⚠️  WARNING: Firm not found in all prequalifications")

if __name__ == "__main__":
    add_missing_firm()
