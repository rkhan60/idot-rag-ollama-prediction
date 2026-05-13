#!/usr/bin/env python3
"""
Debug Excel Column Structure
Examine the actual column structure of the IDOT Excel file
"""

import pandas as pd

def debug_excel_columns():
    """Debug the Excel column structure"""
    data_dir = '../data'
    
    print("🔍 Debugging IDOT Excel Column Structure...")
    
    # Load the PrequalReport sheet
    excel_file = f'{data_dir}/IDOTConsultantList.xlsx'
    df = pd.read_excel(excel_file, sheet_name='PrequalReport')
    
    print(f"📊 Shape: {df.shape}")
    print(f"📊 Columns: {list(df.columns)}")
    
    print(f"\n📋 First 5 rows with all columns:")
    print(df.head().to_string())
    
    print(f"\n🔍 Examining each column for firm names and prequals:")
    
    for i, col in enumerate(df.columns):
        print(f"\nColumn {i}: '{col}'")
        
        # Get non-null values
        non_null_values = df[col].dropna()
        if len(non_null_values) > 0:
            print(f"  Non-null values: {len(non_null_values)}")
            print(f"  Sample values:")
            for val in non_null_values.head(3):
                print(f"    - {val}")
                
            # Check if this looks like firm names
            firm_like = 0
            for val in non_null_values.head(10):
                if isinstance(val, str) and len(val) > 3 and not val.isdigit():
                    firm_like += 1
                    
            if firm_like > 5:
                print(f"  ✅ This looks like firm names column")
                
            # Check if this looks like prequals
            prequal_like = 0
            for val in non_null_values.head(10):
                if isinstance(val, str) and (' - ' in val or 'Highways' in val or 'Special' in val):
                    prequal_like += 1
                    
            if prequal_like > 5:
                print(f"  ✅ This looks like prequalification column")

if __name__ == "__main__":
    debug_excel_columns()
