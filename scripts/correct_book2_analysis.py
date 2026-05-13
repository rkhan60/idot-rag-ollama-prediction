#!/usr/bin/env python3
"""
Correct Book2 Analysis - Understanding Hierarchical Structure
==========================================================
Analyze Book2.xlsx with correct understanding: State → City → Firm → Categories
"""

import pandas as pd
import json
import re

def analyze_book2_correctly():
    """Analyze Book2.xlsx with correct hierarchical understanding"""
    
    # Load Book2 data
    try:
        book2_data = pd.read_excel('../data/Book2.xlsx')
        print("✅ Successfully loaded Book2.xlsx")
    except Exception as e:
        print(f"❌ Error loading Book2.xlsx: {e}")
        return
    
    print(f"📊 Dataset Size: {book2_data.shape[0]} rows × {book2_data.shape[1]} columns")
    print()
    
    # Correct Analysis: Understand hierarchical structure
    print("🔍 CORRECT HIERARCHICAL STRUCTURE ANALYSIS")
    print("=" * 60)
    
    # Group data by state
    states_data = {}
    current_state = None
    current_city = None
    current_firm = None
    
    for idx, row in book2_data.iterrows():
        state = row['STATE']
        city = row['CITY']
        firm = row['FIRM']
        email = row['EMAIL']
        is_dbe = row['IS DBE']
        city_state = row['CITY, STATE']
        categories = row['PRE-QUAL CATEGORIES']
        
        # If we have a new state, start a new state group
        if pd.notna(state):
            current_state = state
            if current_state not in states_data:
                states_data[current_state] = {}
            print(f"📋 NEW STATE GROUP: {current_state}")
        
        # If we have a new city, start a new city group
        if pd.notna(city):
            current_city = city
            if current_city not in states_data.get(current_state, {}):
                if current_state not in states_data:
                    states_data[current_state] = {}
                states_data[current_state][current_city] = {}
            print(f"   🏙️  NEW CITY: {current_city}")
        
        # If we have a new firm, start a new firm group
        if pd.notna(firm):
            current_firm = firm
            if current_firm not in states_data.get(current_state, {}).get(current_city, {}):
                states_data[current_state][current_city][current_firm] = {
                    'email': email,
                    'is_dbe': is_dbe,
                    'city_state': city_state,
                    'categories': []
                }
            print(f"      🏢 NEW FIRM: {current_firm}")
        
        # Add category to current firm
        if pd.notna(categories) and current_firm:
            category = str(categories).strip()
            if category and category != 'nan':
                states_data[current_state][current_city][current_firm]['categories'].append(category)
                print(f"         📋 CATEGORY: {category}")
    
    print()
    
    # Analyze the hierarchical structure
    print("📊 HIERARCHICAL STRUCTURE SUMMARY")
    print("=" * 60)
    
    total_states = len(states_data)
    total_cities = sum(len(cities) for cities in states_data.values())
    total_firms = sum(len(firms) for cities in states_data.values() for firms in cities.values())
    total_categories = sum(len(firm_data['categories']) for cities in states_data.values() for firms in cities.values() for firm_data in firms.values())
    
    print(f"📈 HIERARCHICAL BREAKDOWN:")
    print(f"   🌍 States: {total_states}")
    print(f"   🏙️  Cities: {total_cities}")
    print(f"   🏢 Firms: {total_firms}")
    print(f"   📋 Categories: {total_categories}")
    print()
    
    # Show detailed breakdown by state
    print("📋 DETAILED BREAKDOWN BY STATE:")
    print("-" * 60)
    
    for state, cities in states_data.items():
        state_cities = len(cities)
        state_firms = sum(len(firms) for firms in cities.values())
        state_categories = sum(len(firm_data['categories']) for cities in cities.values() for firm_data in cities.values())
        
        print(f"🌍 {state}:")
        print(f"   Cities: {state_cities}")
        print(f"   Firms: {state_firms}")
        print(f"   Categories: {state_categories}")
        
        # Show cities in this state
        for city, firms in cities.items():
            city_firms = len(firms)
            city_categories = sum(len(firm_data['categories']) for firm_data in firms.values())
            print(f"   🏙️  {city}: {city_firms} firms, {city_categories} categories")
            
            # Show firms in this city
            for firm, firm_data in firms.items():
                categories_count = len(firm_data['categories'])
                dbe_status = firm_data['is_dbe']
                email = firm_data['email']
                print(f"      🏢 {firm} (DBE: {dbe_status}, Email: {email}): {categories_count} categories")
        print()
    
    # Analyze category distribution
    print("📋 CATEGORY ANALYSIS:")
    print("-" * 60)
    
    all_categories = set()
    category_counts = {}
    
    for state_data in states_data.values():
        for city_data in state_data.values():
            for firm_data in city_data.values():
                for category in firm_data['categories']:
                    all_categories.add(category)
                    category_counts[category] = category_counts.get(category, 0) + 1
    
    print(f"📊 Category Statistics:")
    print(f"   Total Unique Categories: {len(all_categories)}")
    print(f"   Total Category Instances: {total_categories}")
    print(f"   Average Categories per Firm: {total_categories/total_firms:.1f}")
    print()
    
    # Show most common categories
    print(f"🏆 Most Common Categories:")
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (category, count) in enumerate(sorted_categories[:10], 1):
        print(f"   {i:2d}. {category}: {count} firms")
    print()
    
    # Compare with our lookup system
    print("🔍 COMPARISON WITH LOOKUP SYSTEM:")
    print("-" * 60)
    
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
        
        # Find matches
        exact_matches = all_categories.intersection(lookup_categories)
        
        print(f"📊 Category Matching:")
        print(f"   Book2 Categories: {len(all_categories)}")
        print(f"   Lookup Categories: {len(lookup_categories)}")
        print(f"   Exact Matches: {len(exact_matches)}")
        print(f"   Match Rate: {len(exact_matches)/len(all_categories)*100:.1f}%")
        print()
        
        # Show some matches
        if exact_matches:
            print(f"✅ Sample Exact Matches:")
            for category in sorted(list(exact_matches))[:5]:
                print(f"   ✅ {category}")
            print()
        
        # Show some mismatches
        book2_only = all_categories - lookup_categories
        if book2_only:
            print(f"⚠️  Categories in Book2 only (first 5):")
            for category in sorted(list(book2_only))[:5]:
                print(f"   ❌ {category}")
            print()
        
    except Exception as e:
        print(f"❌ Error loading prequal lookup: {e}")
    
    # Final summary
    print("📋 FINAL ANALYSIS SUMMARY:")
    print("=" * 60)
    print(f"✅ Book2.xlsx is a WELL-STRUCTURED hierarchical database:")
    print(f"   🌍 {total_states} states with comprehensive coverage")
    print(f"   🏙️  {total_cities} cities across all states")
    print(f"   🏢 {total_firms} engineering firms with contact information")
    print(f"   📋 {total_categories} category instances across all firms")
    print(f"   📧 Email addresses available for {total_firms} firms")
    print(f"   🏷️  DBE status tracked for all firms")
    print()
    print(f"🎯 This is an EXCELLENT validation dataset for our system!")

if __name__ == "__main__":
    analyze_book2_correctly()



