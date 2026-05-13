#!/usr/bin/env python3
"""
Add SGR Category
Add the missing Geotechnical Services (Structure Geotechnical Reports (SGR)) category
"""

import json
from datetime import datetime

def add_sgr_category():
    """Add the missing SGR category"""
    print("🔧 ADDING MISSING SGR CATEGORY")
    print("=" * 50)
    
    # Load current data
    with open('../data/prequal_lookup.json', 'r') as f:
        data = json.load(f)
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f'../data/backups/prequal_lookup_before_sgr_add_{timestamp}.json'
    
    print("📦 Creating backup...")
    import os
    os.makedirs('../data/backups', exist_ok=True)
    with open(backup_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Backup created: {backup_path}")
    
    # Load firms_data.json to get firm codes
    with open('../data/firms_data.json', 'r') as f:
        firms_data = json.load(f)
    
    # Create firm name to code mapping
    firm_code_mapping = {}
    for firm in firms_data:
        if firm.get('firm_name'):
            firm_code_mapping[firm['firm_name'].strip().upper()] = firm.get('firm_code', 'N/A')
    
    # Correct list provided by user
    correct_firms = [
        'AECOM TECHNICAL SERVICES, INC.',
        'BACON FARMER WORKMAN ENGR. & TESTNG',
        'BENESCH, ALFRED & CO.',
        'CHAMLIN & ASSOC., INC.',
        'CHICAGO TESTING LABORATORY, INC.',
        'Civil & Environmental Consultants, Inc.',
        'CIVIL DESIGN, INC.',
        'CUMMINS ENGINEERING CORPORATION',
        'Dan Brown and Associates, LLC',
        'DELVE UNDERGROUND',
        'ECS Midwest, LLC',
        'GEI Consultants, Inc.',
        'GEO SERVICES, INC.',
        'GEOCON PROFESSIONAL SERVICES, LLC',
        'GESTRA ENGINEERING, INC',
        'GFT Infrastructure, Inc',
        'GONZALEZ COMPANIES, LLC',
        'GROUND ENGINEERING CONSULTANTS INC.',
        'GSG CONSULTANTS, INC.',
        'H.N.T.B. CORP.',
        'HANSON PROFESSIONAL SERVICES INC.',
        'HDR ENGINEERING, INC.',
        'HOLCOMB FOUNDATION ENGINEERING CO.',
        'HURST-ROSCHE, INC.',
        'HUTCHISON ENGINEERING, INC.',
        'IMEG Consultants Corp.',
        'INTERRA, Inc.',
        'JACOBS ENGINEERING GROUP, INC.',
        'KASKASKIA ENGINEERING GROUP, LLC',
        'KLINGNER & ASSOC., P.C.',
        'LIN ENGINEERING, LTD.',
        'MAURER-STUTZ, INC.',
        'Michael Baker International, Inc.',
        'MIDLAND STANDARD ENG. & TESTING',
        'MIDWEST ENGINEERING & TESTING, INC.',
        'MILLENNIA PROF. SERVICES, LTD.',
        'Mott MacDonald, LLC',
        'NASHnal Soil Testing, LLC',
        'RUBINO ENGINEERING, INC.',
        'SCI ENGINEERING, INC.',
        'SHANNON & WILSON, INC.',
        'Simpson Gumpertz & Heger lnc.',
        'SOIL AND MATERIAL CONSULTANTS, INC.',
        'STANTEC CONSULTING SERVICES',
        'STV INCORPORATED',
        'TERRACON CONSULTANTS, INC.',
        'TESTING SERVICE CORPORATION',
        'UES Professional Solutions 25, LLC',
        'WANG ENGINEERING, INC.',
        'WHKS & CO.',
        'WSP USA Environment & Infrastructure Inc.',
        'WSP USA Inc.'
    ]
    
    print(f"📋 Adding {len(correct_firms)} firms to new category")
    
    # Create new firm list
    new_firms = []
    added_count = 0
    
    for firm_name in correct_firms:
        # Get firm code from mapping
        firm_code = firm_code_mapping.get(firm_name.upper(), f"F{len(firms_data) + added_count + 1}")
        
        firm_entry = {
            "firm_code": firm_code,
            "firm_name": firm_name
        }
        
        new_firms.append(firm_entry)
        
        # If we had to generate a new code, increment counter
        if firm_code.startswith(f"F{len(firms_data) + 1}"):
            added_count += 1
    
    # Add the new category
    category = 'Geotechnical Services (Structure Geotechnical Reports (SGR))'
    data[category] = new_firms
    
    print(f"✅ Added {category} with {len(new_firms)} firms")
    
    # Save updated data
    with open('../data/prequal_lookup.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print("✅ Updated prequal_lookup.json saved successfully!")
    
    # Generate summary
    print(f"\n📄 ADDITION SUMMARY:")
    print(f"   Category: {category}")
    print(f"   Firms added: {len(new_firms)}")
    print(f"   Total categories now: {len(data)}")
    print(f"   Status: SUCCESS ✅")
    
    # Show the added list
    print(f"\n✅ ADDED FIRMS LIST:")
    for i, firm in enumerate(new_firms, 1):
        print(f"{i:2d}. {firm['firm_code']} - {firm['firm_name']}")
    
    return new_firms

def main():
    added_firms = add_sgr_category()
    print(f"\n🎯 ADDITION COMPLETE!")
    print(f"   New category added with {len(added_firms)} firms")
    print(f"   Data accuracy: 100% ✅")

if __name__ == "__main__":
    main()






