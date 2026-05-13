#!/usr/bin/env python3
"""
Debug PTB160 Extraction
=======================
Analyze PTB160 document structure to understand extraction issues.
"""

import re
from docx import Document

def debug_ptb160():
    """Debug PTB160 extraction"""
    
    # Load PTB160 document
    doc = Document('../../ptb160.docx')
    full_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    
    print("🔍 PTB160 DOCUMENT ANALYSIS")
    print("=" * 50)
    
    # Look for prequalification patterns
    print("📋 LOOKING FOR PREQUALIFICATION PATTERNS:")
    print("-" * 40)
    
    # Pattern 1: "Firms must be prequalified in the following categories"
    categories_pattern = r'Firms must be prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|Statements of Interest|$)'
    categories_match = re.search(categories_pattern, full_text, re.IGNORECASE)
    
    if categories_match:
        print("✅ Found categories section:")
        categories_text = categories_match.group(1)
        print(f"   Length: {len(categories_text)} characters")
        print(f"   Content: {categories_text[:200]}...")
        print()
        
        # Split by lines
        lines = categories_text.split('\n')
        print("📋 CATEGORIES SECTION LINES:")
        for i, line in enumerate(lines, 1):
            if line.strip():
                print(f"   {i:2d}. {line.strip()}")
        print()
    else:
        print("❌ No categories section found")
        print()
    
    # Pattern 2: "prequalified in the" patterns
    individual_pattern = r'prequalified in the ([^)]*\([^)]*\)[^)]*) category'
    individual_matches = re.findall(individual_pattern, full_text, re.IGNORECASE)
    
    print(f"📋 INDIVIDUAL PREQUAL PATTERNS ({len(individual_matches)} found):")
    for i, match in enumerate(individual_matches, 1):
        print(f"   {i:2d}. {match.strip()}")
    print()
    
    # Pattern 3: Look for "Category Name (Subcategory)" patterns
    prequal_pattern = r'([A-Z][a-zA-Z\s&/]+)\s*\(([^)]+)\)'
    pattern_matches = re.findall(prequal_pattern, full_text)
    
    print(f"📋 CATEGORY (SUBCATEGORY) PATTERNS ({len(pattern_matches)} found):")
    for i, (category, subcategory) in enumerate(pattern_matches, 1):
        full_prequal = f"{category.strip()} ({subcategory.strip()})"
        print(f"   {i:2d}. {full_prequal}")
    print()
    
    # Look for specific job sections
    print("📋 JOB SECTIONS:")
    print("-" * 40)
    
    # Split by project sections
    project_sections = re.split(r'(?=Job #|D-\d+|C-\d+|P-\d+)', full_text)
    
    for i, section in enumerate(project_sections):
        if section.strip():
            # Extract job number
            job_match = re.search(r'(?:Job #\s*)?([DCP]-\d+-\d+-\d+)', section)
            if job_match:
                job_number = job_match.group(1)
                print(f"   Job {job_number}:")
                print(f"      Length: {len(section)} characters")
                print(f"      Preview: {section[:100]}...")
                print()
    
    # Look for district information
    print("📋 DISTRICT INFORMATION:")
    print("-" * 40)
    
    district_patterns = [
        r'District\s+(\d+)',
        r'DISTRICT\s+(\d+)',
        r'District\s*(\d+)',
        r'DISTRICT\s*(\d+)'
    ]
    
    for pattern in district_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            print(f"   Pattern '{pattern}': {matches}")
    
    print()
    
    # Show a sample of the full text
    print("📋 SAMPLE FULL TEXT (first 500 chars):")
    print("-" * 40)
    print(full_text[:500])
    print("...")

if __name__ == "__main__":
    debug_ptb160()



