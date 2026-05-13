#!/usr/bin/env python3
"""
Debug PTB160 C-93-084-11 Extraction
Investigate why the prequalification extraction failed for this specific project
"""

from docx import Document
import re

def debug_c93_084_11():
    """Debug the C-93-084-11 project extraction"""
    
    print("🔍 DEBUGGING C-93-084-11 PREQUALIFICATION EXTRACTION")
    print("=" * 80)
    
    # Load PTB160
    ptb_file = '../data/ptb160.docx'
    doc = Document(ptb_file)
    ptb_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    
    # Find the C-93-084-11 project section
    start_pattern = r'Job No\.\s*C-93-084-11[^.]*\.'
    start_match = re.search(start_pattern, ptb_text, re.IGNORECASE)
    
    if start_match:
        start_pos = start_match.start()
        print(f"✅ Found C-93-084-11 at position: {start_pos}")
        
        # Find the end marker
        end_pattern = r'Statements of Interest, including resumes of the key people noted above, must be submitted electronically to the Central Bureau of Design and Environment at the following address:\s*SOIPTB@dot\.il\.gov\.'
        end_matches = list(re.finditer(end_pattern, ptb_text, re.IGNORECASE))
        
        # Find the next end marker after this start
        end_pos = len(ptb_text)
        for end_match in end_matches:
            if end_match.start() > start_pos:
                end_pos = end_match.end()
                break
        
        # Extract project text
        project_text = ptb_text[start_pos:end_pos].strip()
        
        print(f"\n📋 PROJECT TEXT (first 500 chars):")
        print("-" * 50)
        print(project_text[:500])
        print("-" * 50)
        
        print(f"\n🔍 SEARCHING FOR PREQUALIFICATION PATTERNS:")
        print("-" * 50)
        
        # Test different prequalification patterns
        patterns_to_test = [
            r'prequalified in the ([^)]*\([^)]*\)[^)]*) category',
            r'prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|$)',
            r'prequalified in the ([^.]*?) category',
            r'prequalified in ([^.]*?) category',
            r'prequalified ([^.]*?) category',
            r'prequalified in the ([^)]*?) category',
            r'prequalified in the ([^)]*\([^)]*\)[^)]*\([^)]*\)[^)]*) category',
        ]
        
        for i, pattern in enumerate(patterns_to_test, 1):
            matches = re.findall(pattern, project_text, re.IGNORECASE)
            print(f"Pattern {i}: {pattern}")
            print(f"  Matches: {matches}")
            if matches:
                print(f"  ✅ FOUND: {matches}")
            else:
                print(f"  ❌ No matches")
            print()
        
        # Look for "Quality Assurance" specifically
        print(f"\n🔍 SEARCHING FOR 'QUALITY ASSURANCE' KEYWORDS:")
        print("-" * 50)
        
        quality_patterns = [
            r'Quality Assurance[^.]*',
            r'QA[^.]*',
            r'prequalified.*Quality[^.]*',
            r'prequalified.*QA[^.]*',
        ]
        
        for pattern in quality_patterns:
            matches = re.findall(pattern, project_text, re.IGNORECASE)
            if matches:
                print(f"✅ Found 'Quality Assurance' pattern: {pattern}")
                print(f"   Matches: {matches}")
        
        # Show the full project text for manual inspection
        print(f"\n📋 FULL PROJECT TEXT:")
        print("=" * 80)
        print(project_text)
        print("=" * 80)
        
    else:
        print("❌ Could not find C-93-084-11 in PTB160")

if __name__ == "__main__":
    debug_c93_084_11()





