#!/usr/bin/env python3
"""
PTB160 Processing Script
========================
Process PTB160, match with award data, validate sequence, and generate reports.
"""

import json
import os
from datetime import datetime
from collections import defaultdict

def load_award_data():
    """Load award structure data"""
    print("📊 Loading award data...")
    with open('../data/award_structure.json', 'r') as f:
        return json.load(f)

def load_ptb160_extraction():
    """Load PTB160 extraction results"""
    print("📄 Loading PTB160 extraction results...")
    
    # Find PTB160 extraction report
    extraction_reports = [f for f in os.listdir('.') if f.startswith('structured_award_report') and f.endswith('.json')]
    
    if not extraction_reports:
        print("❌ No PTB extraction reports found!")
        return []
    
    # Use the most recent report
    latest_report = max(extraction_reports)
    print(f"✅ Using report: {latest_report}")
    
    with open(latest_report, 'r') as f:
        report = json.load(f)
    
    # Filter for PTB160 projects only
    ptb160_projects = [p for p in report.get('project_results', []) if p.get('ptb_number') == 160]
    return ptb160_projects

def validate_sequence(ptb160_projects, award_data):
    """Validate that PTB160 sequence matches award data sequence"""
    print("🔍 Validating sequence...")
    
    # Get PTB160 awards from award data
    ptb160_awards = [a for a in award_data if a.get('f') == '160']
    
    # Sort by ITEM#
    ptb160_awards.sort(key=lambda x: int(x.get('ITEM#', 0)) if x.get('ITEM#', '').isdigit() else 0)
    
    # Create mapping for validation
    ptb_mapping = {}
    for i, project in enumerate(ptb160_projects):
        job_number = project.get('job_number')
        if job_number:
            # Use sequence order since item_number is not in PTB extraction
            ptb_mapping[job_number] = {
                'ptb_item': str(i + 1),  # 1-based sequence
                'prequals': project.get('prequalifications', [])
            }
    
    award_mapping = {}
    for award in ptb160_awards:
        job_number = award.get('Job #')
        item_number = award.get('ITEM#')
        if job_number and item_number:
            award_mapping[job_number] = {
                'award_item': item_number,
                'firm': award.get('SELECTED FIRM'),
                'district': award.get('Region/District')
            }
    
    # Validate matches
    validation_results = []
    successful_matches = 0
    sequence_mismatches = 0
    missing_matches = 0
    
    for job_number in award_mapping.keys():
        if job_number in ptb_mapping:
            ptb_item = ptb_mapping[job_number]['ptb_item']
            award_item = award_mapping[job_number]['award_item']
            
            if ptb_item == award_item:
                # Successful match with correct sequence
                validation_results.append({
                    'job_number': job_number,
                    'ptb_item': ptb_item,
                    'award_item': award_item,
                    'firm': award_mapping[job_number]['firm'],
                    'district': award_mapping[job_number]['district'],
                    'prequals': ptb_mapping[job_number]['prequals'],
                    'status': 'SUCCESS',
                    'sequence_match': True
                })
                successful_matches += 1
            else:
                # Sequence mismatch
                validation_results.append({
                    'job_number': job_number,
                    'ptb_item': ptb_item,
                    'award_item': award_item,
                    'firm': award_mapping[job_number]['firm'],
                    'district': award_mapping[job_number]['district'],
                    'prequals': [],
                    'status': 'SEQUENCE_MISMATCH',
                    'sequence_match': False
                })
                sequence_mismatches += 1
        else:
            # Missing PTB data
            validation_results.append({
                'job_number': job_number,
                'ptb_item': 'N/A',
                'award_item': award_mapping[job_number]['award_item'],
                'firm': award_mapping[job_number]['firm'],
                'district': award_mapping[job_number]['district'],
                'prequals': [],
                'status': 'MISSING_PTB_DATA',
                'sequence_match': False
            })
            missing_matches += 1
    
    return validation_results, successful_matches, sequence_mismatches, missing_matches

def create_enhanced_award_structure(validation_results):
    """Create enhanced award structure with prequalifications"""
    print("🏗️ Creating enhanced award structure...")
    
    enhanced_awards = []
    
    for result in validation_results:
        # Load original award data for this job
        with open('../data/award_structure.json', 'r') as f:
            award_data = json.load(f)
        
        # Find matching award
        matching_award = None
        for award in award_data:
            if award.get('Job #') == result['job_number'] and award.get('f') == '160':
                matching_award = award.copy()
                break
        
        if matching_award:
            # Add prequalifications field
            matching_award['required_prequals'] = result['prequals']
            matching_award['ptb_match_status'] = result['status']
            matching_award['sequence_validated'] = result['sequence_match']
            
            enhanced_awards.append(matching_award)
    
    return enhanced_awards

def generate_ptb160_report(validation_results, successful_matches, sequence_mismatches, missing_matches, enhanced_awards):
    """Generate comprehensive PTB160 report"""
    print("📋 Generating PTB160 report...")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'ptb_number': 160,
        'summary': {
            'total_awards': len(validation_results),
            'successful_matches': successful_matches,
            'sequence_mismatches': sequence_mismatches,
            'missing_ptb_data': missing_matches,
            'success_rate': f"{(successful_matches/len(validation_results)*100):.1f}%" if validation_results else "0%"
        },
        'detailed_results': validation_results,
        'sample_enhanced_awards': enhanced_awards[:5] if enhanced_awards else []
    }
    
    # Save report
    report_filename = 'ptb_processing_reports/ptb160_matching_report.json'
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Report saved: {report_filename}")
    return report

def main():
    """Main processing function"""
    print("🎯 PTB160 Processing - Sequence Validation and Matching")
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
    
    # Validate sequence and matching
    validation_results, successful_matches, sequence_mismatches, missing_matches = validate_sequence(ptb160_projects, award_data)
    
    print(f"\n📊 VALIDATION RESULTS:")
    print("-" * 40)
    print(f"   Total awards: {len(validation_results)}")
    print(f"   ✅ Successful matches: {successful_matches}")
    print(f"   ⚠️  Sequence mismatches: {sequence_mismatches}")
    print(f"   ❌ Missing PTB data: {missing_matches}")
    print(f"   📈 Success rate: {(successful_matches/len(validation_results)*100):.1f}%" if validation_results else "0%")
    
    # Create enhanced award structure
    enhanced_awards = create_enhanced_award_structure(validation_results)
    
    # Generate report
    report = generate_ptb160_report(validation_results, successful_matches, sequence_mismatches, missing_matches, enhanced_awards)
    
    # Show sample results
    print(f"\n📋 SAMPLE RESULTS:")
    print("-" * 40)
    for i, result in enumerate(validation_results[:5]):
        print(f"Project {i+1}:")
        print(f"  Job: {result['job_number']}")
        print(f"  PTB Item: {result['ptb_item']}")
        print(f"  Award Item: {result['award_item']}")
        print(f"  Firm: {result['firm']}")
        print(f"  Status: {result['status']}")
        print(f"  Sequence Match: {result['sequence_match']}")
        if result['prequals']:
            print(f"  Prequals: {', '.join(result['prequals'][:2])}...")
        print()
    
    print("✅ PTB160 processing complete!")
    print(f"📁 Check ptb_processing_reports/ptb160_matching_report.json for detailed results")

if __name__ == "__main__":
    main()
