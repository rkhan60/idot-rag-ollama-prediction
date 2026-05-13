#!/usr/bin/env python3
"""
Diagnose Performance Matrix Issues
Identify why no firms are being matched in the performance matrix
"""

import pandas as pd
import json
from collections import defaultdict

class PerformanceDiagnostic:
    def __init__(self):
        self.award_file = '../data/award.xlsx'
        self.firms_data_file = '../data/firms_data.json'
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        
        # Load data
        self.award_df = pd.read_excel(self.award_file)
        
        with open(self.firms_data_file, 'r') as f:
            self.firms_data = json.load(f)
        
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        # Create firm mappings
        self.firm_code_to_name = {firm['firm_code']: firm['firm_name'] for firm in self.firms_data}
        self.firm_name_to_code = {firm['firm_name']: firm['firm_code'] for firm in self.firms_data}
    
    def analyze_firm_matching(self):
        """Analyze firm name matching issues"""
        print("🔍 ANALYZING FIRM MATCHING ISSUES")
        print("=" * 80)
        
        # Get unique firms from award data
        award_firms = set()
        
        # Selected firms
        selected_firms = self.award_df['SELECTED FIRM'].dropna().unique()
        award_firms.update(selected_firms)
        
        # Subconsultants
        subconsultants_text = self.award_df['SUBCONSULTANTS'].dropna()
        for text in subconsultants_text:
            if ';' in str(text):
                firms = [f.strip() for f in str(text).split(';') if f.strip()]
                award_firms.update(firms)
        
        # First alternates
        first_alts = self.award_df['First Alternate'].dropna().unique()
        award_firms.update(first_alts)
        
        # Second alternates
        second_alts = self.award_df['Second Alternate'].dropna().unique()
        award_firms.update(second_alts)
        
        print(f"📊 FIRM MATCHING ANALYSIS:")
        print(f"   Total unique firms in award data: {len(award_firms)}")
        print(f"   Total firms in firms_data.json: {len(self.firms_data)}")
        
        # Check direct matches
        direct_matches = 0
        unmatched_firms = []
        
        for award_firm in award_firms:
            if award_firm in self.firm_name_to_code:
                direct_matches += 1
            else:
                unmatched_firms.append(award_firm)
        
        print(f"   Direct matches: {direct_matches}")
        print(f"   Unmatched firms: {len(unmatched_firms)}")
        
        # Show sample unmatched firms
        print(f"\n📋 SAMPLE UNMATCHED FIRMS:")
        for firm in unmatched_firms[:10]:
            print(f"   • {firm}")
        
        if len(unmatched_firms) > 10:
            print(f"   ... and {len(unmatched_firms) - 10} more")
        
        # Show sample firms from firms_data.json
        print(f"\n📋 SAMPLE FIRMS FROM FIRMS_DATA.JSON:")
        for firm in self.firms_data[:10]:
            print(f"   • {firm['firm_name']} ({firm['firm_code']})")
        
        return direct_matches, len(unmatched_firms)
    
    def analyze_prequalification_extraction(self):
        """Analyze prequalification extraction issues"""
        print(f"\n🔍 ANALYZING PREQUALIFICATION EXTRACTION")
        print("=" * 80)
        
        # Check prequalification data in award file
        prequal_column = self.award_df['Prequals']
        non_empty_prequals = prequal_column.dropna()
        
        print(f"📊 PREQUALIFICATION DATA:")
        print(f"   Total rows in award data: {len(self.award_df)}")
        print(f"   Rows with prequalification data: {len(non_empty_prequals)}")
        print(f"   Rows without prequalification data: {len(self.award_df) - len(non_empty_prequals)}")
        
        # Show sample prequalification data
        print(f"\n📋 SAMPLE PREQUALIFICATION DATA:")
        for i, prequal in enumerate(non_empty_prequals.head(5)):
            print(f"   {i+1}. {prequal}")
        
        # Get all prequalifications from lookup
        lookup_prequals = set()
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                lookup_prequals.add(sub_data['full_prequal_name'])
        
        print(f"\n📊 PREQUALIFICATION COMPARISON:")
        print(f"   Total prequalifications in lookup: {len(lookup_prequals)}")
        print(f"   Sample lookup prequalifications:")
        for prequal in list(lookup_prequals)[:5]:
            print(f"     • {prequal}")
        
        return len(non_empty_prequals), len(lookup_prequals)
    
    def analyze_award_data_structure(self):
        """Analyze the structure of award data"""
        print(f"\n🔍 ANALYZING AWARD DATA STRUCTURE")
        print("=" * 80)
        
        print(f"📊 AWARD DATA COLUMNS:")
        for i, col in enumerate(self.award_df.columns):
            non_null = self.award_df[col].notna().sum()
            print(f"   {i+1:2d}. {col}: {non_null}/{len(self.award_df)} non-null")
        
        # Analyze job numbers
        job_numbers = self.award_df['Job #'].dropna()
        print(f"\n📊 JOB NUMBER ANALYSIS:")
        print(f"   Total job numbers: {len(job_numbers)}")
        print(f"   Sample job numbers:")
        for job in job_numbers.head(10):
            print(f"     • {job}")
        
        # Analyze years
        years = job_numbers.astype(str).str.extract(r'(\d{2})')[0].astype(float)
        print(f"\n📊 YEAR ANALYSIS:")
        print(f"   Year range: {years.min()} - {years.max()}")
        print(f"   Most common years: {years.value_counts().head(5).to_dict()}")
    
    def test_firm_matching_function(self):
        """Test the firm matching function with sample data"""
        print(f"\n🔍 TESTING FIRM MATCHING FUNCTION")
        print("=" * 80)
        
        def normalize_firm_name(firm_name):
            if pd.isna(firm_name) or firm_name == 'nan':
                return None
            
            normalized = str(firm_name).strip().upper()
            
            suffixes = [' INC', ' LLC', ' P.C.', ' CORP', ' CORPORATION', ' LTD', ' CO', ' COMPANY']
            for suffix in suffixes:
                if normalized.endswith(suffix):
                    normalized = normalized[:-len(suffix)]
            
            return normalized.strip()
        
        def match_firm_to_code(firm_name):
            if not firm_name or firm_name == 'nan':
                return None
            
            # Direct match
            if firm_name in self.firm_name_to_code:
                return self.firm_name_to_code[firm_name]
            
            # Normalized match
            normalized_name = normalize_firm_name(firm_name)
            for name, code in self.firm_name_to_code.items():
                if normalize_firm_name(name) == normalized_name:
                    return code
            
            return None
        
        # Test with sample firms from award data
        sample_firms = self.award_df['SELECTED FIRM'].dropna().head(10)
        
        print(f"📊 FIRM MATCHING TEST:")
        for firm in sample_firms:
            matched_code = match_firm_to_code(firm)
            status = f"✅ {matched_code}" if matched_code else "❌ No match"
            print(f"   {firm} -> {status}")
    
    def run_complete_diagnosis(self):
        """Run complete diagnosis"""
        print("🚀 COMPLETE PERFORMANCE MATRIX DIAGNOSIS")
        print("=" * 80)
        
        # Analyze firm matching
        direct_matches, unmatched_count = self.analyze_firm_matching()
        
        # Analyze prequalification extraction
        prequal_count, lookup_count = self.analyze_prequalification_extraction()
        
        # Analyze award data structure
        self.analyze_award_data_structure()
        
        # Test firm matching function
        self.test_firm_matching_function()
        
        # Summary
        print(f"\n📊 DIAGNOSIS SUMMARY")
        print("=" * 80)
        print(f"🔍 MAIN ISSUES IDENTIFIED:")
        
        if direct_matches == 0:
            print(f"   ❌ CRITICAL: No direct firm name matches found")
            print(f"      This is the primary issue - firm names don't match between award data and firms_data.json")
        
        if prequal_count == 0:
            print(f"   ❌ CRITICAL: No prequalification data found in award file")
            print(f"      The 'Prequals' column is mostly empty")
        
        if direct_matches > 0 and prequal_count > 0:
            print(f"   ✅ Firm matching and prequalification data are available")
            print(f"   🔍 Check the matching logic in the main script")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if direct_matches == 0:
            print(f"   1. Standardize firm names between award data and firms_data.json")
            print(f"   2. Implement better fuzzy matching for firm names")
            print(f"   3. Create a firm name mapping table")
        
        if prequal_count == 0:
            print(f"   1. Extract prequalifications from project descriptions")
            print(f"   2. Use PTB files to map projects to prequalifications")
            print(f"   3. Create a project-to-prequalification mapping")
        
        print(f"\n✅ Diagnosis complete!")

def main():
    diagnostic = PerformanceDiagnostic()
    diagnostic.run_complete_diagnosis()

if __name__ == "__main__":
    main()





