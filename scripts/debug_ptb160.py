#!/usr/bin/env python3
"""
Debug PTB160 Matching
====================
Debug why PTB160 matching is failing.
"""

import json

def debug_ptb160_matching():
    """Debug PTB160 matching logic"""
    
    # Load data
    with open('structured_award_report_20250812_134636.json', 'r') as f:
        report = json.load(f)
    
    with open('../data/award_structure.json', 'r') as f:
        awards = json.load(f)
    
    # Get PTB160 data
    ptb160_projects = [p for p in report.get('project_results', []) if p.get('ptb_number') == 160]
    ptb160_awards = [a for a in awards if a.get('f') == '160']
    
    print(f"PTB160 projects: {len(ptb160_projects)}")
    print(f"PTB160 awards: {len(ptb160_awards)}")
    
    # Create mappings
    ptb_jobs = set(p['job_number'] for p in ptb160_projects)
    award_jobs = set(a['Job #'] for a in ptb160_awards)
    
    print(f"PTB job numbers: {len(ptb_jobs)}")
    print(f"Award job numbers: {len(award_jobs)}")
    
    # Find matches
    matches = ptb_jobs & award_jobs
    print(f"Matches: {len(matches)}")
    
    # Show matches
    print("\nMATCHES:")
    for job in sorted(matches):
        print(f"  {job}")
    
    # Show PTB only
    ptb_only = ptb_jobs - award_jobs
    print(f"\nPTB ONLY ({len(ptb_only)}):")
    for job in sorted(ptb_only):
        print(f"  {job}")
    
    # Show awards only
    awards_only = award_jobs - ptb_jobs
    print(f"\nAWARDS ONLY ({len(awards_only)}):")
    for job in sorted(awards_only):
        print(f"  {job}")
    
    # Show first few of each
    print(f"\nFIRST 5 PTB PROJECTS:")
    for i, project in enumerate(ptb160_projects[:5]):
        print(f"  {i+1}. {project['job_number']} - Item {project.get('item_number')}")
    
    print(f"\nFIRST 5 AWARDS:")
    for i, award in enumerate(ptb160_awards[:5]):
        print(f"  {i+1}. {award['Job #']} - Item {award.get('ITEM#')}")

if __name__ == "__main__":
    debug_ptb160_matching()




