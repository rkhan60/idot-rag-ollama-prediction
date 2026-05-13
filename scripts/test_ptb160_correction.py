#!/usr/bin/env python3
"""
Test PTB160 Correction
Test the corrected parsing on PTB160 specifically
"""

from docx import Document
import re
import json

def test_ptb160_parsing():
    """Test parsing of PTB160 to verify individual project extraction"""
    
    # Load prequalification lookup
    with open('../data/prequal_lookup.json', 'r') as f:
        prequal_lookup = json.load(f)
    
    # Extract text from PTB160
    doc = Document('../data/ptb160.docx')
    ptb_text = '\n'.join([p.text for p in doc.paragraphs])
    
    print("🔍 TESTING PTB160 PARSING")
    print("=" * 80)
    
    # Parse individual projects
    projects = []
    
    # Look for job numbers in the text
    job_numbers = re.findall(r'([A-Z]-\d{2}-\d{3}-\d{2})', ptb_text)
    print(f"📋 Found {len(job_numbers)} job numbers: {job_numbers}")
    
    # Split text by job numbers and create projects
    for i, job_number in enumerate(job_numbers):
        start_idx = ptb_text.find(job_number)
        if start_idx != -1:
            # Find the end of this project (next job number or end of text)
            end_idx = len(ptb_text)
            for next_job in job_numbers[i+1:]:
                next_idx = ptb_text.find(next_job, start_idx + 1)
                if next_idx != -1:
                    end_idx = next_idx
                    break
            
            project_text = ptb_text[start_idx:end_idx].strip()
            projects.append({
                'job_number': job_number,
                'project_text': project_text
            })
    
    print(f"📝 Parsed {len(projects)} individual projects")
    print()
    
    # Process each project
    for i, project in enumerate(projects, 1):
        job_number = project['job_number']
        project_text = project['project_text']
        
        print(f"🔍 PROJECT {i}: {job_number}")
        print("-" * 50)
        
        # Extract prequalifications for this specific project
        prequalifications = []
        
        # Look for Exhibit A section within this project
        exhibit_patterns = [
            r'Exhibit\s*A[:\s]*([\s\S]*?)(?=Exhibit\s*B|$)',
            r'Prequalification\s*Requirements[:\s]*([\s\S]*?)(?=\n\n|$)',
            r'Required\s*Prequalifications[:\s]*([\s\S]*?)(?=\n\n|$)',
        ]
        
        exhibit_text = ""
        for pattern in exhibit_patterns:
            matches = re.findall(pattern, project_text, re.IGNORECASE)
            if matches:
                exhibit_text = matches[0]
                break
        
        # If no Exhibit A found, look for prequalification keywords in project text
        if not exhibit_text:
            prequal_keywords = ['prequalification', 'qualification', 'required', 'must have']
            if any(keyword in project_text.lower() for keyword in prequal_keywords):
                exhibit_text = project_text
        
        # Extract prequalification categories from exhibit text
        if exhibit_text:
            # Match against prequal_lookup categories
            for category in prequal_lookup.keys():
                # Create flexible matching patterns
                category_patterns = [
                    re.escape(category),
                    re.escape(category.replace('(', ' (').replace(')', ') ')),
                    re.escape(category.replace(' - ', ' (').replace(':', ') ')),
                ]
                
                for pattern in category_patterns:
                    if re.search(pattern, exhibit_text, re.IGNORECASE):
                        prequalifications.append(category)
                        break
        
        # Remove duplicates
        prequalifications = list(set(prequalifications))
        
        print(f"📋 Job Number: {job_number}")
        print(f"📝 Prequalifications: {prequalifications}")
        print(f"📄 Project Text Sample: {project_text[:200]}...")
        print()
    
    # Expected results based on your feedback
    expected_results = {
        'D-91-516-11': ['Special Services (Subsurface Utility Engineering)'],
        'C-91-390-11': ['Special Services (Construction Inspection)'],
        'D-91-506-11': ['Highways (Roads & Streets)', 'Structures (Highway: Typical)', 'Special Services (Surveying)'],
        'P-91-526-11': ['Location Design Studies (Reconstruction/Major Rehabilitation)', 'Structures (Highway: Complex)'],
        'C-92-125-11': ['Special Studies (Traffic)'],
        'C-92-126-11': ['Special Services (Surveying)'],
        'C-93-084-11': ['Special Services (Construction Inspection)']
    }
    
    print("🎯 EXPECTED RESULTS vs ACTUAL RESULTS:")
    print("=" * 80)
    
    for job_number, expected_prequals in expected_results.items():
        # Find actual result
        actual_result = None
        for project in projects:
            if project['job_number'] == job_number:
                actual_result = project
                break
        
        if actual_result:
            actual_prequals = []
            # Extract prequalifications using the same logic
            project_text = actual_result['project_text']
            
            # Look for Exhibit A section within this project
            exhibit_patterns = [
                r'Exhibit\s*A[:\s]*([\s\S]*?)(?=Exhibit\s*B|$)',
                r'Prequalification\s*Requirements[:\s]*([\s\S]*?)(?=\n\n|$)',
                r'Required\s*Prequalifications[:\s]*([\s\S]*?)(?=\n\n|$)',
            ]
            
            exhibit_text = ""
            for pattern in exhibit_patterns:
                matches = re.findall(pattern, project_text, re.IGNORECASE)
                if matches:
                    exhibit_text = matches[0]
                    break
            
            # If no Exhibit A found, look for prequalification keywords in project text
            if not exhibit_text:
                prequal_keywords = ['prequalification', 'qualification', 'required', 'must have']
                if any(keyword in project_text.lower() for keyword in prequal_keywords):
                    exhibit_text = project_text
            
            # Extract prequalification categories from exhibit text
            if exhibit_text:
                # Match against prequal_lookup categories
                for category in prequal_lookup.keys():
                    # Create flexible matching patterns
                    category_patterns = [
                        re.escape(category),
                        re.escape(category.replace('(', ' (').replace(')', ') ')),
                        re.escape(category.replace(' - ', ' (').replace(':', ') ')),
                    ]
                    
                    for pattern in category_patterns:
                        if re.search(pattern, exhibit_text, re.IGNORECASE):
                            actual_prequals.append(category)
                            break
            
            actual_prequals = list(set(actual_prequals))
            
            print(f"🔍 {job_number}:")
            print(f"  Expected: {expected_prequals}")
            print(f"  Actual:   {actual_prequals}")
            
            # Check if they match
            if set(expected_prequals) == set(actual_prequals):
                print(f"  ✅ MATCH!")
            else:
                print(f"  ❌ MISMATCH!")
            print()
        else:
            print(f"❌ {job_number}: Not found in parsed projects")
            print()

if __name__ == "__main__":
    test_ptb160_parsing()





