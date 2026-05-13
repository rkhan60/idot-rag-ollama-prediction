#!/usr/bin/env python3
"""
PAScore Demo - Generate PAScore_data.csv
========================================
Extracts prequalifications from PTB160-170, identifies winners, and labels projects.
"""

import json
import csv
import re
from datetime import datetime
from collections import defaultdict

def load_award_data():
    """Load award structure data"""
    print("📊 Loading award data...")
    with open('../data/award_structure.json', 'r') as f:
        return json.load(f)

def load_ptb_extraction_results():
    """Load PTB extraction results"""
    print("📄 Loading PTB extraction results...")
    
    # Find all structured award reports
    import os
    extraction_reports = [f for f in os.listdir('.') if f.startswith('structured_award_report') and f.endswith('.json')]
    
    if not extraction_reports:
        print("❌ No PTB extraction reports found!")
        return []
    
    # Use the most recent report
    latest_report = max(extraction_reports)
    print(f"✅ Using report: {latest_report}")
    
    with open(latest_report, 'r') as f:
        report = json.load(f)
    
    return report.get('project_results', [])

def determine_project_label(job_number):
    """Determine project label based on job number pattern"""
    if not job_number:
        return "Unknown"
    
    # Extract prefix from job number
    prefix = job_number.split('-')[0] if '-' in job_number else job_number[:2]
    
    label_mapping = {
        'C': 'Construction',
        'D': 'Design',
        'P': 'Planning',
        'S': 'Special Services',
        'E': 'Environmental',
        'G': 'Geotechnical',
        'H': 'Hydraulic',
        'L': 'Location Design',
        'T': 'Traffic',
        'Q': 'Quality Assurance'
    }
    
    return label_mapping.get(prefix, 'Other')

def calculate_base_score():
    """Calculate a base score (placeholder for now)"""
    # This would be replaced with actual scoring logic
    return 85

def match_winners(ptb_projects, award_data):
    """Match PTB projects with award winners"""
    print("🏆 Matching winners...")
    
    # Create job number to award mapping
    job_to_award = {}
    for award in award_data:
        job_num = award.get('Job #')
        if job_num:
            job_to_award[job_num] = award
    
    # Match PTB projects with winners
    matched_projects = []
    
    for ptb_project in ptb_projects:
        job_number = ptb_project.get('job_number')
        ptb_number = ptb_project.get('ptb_number')
        
        # Find matching award
        award = job_to_award.get(job_number)
        winner = award.get('SELECTED FIRM') if award else "Unknown"
        
        # Create project record
        project_record = {
            'ptb_number': ptb_number,
            'project_sequence': ptb_project.get('item_number', ''),
            'job_number': job_number,
            'prequals': '; '.join(ptb_project.get('prequalifications', [])),
            'winner': winner,
            'project_label': determine_project_label(job_number),
            'score': calculate_base_score()
        }
        
        matched_projects.append(project_record)
    
    return matched_projects

def export_pascore_csv(projects, filename='PAScore_data.csv'):
    """Export projects to CSV file"""
    print(f"💾 Exporting to {filename}...")
    
    fieldnames = [
        'ptb_number',
        'project_sequence', 
        'job_number',
        'prequals',
        'winner',
        'project_label',
        'score'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for project in projects:
            writer.writerow(project)
    
    print(f"✅ Exported {len(projects)} projects to {filename}")

def main():
    """Main demo function"""
    print("🎯 PAScore Demo - Generating PAScore_data.csv")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load data
    award_data = load_award_data()
    ptb_projects = load_ptb_extraction_results()
    
    print(f"📊 Loaded {len(award_data)} award records")
    print(f"📄 Loaded {len(ptb_projects)} PTB projects")
    
    if not ptb_projects:
        print("❌ No PTB projects found. Demo cannot proceed.")
        return
    
    # Match winners
    matched_projects = match_winners(ptb_projects, award_data)
    
    print(f"🏆 Matched {len(matched_projects)} projects with winners")
    
    # Show sample data
    print("\n📋 SAMPLE DATA:")
    print("-" * 60)
    for i, project in enumerate(matched_projects[:5]):
        print(f"Project {i+1}:")
        print(f"  PTB: {project['ptb_number']}")
        print(f"  Job: {project['job_number']}")
        print(f"  Label: {project['project_label']}")
        print(f"  Winner: {project['winner']}")
        print(f"  Prequals: {project['prequals'][:50]}...")
        print()
    
    # Export to CSV
    export_pascore_csv(matched_projects)
    
    # Summary
    print("📊 SUMMARY:")
    print("-" * 60)
    print(f"✅ Total projects processed: {len(matched_projects)}")
    print(f"✅ Winners identified: {len([p for p in matched_projects if p['winner'] != 'Unknown'])}")
    print(f"✅ Project labels assigned: {len(set([p['project_label'] for p in matched_projects]))}")
    print(f"✅ File exported: PAScore_data.csv")
    
    # Show project label distribution
    label_counts = defaultdict(int)
    for project in matched_projects:
        label_counts[project['project_label']] += 1
    
    print(f"\n🏷️  PROJECT LABEL DISTRIBUTION:")
    for label, count in sorted(label_counts.items()):
        print(f"   {label}: {count}")

if __name__ == "__main__":
    main()




