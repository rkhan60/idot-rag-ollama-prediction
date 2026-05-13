#!/usr/bin/env python3
"""
Book2 Data Verification & Cross-Reference Analysis
=================================================
Analyze Book2.xlsx and cross-reference with existing data frames for validation.
"""

import pandas as pd
import json
import os
from collections import Counter
import re

class Book2Verifier:
    def __init__(self):
        self.book2_data = None
        self.award_data = None
        self.firms_data = None
        self.district_mapping = None
        self.prequal_lookup = None
        
    def load_book2_data(self, filepath='../data/Book2.xlsx'):
        """Load Book2.xlsx data"""
        try:
            self.book2_data = pd.read_excel(filepath)
            print(f"✅ Successfully loaded Book2.xlsx")
            print(f"   Shape: {self.book2_data.shape}")
            print(f"   Columns: {list(self.book2_data.columns)}")
            return True
        except Exception as e:
            print(f"❌ Error loading Book2.xlsx: {e}")
            return False
    
    def load_existing_data(self):
        """Load existing data frames for comparison"""
        try:
            # Load award structure
            with open('../data/award_structure.json', 'r') as f:
                self.award_data = json.load(f)
            print(f"✅ Loaded award_structure.json: {len(self.award_data)} records")
            
            # Load firms data
            with open('../data/firms_data.json', 'r') as f:
                self.firms_data = json.load(f)
            print(f"✅ Loaded firms_data.json: {len(self.firms_data)} records")
            
            # Load district mapping
            with open('../data/district_mapping.json', 'r') as f:
                self.district_mapping = json.load(f)
            print(f"✅ Loaded district_mapping.json: {len(self.district_mapping)} records")
            
            # Load prequal lookup
            with open('../data/prequal_lookup.json', 'r') as f:
                self.prequal_lookup = json.load(f)
            print(f"✅ Loaded prequal_lookup.json: {len(self.prequal_lookup)} records")
            
            return True
        except Exception as e:
            print(f"❌ Error loading existing data: {e}")
            return False
    
    def analyze_book2_structure(self):
        """Analyze Book2 data structure and content"""
        if self.book2_data is None:
            print("❌ No Book2 data loaded")
            return
        
        print("\n📊 BOOK2 DATA STRUCTURE ANALYSIS")
        print("=" * 50)
        
        # Basic info
        print(f"📈 Dataset Size: {self.book2_data.shape[0]} rows × {self.book2_data.shape[1]} columns")
        print(f"📋 Column Names: {list(self.book2_data.columns)}")
        print()
        
        # Data types
        print("🔍 DATA TYPES:")
        for col in self.book2_data.columns:
            dtype = self.book2_data[col].dtype
            non_null = self.book2_data[col].count()
            total = len(self.book2_data)
            print(f"   {col}: {dtype} ({non_null}/{total} non-null, {(non_null/total*100):.1f}%)")
        print()
        
        # Sample data
        print("📋 SAMPLE DATA (first 3 rows):")
        print(self.book2_data.head(3).to_string())
        print()
        
        # Unique values analysis
        print("🔍 UNIQUE VALUES ANALYSIS:")
        for col in self.book2_data.columns:
            unique_count = self.book2_data[col].nunique()
            total_count = len(self.book2_data)
            print(f"   {col}: {unique_count} unique values ({unique_count/total_count*100:.1f}% uniqueness)")
        print()
    
    def verify_firm_names(self):
        """Verify firm names between Book2 and existing data"""
        if self.book2_data is None or self.award_data is None:
            print("❌ Required data not loaded")
            return
        
        print("🏢 FIRM NAME VERIFICATION")
        print("=" * 50)
        
        # Extract firm names from Book2
        book2_firms = set(self.book2_data['FIRM'].dropna().str.strip().str.upper())
        
        # Extract firm names from award data
        award_firms = set()
        for award in self.award_data:
            firm = award.get('SELECTED FIRM')
            if firm:
                award_firms.add(str(firm).strip().upper())
        
        # Extract firm names from firms data
        firms_data_firms = set()
        for firm_info in self.firms_data:
            firm_name = firm_info.get('firm_name')
            if firm_name:
                firms_data_firms.add(str(firm_name).strip().upper())
        
        print(f"📊 Firm Counts:")
        print(f"   Book2: {len(book2_firms)} unique firms")
        print(f"   Award Data: {len(award_firms)} unique firms")
        print(f"   Firms Data: {len(firms_data_firms)} unique firms")
        print()
        
        # Find matches and mismatches
        book2_award_matches = book2_firms.intersection(award_firms)
        book2_firms_matches = book2_firms.intersection(firms_data_firms)
        all_matches = book2_firms.intersection(award_firms).intersection(firms_data_firms)
        
        print(f"🔍 Firm Name Matches:")
        print(f"   Book2 ↔ Award Data: {len(book2_award_matches)} matches")
        print(f"   Book2 ↔ Firms Data: {len(book2_firms_matches)} matches")
        print(f"   All Sources Match: {len(all_matches)} firms")
        print()
        
        # Show sample matches
        if all_matches:
            print(f"📋 Sample Matching Firms (first 10):")
            for firm in sorted(list(all_matches))[:10]:
                print(f"   ✅ {firm}")
            print()
        
        # Show mismatches
        book2_only = book2_firms - award_firms - firms_data_firms
        if book2_only:
            print(f"⚠️  Firms in Book2 only (first 10):")
            for firm in sorted(list(book2_only))[:10]:
                print(f"   ❌ {firm}")
            print()
        
        return {
            'book2_firms': book2_firms,
            'award_firms': award_firms,
            'firms_data_firms': firms_data_firms,
            'matches': all_matches,
            'book2_only': book2_only
        }
    
    def verify_geographic_data(self):
        """Verify city/state data between Book2 and district mapping"""
        if self.book2_data is None or self.district_mapping is None:
            print("❌ Required data not loaded")
            return
        
        print("🌍 GEOGRAPHIC DATA VERIFICATION")
        print("=" * 50)
        
        # Extract city/state from Book2
        book2_cities = set()
        book2_states = set()
        book2_city_state = set()
        
        for _, row in self.book2_data.iterrows():
            city = str(row.get('CITY', '')).strip()
            state = str(row.get('STATE', '')).strip()
            
            if city and city != 'nan':
                book2_cities.add(city.upper())
            if state and state != 'nan':
                book2_states.add(state.upper())
            if city and state and city != 'nan' and state != 'nan':
                book2_city_state.add(f"{city.upper()}, {state.upper()}")
        
        # Extract cities from district mapping
        district_cities = set()
        for district, firms in self.district_mapping.items():
            if isinstance(firms, list) and firms:  # Check if firms is a non-empty list
                for firm in firms:
                    city = firm.get('city', '')
                    if city:
                        district_cities.add(str(city).strip().upper())
        
        print(f"📊 Geographic Counts:")
        print(f"   Book2 Cities: {len(book2_cities)}")
        print(f"   Book2 States: {len(book2_states)}")
        print(f"   Book2 City-State: {len(book2_city_state)}")
        print(f"   District Mapping Cities: {len(district_cities)}")
        print()
        
        # Find matches
        city_matches = book2_cities.intersection(district_cities)
        
        print(f"🔍 City Matches:")
        print(f"   Book2 ↔ District Mapping: {len(city_matches)} cities")
        print(f"   Match Rate: {len(city_matches)/len(book2_cities)*100:.1f}%")
        print()
        
        # Show sample matches
        if city_matches:
            print(f"📋 Sample Matching Cities (first 10):")
            for city in sorted(list(city_matches))[:10]:
                print(f"   ✅ {city}")
            print()
        
        # Show mismatches
        book2_cities_only = book2_cities - district_cities
        if book2_cities_only:
            print(f"⚠️  Cities in Book2 only (first 10):")
            for city in sorted(list(book2_cities_only))[:10]:
                print(f"   ❌ {city}")
            print()
        
        return {
            'book2_cities': book2_cities,
            'book2_states': book2_states,
            'district_cities': district_cities,
            'city_matches': city_matches,
            'book2_cities_only': book2_cities_only
        }
    
    def verify_prequal_categories(self):
        """Verify prequalification categories between Book2 and prequal lookup"""
        if self.book2_data is None or self.prequal_lookup is None:
            print("❌ Required data not loaded")
            return
        
        print("📋 PREQUALIFICATION CATEGORIES VERIFICATION")
        print("=" * 50)
        
        # Extract prequal categories from Book2
        book2_prequals = set()
        for _, row in self.book2_data.iterrows():
            prequals = str(row.get('PRE-QUAL CATEGORIES', ''))
            if prequals and prequals != 'nan':
                # Split by common delimiters and clean
                categories = re.split(r'[,;|]', prequals)
                for cat in categories:
                    cat_clean = cat.strip().upper()
                    if cat_clean:
                        book2_prequals.add(cat_clean)
        
        # Extract prequal categories from lookup
        lookup_prequals = set()
        for main_cat, subcats_data in self.prequal_lookup.items():
            lookup_prequals.add(main_cat.upper())
            if 'sub_categories' in subcats_data:
                for subcat_key, subcat_info in subcats_data['sub_categories'].items():
                    full_name = subcat_info.get('full_prequal_name', '')
                    if full_name:
                        lookup_prequals.add(full_name.upper())
        
        print(f"📊 Prequalification Counts:")
        print(f"   Book2: {len(book2_prequals)} unique categories")
        print(f"   Lookup: {len(lookup_prequals)} unique categories")
        print()
        
        # Find matches
        prequal_matches = book2_prequals.intersection(lookup_prequals)
        
        print(f"🔍 Prequalification Matches:")
        print(f"   Book2 ↔ Lookup: {len(prequal_matches)} categories")
        print(f"   Match Rate: {len(prequal_matches)/len(book2_prequals)*100:.1f}%")
        print()
        
        # Show sample matches
        if prequal_matches:
            print(f"📋 Sample Matching Categories (first 10):")
            for cat in sorted(list(prequal_matches))[:10]:
                print(f"   ✅ {cat}")
            print()
        
        # Show mismatches
        book2_prequals_only = book2_prequals - lookup_prequals
        if book2_prequals_only:
            print(f"⚠️  Categories in Book2 only (first 10):")
            for cat in sorted(list(book2_prequals_only))[:10]:
                print(f"   ❌ {cat}")
            print()
        
        return {
            'book2_prequals': book2_prequals,
            'lookup_prequals': lookup_prequals,
            'prequal_matches': prequal_matches,
            'book2_prequals_only': book2_prequals_only
        }
    
    def verify_dbe_status(self):
        """Verify DBE status between Book2 and award data"""
        if self.book2_data is None or self.award_data is None:
            print("❌ Required data not loaded")
            return
        
        print("🏷️ DBE STATUS VERIFICATION")
        print("=" * 50)
        
        # Extract DBE status from Book2
        book2_dbe_firms = set()
        book2_non_dbe_firms = set()
        
        for _, row in self.book2_data.iterrows():
            firm = str(row.get('FIRM', '')).strip().upper()
            is_dbe = str(row.get('IS DBE', '')).strip().upper()
            
            if firm and firm != 'NAN':
                if is_dbe in ['YES', 'TRUE', '1', 'Y']:
                    book2_dbe_firms.add(firm)
                else:
                    book2_non_dbe_firms.add(firm)
        
        # Extract DBE status from award data
        award_dbe_firms = set()
        award_non_dbe_firms = set()
        
        for award in self.award_data:
            firm = award.get('SELECTED FIRM')
            dbe_percent = award.get('DBE %')
            
            if firm:
                firm_upper = str(firm).strip().upper()
                if dbe_percent and str(dbe_percent).strip() != '0' and str(dbe_percent).strip() != '0.0':
                    award_dbe_firms.add(firm_upper)
                else:
                    award_non_dbe_firms.add(firm_upper)
        
        print(f"📊 DBE Status Counts:")
        print(f"   Book2 DBE Firms: {len(book2_dbe_firms)}")
        print(f"   Book2 Non-DBE Firms: {len(book2_non_dbe_firms)}")
        print(f"   Award DBE Firms: {len(award_dbe_firms)}")
        print(f"   Award Non-DBE Firms: {len(award_non_dbe_firms)}")
        print()
        
        # Find matches
        dbe_matches = book2_dbe_firms.intersection(award_dbe_firms)
        non_dbe_matches = book2_non_dbe_firms.intersection(award_non_dbe_firms)
        
        print(f"🔍 DBE Status Matches:")
        print(f"   DBE Firms Match: {len(dbe_matches)} firms")
        print(f"   Non-DBE Firms Match: {len(non_dbe_matches)} firms")
        print()
        
        return {
            'book2_dbe_firms': book2_dbe_firms,
            'book2_non_dbe_firms': book2_non_dbe_firms,
            'award_dbe_firms': award_dbe_firms,
            'award_non_dbe_firms': award_non_dbe_firms,
            'dbe_matches': dbe_matches,
            'non_dbe_matches': non_dbe_matches
        }
    
    def generate_verification_report(self):
        """Generate comprehensive verification report"""
        print("📊 COMPREHENSIVE VERIFICATION REPORT")
        print("=" * 60)
        
        # Run all verifications
        firm_results = self.verify_firm_names()
        geo_results = self.verify_geographic_data()
        prequal_results = self.verify_prequal_categories()
        dbe_results = self.verify_dbe_status()
        
        # Summary
        print("\n📋 VERIFICATION SUMMARY")
        print("-" * 40)
        
        if firm_results:
            print(f"✅ Firm Names: {len(firm_results['matches'])}/{len(firm_results['book2_firms'])} match ({len(firm_results['matches'])/len(firm_results['book2_firms'])*100:.1f}%)")
        
        if geo_results:
            print(f"✅ Cities: {len(geo_results['city_matches'])}/{len(geo_results['book2_cities'])} match ({len(geo_results['city_matches'])/len(geo_results['book2_cities'])*100:.1f}%)")
        
        if prequal_results:
            print(f"✅ Prequal Categories: {len(prequal_results['prequal_matches'])}/{len(prequal_results['book2_prequals'])} match ({len(prequal_results['prequal_matches'])/len(prequal_results['book2_prequals'])*100:.1f}%)")
        
        if dbe_results:
            print(f"✅ DBE Status: {len(dbe_results['dbe_matches'])}/{len(dbe_results['book2_dbe_firms'])} DBE firms match")
        
        return {
            'firm_verification': firm_results,
            'geographic_verification': geo_results,
            'prequal_verification': prequal_results,
            'dbe_verification': dbe_results
        }

def main():
    """Main verification process"""
    verifier = Book2Verifier()
    
    # Load Book2 data
    if not verifier.load_book2_data():
        print("❌ Cannot proceed without Book2.xlsx")
        return
    
    # Load existing data
    if not verifier.load_existing_data():
        print("❌ Cannot proceed without existing data")
        return
    
    # Analyze Book2 structure
    verifier.analyze_book2_structure()
    
    # Generate comprehensive verification report
    verification_results = verifier.generate_verification_report()
    
    print("\n🎯 VERIFICATION COMPLETE!")
    print("Book2.xlsx has been analyzed and cross-referenced with existing data frames.")

if __name__ == "__main__":
    main()
