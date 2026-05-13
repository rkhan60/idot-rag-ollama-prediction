#!/usr/bin/env python3
"""
Analyze Actual Bulletin Structure
Analyze the actual bulletin text provided by the user
"""

import json
import re
from datetime import datetime

def analyze_bulletin_structure():
    """Analyze the actual bulletin structure"""
    print("🔍 ANALYZING ACTUAL BULLETIN STRUCTURE")
    print("=" * 60)
    
    # Actual bulletin text from user
    bulletin_text = """
    1. Job No. D-91-516-11, Various Subsurface Utility Engineering Projects, Various Routes, Various Counties, Region One, District One.
    
    The prime firm must be prequalified in the Special Services (Subsurface Utility Engineering) category to be considered for this project.
    
    2. Job No. C-91-390-11, US-30 – Briarcliff Rd. to US 34 & West of IL 31 (West Lake St.) to East of BNSF RR, Phase III Project, Kane and Kendall Counties, Region One/District One.
    
    The prime firm must be prequalified in the Special Services (Construction Inspection) category to be considered for this project.
    
    3. Job No. D-91-506-11, Various Phase II Projects, Various Routes, Various Counties, Region One, District One.
    
    The prime firm must be prequalified in the following categories to be considered for this project:
    Highways (Roads & Streets)
    Structures (Highway: Typical)
    Special Services (Surveying)
    
    4. Job No. P-91-526-11, Various Phase I Projects, Various Routes, Various Counties, Region One, District One.
    
    The prime firm must be prequalified in the following categories to be considered for this project:
    Location Design Studies (Reconstruction/Major Rehabilitation)
    Structures (Highway: Complex)
    
    5. Job No. P-91-500-11, Various Traffic Studies, Various Routes, Various Counties, Region One, District One.
    
    The prime firm must be prequalified in the Special Studies (Traffic) category to be considered for this project.
    """
    
    # Extract key patterns
    patterns = extract_patterns(bulletin_text)
    
    # Analyze prequalification formats
    prequal_analysis = analyze_prequalification_formats(bulletin_text)
    
    # Generate mapping rules
    mapping_rules = generate_mapping_rules(prequal_analysis)
    
    # Create training recommendations
    recommendations = create_training_recommendations()
    
    # Generate report
    generate_report(patterns, prequal_analysis, mapping_rules, recommendations)
    
def extract_patterns(bulletin_text):
    """Extract key patterns from bulletin"""
    print("📊 EXTRACTING PATTERNS...")
    
    patterns = {
        'job_numbers': [],
        'locations': [],
        'districts': [],
        'phases': [],
        'prequalifications': []
    }
    
    lines = bulletin_text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Job numbers
        if 'Job No.' in line:
            patterns['job_numbers'].append(line)
            
        # Locations
        if any(word in line for word in ['County', 'Counties', 'Route', 'Routes']):
            patterns['locations'].append(line)
            
        # Districts
        if 'District' in line:
            patterns['districts'].append(line)
            
        # Phases
        if 'Phase' in line:
            patterns['phases'].append(line)
            
        # Prequalifications
        if 'prequalified' in line.lower():
            patterns['prequalifications'].append(line)
            
    return patterns

def analyze_prequalification_formats(bulletin_text):
    """Analyze prequalification format variations"""
    print("🔍 ANALYZING PREQUALIFICATION FORMATS...")
    
    prequal_formats = []
    
    # Extract prequalification statements
    lines = bulletin_text.split('\n')
    for line in lines:
        if 'prequalified' in line.lower():
            prequal_formats.append(line.strip())
    
    # Analyze format variations
    format_analysis = {
        'parentheses_format': [],
        'colon_format': [],
        'hyphen_format': [],
        'multiple_categories': []
    }
    
    for prequal in prequal_formats:
        if '(' in prequal and ')' in prequal:
            format_analysis['parentheses_format'].append(prequal)
        elif ':' in prequal:
            format_analysis['colon_format'].append(prequal)
        elif ' - ' in prequal:
            format_analysis['hyphen_format'].append(prequal)
        elif 'categories' in prequal.lower():
            format_analysis['multiple_categories'].append(prequal)
    
    return format_analysis

def generate_mapping_rules(format_analysis):
    """Generate mapping rules"""
    print("🗺️ GENERATING MAPPING RULES...")
    
    mapping_rules = {
        'parentheses_to_hyphen': {},
        'colon_to_hyphen': {},
        'standardization_rules': []
    }
    
    # Map parentheses format to hyphen format
    for prequal in format_analysis['parentheses_format']:
        if '(' in prequal and ')' in prequal:
            category = prequal.split('(')[0].strip()
            service = prequal.split('(')[1].split(')')[0].strip()
            hyphen_format = f"{category} - {service}"
            mapping_rules['parentheses_to_hyphen'][prequal] = hyphen_format
    
    # Map colon format to hyphen format
    for prequal in format_analysis['colon_format']:
        if ':' in prequal:
            parts = prequal.split(':')
            if len(parts) >= 2:
                category = parts[0].strip()
                service = parts[1].strip()
                hyphen_format = f"{category} - {service}"
                mapping_rules['colon_to_hyphen'][prequal] = hyphen_format
    
    # Standardization rules
    mapping_rules['standardization_rules'] = [
        "Replace parentheses () with hyphens -",
        "Replace colons : with hyphens -",
        "Standardize spacing around hyphens",
        "Handle multiple categories per project"
    ]
    
    return mapping_rules

def create_training_recommendations():
    """Create training recommendations"""
    print("📋 CREATING TRAINING RECOMMENDATIONS...")
    
    return {
        'extraction_strategies': [
            "Extract Job Number: 'Job No. [A-Z]-\\d+-\\d+-\\d+'",
            "Extract Location: Lines with 'County' or 'Route'",
            "Extract District: Lines with 'District'",
            "Extract Phase: Lines with 'Phase'",
            "Extract Prequalifications: Lines with 'prequalified'"
        ],
        'format_standardization': [
            "Convert bulletin format to lookup format",
            "Handle parentheses to hyphen conversion",
            "Handle colon to hyphen conversion",
            "Standardize spacing and punctuation"
        ],
        'model_training': [
            "Train on bulletin text extraction",
            "Train on format standardization",
            "Train on category mapping",
            "Train on multi-label classification"
        ]
    }

def generate_report(patterns, prequal_analysis, mapping_rules, recommendations):
    """Generate comprehensive report"""
    print("📄 GENERATING COMPREHENSIVE REPORT...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f'actual_bulletin_analysis_{timestamp}.txt'
    
    with open(report_file, 'w') as f:
        f.write("ACTUAL BULLETIN STRUCTURE ANALYSIS REPORT\n")
        f.write("=" * 55 + "\n\n")
        
        f.write("EXECUTIVE SUMMARY\n")
        f.write("-" * 20 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Analysis of actual IDOT bulletin structure\n")
        f.write("Focus: Extract 5 critical project details\n\n")
        
        f.write("KEY FINDINGS\n")
        f.write("-" * 15 + "\n")
        f.write("1. Job Numbers follow pattern: [Letter]-[2 digits]-[3 digits]-[2 digits]\n")
        f.write("2. Prequalifications use parentheses format: Category (Service)\n")
        f.write("3. Multiple prequalifications can be listed per project\n")
        f.write("4. District information is consistently formatted\n")
        f.write("5. Phase information is clearly stated\n\n")
        
        f.write("PATTERN ANALYSIS\n")
        f.write("-" * 20 + "\n")
        for pattern_type, pattern_list in patterns.items():
            f.write(f"\n{pattern_type.upper()}:\n")
            for pattern in pattern_list:
                f.write(f"  - {pattern}\n")
        f.write("\n")
        
        f.write("PREQUALIFICATION FORMAT ANALYSIS\n")
        f.write("-" * 35 + "\n")
        for format_type, format_list in prequal_analysis.items():
            f.write(f"\n{format_type.upper()}:\n")
            for fmt in format_list:
                f.write(f"  - {fmt}\n")
        f.write("\n")
        
        f.write("MAPPING RULES\n")
        f.write("-" * 15 + "\n")
        for rule_type, rule_dict in mapping_rules.items():
            f.write(f"\n{rule_type.upper()}:\n")
            if isinstance(rule_dict, dict):
                for key, value in rule_dict.items():
                    f.write(f"  {key} -> {value}\n")
            elif isinstance(rule_dict, list):
                for rule in rule_dict:
                    f.write(f"  - {rule}\n")
        f.write("\n")
        
        f.write("TRAINING RECOMMENDATIONS\n")
        f.write("-" * 25 + "\n")
        for rec_type, rec_list in recommendations.items():
            f.write(f"\n{rec_type.upper()}:\n")
            for rec in rec_list:
                f.write(f"  - {rec}\n")
        f.write("\n")
        
        f.write("CRITICAL INSIGHTS\n")
        f.write("-" * 20 + "\n")
        f.write("1. Bulletin uses parentheses format: 'Category (Service)'\n")
        f.write("2. Lookup uses hyphen format: 'Category - Service'\n")
        f.write("3. Need standardization pipeline: () -> -\n")
        f.write("4. Multiple categories per project are common\n")
        f.write("5. Job numbers are consistently formatted\n\n")
        
        f.write("NEXT STEPS\n")
        f.write("-" * 12 + "\n")
        f.write("1. Standardize prequal_lookup.json to match bulletin format\n")
        f.write("2. Create bulletin text extraction model\n")
        f.write("3. Implement format standardization pipeline\n")
        f.write("4. Train category mapping model\n")
        f.write("5. Validate with real bulletin data\n")
    
    print(f"✅ Report saved: {report_file}")
    
    # Print summary
    print(f"\n🎯 ANALYSIS SUMMARY:")
    print(f"   Job Numbers found: {len(patterns['job_numbers'])}")
    print(f"   Prequalification formats: {len(prequal_analysis['parentheses_format'])}")
    print(f"   Mapping rules generated: {len(mapping_rules['parentheses_to_hyphen'])}")
    print(f"   Report saved: {report_file}")

if __name__ == "__main__":
    analyze_bulletin_structure()
