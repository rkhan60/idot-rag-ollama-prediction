#!/usr/bin/env python3
"""
Check IDOT District Information
Check if there's district information in the IDOT Excel file
"""

import pandas as pd
import json

def check_idot_district_info():
    """Check for district information in IDOT Excel file"""
    print("🔍 CHECKING IDOT DISTRICT INFORMATION")
    print("=" * 50)
    
    # Load IDOT Excel file
    print("📂 Loading IDOTConsultantList.xlsx...")
    idot_excel = pd.read_excel('../data/IDOTConsultantList.xlsx', sheet_name='PrequalReport')
    
    print(f"✅ Loaded {len(idot_excel)} rows from IDOT Excel")
    
    # Check all column names
    print(f"\n📋 ALL COLUMN NAMES:")
    for i, col in enumerate(idot_excel.columns):
        print(f"   {i:2d}. {col}")
        
    # Check for district-related columns
    print(f"\n🔍 SEARCHING FOR DISTRICT-RELATED COLUMNS:")
    district_columns = []
    for col in idot_excel.columns:
        if 'district' in col.lower() or 'region' in col.lower() or 'area' in col.lower():
            district_columns.append(col)
            print(f"   Found: {col}")
            
    if not district_columns:
        print("   No district-related columns found")
        
    # Check sample data from first few columns
    print(f"\n📊 SAMPLE DATA FROM FIRST 5 COLUMNS:")
    for i, col in enumerate(idot_excel.columns[:5]):
        print(f"\n   Column {i}: {col}")
        sample_values = idot_excel[col].dropna().unique()[:5]
        for j, value in enumerate(sample_values, 1):
            print(f"     {j}. {value}")
            
    # Check if there are any other sheets
    print(f"\n📋 CHECKING ALL SHEETS:")
    try:
        all_sheets = pd.read_excel('../data/IDOTConsultantList.xlsx', sheet_name=None)
        for sheet_name in all_sheets.keys():
            print(f"   Sheet: {sheet_name}")
            sheet_data = all_sheets[sheet_name]
            print(f"     Rows: {len(sheet_data)}")
            print(f"     Columns: {len(sheet_data.columns)}")
            
            # Check for district columns in each sheet
            district_cols = [col for col in sheet_data.columns if 'district' in col.lower()]
            if district_cols:
                print(f"     District columns: {district_cols}")
                
    except Exception as e:
        print(f"   Error reading all sheets: {e}")
        
    # Check if we can infer districts from location data
    print(f"\n🌍 ANALYZING LOCATION DATA:")
    
    # Load firms_data.json to see location patterns
    with open('../data/firms_data.json', 'r') as f:
        firms_data = json.load(f)
        
    # Analyze cities and states
    cities = {}
    states = {}
    
    for firm in firms_data:
        city = firm.get('city', '')
        state = firm.get('state', '')
        
        if city:
            cities[city] = cities.get(city, 0) + 1
        if state:
            states[state] = states.get(state, 0) + 1
            
    print(f"   Top 10 Cities:")
    sorted_cities = sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]
    for city, count in sorted_cities:
        print(f"     {city}: {count} firms")
        
    print(f"   States:")
    for state, count in sorted(states.items()):
        print(f"     {state}: {count} firms")
        
    # Check if we can create district mapping based on location
    print(f"\n🗺️  DISTRICT MAPPING SUGGESTIONS:")
    
    # Illinois has 9 IDOT districts
    illinois_districts = {
        'District 1': ['Chicago', 'Cook County', 'Lake County', 'McHenry County'],
        'District 2': ['DeKalb', 'Kane', 'Kendall', 'LaSalle', 'Lee', 'Ogle', 'Winnebago'],
        'District 3': ['Bureau', 'Grundy', 'Iroquois', 'Kankakee', 'Livingston', 'Vermilion', 'Will'],
        'District 4': ['Adams', 'Brown', 'Cass', 'Fulton', 'Hancock', 'Henderson', 'Knox', 'McDonough', 'Mason', 'Mercer', 'Peoria', 'Putnam', 'Rock Island', 'Schuyler', 'Stark', 'Tazewell', 'Warren', 'Woodford'],
        'District 5': ['Champaign', 'Clark', 'Coles', 'Crawford', 'Cumberland', 'DeWitt', 'Douglas', 'Edgar', 'Effingham', 'Fayette', 'Ford', 'Iroquois', 'Jasper', 'Macon', 'Moultrie', 'Piatt', 'Shelby', 'Vermilion'],
        'District 6': ['Alexander', 'Clay', 'Clinton', 'Edwards', 'Franklin', 'Gallatin', 'Hamilton', 'Hardin', 'Jackson', 'Jefferson', 'Johnson', 'Lawrence', 'Madison', 'Marion', 'Massac', 'Monroe', 'Perry', 'Pope', 'Pulaski', 'Randolph', 'Saline', 'St. Clair', 'Union', 'Wabash', 'Washington', 'Wayne', 'White', 'Williamson'],
        'District 7': ['Bond', 'Calhoun', 'Christian', 'Greene', 'Jersey', 'Macoupin', 'Madison', 'Montgomery', 'Morgan', 'Sangamon', 'Scott'],
        'District 8': ['Boone', 'Carroll', 'Jo Daviess', 'Ogle', 'Stephenson', 'Whiteside', 'Winnebago'],
        'District 9': ['Champaign', 'Clark', 'Coles', 'Crawford', 'Cumberland', 'DeWitt', 'Douglas', 'Edgar', 'Effingham', 'Fayette', 'Ford', 'Iroquois', 'Jasper', 'Macon', 'Moultrie', 'Piatt', 'Shelby', 'Vermilion']
    }
    
    print(f"   Illinois has 9 IDOT districts")
    print(f"   We can create district mapping based on city/location data")
    print(f"   This would require:")
    print(f"     1. Analyzing firm locations")
    print(f"     2. Mapping cities to districts")
    print(f"     3. Creating district assignments")
    
    return {
        'has_district_columns': bool(district_columns),
        'district_columns': district_columns,
        'total_firms': len(firms_data),
        'cities': len(cities),
        'states': len(states)
    }

if __name__ == "__main__":
    result = check_idot_district_info()
    print(f"\n🎯 SUMMARY:")
    print(f"   Has District Columns: {result['has_district_columns']}")
    print(f"   Total Firms: {result['total_firms']}")
    print(f"   Unique Cities: {result['cities']}")
    print(f"   Unique States: {result['states']}")
