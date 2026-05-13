#!/usr/bin/env python3
"""
Award Data Extractor
Comprehensive system to extract and structure award data from Excel for firm experience matrix
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime, timedelta
import re
import os

class AwardDataExtractor:
    def __init__(self):
        self.excel_file = '../data/award.xlsx'
        self.output_file = '../data/structured_award_data.json'
        self.extraction_config = {
            'required_columns': [
                'job_number', 'project_title', 'prime_firm', 'subconsultants',
                'award_date', 'project_value', 'district', 'location'
            ],
            'date_formats': ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y'],
            'value_patterns': [r'\$[\d,]+', r'[\d,]+'],
            'firm_cleaning_patterns': [
                (r',\s*Inc\.?', ' Inc'),
                (r',\s*LLC', ' LLC'),
                (r',\s*Ltd\.?', ' Ltd'),
                (r',\s*Corp\.?', ' Corp'),
                (r',\s*Company', ' Company'),
                (r'\s+', ' ')  # Multiple spaces to single space
            ]
        }
    
    def analyze_excel_structure(self):
        """Analyze the structure of the award Excel file"""
        print("🔍 ANALYZING AWARD EXCEL STRUCTURE")
        print("=" * 60)
        
        try:
            # Read Excel file
            df = pd.read_excel(self.excel_file)
            
            print(f"📊 EXCEL FILE ANALYSIS:")
            print(f"  • File: {self.excel_file}")
            print(f"  • Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            print(f"  • Columns: {list(df.columns)}")
            
            # Show sample data
            print(f"\n📋 SAMPLE DATA (First 3 rows):")
            print(df.head(3).to_string())
            
            # Check for missing values
            missing_data = df.isnull().sum()
            print(f"\n❌ MISSING DATA ANALYSIS:")
            for col, missing in missing_data.items():
                if missing > 0:
                    print(f"  • {col}: {missing} missing values ({missing/len(df)*100:.1f}%)")
            
            # Check data types
            print(f"\n📝 DATA TYPES:")
            for col, dtype in df.dtypes.items():
                print(f"  • {col}: {dtype}")
            
            return df
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return None
    
    def identify_key_columns(self, df):
        """Identify and map key columns from the Excel structure"""
        print("\n🎯 IDENTIFYING KEY COLUMNS")
        print("=" * 60)
        
        column_mapping = {}
        available_columns = list(df.columns)
        
        # Common column name patterns
        patterns = {
            'job_number': ['job', 'number', 'job_number', 'job_no', 'project_number'],
            'project_title': ['title', 'project', 'description', 'project_title', 'project_description'],
            'prime_firm': ['prime', 'firm', 'contractor', 'prime_firm', 'prime_contractor', 'selected_firm'],
            'subconsultants': ['sub', 'subconsultant', 'subconsultants', 'sub_consultant', 'sub_consultants'],
            'award_date': ['date', 'award', 'award_date', 'selection_date', 'contract_date'],
            'project_value': ['value', 'amount', 'cost', 'project_value', 'contract_value', 'budget'],
            'district': ['district', 'dist', 'region'],
            'location': ['location', 'city', 'county', 'area']
        }
        
        print("🔍 COLUMN MAPPING:")
        for target_col, patterns_list in patterns.items():
            found = False
            for pattern in patterns_list:
                for col in available_columns:
                    if pattern.lower() in col.lower():
                        column_mapping[target_col] = col
                        print(f"  • {target_col} → {col}")
                        found = True
                        break
                if found:
                    break
            
            if not found:
                print(f"  • {target_col} → NOT FOUND")
                column_mapping[target_col] = None
        
        return column_mapping
    
    def clean_and_validate_data(self, df, column_mapping):
        """Clean and validate the extracted data"""
        print("\n🧹 CLEANING AND VALIDATING DATA")
        print("=" * 60)
        
        cleaned_data = []
        validation_stats = {
            'total_records': len(df),
            'valid_records': 0,
            'invalid_records': 0,
            'missing_job_numbers': 0,
            'missing_prime_firms': 0,
            'missing_dates': 0,
            'invalid_dates': 0,
            'invalid_values': 0
        }
        
        for idx, row in df.iterrows():
            try:
                # Extract data using column mapping
                record = {}
                
                # Job Number
                job_col = column_mapping.get('job_number')
                if job_col and pd.notna(row[job_col]):
                    record['job_number'] = str(row[job_col]).strip()
                else:
                    validation_stats['missing_job_numbers'] += 1
                    continue
                
                # Project Title
                title_col = column_mapping.get('project_title')
                if title_col and pd.notna(row[title_col]):
                    record['project_title'] = str(row[title_col]).strip()
                else:
                    record['project_title'] = ''
                
                # Prime Firm
                prime_col = column_mapping.get('prime_firm')
                if prime_col and pd.notna(row[prime_col]):
                    record['prime_firm'] = self.clean_firm_name(str(row[prime_col]))
                else:
                    validation_stats['missing_prime_firms'] += 1
                    continue
                
                # Subconsultants
                sub_col = column_mapping.get('subconsultants')
                if sub_col and pd.notna(row[sub_col]):
                    subconsultants = str(row[sub_col]).strip()
                    if subconsultants and subconsultants.lower() not in ['nan', 'none', '']:
                        # Split subconsultants (assuming comma or semicolon separated)
                        sub_list = re.split(r'[,;]', subconsultants)
                        record['subconsultants'] = [self.clean_firm_name(sub.strip()) for sub in sub_list if sub.strip()]
                    else:
                        record['subconsultants'] = []
                else:
                    record['subconsultants'] = []
                
                # Award Date
                date_col = column_mapping.get('award_date')
                if date_col and pd.notna(row[date_col]):
                    parsed_date = self.parse_date(row[date_col])
                    if parsed_date:
                        record['award_date'] = parsed_date
                    else:
                        validation_stats['invalid_dates'] += 1
                        record['award_date'] = None
                else:
                    validation_stats['missing_dates'] += 1
                    record['award_date'] = None
                
                # Project Value
                value_col = column_mapping.get('project_value')
                if value_col and pd.notna(row[value_col]):
                    parsed_value = self.parse_project_value(row[value_col])
                    if parsed_value:
                        record['project_value'] = parsed_value
                    else:
                        validation_stats['invalid_values'] += 1
                        record['project_value'] = None
                else:
                    record['project_value'] = None
                
                # District
                district_col = column_mapping.get('district')
                if district_col and pd.notna(row[district_col]):
                    record['district'] = str(row[district_col]).strip()
                else:
                    record['district'] = None
                
                # Location
                location_col = column_mapping.get('location')
                if location_col and pd.notna(row[location_col]):
                    record['location'] = str(row[location_col]).strip()
                else:
                    record['location'] = None
                
                # Add record index and processing timestamp
                record['record_id'] = idx
                record['processing_date'] = datetime.now().isoformat()
                
                cleaned_data.append(record)
                validation_stats['valid_records'] += 1
                
            except Exception as e:
                print(f"❌ Error processing row {idx}: {str(e)}")
                validation_stats['invalid_records'] += 1
                continue
        
        # Print validation statistics
        print("📊 VALIDATION STATISTICS:")
        print(f"  • Total Records: {validation_stats['total_records']}")
        print(f"  • Valid Records: {validation_stats['valid_records']}")
        print(f"  • Invalid Records: {validation_stats['invalid_records']}")
        print(f"  • Missing Job Numbers: {validation_stats['missing_job_numbers']}")
        print(f"  • Missing Prime Firms: {validation_stats['missing_prime_firms']}")
        print(f"  • Missing Dates: {validation_stats['missing_dates']}")
        print(f"  • Invalid Dates: {validation_stats['invalid_dates']}")
        print(f"  • Invalid Values: {validation_stats['invalid_values']}")
        
        return cleaned_data, validation_stats
    
    def clean_firm_name(self, firm_name):
        """Clean and standardize firm names"""
        if not firm_name or pd.isna(firm_name):
            return None
        
        cleaned = str(firm_name).strip()
        
        # Apply cleaning patterns
        for pattern, replacement in self.extraction_config['firm_cleaning_patterns']:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    def parse_date(self, date_value):
        """Parse date from various formats"""
        if pd.isna(date_value):
            return None
        
        # If it's already a datetime object
        if isinstance(date_value, (datetime, pd.Timestamp)):
            return date_value.strftime('%Y-%m-%d')
        
        # Try to parse string date
        date_str = str(date_value).strip()
        
        for date_format in self.extraction_config['date_formats']:
            try:
                parsed_date = datetime.strptime(date_str, date_format)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def parse_project_value(self, value):
        """Parse project value from various formats"""
        if pd.isna(value):
            return None
        
        # If it's already a number
        if isinstance(value, (int, float)):
            return float(value)
        
        # Try to extract from string
        value_str = str(value).strip()
        
        # Remove currency symbols and commas
        cleaned_value = re.sub(r'[$,]', '', value_str)
        
        try:
            return float(cleaned_value)
        except ValueError:
            return None
    
    def generate_structured_output(self, cleaned_data, validation_stats):
        """Generate structured output for the firm experience matrix"""
        print("\n📊 GENERATING STRUCTURED OUTPUT")
        print("=" * 60)
        
        structured_data = {
            'metadata': {
                'extraction_date': datetime.now().isoformat(),
                'source_file': self.excel_file,
                'total_records': validation_stats['total_records'],
                'valid_records': validation_stats['valid_records'],
                'data_quality_score': validation_stats['valid_records'] / validation_stats['total_records'] * 100
            },
            'validation_stats': validation_stats,
            'awards': cleaned_data
        }
        
        # Save to JSON file
        with open(self.output_file, 'w') as f:
            json.dump(structured_data, f, indent=2)
        
        print(f"✅ Structured data saved: {self.output_file}")
        print(f"📊 Data Quality Score: {structured_data['metadata']['data_quality_score']:.1f}%")
        
        return structured_data
    
    def analyze_extracted_data(self, structured_data):
        """Analyze the extracted data for insights"""
        print("\n🔍 ANALYZING EXTRACTED DATA")
        print("=" * 60)
        
        awards = structured_data['awards']
        
        # Date range analysis
        dates = [award['award_date'] for award in awards if award['award_date']]
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            print(f"📅 DATE RANGE: {min_date} to {max_date}")
        
        # Firm analysis
        prime_firms = set(award['prime_firm'] for award in awards if award['prime_firm'])
        sub_firms = set()
        for award in awards:
            sub_firms.update(award['subconsultants'])
        
        print(f"🏢 FIRM ANALYSIS:")
        print(f"  • Unique Prime Firms: {len(prime_firms)}")
        print(f"  • Unique Subconsultant Firms: {len(sub_firms)}")
        print(f"  • Total Unique Firms: {len(prime_firms.union(sub_firms))}")
        
        # Project value analysis
        values = [award['project_value'] for award in awards if award['project_value']]
        if values:
            print(f"💰 PROJECT VALUE ANALYSIS:")
            print(f"  • Total Projects with Values: {len(values)}")
            print(f"  • Total Value: ${sum(values):,.2f}")
            print(f"  • Average Value: ${np.mean(values):,.2f}")
            print(f"  • Median Value: ${np.median(values):,.2f}")
        
        # District analysis
        districts = [award['district'] for award in awards if award['district']]
        if districts:
            district_counts = pd.Series(districts).value_counts()
            print(f"🗺️  DISTRICT ANALYSIS:")
            print(f"  • Projects by District:")
            for district, count in district_counts.head(10).items():
                print(f"    - {district}: {count} projects")
    
    def run_complete_extraction(self):
        """Run the complete extraction process"""
        print("🚀 AWARD DATA EXTRACTION SYSTEM")
        print("=" * 80)
        
        # Step 1: Analyze Excel structure
        df = self.analyze_excel_structure()
        if df is None:
            return None
        
        # Step 2: Identify key columns
        column_mapping = self.identify_key_columns(df)
        
        # Step 3: Clean and validate data
        cleaned_data, validation_stats = self.clean_and_validate_data(df, column_mapping)
        
        # Step 4: Generate structured output
        structured_data = self.generate_structured_output(cleaned_data, validation_stats)
        
        # Step 5: Analyze extracted data
        self.analyze_extracted_data(structured_data)
        
        print("\n🎉 EXTRACTION COMPLETE!")
        print("=" * 80)
        print(f"📄 Output file: {self.output_file}")
        print(f"📊 Valid records: {validation_stats['valid_records']}")
        print(f"✅ Ready for firm experience matrix development!")
        
        return structured_data

def main():
    """Main execution function"""
    extractor = AwardDataExtractor()
    result = extractor.run_complete_extraction()
    
    if result:
        print("\n✅ Extraction completed successfully!")
        print("📋 The structured data is ready for firm experience matrix development.")
    else:
        print("\n❌ Extraction failed. Please check the error messages above.")

if __name__ == "__main__":
    main()





