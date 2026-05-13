#!/usr/bin/env python3
"""
Analyze Award Data Structure
Examine award.xlsx to understand historical award data for past performance matrix
"""

import pandas as pd
import json
from datetime import datetime

class AwardDataAnalyzer:
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
    
    def analyze_award_structure(self):
        """Analyze the structure of award.xlsx"""
        print("🔍 ANALYZING AWARD.XLSX STRUCTURE")
        print("=" * 80)
        
        print(f"📊 BASIC INFORMATION:")
        print(f"   Total rows: {len(self.award_df)}")
        print(f"   Total columns: {len(self.award_df.columns)}")
        print(f"   Column names: {list(self.award_df.columns)}")
        print()
        
        print(f"📋 COLUMN DETAILS:")
        for i, col in enumerate(self.award_df.columns):
            non_null_count = self.award_df[col].notna().sum()
            null_count = self.award_df[col].isna().sum()
            unique_count = self.award_df[col].nunique()
            
            print(f"   {i+1:2d}. {col}")
            print(f"       Non-null: {non_null_count}, Null: {null_count}, Unique: {unique_count}")
            
            # Show sample values for first few columns
            if i < 5:
                sample_values = self.award_df[col].dropna().head(3).tolist()
                print(f"       Sample: {sample_values}")
            print()
    
    def analyze_job_numbers(self):
        """Analyze job numbers and their patterns"""
        print("🔍 ANALYZING JOB NUMBERS")
        print("=" * 80)
        
        if 'Job #' in self.award_df.columns:
            job_numbers = self.award_df['Job #'].dropna()
            print(f"Total job numbers: {len(job_numbers)}")
            print(f"Unique job numbers: {job_numbers.nunique()}")
            
            # Show sample job numbers
            print(f"Sample job numbers:")
            for job in job_numbers.head(10):
                print(f"   • {job}")
            
            # Check for patterns
            print(f"\nJob number patterns:")
            patterns = job_numbers.astype(str).str.extract(r'(\d+)')[0].value_counts()
            print(f"   Most common patterns: {patterns.head(5).to_dict()}")
        
        print()
    
    def analyze_firms_in_awards(self):
        """Analyze firms mentioned in award data"""
        print("🔍 ANALYZING FIRMS IN AWARD DATA")
        print("=" * 80)
        
        firm_columns = []
        for col in self.award_df.columns:
            if 'firm' in col.lower() or 'selected' in col.lower() or 'consultant' in col.lower():
                firm_columns.append(col)
        
        print(f"Firm-related columns found: {firm_columns}")
        
        for col in firm_columns:
            firms = self.award_df[col].dropna()
            print(f"\n{col}:")
            print(f"   Total entries: {len(firms)}")
            print(f"   Unique firms: {firms.nunique()}")
            print(f"   Sample firms:")
            for firm in firms.head(5):
                print(f"     • {firm}")
        
        print()
    
    def analyze_prequalifications(self):
        """Analyze prequalification data in awards"""
        print("🔍 ANALYZING PREQUALIFICATIONS IN AWARD DATA")
        print("=" * 80)
        
        prequal_columns = []
        for col in self.award_df.columns:
            if 'prequal' in col.lower() or 'qual' in col.lower():
                prequal_columns.append(col)
        
        if prequal_columns:
            print(f"Prequalification columns found: {prequal_columns}")
            
            for col in prequal_columns:
                prequals = self.award_df[col].dropna()
                print(f"\n{col}:")
                print(f"   Total entries: {len(prequals)}")
                print(f"   Unique prequals: {prequals.nunique()}")
                print(f"   Sample prequals:")
                for prequal in prequals.head(5):
                    print(f"     • {prequal}")
        else:
            print("No prequalification columns found in award data")
        
        print()
    
    def analyze_dates_and_timing(self):
        """Analyze date and timing information"""
        print("🔍 ANALYZING DATES AND TIMING")
        print("=" * 80)
        
        date_columns = []
        for col in self.award_df.columns:
            if 'date' in col.lower() or 'year' in col.lower():
                date_columns.append(col)
        
        if date_columns:
            print(f"Date-related columns found: {date_columns}")
            
            for col in date_columns:
                dates = self.award_df[col].dropna()
                print(f"\n{col}:")
                print(f"   Total entries: {len(dates)}")
                print(f"   Date range: {dates.min()} to {dates.max()}")
                print(f"   Sample dates:")
                for date in dates.head(5):
                    print(f"     • {date}")
        else:
            print("No date-related columns found")
        
        print()
    
    def check_data_quality(self):
        """Check overall data quality"""
        print("🔍 DATA QUALITY ASSESSMENT")
        print("=" * 80)
        
        print(f"📊 OVERALL QUALITY:")
        print(f"   Total rows: {len(self.award_df)}")
        print(f"   Complete rows: {self.award_df.dropna().shape[0]}")
        print(f"   Rows with any missing data: {len(self.award_df) - self.award_df.dropna().shape[0]}")
        
        # Check for duplicates
        duplicates = self.award_df.duplicated().sum()
        print(f"   Duplicate rows: {duplicates}")
        
        # Check column completeness
        print(f"\n📋 COLUMN COMPLETENESS:")
        for col in self.award_df.columns:
            completeness = (self.award_df[col].notna().sum() / len(self.award_df)) * 100
            print(f"   {col}: {completeness:.1f}% complete")
        
        print()
    
    def generate_sample_records(self):
        """Generate sample records for understanding"""
        print("🔍 SAMPLE RECORDS")
        print("=" * 80)
        
        print("First 3 complete records:")
        complete_records = self.award_df.dropna()
        if len(complete_records) > 0:
            for i, (idx, row) in enumerate(complete_records.head(3).iterrows()):
                print(f"\nRecord {i+1}:")
                for col in self.award_df.columns:
                    print(f"   {col}: {row[col]}")
        else:
            print("No complete records found")
        
        print()
    
    def run_complete_analysis(self):
        """Run complete analysis of award data"""
        print("🚀 COMPLETE AWARD DATA ANALYSIS")
        print("=" * 80)
        
        # Analyze structure
        self.analyze_award_structure()
        
        # Analyze specific aspects
        self.analyze_job_numbers()
        self.analyze_firms_in_awards()
        self.analyze_prequalifications()
        self.analyze_dates_and_timing()
        
        # Check data quality
        self.check_data_quality()
        
        # Show sample records
        self.generate_sample_records()
        
        print("✅ Award data analysis complete!")
        
        return {
            'total_rows': len(self.award_df),
            'total_columns': len(self.award_df.columns),
            'columns': list(self.award_df.columns),
            'data_quality': {
                'complete_rows': self.award_df.dropna().shape[0],
                'duplicate_rows': self.award_df.duplicated().sum()
            }
        }

def main():
    analyzer = AwardDataAnalyzer()
    results = analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()





