#!/usr/bin/env python3
"""
Simple PTB160 Processing - Job Number Matching
==============================================
Focus on job number matching and sequence order.
"""

import json
import os
from datetime import datetime

def load_award_data():
    """Load award structure data"""
    print("📊 Loading award data...")
    with open('../data/award_structure.json', 'r') as f:
        return json.load(f)

def load_ptb160_extraction():
    """Load PTB160 extraction results"""
    print("📄 Loading PTB160 extraction results...")
    
    extraction_reports = [f for f in os.listdir('.') if f.startswith('structured_award_report') and f.endswith('.json')]
    
    if not extraction_reports:
        print("❌ No PTB extraction reports found!")
        return []
    
    latest_report = max(extraction_reports)
    print(f"✅ Using report: {latest_report}")
    
    with open(latest_report, 'r') as f:
        report = json.load(f)
    
    # Filter for PTB160 projects only
    ptb160_projects = [p for p in report.get('project_results', []) if p.get('ptb_number') == 160]
    return ptb160_projects

def simple_job_matching(ptb160_projects, award_data):
    """Simple job number matching - focus on matches, not sequence validation"""
    print("🔍 Simple job number matching...")
    
    # Get PTB160 awards from award data
    ptb160_awards = [a for a in award_data if a.get('f') == '160']
    
    # Create PTB mapping by job number
    ptb_mapping = {}
    for i, project in enumerate(ptb160_projects):
        job_number = project.get('job_number')
        if job_number:
            ptb_mapping[job_number] = {
                'ptb_sequence': i + 1,  # 1-based sequence
                'prequals': project.get('prequalifications', [])
            }
    
    # Process each award
    enhanced_awards = []
    successful_matches = 0
    missing_matches = 0
    
    for award in ptb160_awards:
        job_number = award.get('Job #')
        
        if job_number in ptb_mapping:
            # Found match - add prequalifications
            ptb_data = ptb_mapping[job_number]
            
            enhanced_award = award.copy()
            enhanced_award['required_prequals'] = ptb_data['prequals']
            enhanced_award['ptb_sequence'] = ptb_data['ptb_sequence']
            enhanced_award['ptb_match_status'] = 'SUCCESS'
            
            enhanced_awards.append(enhanced_award)
            successful_matches += 1
            
            print(f"✅ MATCH: {job_number} → {award.get('SELECTED FIRM')} (PTB Seq: {ptb_data['ptb_sequence']})")
        else:
            # No match - keep original award
            enhanced_award = award.copy()
            enhanced_award['required_prequals'] = []
            enhanced_award['ptb_sequence'] = None
            enhanced_award['ptb_match_status'] = 'NO_PTB_DATA'
            
            enhanced_awards.append(enhanced_award)
            missing_matches += 1
            
            print(f"❌ NO MATCH: {job_number} → {award.get('SELECTED FIRM')}")
    
    return enhanced_awards, successful_matches, missing_matches

def generate_simple_report(enhanced_awards, successful_matches, missing_matches):
    """Generate simple report"""
    print("📋 Generating simple report...")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'ptb_number': 160,
        'summary': {
            'total_awards': len(enhanced_awards),
            'successful_matches': successful_matches,
            'missing_ptb_data': missing_matches,
            'success_rate': f"{(successful_matches/len(enhanced_awards)*100):.1f}%" if enhanced_awards else "0%"
        },
        'successful_matches': [
            {
                'job_number': award.get('Job #'),
                'firm': award.get('SELECTED FIRM'),
                'ptb_sequence': award.get('ptb_sequence'),
                'prequals': award.get('required_prequals'),
                'district': award.get('Region/District')
            }
            for award in enhanced_awards if award.get('ptb_match_status') == 'SUCCESS'
        ],
        'missing_matches': [
            {
                'job_number': award.get('Job #'),
                'firm': award.get('SELECTED FIRM'),
                'district': award.get('Region/District')
            }
            for award in enhanced_awards if award.get('ptb_match_status') == 'NO_PTB_DATA'
        ]
    }
    
    # Save report
    report_filename = 'ptb_processing_reports/ptb160_simple_report.json'
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Report saved: {report_filename}")
    return report

def save_enhanced_awards(enhanced_awards):
    """Save enhanced awards structure"""
    print("💾 Saving enhanced awards...")
    
    # Save as JSON for now (we'll convert to Parquet later)
    enhanced_filename = 'ptb_processing_reports/ptb160_enhanced_awards.json'
    with open(enhanced_filename, 'w') as f:
        json.dump(enhanced_awards, f, indent=2)
    
    print(f"✅ Enhanced awards saved: {enhanced_filename}")

def main():
    """Main processing function"""
    print("🎯 Simple PTB160 Processing - Job Number Matching")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load data
    award_data = load_award_data()
    ptb160_projects = load_ptb160_extraction()
    
    print(f"📊 Loaded {len(award_data)} total award records")
    print(f"📄 Loaded {len(ptb160_projects)} PTB160 projects")
    
    # Get PTB160 awards
    ptb160_awards = [a for a in award_data if a.get('f') == '160']
    print(f"🎯 Found {len(ptb160_awards)} PTB160 awards")
    
    if not ptb160_projects:
        print("❌ No PTB160 projects found. Cannot proceed.")
        return
    
    # Simple job matching
    enhanced_awards, successful_matches, missing_matches = simple_job_matching(ptb160_projects, ptb160_awards)
    
    print(f"\n📊 SIMPLE MATCHING RESULTS:")
    print("-" * 40)
    print(f"   Total awards: {len(enhanced_awards)}")
    print(f"   ✅ Successful matches: {successful_matches}")
    print(f"   ❌ Missing PTB data: {missing_matches}")
    print(f"   📈 Success rate: {(successful_matches/len(enhanced_awards)*100):.1f}%" if enhanced_awards else "0%")
    
    # Generate report
    report = generate_simple_report(enhanced_awards, successful_matches, missing_matches)
    
    # Save enhanced awards
    save_enhanced_awards(enhanced_awards)
    
    # Show sample successful matches
    successful_list = [a for a in enhanced_awards if a.get('ptb_match_status') == 'SUCCESS']
    print(f"\n📋 SAMPLE SUCCESSFUL MATCHES:")
    print("-" * 40)
    for i, award in enumerate(successful_list[:5]):
        print(f"Match {i+1}:")
        print(f"  Job: {award.get('Job #')}")
        print(f"  Firm: {award.get('SELECTED FIRM')}")
        print(f"  PTB Seq: {award.get('ptb_sequence')}")
        print(f"  Prequals: {', '.join(award.get('required_prequals', [])[:2])}...")
        print()
    
    print("✅ Simple PTB160 processing complete!")
    print(f"📁 Check ptb_processing_reports/ for results")

if __name__ == "__main__":
    main()




