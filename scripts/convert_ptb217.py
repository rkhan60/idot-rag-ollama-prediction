#!/usr/bin/env python3
"""
Convert ptb217.docx to text format
"""

from docx import Document
import os

def convert_docx_to_text(docx_path, output_path):
    """Convert docx file to text"""
    print(f"Converting {docx_path} to {output_path}")
    
    # Load the document
    doc = Document(docx_path)
    
    # Extract text from all paragraphs
    full_text = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            full_text.append(paragraph.text.strip())
    
    # Join all text
    text_content = '\n\n'.join(full_text)
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text_content)
    
    print(f"Conversion complete. File size: {len(text_content)} characters")
    return len(text_content)

if __name__ == "__main__":
    # Define paths
    docx_file = "../../../ptb217.docx"
    output_file = "../data/ptb217_docx_text.txt"
    
    # Check if input file exists
    if not os.path.exists(docx_file):
        print(f"Error: {docx_file} not found")
        exit(1)
    
    # Convert the file
    char_count = convert_docx_to_text(docx_file, output_file)
    
    # Verify the output
    if os.path.exists(output_file):
        print(f"✅ Successfully created {output_file}")
        print(f"📄 File contains {char_count} characters")
    else:
        print(f"❌ Failed to create {output_file}") 