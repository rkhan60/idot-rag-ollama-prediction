#!/usr/bin/env python3
"""
Test Final PTB160 Processing
Test the final corrected processor on PTB160
"""

from final_corrected_ptb_processor import FinalCorrectedPTBProcessor
import json

def test_ptb160_final():
    """Test the final corrected processor on PTB160"""
    
    print("🔍 TESTING FINAL PTB160 PROCESSING")
    print("=" * 80)
    
    # Create processor instance
    processor = FinalCorrectedPTBProcessor()
    
    # Process PTB160
    projects = processor.process_single_ptb(160)
    
    if projects:
        print(f"\n📋 PTB160 Results: {len(projects)} projects found")
        print("-" * 50)
        
        # Expected results based on your feedback
        expected_results = {
            'D-91-516-11': ['Special Services (Subsurface Utility Engineering)'],
            'C-91-390-11': ['Special Services (Construction Inspection)'],
            'D-91-506-11': ['Highways (Roads & Streets)', 'Structures (Highway: Typical)', 'Special Services (Surveying)'],
            'P-91-526-11': ['Special Studies (Traffic)'],
            'P-91-500-11': ['Special Services (Surveying)'],
            'D-91-525-11': ['Special Services (Construction Inspection)'],
            'C-92-125-11': ['Special Services (Construction Inspection)'],
            'C-92-126-11': ['Special Services (Construction Inspection)'],
            'C-93-084-11': ['Special Services (Quality Assurance: QA PCC & Aggregate)']
        }
        
        print("\n🎯 COMPARISON WITH EXPECTED RESULTS:")
        print("-" * 50)
        
        for project in projects:
            job_number = project['job_number']
            actual_prequals = project['prequalifications']
            
            print(f"\n🔍 {job_number}:")
            print(f"  Actual:   {actual_prequals}")
            
            if job_number in expected_results:
                expected_prequals = expected_results[job_number]
                print(f"  Expected: {expected_prequals}")
                
                # Check if they match
                if set(actual_prequals) == set(expected_prequals):
                    print(f"  ✅ MATCH!")
                else:
                    print(f"  ❌ MISMATCH!")
            else:
                print(f"  ⚠️ No expected result for this job number")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"  • Total projects: {len(projects)}")
        print(f"  • Projects with prequals: {sum(1 for p in projects if p['prequalifications'])}")
        print(f"  • Total prequalifications: {sum(len(p['prequalifications']) for p in projects)}")
        
        return projects
    else:
        print("❌ Failed to process PTB160")
        return None

if __name__ == "__main__":
    test_ptb160_final()





