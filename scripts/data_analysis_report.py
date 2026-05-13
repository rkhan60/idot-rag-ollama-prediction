#!/usr/bin/env python3
"""
COMPREHENSIVE DATA ANALYSIS REPORT
==================================
Analyzes current data sources and identifies gaps for the Base 2.1 system.
"""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime

def analyze_award_data():
    """Analyze award_structure.json"""
    print("📊 1. AWARD DATA ANALYSIS")
    print("=" * 50)
    
    with open('../data/award_structure.json', 'r') as f:
        awards = json.load(f)
    
    print(f"   Total records: {len(awards)}")
    
    # Date analysis
    dates = [r['Selection Date'] for r in awards if r['Selection Date']]
    if dates:
        print(f"   Date range: {min(dates)} to {max(dates)}")
    
    # Job numbers
    job_nums = [r['Job #'] for r in awards if r['Job #']]
    print(f"   Unique job numbers: {len(set(job_nums))}")
    
    # Firms
    firms = [r['SELECTED FIRM'] for r in awards if r['SELECTED FIRM']]
    print(f"   Unique firms: {len(set(firms))}")
    
    # Districts
    districts = [r['Region/District'] for r in awards if r['Region/District']]
    district_counts = Counter(districts)
    print(f"   District formats: {len(district_counts)}")
    print(f"   Most common districts: {dict(district_counts.most_common(5))}")
    
    # Subconsultants
    subcons = [r for r in awards if r['SUBCONSULTANTS'] is not None]
    print(f"   Records with subconsultants: {len(subcons)} ({len(subcons)/len(awards)*100:.1f}%)")
    
    # Fee estimates
    fees = [r for r in awards if r['Fee Estimate']]
    print(f"   Records with fee estimates: {len(fees)} ({len(fees)/len(awards)*100:.1f}%)")
    
    return awards

def analyze_firm_data():
    """Analyze firms_data.json"""
    print("\n🏢 2. FIRM DATA ANALYSIS")
    print("=" * 50)
    
    with open('../data/firms_data.json', 'r') as f:
        firms_data = json.load(f)
    
    print(f"   Total firms: {len(firms_data)}")
    
    # Prequalifications
    firms_with_prequals = [f for f in firms_data if f.get('prequalifications')]
    print(f"   Firms with prequals: {len(firms_with_prequals)}")
    
    # Districts
    firms_with_districts = [f for f in firms_data if f.get('district')]
    print(f"   Firms with districts: {len(firms_with_districts)}")
    
    # DBE status
    dbe_firms = [f for f in firms_data if f.get('dbe_status')]
    print(f"   Firms with DBE status: {len(dbe_firms)}")
    
    # District distribution
    districts = [f.get('district') for f in firms_data if f.get('district')]
    district_counts = Counter(districts)
    print(f"   District distribution: {dict(district_counts)}")
    
    return firms_data

def analyze_ptb_extraction():
    """Analyze PTB extraction results"""
    print("\n📄 3. PTB EXTRACTION ANALYSIS")
    print("=" * 50)
    
    # Check available PTB files
    ptb_files = [f for f in os.listdir('../../') if f.startswith('ptb') and f.endswith('.docx')]
    print(f"   PTB files available: {len(ptb_files)}")
    
    if ptb_files:
        ptb_numbers = [int(f[3:6]) for f in ptb_files if f[3:6].isdigit()]
        print(f"   PTB range: {min(ptb_numbers)} to {max(ptb_numbers)}")
    
    # Check extraction reports
    extraction_reports = [f for f in os.listdir('.') if f.startswith('structured_award_report') and f.endswith('.json')]
    print(f"   Extraction reports: {len(extraction_reports)}")
    
    if extraction_reports:
        # Use the most recent report
        latest_report = max(extraction_reports)
        with open(latest_report, 'r') as f:
            report = json.load(f)
        
        print(f"   Projects with prequals: {report['processing_summary']['projects_with_prequals']}")
        print(f"   Job number matches: {report['processing_summary']['job_number_matches']}")
        print(f"   Prequals extracted: {report['processing_summary']['prequalifications_extracted']}")
        
        return report
    
    return None

def analyze_data_coverage(awards, ptb_report):
    """Analyze data coverage and gaps"""
    print("\n🎯 4. DATA COVERAGE ANALYSIS")
    print("=" * 50)
    
    # Award job numbers
    award_jobs = set([r['Job #'] for r in awards if r['Job #']])
    print(f"   Award jobs: {len(award_jobs)}")
    
    # PTB job numbers
    ptb_jobs = set()
    if ptb_report:
        ptb_jobs = set([p['job_number'] for p in ptb_report.get('project_results', [])])
        print(f"   PTB jobs: {len(ptb_jobs)}")
        
        # Overlap
        overlap = award_jobs & ptb_jobs
        print(f"   Overlap: {len(overlap)}")
        print(f"   Coverage: {len(overlap)/len(award_jobs)*100:.1f}%")
        
        # Missing coverage
        missing = award_jobs - ptb_jobs
        print(f"   Missing PTB data: {len(missing)}")
        
        if missing:
            print(f"   Sample missing jobs: {list(missing)[:5]}")
    
    return award_jobs, ptb_jobs

def analyze_prequal_lookup():
    """Analyze prequal_lookup.json"""
    print("\n🔧 5. PREQUAL LOOKUP ANALYSIS")
    print("=" * 50)
    
    with open('../data/prequal_lookup.json', 'r') as f:
        prequal_data = json.load(f)
    
    print(f"   Main categories: {len(prequal_data)}")
    
    total_subcategories = 0
    total_firms = 0
    
    for category, data in prequal_data.items():
        subcategories = data.get('sub_categories', {})
        total_subcategories += len(subcategories)
        
        for subcat, subcat_data in subcategories.items():
            firms = subcat_data.get('firms', [])
            total_firms += len(firms)
    
    print(f"   Subcategories: {total_subcategories}")
    print(f"   Total firm entries: {total_firms}")
    
    return prequal_data

def generate_recommendations(awards, firms_data, ptb_report, award_jobs, ptb_jobs):
    """Generate recommendations based on analysis"""
    print("\n💡 6. RECOMMENDATIONS")
    print("=" * 50)
    
    recommendations = []
    
    # Data coverage
    if ptb_jobs:
        coverage = len(award_jobs & ptb_jobs) / len(award_jobs) * 100
        if coverage < 50:
            recommendations.append(f"⚠️  Low PTB coverage ({coverage:.1f}%) - need to process more PTB files")
        elif coverage < 80:
            recommendations.append(f"⚠️  Moderate PTB coverage ({coverage:.1f}%) - consider processing additional PTB files")
        else:
            recommendations.append(f"✅ Good PTB coverage ({coverage:.1f}%)")
    
    # District standardization
    district_formats = set([r['Region/District'] for r in awards if r['Region/District']])
    if len(district_formats) > 20:
        recommendations.append("⚠️  Many district formats - need standardization")
    
    # Fee parsing
    fees_with_values = [r for r in awards if r['Fee Estimate']]
    if len(fees_with_values) < len(awards) * 0.5:
        recommendations.append("⚠️  Many missing fee estimates - consider fee parsing")
    
    # Subconsultant parsing
    subcons = [r for r in awards if r['SUBCONSULTANTS'] is not None]
    if subcons:
        recommendations.append("✅ Subconsultant data available - need parsing")
    
    # Storage optimization
    recommendations.append("✅ Ready for Parquet + JSONL migration")
    
    for rec in recommendations:
        print(f"   {rec}")
    
    return recommendations

def main():
    """Main analysis function"""
    print("🔍 COMPREHENSIVE DATA ANALYSIS REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all analyses
    awards = analyze_award_data()
    firms_data = analyze_firm_data()
    ptb_report = analyze_ptb_extraction()
    award_jobs, ptb_jobs = analyze_data_coverage(awards, ptb_report)
    prequal_data = analyze_prequal_lookup()
    recommendations = generate_recommendations(awards, firms_data, ptb_report, award_jobs, ptb_jobs)
    
    print("\n" + "=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)
    print(f"✅ Award data: {len(awards)} records")
    print(f"✅ Firm data: {len(firms_data)} firms")
    print(f"✅ Prequal lookup: {len(prequal_data)} categories")
    if ptb_report:
        print(f"✅ PTB extraction: {ptb_report['processing_summary']['projects_with_prequals']} projects")
    print(f"📊 Data coverage: {len(award_jobs & ptb_jobs)/len(award_jobs)*100:.1f}%")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Process additional PTB files for better coverage")
    print("2. Standardize district formats")
    print("3. Parse subconsultant data")
    print("4. Migrate to Parquet + JSONL storage")
    print("5. Implement KO1-KO3 pipeline")

if __name__ == "__main__":
    main()




