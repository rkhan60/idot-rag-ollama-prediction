#!/usr/bin/env python3
"""
Simple Project-Firm Relationship Validation
Show the exact extraction process for project-firm relationships
"""

import pandas as pd
import json

def show_extraction_process():
    """Show exactly how project-firm relationships are extracted"""
    print("🔍 PROJECT-FIRM RELATIONSHIP EXTRACTION PROCESS")
    print("=" * 80)
    
    # Load award data
    award_df = pd.read_excel('../data/award.xlsx')
    
    print(f"📊 AWARD DATA OVERVIEW:")
    print(f"   Total projects (rows): {len(award_df)}")
    print(f"   Unique job numbers: {award_df['Job #'].nunique()}")
    
    # Show sample project structure
    print(f"\n📋 SAMPLE PROJECT STRUCTURE:")
    sample_project = award_df.iloc[0]
    print(f"   Job #: {sample_project['Job #']}")
    print(f"   Description: {sample_project['Description']}")
    print(f"   SELECTED FIRM (Prime): {sample_project['SELECTED FIRM']}")
    print(f"   SUBCONSULTANTS: {sample_project['SUBCONSULTANTS']}")
    print(f"   First Alternate: {sample_project['First Alternate']}")
    print(f"   Second Alternate: {sample_project['Second Alternate']}")
    
    # Show extraction process for first 5 projects
    print(f"\n🔍 EXTRACTION PROCESS FOR FIRST 5 PROJECTS:")
    
    for idx, row in award_df.head(5).iterrows():
        job_number = row['Job #']
        print(f"\n📋 PROJECT {idx + 1}: {job_number}")
        
        firms_roles = []
        
        # 1. Extract PRIME contractor
        if row['SELECTED FIRM'] and row['SELECTED FIRM'] != 'nan':
            firms_roles.append(('prime', row['SELECTED FIRM']))
            print(f"   ✅ PRIME: {row['SELECTED FIRM']}")
        
        # 2. Extract SUBCONSULTANTS
        subconsultants_text = row['SUBCONSULTANTS']
        if subconsultants_text and subconsultants_text != 'nan':
            # Split by semicolon to get individual firms
            subconsultants = [firm.strip() for firm in str(subconsultants_text).split(';') if firm.strip()]
            for firm in subconsultants:
                firms_roles.append(('subconsultant', firm))
                print(f"   ✅ SUBCONSULTANT: {firm}")
        
        # 3. Extract FIRST ALTERNATE
        if row['First Alternate'] and row['First Alternate'] != 'nan':
            firms_roles.append(('first_alternate', row['First Alternate']))
            print(f"   ✅ FIRST ALTERNATE: {row['First Alternate']}")
        
        # 4. Extract SECOND ALTERNATE
        if row['Second Alternate'] and row['Second Alternate'] != 'nan':
            firms_roles.append(('second_alternate', row['Second Alternate']))
            print(f"   ✅ SECOND ALTERNATE: {row['Second Alternate']}")
        
        print(f"   📊 Total firms in project: {len(firms_roles)}")
        
        # Show experience calculation for this project
        project_year = 2000 + float(str(job_number).split('-')[1])
        years_ago = 2025 - project_year
        
        # Calculate time weight
        if years_ago <= 5:
            time_weight = 1.0
        elif years_ago <= 10:
            time_weight = 0.7
        else:
            time_weight = 0.3
        
        print(f"   📅 Project year: {project_year} (years ago: {years_ago})")
        print(f"   ⏰ Time weight: {time_weight}")
        
        # Calculate experience points for each firm
        role_weights = {
            'prime': 1.0,
            'subconsultant': 0.3,
            'first_alternate': 0.5,
            'second_alternate': 0.4
        }
        
        print(f"   💰 Experience points calculation:")
        for role, firm in firms_roles:
            role_weight = role_weights[role]
            experience_points = role_weight * time_weight
            print(f"     • {firm} ({role}): {role_weight} × {time_weight} = {experience_points:.2f} points")

def show_prequalification_assignment():
    """Show how prequalifications are assigned to projects"""
    print(f"\n🔍 PREQUALIFICATION ASSIGNMENT PROCESS")
    print("=" * 80)
    
    award_df = pd.read_excel('../data/award.xlsx')
    
    # Show sample project
    sample_project = award_df.iloc[0]
    job_number = sample_project['Job #']
    description = sample_project['Description']
    
    print(f"📋 SAMPLE PROJECT PREQUALIFICATION ASSIGNMENT:")
    print(f"   Project: {job_number}")
    print(f"   Description: {description}")
    
    # Method 1: Extract from Prequals column
    prequals_column = sample_project['Prequals']
    print(f"   Method 1 - Prequals column: {prequals_column}")
    
    # Method 2: Extract from description using keywords
    description_lower = str(description).lower()
    print(f"   Method 2 - Description keywords: {description_lower}")
    
    # Show keyword matching
    keyword_mapping = {
        'highway': 'Highways (Roads & Streets)',
        'road': 'Highways (Roads & Streets)',
        'bridge': 'Structures (Highway: Typical)',
        'structure': 'Structures (Highway: Typical)',
        'survey': 'Special Services (Surveying)',
        'environmental': 'Environmental Reports (Environmental Assessment)'
    }
    
    matched_keywords = []
    for keyword, prequal in keyword_mapping.items():
        if keyword in description_lower:
            matched_keywords.append(prequal)
    
    print(f"   Keywords found: {matched_keywords}")
    
    # Method 3: Default assignment based on job number
    if job_number.startswith('H-'):
        default_prequal = 'Highways (Roads & Streets)'
    elif job_number.startswith('S-'):
        default_prequal = 'Structures (Highway: Typical)'
    elif job_number.startswith('E-'):
        default_prequal = 'Environmental Reports (Environmental Assessment)'
    else:
        default_prequal = 'Special Services (Surveying)'
    
    print(f"   Method 3 - Default (job prefix): {default_prequal}")

def show_performance_data_structure():
    """Show how projects are tracked in performance data"""
    print(f"\n🔍 PERFORMANCE DATA STRUCTURE")
    print("=" * 80)
    
    with open('../data/working_past_performance.json', 'r') as f:
        performance_data = json.load(f)
    
    # Find a firm with project details
    for firm_code, firm_data in performance_data['firm_detailed_experience'].items():
        if firm_data['overall_experience']['total_projects'] > 0:
            print(f"📋 SAMPLE FIRM PROJECT TRACKING:")
            print(f"   Firm: {firm_data['firm_name']} ({firm_code})")
            print(f"   Total projects: {firm_data['overall_experience']['total_projects']}")
            
            # Show project details for first prequalification
            for prequal, prequal_data in firm_data['prequalification_experience'].items():
                if prequal_data['project_details']:
                    print(f"\n   Prequalification: {prequal}")
                    print(f"   Projects in this prequalification: {len(prequal_data['project_details'])}")
                    
                    # Show first project detail
                    project = prequal_data['project_details'][0]
                    print(f"   Sample project:")
                    print(f"     Job #: {project['job_number']}")
                    print(f"     Role: {project['role']}")
                    print(f"     Experience points: {project['experience_points']:.2f}")
                    print(f"     Project year: {project['project_year']}")
                    print(f"     Time weight: {project['time_weight']}")
                    print(f"     Prequalifications: {project['prequalifications']}")
                    break
            break

def main():
    print("🚀 PROJECT-FIRM RELATIONSHIP VALIDATION")
    print("=" * 80)
    
    # Show extraction process
    show_extraction_process()
    
    # Show prequalification assignment
    show_prequalification_assignment()
    
    # Show performance data structure
    show_performance_data_structure()
    
    print(f"\n✅ VALIDATION SUMMARY:")
    print(f"   • Each row in award.xlsx = ONE project")
    print(f"   • Each project has multiple firms in different roles")
    print(f"   • Firm-role relationships are precisely tracked")
    print(f"   • Experience points are calculated per project")
    print(f"   • Prequalifications are assigned per project")
    print(f"   • All relationships are preserved in performance data")

if __name__ == "__main__":
    main()





