#!/usr/bin/env python3
"""
Fix Specialty Agents (Appraiser) category with correct firm list
"""

import json
import os

def fix_specialty_agents_appraiser():
    """Fix the Specialty Agents (Appraiser) category with the correct firm list"""
    
    # Load current data
    data_file = '../data/prequal_lookup.json'
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Correct firms for Specialty Agents (Appraiser)
    correct_firms = [
        '"T" Engineering Service, Ltd.',
        '1st AEROW Valuation Group',
        'ABNA ENGINEERING, INC.',
        'AMERICAN SURVEYING & ENGINEERING, Ltd.',
        'CBRE, Inc',
        'CHICAGO METRO REALTY VALUATION CORP.',
        'CIVILTECH ENGINEERING, INC.',
        'CRAWFORD, MURPHY, & TILLY, INC.',
        'DECA Properties',
        'Elder Valuation Services',
        'HAMPTON, LENZINI AND RENWICK, INC.',
        'HANSON PROFESSIONAL SERVICES INC.',
        'Jay Heap & Associates, Ltd.',
        'JLL Valuation & Advisory Services LLC',
        'Planning & Valuation Consultants, Inc.',
        'Valu Pros',
        'Webster & Associates, Inc.'
    ]
    
    # Create new firm entries
    new_firms = []
    for firm_name in correct_firms:
        # Generate firm code (F417-F433)
        firm_code = f"F{417 + len(new_firms)}"
        
        firm_entry = {
            "firm_code": firm_code,
            "firm_name": firm_name,
            "email": "",
            "dbe_status": "NO",
            "location": "",
            "city": "",
            "state": "",
            "prequalifications": ["Specialty Agents (Appraiser)"],
            "processing_date": "2025-08-07T00:00:00.000000",
            "last_updated": "2025-08-07T00:00:00.000000"
        }
        new_firms.append(firm_entry)
    
    # Update the category
    category = 'Specialty Agents (Appraiser)'
    data[category] = new_firms
    
    # Save updated data
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ FIXED: {category}")
    print(f"   Updated with {len(correct_firms)} firms")
    print(f"   Firm codes: F417-F{416 + len(correct_firms)}")
    
    # Verify the fix
    print(f"\n📋 VERIFICATION:")
    print(f"   Category: {category}")
    print(f"   Firms in data: {len(data[category])}")
    print(f"   Expected: {len(correct_firms)}")
    
    if len(data[category]) == len(correct_firms):
        print("   ✅ Count matches!")
    else:
        print("   ❌ Count mismatch!")

if __name__ == "__main__":
    fix_specialty_agents_appraiser()





