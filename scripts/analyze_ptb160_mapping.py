#!/usr/bin/env python3
"""
Analyze PTB160 Job Number to Exhibit A Mapping
"""

from docx import Document
import re

def analyze_ptb160_mapping():
    """Analyze the mapping between job numbers and Exhibit A sections"""
    
    # Extract text from PTB160
    doc = Document('../data/ptb160.docx')
    text = '\n'.join([p.text for p in doc.paragraphs])
    
    print("🔍 ANALYZING PTB160 JOB NUMBER TO EXHIBIT A MAPPING")
    print("=" * 80)
    
    # Find all job numbers
    job_numbers = re.findall(r'([A-Z]-\d{2}-\d{3}-\d{2})', text)
    print(f"📋 Found {len(job_numbers)} job numbers: {job_numbers}")
    
    # Find all Exhibit A sections
    exhibit_sections = text.split('Exhibit A')
    print(f"📝 Found {len(exhibit_sections)} Exhibit A sections")
    
    # Look for specific job numbers mentioned in your feedback
    target_jobs = ['D-91-516-11', 'C-91-390-11', 'D-91-506-11', 'P-91-526-11', 'C-92-125-11', 'C-92-126-11', 'C-93-084-11']
    
    print("\n🎯 ANALYZING TARGET JOB NUMBERS:")
    print("-" * 50)
    
    for job in target_jobs:
        print(f"\n🔍 {job}:")
        
        # Find where this job number appears in the text
        job_positions = []
        for match in re.finditer(re.escape(job), text):
            job_positions.append(match.start())
        
        print(f"  Found at positions: {job_positions}")
        
        # Find the nearest Exhibit A section for each occurrence
        for i, pos in enumerate(job_positions):
            # Find which Exhibit A section comes after this job number
            exhibit_positions = []
            for j, section in enumerate(exhibit_sections[1:], 1):  # Skip first empty section
                exhibit_start = text.find(f"Exhibit A", text.find(section))
                if exhibit_start > pos:
                    exhibit_positions.append((j, exhibit_start))
            
            if exhibit_positions:
                nearest_exhibit = min(exhibit_positions, key=lambda x: x[1])
                print(f"  Occurrence {i+1}: Nearest Exhibit A {nearest_exhibit[0]}")
                
                # Get the Exhibit A content
                exhibit_content = exhibit_sections[nearest_exhibit[0]]
                print(f"  Exhibit A {nearest_exhibit[0]} content: {exhibit_content[:200]}...")
            else:
                print(f"  Occurrence {i+1}: No Exhibit A found after this position")
    
    # Look for prequalification requirements in Exhibit A sections
    print("\n📋 PREQUALIFICATION REQUIREMENTS IN EXHIBIT A SECTIONS:")
    print("-" * 50)
    
    for i, section in enumerate(exhibit_sections[1:], 1):  # Skip first empty section
        if 'prequalified' in section.lower():
            print(f"\nExhibit A {i}:")
            # Find the prequalification requirement
            prequal_match = re.search(r'prequalified in the ([^)]+) category', section, re.IGNORECASE)
            if prequal_match:
                print(f"  Prequalification: {prequal_match.group(1)}")
            else:
                print(f"  Content: {section[:200]}...")

if __name__ == "__main__":
    analyze_ptb160_mapping()





