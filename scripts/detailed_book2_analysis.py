#!/usr/bin/env python3
"""
Detailed Book2 Analysis - Show Exact Data Issues
===============================================
Pinpoint exactly where STATE, CITY, and naming convention issues are located.
"""

import pandas as pd
import json
import re

def analyze_book2_issues():
    """Analyze Book2.xlsx to show exact data issues"""
    
    # Load Book2 data
    try:
        book2_data = pd.read_excel('../data/Book2.xlsx')
        print("✅ Successfully loaded Book2.xlsx")
    except Exception as e:
        print(f"❌ Error loading Book2.xlsx: {e}")
        return
    
    print(f"📊 Dataset Size: {book2_data.shape[0]} rows × {book2_data.shape[1]} columns")
    print()
    
    # Issue 1: STATE and CITY fields mostly empty
    print("🚨 ISSUE 1: STATE and CITY FIELDS MOSTLY EMPTY")
    print("=" * 60)
    
    state_population = book2_data['STATE'].notna().sum()
    city_population = book2_data['CITY'].notna().sum()
    total_rows = len(book2_data)
    
    print(f"📊 Population Statistics:")
    print(f"   STATE field: {state_population}/{total_rows} populated ({state_population/total_rows*100:.1f}%)")
    print(f"   CITY field: {city_population}/{total_rows} populated ({city_population/total_rows*100:.1f}%)")
    print()
    
    # Show rows with populated STATE/CITY
    populated_geo = book2_data[book2_data['STATE'].notna() | book2_data['CITY'].notna()]
    print(f"📋 Rows with Geographic Data ({len(populated_geo)} rows):")
    print(populated_geo[['STATE', 'CITY', 'FIRM', 'PRE-QUAL CATEGORIES']].head(10).to_string())
    print()
    
    # Show rows without geographic data
    empty_geo = book2_data[book2_data['STATE'].isna() & book2_data['CITY'].isna()]
    print(f"📋 Rows WITHOUT Geographic Data ({len(empty_geo)} rows):")
    print(empty_geo[['STATE', 'CITY', 'FIRM', 'PRE-QUAL CATEGORIES']].head(10).to_string())
    print()
    
    # Issue 2: Mixed population patterns
    print("🚨 ISSUE 2: MIXED POPULATION PATTERNS")
    print("=" * 60)
    
    # Analyze different row patterns
    patterns = {
        'Complete Records': book2_data.dropna(subset=['STATE', 'CITY', 'FIRM', 'EMAIL', 'IS DBE', 'CITY, STATE', 'PRE-QUAL CATEGORIES']),
        'Firm Only': book2_data.dropna(subset=['FIRM']).fillna(''),
        'Category Only': book2_data[book2_data['FIRM'].isna() & book2_data['PRE-QUAL CATEGORIES'].notna()],
        'Mixed': book2_data[~book2_data.index.isin(book2_data.dropna(subset=['STATE', 'CITY', 'FIRM', 'EMAIL', 'IS DBE', 'CITY, STATE', 'PRE-QUAL CATEGORIES']).index) & 
                        ~book2_data.index.isin(book2_data[book2_data['FIRM'].isna() & book2_data['PRE-QUAL CATEGORIES'].notna()].index)]
    }
    
    print(f"📊 Row Pattern Analysis:")
    for pattern_name, pattern_data in patterns.items():
        print(f"   {pattern_name}: {len(pattern_data)} rows")
    print()
    
    # Show examples of each pattern
    for pattern_name, pattern_data in patterns.items():
        if len(pattern_data) > 0:
            print(f"📋 {pattern_name} - Sample Data:")
            sample_cols = ['STATE', 'CITY', 'FIRM', 'PRE-QUAL CATEGORIES']
            available_cols = [col for col in sample_cols if col in pattern_data.columns]
            print(pattern_data[available_cols].head(3).to_string())
            print()
    
    # Issue 3: Category naming conventions
    print("🚨 ISSUE 3: CATEGORY NAMING CONVENTIONS")
    print("=" * 60)
    
    # Load our prequal lookup for comparison
    try:
        with open('../data/prequal_lookup.json', 'r') as f:
            prequal_lookup = json.load(f)
        
        # Extract our lookup categories
        lookup_categories = set()
        for main_cat, subcats_data in prequal_lookup.items():
            lookup_categories.add(main_cat.upper())
            if 'sub_categories' in subcats_data:
                for subcat_key, subcat_info in subcats_data['sub_categories'].items():
                    full_name = subcat_info.get('full_prequal_name', '')
                    if full_name:
                        lookup_categories.add(full_name.upper())
        
        # Extract Book2 categories
        book2_categories = set()
        for _, row in book2_data.iterrows():
            prequals = str(row.get('PRE-QUAL CATEGORIES', ''))
            if prequals and prequals != 'nan':
                categories = re.split(r'[,;|]', prequals)
                for cat in categories:
                    cat_clean = cat.strip().upper()
                    if cat_clean:
                        book2_categories.add(cat_clean)
        
        print(f"📊 Category Counts:")
        print(f"   Book2 Categories: {len(book2_categories)}")
        print(f"   Lookup Categories: {len(lookup_categories)}")
        print()
        
        # Show naming convention differences
        print(f"🔍 NAMING CONVENTION COMPARISON:")
        print()
        
        # Book2 format examples
        print(f"📋 Book2 Format Examples (first 10):")
        for cat in sorted(list(book2_categories))[:10]:
            print(f"   📝 {cat}")
        print()
        
        # Lookup format examples
        print(f"📋 Lookup Format Examples (first 10):")
        for cat in sorted(list(lookup_categories))[:10]:
            print(f"   🔍 {cat}")
        print()
        
        # Find exact matches
        exact_matches = book2_categories.intersection(lookup_categories)
        print(f"✅ Exact Matches ({len(exact_matches)}):")
        for cat in sorted(list(exact_matches)):
            print(f"   ✅ {cat}")
        print()
        
        # Show format differences
        print(f"⚠️  FORMAT DIFFERENCES:")
        print(f"   Book2 uses: 'MAIN CATEGORY - SUBCATEGORY'")
        print(f"   Lookup uses: 'Main Category (Subcategory)'")
        print()
        
        # Example conversion
        print(f"🔄 EXAMPLE CONVERSION:")
        book2_example = "AIRPORTS - CONSTRUCTION INSPECTION"
        lookup_example = "Airports (Construction Inspection)"
        print(f"   Book2: {book2_example}")
        print(f"   Lookup: {lookup_example}")
        print(f"   Conversion needed: Replace ' - ' with ' (' and add ')' at end")
        
    except Exception as e:
        print(f"❌ Error loading prequal lookup: {e}")
    
    # Summary of issues
    print("\n📋 SUMMARY OF DATA ISSUES IN BOOK2.XLSX:")
    print("=" * 60)
    print("🚨 ISSUE 1: STATE and CITY FIELDS MOSTLY EMPTY")
    print(f"   - STATE: {state_population}/{total_rows} populated ({state_population/total_rows*100:.1f}%)")
    print(f"   - CITY: {city_population}/{total_rows} populated ({city_population/total_rows*100:.1f}%)")
    print(f"   - Most rows ({(total_rows-state_population)/total_rows*100:.1f}%) have no geographic data")
    print()
    
    print("🚨 ISSUE 2: MIXED POPULATION PATTERNS")
    print(f"   - Complete Records: {len(patterns['Complete Records'])} rows")
    print(f"   - Firm Only: {len(patterns['Firm Only'])} rows")
    print(f"   - Category Only: {len(patterns['Category Only'])} rows")
    print(f"   - Mixed: {len(patterns['Mixed'])} rows")
    print()
    
    print("🚨 ISSUE 3: CATEGORY NAMING CONVENTIONS")
    print(f"   - Book2 Format: 'MAIN CATEGORY - SUBCATEGORY'")
    print(f"   - Lookup Format: 'Main Category (Subcategory)'")
    print(f"   - Exact Matches: {len(exact_matches) if 'exact_matches' in locals() else 'Unknown'}")
    print(f"   - Conversion needed for {len(book2_categories) - len(exact_matches) if 'exact_matches' in locals() else 'Unknown'} categories")

if __name__ == "__main__":
    analyze_book2_issues()



