#!/usr/bin/env python3
"""
Award Structure Analysis
========================
Comprehensive analysis of the 2,166 historical award records.
"""

import json
import pandas as pd
from collections import Counter
import re

def analyze_award_structure():
    """Analyze the award structure data comprehensively"""
    
    # Load award data
    with open('../data/award_structure.json', 'r') as f:
        awards = json.load(f)
    
    print("📊 AWARD STRUCTURE COMPREHENSIVE ANALYSIS")
    print("=" * 60)
    print(f"📈 Total Records: {len(awards):,}")
    print()
    
    # Basic structure analysis
    print("🔍 DATA STRUCTURE ANALYSIS:")
    print("-" * 40)
    
    if awards:
        sample_record = awards[0]
        print(f"📋 Fields Available: {len(sample_record)}")
        for i, (key, value) in enumerate(sample_record.items(), 1):
            value_type = type(value).__name__
            value_preview = str(value)[:50] + "..." if value and len(str(value)) > 50 else str(value)
            print(f"   {i:2d}. {key}: {value_type} = {value_preview}")
        print()
    
    # PTB Bulletin Analysis
    print("📋 PTB BULLETIN ANALYSIS:")
    print("-" * 40)
    
    ptb_counts = Counter()
    ptb_years = Counter()
    ptb_formats = Counter()
    
    for award in awards:
        ptb_num = award.get('f', 'Unknown')
        ptb_counts[ptb_num] += 1
        
        # Extract year from PTB number
        if isinstance(ptb_num, str) and ptb_num.isdigit():
            ptb_years[ptb_num[:2]] += 1
        
        # Check PTB format
        if isinstance(ptb_num, str):
            if ptb_num.isdigit():
                ptb_formats['Numeric'] += 1
            else:
                ptb_formats['Non-numeric'] += 1
        else:
            ptb_formats['Missing/Invalid'] += 1
    
    print(f"📊 PTB Distribution:")
    print(f"   Total Unique PTBs: {len(ptb_counts)}")
    print(f"   Most Common PTBs:")
    for ptb, count in ptb_counts.most_common(10):
        print(f"      PTB{ptb}: {count} awards")
    
    print(f"\n📅 PTB Year Distribution:")
    for year, count in sorted(ptb_years.items()):
        print(f"   20{year}: {count} awards")
    
    print(f"\n🔤 PTB Format Analysis:")
    for format_type, count in ptb_formats.items():
        print(f"   {format_type}: {count} awards")
    print()
    
    # Firm Analysis
    print("🏢 FIRM ANALYSIS:")
    print("-" * 40)
    
    firm_counts = Counter()
    subconsultant_stats = Counter()
    
    for award in awards:
        firm = award.get('SELECTED FIRM', 'Unknown')
        firm_counts[firm] += 1
        
        subconsultants = award.get('SUBCONSULTANTS')
        if subconsultants:
            subconsultant_stats['Has Subconsultants'] += 1
        else:
            subconsultant_stats['No Subconsultants'] += 1
    
    print(f"📊 Firm Statistics:")
    print(f"   Total Unique Firms: {len(firm_counts)}")
    print(f"   Most Active Firms:")
    for firm, count in firm_counts.most_common(10):
        print(f"      {firm}: {count} awards")
    
    print(f"\n👥 Subconsultant Analysis:")
    for status, count in subconsultant_stats.items():
        percentage = (count / len(awards)) * 100
        print(f"   {status}: {count} awards ({percentage:.1f}%)")
    print()
    
    # Geographic Analysis
    print("🌍 GEOGRAPHIC ANALYSIS:")
    print("-" * 40)
    
    region_district_counts = Counter()
    district_patterns = Counter()
    
    for award in awards:
        region_district = award.get('Region/District', 'Unknown')
        region_district_counts[region_district] += 1
        
        # Analyze district patterns
        if isinstance(region_district, str):
            if 'District' in region_district:
                district_patterns['District Format'] += 1
            elif 'Region' in region_district:
                district_patterns['Region Format'] += 1
            elif '/' in region_district:
                district_patterns['Slash Format'] += 1
            else:
                district_patterns['Other Format'] += 1
        else:
            district_patterns['Missing/Invalid'] += 1
    
    print(f"📊 Region/District Distribution:")
    print(f"   Total Unique Values: {len(region_district_counts)}")
    print(f"   Most Common Values:")
    for value, count in region_district_counts.most_common(10):
        print(f"      {value}: {count} awards")
    
    print(f"\n🔤 District Format Analysis:")
    for format_type, count in district_patterns.items():
        percentage = (count / len(awards)) * 100
        print(f"   {format_type}: {count} awards ({percentage:.1f}%)")
    print()
    
    # Financial Analysis
    print("💰 FINANCIAL ANALYSIS:")
    print("-" * 40)
    
    fee_estimate_stats = Counter()
    dbe_stats = Counter()
    
    for award in awards:
        fee_estimate = award.get('Fee Estimate')
        if fee_estimate:
            fee_estimate_stats['Has Fee Estimate'] += 1
        else:
            fee_estimate_stats['No Fee Estimate'] += 1
        
        dbe_percent = award.get('DBE %')
        if dbe_percent:
            dbe_stats['Has DBE %'] += 1
        else:
            dbe_stats['No DBE %'] += 1
    
    print(f"📊 Fee Estimate Analysis:")
    for status, count in fee_estimate_stats.items():
        percentage = (count / len(awards)) * 100
        print(f"   {status}: {count} awards ({percentage:.1f}%)")
    
    print(f"\n📊 DBE Participation Analysis:")
    for status, count in dbe_stats.items():
        percentage = (count / len(awards)) * 100
        print(f"   {status}: {count} awards ({percentage:.1f}%)")
    print()
    
    # Temporal Analysis
    print("📅 TEMPORAL ANALYSIS:")
    print("-" * 40)
    
    selection_date_stats = Counter()
    year_counts = Counter()
    
    for award in awards:
        selection_date = award.get('Selection Date')
        if selection_date:
            selection_date_stats['Has Selection Date'] += 1
            # Extract year if possible
            if isinstance(selection_date, str) and len(selection_date) >= 4:
                try:
                    year = selection_date[:4]
                    if year.isdigit():
                        year_counts[year] += 1
                except:
                    pass
        else:
            selection_date_stats['No Selection Date'] += 1
    
    print(f"📊 Selection Date Analysis:")
    for status, count in selection_date_stats.items():
        percentage = (count / len(awards)) * 100
        print(f"   {status}: {count} awards ({percentage:.1f}%)")
    
    print(f"\n📅 Year Distribution:")
    for year, count in sorted(year_counts.items()):
        print(f"   {year}: {count} awards")
    print()
    
    # Data Quality Analysis
    print("🔍 DATA QUALITY ANALYSIS:")
    print("-" * 40)
    
    missing_fields = Counter()
    total_fields = len(awards[0]) if awards else 0
    
    for award in awards:
        for field, value in award.items():
            if value is None or value == '' or value == 'Unknown':
                missing_fields[field] += 1
    
    print(f"📊 Missing Data Analysis:")
    for field, count in missing_fields.most_common():
        percentage = (count / len(awards)) * 100
        print(f"   {field}: {count} missing values ({percentage:.1f}%)")
    
    print(f"\n📊 Overall Data Completeness:")
    total_possible_values = len(awards) * total_fields
    total_missing_values = sum(missing_fields.values())
    completeness_percentage = ((total_possible_values - total_missing_values) / total_possible_values) * 100
    print(f"   Data Completeness: {completeness_percentage:.1f}%")
    print()
    
    # Summary
    print("📋 SUMMARY:")
    print("-" * 40)
    print(f"✅ Total Awards: {len(awards):,}")
    print(f"✅ Unique PTBs: {len(ptb_counts)}")
    print(f"✅ Unique Firms: {len(firm_counts)}")
    print(f"✅ Unique Region/Districts: {len(region_district_counts)}")
    print(f"✅ Data Completeness: {completeness_percentage:.1f}%")
    print(f"✅ Subconsultant Coverage: {(subconsultant_stats['Has Subconsultants']/len(awards)*100):.1f}%")
    print(f"✅ Fee Estimate Coverage: {(fee_estimate_stats['Has Fee Estimate']/len(awards)*100):.1f}%")
    
    return {
        'total_awards': len(awards),
        'unique_ptbs': len(ptb_counts),
        'unique_firms': len(firm_counts),
        'data_completeness': completeness_percentage,
        'ptb_distribution': dict(ptb_counts),
        'firm_distribution': dict(firm_counts),
        'region_district_distribution': dict(region_district_counts)
    }

if __name__ == "__main__":
    analysis_results = analyze_award_structure()



