#!/usr/bin/env python3
"""
PTB Enrichment Analyzer
Analyze existing Prequals column format and available PTB files before enrichment
"""

import pandas as pd
import json
import os
from datetime import datetime

class PTBEnrichmentAnalyzer:
    def __init__(self):
        self.award_file = '../data/award.xlsx'
        self.ptb_directory = '../data/'
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        
    def analyze_award_file_structure(self):
        """Analyze the award.xlsx file structure and Prequals column format"""
        print("🔍 ANALYZING AWARD FILE STRUCTURE")
        print("=" * 60)
        
        try:
            # Read Excel file
            df = pd.read_excel(self.award_file)
            
            print(f"📊 AWARD FILE ANALYSIS:")
            print(f"  • File: {self.award_file}")
            print(f"  • Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            print(f"  • Columns: {list(df.columns)}")
            
            # Check if Prequals column exists
            if 'Prequals' in df.columns:
                print(f"\n✅ PREQUALS COLUMN FOUND:")
                print(f"  • Column Name: 'Prequals'")
                print(f"  • Data Type: {df['Prequals'].dtype}")
                print(f"  • Non-null values: {df['Prequals'].notna().sum()}")
                print(f"  • Null values: {df['Prequals'].isna().sum()}")
                
                # Show first 4 rows as reference
                print(f"\n📋 FIRST 4 ROWS OF PREQUALS COLUMN (REFERENCE FORMAT):")
                for i in range(min(4, len(df))):
                    prequal_value = df.iloc[i]['Prequals']
                    job_number = df.iloc[i].get('Job #', 'N/A')
                    print(f"  Row {i+1} (Job: {job_number}): {prequal_value}")
                
                # Show sample of non-null values
                non_null_prequals = df[df['Prequals'].notna()]['Prequals'].head(10)
                if len(non_null_prequals) > 0:
                    print(f"\n📝 SAMPLE NON-NULL PREQUALS VALUES:")
                    for i, value in enumerate(non_null_prequals, 1):
                        print(f"  {i}. {value}")
                
            else:
                print(f"\n❌ PREQUALS COLUMN NOT FOUND!")
                print(f"  • Available columns: {list(df.columns)}")
                # Look for similar column names
                similar_cols = [col for col in df.columns if 'prequal' in col.lower() or 'qual' in col.lower()]
                if similar_cols:
                    print(f"  • Similar columns found: {similar_cols}")
            
            return df
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return None
    
    def analyze_ptb_files_availability(self):
        """Analyze available PTB files (160-200)"""
        print(f"\n📁 ANALYZING PTB FILES AVAILABILITY")
        print("=" * 60)
        
        ptb_files = {}
        missing_files = []
        
        # Check for PTB 160-200 files
        for ptb_num in range(160, 201):
            # Check for different possible formats
            possible_files = [
                f"ptb{ptb_num}.docx",
                f"ptb{ptb_num}.txt",
                f"PTB{ptb_num}.docx",
                f"PTB{ptb_num}.txt"
            ]
            
            found_file = None
            for filename in possible_files:
                filepath = os.path.join(self.ptb_directory, filename)
                if os.path.exists(filepath):
                    found_file = filename
                    break
            
            if found_file:
                ptb_files[ptb_num] = found_file
                print(f"  ✅ PTB{ptb_num}: {found_file}")
            else:
                missing_files.append(ptb_num)
                print(f"  ❌ PTB{ptb_num}: NOT FOUND")
        
        print(f"\n📊 PTB FILES SUMMARY:")
        print(f"  • Available: {len(ptb_files)} files")
        print(f"  • Missing: {len(missing_files)} files")
        print(f"  • Coverage: {len(ptb_files)/41*100:.1f}%")
        
        if missing_files:
            print(f"  • Missing files: {missing_files}")
        
        return ptb_files, missing_files
    
    def analyze_job_number_patterns(self):
        """Analyze job number patterns in award file"""
        print(f"\n🔢 ANALYZING JOB NUMBER PATTERNS")
        print("=" * 60)
        
        try:
            df = pd.read_excel(self.award_file)
            
            if 'Job #' in df.columns:
                job_numbers = df['Job #'].dropna()
                
                print(f"📊 JOB NUMBER ANALYSIS:")
                print(f"  • Total job numbers: {len(job_numbers)}")
                print(f"  • Unique job numbers: {job_numbers.nunique()}")
                print(f"  • Missing job numbers: {df['Job #'].isna().sum()}")
                
                # Show sample job numbers
                print(f"\n📝 SAMPLE JOB NUMBERS:")
                sample_jobs = job_numbers.head(10).tolist()
                for i, job in enumerate(sample_jobs, 1):
                    print(f"  {i}. {job}")
                
                # Analyze patterns
                patterns = {}
                for job in job_numbers:
                    if pd.notna(job):
                        job_str = str(job).strip()
                        if job_str:
                            # Extract pattern (e.g., "D-91-516-11" -> "Letter-Number-Number-Number")
                            parts = job_str.split('-')
                            if len(parts) >= 2:
                                pattern = f"{len(parts)}-parts"
                                patterns[pattern] = patterns.get(pattern, 0) + 1
                
                print(f"\n🔍 JOB NUMBER PATTERNS:")
                for pattern, count in patterns.items():
                    print(f"  • {pattern}: {count} jobs")
                
                return job_numbers.tolist()
            else:
                print(f"❌ JOB # COLUMN NOT FOUND!")
                return []
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return []
    
    def analyze_prequal_lookup_structure(self):
        """Analyze prequal_lookup.json structure for validation"""
        print(f"\n📚 ANALYZING PREQUAL LOOKUP STRUCTURE")
        print("=" * 60)
        
        try:
            with open(self.prequal_lookup_file, 'r') as f:
                prequal_data = json.load(f)
            
            print(f"📊 PREQUAL LOOKUP ANALYSIS:")
            print(f"  • Total categories: {len(prequal_data)}")
            print(f"  • File size: {os.path.getsize(self.prequal_lookup_file) / 1024:.1f} KB")
            
            # Show sample categories
            print(f"\n📝 SAMPLE PREQUALIFICATION CATEGORIES:")
            sample_categories = list(prequal_data.keys())[:10]
            for i, category in enumerate(sample_categories, 1):
                firm_count = len(prequal_data[category]) if isinstance(prequal_data[category], list) else 0
                print(f"  {i}. {category} ({firm_count} firms)")
            
            # Check for common patterns
            print(f"\n🔍 CATEGORY PATTERNS:")
            patterns = {}
            for category in prequal_data.keys():
                if ' - ' in category:
                    patterns['hyphen-separated'] = patterns.get('hyphen-separated', 0) + 1
                elif ' (' in category:
                    patterns['parentheses'] = patterns.get('parentheses', 0) + 1
                else:
                    patterns['other'] = patterns.get('other', 0) + 1
            
            for pattern, count in patterns.items():
                print(f"  • {pattern}: {count} categories")
            
            return prequal_data
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return None
    
    def generate_analysis_report(self):
        """Generate comprehensive analysis report"""
        print(f"\n📊 GENERATING ANALYSIS REPORT")
        print("=" * 60)
        
        # Collect all analysis results
        award_df = self.analyze_award_file_structure()
        ptb_files, missing_files = self.analyze_ptb_files_availability()
        job_numbers = self.analyze_job_number_patterns()
        prequal_lookup = self.analyze_prequal_lookup_structure()
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'award_file_analysis': {
                'file_exists': award_df is not None,
                'total_rows': len(award_df) if award_df is not None else 0,
                'prequals_column_exists': 'Prequals' in award_df.columns if award_df is not None else False,
                'prequals_non_null_count': award_df['Prequals'].notna().sum() if award_df is not None and 'Prequals' in award_df.columns else 0
            },
            'ptb_files_analysis': {
                'available_files': len(ptb_files),
                'missing_files': len(missing_files),
                'coverage_percentage': len(ptb_files)/41*100,
                'available_ptb_files': ptb_files,
                'missing_ptb_files': missing_files
            },
            'job_number_analysis': {
                'total_job_numbers': len(job_numbers),
                'unique_job_numbers': len(set(job_numbers)),
                'sample_job_numbers': job_numbers[:10] if job_numbers else []
            },
            'prequal_lookup_analysis': {
                'file_exists': prequal_lookup is not None,
                'total_categories': len(prequal_lookup) if prequal_lookup else 0,
                'sample_categories': list(prequal_lookup.keys())[:10] if prequal_lookup else []
            }
        }
        
        # Save report
        report_filename = f"ptb_enrichment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Analysis report saved: {report_filename}")
        
        # Print summary
        print(f"\n📋 ANALYSIS SUMMARY:")
        print(f"  • Award file: {'✅ Ready' if award_df is not None else '❌ Issues'}")
        print(f"  • Prequals column: {'✅ Found' if award_df is not None and 'Prequals' in award_df.columns else '❌ Missing'}")
        print(f"  • PTB files: {len(ptb_files)}/41 available ({len(ptb_files)/41*100:.1f}%)")
        print(f"  • Job numbers: {len(job_numbers)} found")
        print(f"  • Prequal lookup: {'✅ Ready' if prequal_lookup is not None else '❌ Issues'}")
        
        return report

def main():
    """Main execution function"""
    print("🔍 PTB ENRICHMENT ANALYSIS")
    print("=" * 80)
    
    analyzer = PTBEnrichmentAnalyzer()
    report = analyzer.generate_analysis_report()
    
    print(f"\n🎯 ANALYSIS COMPLETE!")
    print("=" * 80)
    print("📋 Review the analysis results above before proceeding with enrichment.")
    print("📄 Check the generated report for detailed findings.")

if __name__ == "__main__":
    main()





