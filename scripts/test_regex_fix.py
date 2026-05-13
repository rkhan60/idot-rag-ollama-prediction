#!/usr/bin/env python3
"""
Test Regex Fix for Prequalification Extraction
"""

from docx import Document
import re

def test_regex_patterns():
    """Test different regex patterns for extracting prequalifications"""
    
    # Extract text from PTB160
    doc = Document('../data/ptb160.docx')
    text = '\n'.join([p.text for p in doc.paragraphs])
    
    # Split into Exhibit A sections
    exhibits = re.split(r'Exhibit A', text)
    
    print("🔍 TESTING REGEX PATTERNS FOR PREQUALIFICATION EXTRACTION")
    print("=" * 80)
    
    # Test patterns
    patterns = [
        r'prequalified in the ([^)]+) category',
        r'prequalified in the ([^)]*\([^)]*\)[^)]*) category',
        r'prequalified in the ([^)]*\([^)]*\)[^)]*\([^)]*\)[^)]*) category',
        r'prequalified in the ([^)]*\([^)]*\)[^)]*\([^)]*\)[^)]*\([^)]*\)[^)]*) category',
    ]
    
    # Test on first few Exhibit A sections
    for i in range(1, 6):  # Exhibit A 0-4
        exhibit_content = exhibits[i]
        print(f"\n📝 Exhibit A {i-1}:")
        
        # Show the prequalification text
        prequal_start = exhibit_content.lower().find('prequalified')
        if prequal_start != -1:
            prequal_text = exhibit_content[prequal_start:prequal_start+150]
            print(f"  Text: {prequal_text}")
        
        # Test each pattern
        for j, pattern in enumerate(patterns):
            match = re.search(pattern, exhibit_content, re.IGNORECASE)
            if match:
                print(f"  Pattern {j}: ✅ {match.group(1)}")
            else:
                print(f"  Pattern {j}: ❌ No match")
    
    # Find the best pattern
    print(f"\n🎯 FINDING BEST PATTERN:")
    print("-" * 50)
    
    # Test a comprehensive pattern
    comprehensive_pattern = r'prequalified in the ([^)]*\([^)]*\)[^)]*\([^)]*\)[^)]*\([^)]*\)[^)]*\([^)]*\)[^)]*) category'
    
    for i in range(1, 10):  # Exhibit A 0-8
        exhibit_content = exhibits[i]
        match = re.search(comprehensive_pattern, exhibit_content, re.IGNORECASE)
        if match:
            print(f"Exhibit A {i-1}: ✅ {match.group(1)}")
        else:
            print(f"Exhibit A {i-1}: ❌ No match")

if __name__ == "__main__":
    test_regex_patterns()





