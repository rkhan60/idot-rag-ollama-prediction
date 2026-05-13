#!/usr/bin/env python3
"""
Check PTB160 Prequalifications
==============================
Manually check what prequalifications are in PTB160 for P-30-006-12
"""

import re
from docx import Document

def check_ptb160_prequals():
    """Check PTB160 document for prequalifications"""
    
    # Load PTB160 document
    doc_path = '../../ptb160.docx'
    
    try:
        doc = Document(doc_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        full_text = '\n'.join(text)
        
        print("🔍 CHECKING PTB160 FOR P-30-006-12")
        print("=" * 50)
        
        # Find P-30-006-12 section
        job_pattern = r'Job No\.\s*P-30-006-12[^.]*\.(.*?)(?=Job No\.|$)'
        job_match = re.search(job_pattern, full_text, re.DOTALL | re.IGNORECASE)
        
        if job_match:
            job_text = job_match.group(1)
            print("📄 FOUND P-30-006-12 SECTION:")
            print("-" * 30)
            print(job_text[:500] + "..." if len(job_text) > 500 else job_text)
            print()
            
            # Look for prequalification patterns
            print("🔍 LOOKING FOR PREQUALIFICATIONS:")
            print("-" * 30)
            
            # Pattern 1: "prequalified in the" pattern
            prequal_pattern1 = r'prequalified in the ([^)]*\([^)]*\)[^)]*) category'
            matches1 = re.findall(prequal_pattern1, job_text, re.IGNORECASE)
            print(f"Pattern 1 matches: {matches1}")
            
            # Pattern 2: "prequalified in the following categories"
            prequal_pattern2 = r'prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|$)'
            matches2 = re.findall(prequal_pattern2, job_text, re.IGNORECASE)
            print(f"Pattern 2 matches: {matches2}")
            
            # Pattern 3: Look for any mention of "Location/Design Studies"
            location_pattern = r'Location/Design Studies[^.]*'
            location_matches = re.findall(location_pattern, job_text, re.IGNORECASE)
            print(f"Location/Design Studies mentions: {location_matches}")
            
            # Pattern 4: Look for any prequalification-like text
            prequal_like_pattern = r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+\([^)]+\)'
            prequal_like_matches = re.findall(prequal_like_pattern, job_text)
            print(f"Prequalification-like patterns: {prequal_like_matches[:10]}")
            
            # Pattern 5: Look for "New Construction/Major Reconstruction"
            new_construction_pattern = r'New Construction/Major Reconstruction'
            new_construction_matches = re.findall(new_construction_pattern, job_text, re.IGNORECASE)
            print(f"New Construction/Major Reconstruction mentions: {new_construction_matches}")
            
            # Show full job text for manual inspection
            print("\n📋 FULL JOB TEXT FOR MANUAL INSPECTION:")
            print("-" * 50)
            print(job_text)
            
        else:
            print("❌ P-30-006-12 not found in PTB160")
            
    except Exception as e:
        print(f"❌ Error reading PTB160: {e}")

if __name__ == "__main__":
    check_ptb160_prequals()




