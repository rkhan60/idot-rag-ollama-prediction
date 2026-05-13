#!/usr/bin/env python3
"""
Debug PTB160 P-95-052-11 and D-30-001-12 Extraction
Investigate why the prequalification extraction failed for these specific projects
"""

from docx import Document
import re

def debug_p95_052_d30_001():
    """Debug the P-95-052-11 and D-30-001-12 project extraction"""
    
    print("🔍 DEBUGGING P-95-052-11 AND D-30-001-12 PREQUALIFICATION EXTRACTION")
    print("=" * 80)
    
    # Load PTB160
    ptb_file = '../data/ptb160.docx'
    doc = Document(ptb_file)
    ptb_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    
    # Debug P-95-052-11
    print("\n🔍 DEBUGGING P-95-052-11:")
    print("-" * 50)
    
    start_pattern_p95 = r'Job No\.\s*P-95-052-11[^.]*\.'
    start_match_p95 = re.search(start_pattern_p95, ptb_text, re.IGNORECASE)
    
    if start_match_p95:
        start_pos = start_match_p95.start()
        print(f"✅ Found P-95-052-11 at position: {start_pos}")
        
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
        
        print(f"\n📋 P-95-052-11 PROJECT TEXT (first 500 chars):")
        print("-" * 50)
        print(project_text[:500])
        print("-" * 50)
        
        # Test prequalification patterns
        print(f"\n🔍 SEARCHING FOR PREQUALIFICATION PATTERNS (P-95-052-11):")
        print("-" * 50)
        
        patterns_to_test = [
            r'prequalified in the ([^)]*\([^)]*\)[^)]*) category',
            r'prequalified in the following categories[^:]*:\s*([\s\S]*?)(?=\n\n|$)',
            r'prequalified in the ([^.]*?) category',
            r'prequalified in ([^.]*?) category',
            r'prequalified ([^.]*?) category',
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
        
        # Look for "Aerial Mapping" specifically
        print(f"\n🔍 SEARCHING FOR 'AERIAL MAPPING' KEYWORDS:")
        print("-" * 50)
        
        aerial_patterns = [
            r'Aerial Mapping[^.]*',
            r'LiDAR[^.]*',
            r'Photogrammetry[^.]*',
            r'prequalified.*Aerial[^.]*',
            r'prequalified.*LiDAR[^.]*',
        ]
        
        for pattern in aerial_patterns:
            matches = re.findall(pattern, project_text, re.IGNORECASE)
            if matches:
                print(f"✅ Found 'Aerial Mapping' pattern: {pattern}")
                print(f"   Matches: {matches}")
        
        print(f"\n📋 FULL P-95-052-11 PROJECT TEXT:")
        print("=" * 80)
        print(project_text)
        print("=" * 80)
    
    # Debug D-30-001-12
    print("\n🔍 DEBUGGING D-30-001-12:")
    print("-" * 50)
    
    start_pattern_d30 = r'Job No\.\s*D-30-001-12[^.]*\.'
    start_match_d30 = re.search(start_pattern_d30, ptb_text, re.IGNORECASE)
    
    if start_match_d30:
        start_pos = start_match_d30.start()
        print(f"✅ Found D-30-001-12 at position: {start_pos}")
        
        # Find the next end marker after this start
        end_pos = len(ptb_text)
        for end_match in end_matches:
            if end_match.start() > start_pos:
                end_pos = end_match.end()
                break
        
        # Extract project text
        project_text = ptb_text[start_pos:end_pos].strip()
        
        print(f"\n📋 D-30-001-12 PROJECT TEXT (first 500 chars):")
        print("-" * 50)
        print(project_text[:500])
        print("-" * 50)
        
        # Test prequalification patterns
        print(f"\n🔍 SEARCHING FOR PREQUALIFICATION PATTERNS (D-30-001-12):")
        print("-" * 50)
        
        for i, pattern in enumerate(patterns_to_test, 1):
            matches = re.findall(pattern, project_text, re.IGNORECASE)
            print(f"Pattern {i}: {pattern}")
            print(f"  Matches: {matches}")
            if matches:
                print(f"  ✅ FOUND: {matches}")
            else:
                print(f"  ❌ No matches")
            print()
        
        # Look for "Structures" specifically
        print(f"\n🔍 SEARCHING FOR 'STRUCTURES' KEYWORDS:")
        print("-" * 50)
        
        structures_patterns = [
            r'Structures[^.]*',
            r'Highway[^.]*',
            r'Advanced[^.]*',
            r'prequalified.*Structures[^.]*',
            r'prequalified.*Highway[^.]*',
        ]
        
        for pattern in structures_patterns:
            matches = re.findall(pattern, project_text, re.IGNORECASE)
            if matches:
                print(f"✅ Found 'Structures' pattern: {pattern}")
                print(f"   Matches: {matches}")
        
        print(f"\n📋 FULL D-30-001-12 PROJECT TEXT:")
        print("=" * 80)
        print(project_text)
        print("=" * 80)
    else:
        print("❌ Could not find D-30-001-12 in PTB160")

if __name__ == "__main__":
    debug_p95_052_d30_001()





