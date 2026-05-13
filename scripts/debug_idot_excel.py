#!/usr/bin/env python3
"""
Debug IDOT Excel Structure
Examine the actual structure of the IDOT Excel file
"""

import pandas as pd
import json

def debug_idot_excel():
    """Debug the IDOT Excel file structure"""
    data_dir = '../data'
    
    print("🔍 Debugging IDOT Excel Structure...")
    
    # Check available sheets
    excel_file = f'{data_dir}/IDOTConsultantList.xlsx'
    xl = pd.ExcelFile(excel_file)
    print(f"📋 Available sheets: {xl.sheet_names}")
    
    # Examine each sheet
    for sheet_name in xl.sheet_names:
        print(f"\n📊 Sheet: {sheet_name}")
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   First 3 rows:")
        print(df.head(3).to_string())
        
        # Check for firm names in different columns
        for col in df.columns:
            if 'firm' in str(col).lower() or 'unnamed' in str(col).lower():
                non_null_values = df[col].dropna()
                if len(non_null_values) > 0:
                    print(f"   Column '{col}' has {len(non_null_values)} non-null values")
                    print(f"   Sample values: {list(non_null_values.head(5))}")
                    
        print("-" * 50)

if __name__ == "__main__":
    debug_idot_excel()
