#!/usr/bin/env python3
"""
Phase 1 Data Standardization
Fix critical data quality issues identified by DeepSeek analysis
"""

import json
import re
import pandas as pd
from datetime import datetime
from difflib import SequenceMatcher
from collections import defaultdict

class Phase1DataStandardization:
    def __init__(self):
        self.data_dir = '../data'
        self.backup_dir = '../data/backups'
        self.standardization_results = {}
        
    def load_data_files(self):
        """Load all data files for standardization"""
        print("🔄 Loading data files for standardization...")
        
        # Load award structure
        with open(f'{self.data_dir}/award_structure.json', 'r') as f:
            self.award_structure = json.load(f)
        print(f"✅ Loaded {len(self.award_structure)} award records")
        
        # Load firms data
        with open(f'{self.data_dir}/firms_data.json', 'r') as f:
            self.firms_data = json.load(f)
        print(f"✅ Loaded {len(self.firms_data)} firm records")
        
        # Load prequal lookup
        with open(f'{self.data_dir}/prequal_lookup.json', 'r') as f:
            self.prequal_lookup = json.load(f)
        print(f"✅ Loaded {len(self.prequal_lookup)} prequalification categories")
        
    def create_backup(self):
        """Create backup of original data files"""
        print("📋 Creating backups...")
        
        import os
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup award structure
        backup_file = f'{self.backup_dir}/award_structure_backup_{timestamp}.json'
        with open(backup_file, 'w') as f:
            json.dump(self.award_structure, f, indent=2)
        print(f"✅ Award structure backup: {backup_file}")
        
        # Backup firms data
        backup_file = f'{self.backup_dir}/firms_data_backup_{timestamp}.json'
        with open(backup_file, 'w') as f:
            json.dump(self.firms_data, f, indent=2)
        print(f"✅ Firms data backup: {backup_file}")
        
    def standardize_job_numbers(self):
        """Standardize job number formats (61 variations -> standardized)"""
        print("\n🔧 Standardizing Job Number Formats...")
        
        job_patterns = {
            'standard': r'^([A-Z])-(\d{2})-(\d{3})-(\d{2})$',  # V-91-010-25
            'no_hyphens': r'^([A-Z])(\d{2})(\d{3})(\d{2})$',   # V9101025
            'extra_spaces': r'^([A-Z])\s*-\s*(\d{2})\s*-\s*(\d{3})\s*-\s*(\d{2})$',
            'different_separators': r'^([A-Z])[._](\d{2})[._](\d{3})[._](\d{2})$'
        }
        
        standardized_count = 0
        original_formats = defaultdict(int)
        
        for record in self.award_structure:
            if 'Job #' in record and record['Job #']:
                original_job = str(record['Job #']).strip()
                original_formats[original_job[:3]] += 1
                
                # Try to standardize
                standardized_job = self.normalize_job_number(original_job)
                if standardized_job != original_job:
                    record['Job #'] = standardized_job
                    standardized_count += 1
                    
        self.standardization_results['job_numbers'] = {
            'original_formats': len(original_formats),
            'standardized_count': standardized_count,
            'format_variations': dict(original_formats)
        }
        
        print(f"✅ Standardized {standardized_count} job numbers")
        print(f"📊 Original format variations: {len(original_formats)}")
        
    def normalize_job_number(self, job_number):
        """Normalize a job number to standard format"""
        if not job_number:
            return job_number
            
        job_str = str(job_number).strip().upper()
        
        # Remove extra spaces and normalize separators
        job_str = re.sub(r'\s+', '', job_str)
        job_str = re.sub(r'[._]', '-', job_str)
        
        # Handle different patterns
        patterns = [
            r'^([A-Z])-(\d{2})-(\d{3})-(\d{2})$',  # Standard
            r'^([A-Z])(\d{2})(\d{3})(\d{2})$',     # No hyphens
            r'^([A-Z])-(\d{1})-(\d{3})-(\d{2})$',  # Single digit
            r'^([A-Z])-(\d{2})-(\d{2})-(\d{2})$',  # Different lengths
        ]
        
        for pattern in patterns:
            match = re.match(pattern, job_str)
            if match:
                parts = match.groups()
                # Ensure proper formatting
                if len(parts[1]) == 1:
                    parts = (parts[0], f"0{parts[1]}", parts[2], parts[3])
                if len(parts[2]) == 2:
                    parts = (parts[0], parts[1], f"0{parts[2]}", parts[3])
                return f"{parts[0]}-{parts[1]}-{parts[2]}-{parts[3]}"
                
        return job_number  # Return original if no pattern matches
        
    def fix_missing_subconsultants(self):
        """Fix missing subconsultant data (630 records)"""
        print("\n🔧 Fixing Missing Subconsultant Data...")
        
        missing_count = 0
        fixed_count = 0
        
        for record in self.award_structure:
            if not record.get('SUBCONSULTANTS') or record['SUBCONSULTANTS'] is None:
                missing_count += 1
                
                # Try to find subconsultants from similar projects
                subconsultants = self.find_subconsultants_from_similar_projects(record)
                if subconsultants:
                    record['SUBCONSULTANTS'] = subconsultants
                    fixed_count += 1
                else:
                    # Set default empty list instead of None
                    record['SUBCONSULTANTS'] = []
                    
        self.standardization_results['subconsultants'] = {
            'missing_count': missing_count,
            'fixed_count': fixed_count,
            'fix_rate': (fixed_count / missing_count * 100) if missing_count > 0 else 0
        }
        
        print(f"✅ Fixed {fixed_count}/{missing_count} missing subconsultant records")
        print(f"📊 Fix rate: {self.standardization_results['subconsultants']['fix_rate']:.1f}%")
        
    def find_subconsultants_from_similar_projects(self, record):
        """Find subconsultants from similar projects"""
        if not record.get('Job #'):
            return None
            
        job_number = record['Job #']
        base_job = self.get_base_job_number(job_number)
        
        # Look for similar projects with subconsultants
        for other_record in self.award_structure:
            if (other_record.get('SUBCONSULTANTS') and 
                other_record['SUBCONSULTANTS'] and 
                self.get_base_job_number(other_record.get('Job #', '')) == base_job):
                return other_record['SUBCONSULTANTS']
                
        return None
        
    def get_base_job_number(self, job_number):
        """Get base job number for comparison"""
        if not job_number:
            return ""
        # Extract the main part (e.g., V-91-010 from V-91-010-25)
        parts = str(job_number).split('-')
        if len(parts) >= 3:
            return f"{parts[0]}-{parts[1]}-{parts[2]}"
        return str(job_number)
        
    def normalize_firm_names(self):
        """Normalize firm names (remove duplicates)"""
        print("\n🔧 Normalizing Firm Names...")
        
        firm_name_mapping = {}
        duplicate_count = 0
        
        # Create mapping for common variations
        name_variations = {
            'COTTER CONSULTING': 'COTTER CONSULTING, INC.',
            'COTTER CONSULTING, INC': 'COTTER CONSULTING, INC.',
            'CARDNO TBE': 'CARDNO TBE, INC.',
            'CARDNO TBE, INC': 'CARDNO TBE, INC.',
            'HNTB CORPORATION': 'HNTB CORPORATION, INC.',
            'HNTB CORP': 'HNTB CORPORATION, INC.',
            'AECOM TECHNICAL SERVICES': 'AECOM TECHNICAL SERVICES, INC.',
            'AECOM TECH SERVICES': 'AECOM TECHNICAL SERVICES, INC.',
        }
        
        # Process award structure
        for record in self.award_structure:
            if 'SELECTED FIRM' in record and record['SELECTED FIRM']:
                original_name = record['SELECTED FIRM'].strip()
                normalized_name = self.normalize_firm_name(original_name, name_variations)
                
                if normalized_name != original_name:
                    record['SELECTED FIRM'] = normalized_name
                    duplicate_count += 1
                    
        # Process firms data
        for firm in self.firms_data:
            if 'firm_name' in firm and firm['firm_name']:
                original_name = firm['firm_name'].strip()
                normalized_name = self.normalize_firm_name(original_name, name_variations)
                
                if normalized_name != original_name:
                    firm['firm_name'] = normalized_name
                    duplicate_count += 1
                    
        self.standardization_results['firm_names'] = {
            'normalized_count': duplicate_count,
            'name_variations': len(name_variations)
        }
        
        print(f"✅ Normalized {duplicate_count} firm names")
        print(f"📊 Name variations handled: {len(name_variations)}")
        
    def normalize_firm_name(self, firm_name, variations):
        """Normalize a single firm name"""
        if not firm_name:
            return firm_name
            
        # Check exact matches first
        if firm_name.upper() in variations:
            return variations[firm_name.upper()]
            
        # Check fuzzy matches
        for original, normalized in variations.items():
            if SequenceMatcher(None, firm_name.upper(), original).ratio() > 0.85:
                return normalized
                
        return firm_name
        
    def add_missing_fields(self):
        """Add missing fields with default values"""
        print("\n🔧 Adding Missing Fields...")
        
        missing_fields = {
            'Fee Estimate': 0,
            'Submitted': 0,
            'Eligible': 0,
            'First Alternate': '',
            'Second Alternate': ''
        }
        
        added_count = 0
        
        for record in self.award_structure:
            for field, default_value in missing_fields.items():
                if field not in record or record[field] is None:
                    record[field] = default_value
                    added_count += 1
                    
        self.standardization_results['missing_fields'] = {
            'added_count': added_count,
            'fields_added': list(missing_fields.keys())
        }
        
        print(f"✅ Added {added_count} missing field values")
        print(f"📊 Fields processed: {len(missing_fields)}")
        
    def validate_data_quality(self):
        """Validate data quality after standardization"""
        print("\n🔍 Validating Data Quality...")
        
        validation_results = {
            'total_award_records': len(self.award_structure),
            'total_firm_records': len(self.firms_data),
            'missing_job_numbers': 0,
            'missing_firm_names': 0,
            'missing_subconsultants': 0,
            'inconsistent_formats': 0
        }
        
        # Check award structure
        for record in self.award_structure:
            if not record.get('Job #'):
                validation_results['missing_job_numbers'] += 1
            if not record.get('SELECTED FIRM'):
                validation_results['missing_firm_names'] += 1
            if not record.get('SUBCONSULTANTS'):
                validation_results['missing_subconsultants'] += 1
                
        # Check job number format consistency
        job_formats = set()
        for record in self.award_structure:
            if record.get('Job #'):
                job_formats.add(str(record['Job #'])[:3])
        validation_results['inconsistent_formats'] = len(job_formats)
        
        self.standardization_results['validation'] = validation_results
        
        print(f"✅ Validation complete")
        print(f"📊 Job format variations: {validation_results['inconsistent_formats']}")
        print(f"📊 Missing job numbers: {validation_results['missing_job_numbers']}")
        print(f"📊 Missing firm names: {validation_results['missing_firm_names']}")
        print(f"📊 Missing subconsultants: {validation_results['missing_subconsultants']}")
        
    def save_standardized_data(self):
        """Save standardized data files"""
        print("\n💾 Saving Standardized Data...")
        
        # Save standardized award structure
        with open(f'{self.data_dir}/award_structure_standardized.json', 'w') as f:
            json.dump(self.award_structure, f, indent=2)
        print(f"✅ Saved standardized award structure")
        
        # Save standardized firms data
        with open(f'{self.data_dir}/firms_data_standardized.json', 'w') as f:
            json.dump(self.firms_data, f, indent=2)
        print(f"✅ Saved standardized firms data")
        
        # Save standardization results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f'phase1_standardization_results_{timestamp}.json'
        with open(results_file, 'w') as f:
            json.dump(self.standardization_results, f, indent=2)
        print(f"✅ Saved standardization results: {results_file}")
        
    def generate_standardization_report(self):
        """Generate comprehensive standardization report"""
        print("\n📋 Generating Standardization Report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'phase1_standardization_report_{timestamp}.txt'
        
        with open(report_file, 'w') as f:
            f.write("PHASE 1 DATA STANDARDIZATION REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("STANDARDIZATION SUMMARY\n")
            f.write("-" * 25 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Award Records: {len(self.award_structure)}\n")
            f.write(f"Total Firm Records: {len(self.firms_data)}\n\n")
            
            # Job Numbers
            job_results = self.standardization_results.get('job_numbers', {})
            f.write("JOB NUMBER STANDARDIZATION\n")
            f.write("-" * 30 + "\n")
            f.write(f"Original Format Variations: {job_results.get('original_formats', 0)}\n")
            f.write(f"Standardized Count: {job_results.get('standardized_count', 0)}\n\n")
            
            # Subconsultants
            sub_results = self.standardization_results.get('subconsultants', {})
            f.write("SUBCONSULTANT DATA FIXES\n")
            f.write("-" * 30 + "\n")
            f.write(f"Missing Records: {sub_results.get('missing_count', 0)}\n")
            f.write(f"Fixed Records: {sub_results.get('fixed_count', 0)}\n")
            f.write(f"Fix Rate: {sub_results.get('fix_rate', 0):.1f}%\n\n")
            
            # Firm Names
            firm_results = self.standardization_results.get('firm_names', {})
            f.write("FIRM NAME NORMALIZATION\n")
            f.write("-" * 30 + "\n")
            f.write(f"Normalized Count: {firm_results.get('normalized_count', 0)}\n")
            f.write(f"Name Variations Handled: {firm_results.get('name_variations', 0)}\n\n")
            
            # Missing Fields
            field_results = self.standardization_results.get('missing_fields', {})
            f.write("MISSING FIELD ADDITIONS\n")
            f.write("-" * 30 + "\n")
            f.write(f"Added Count: {field_results.get('added_count', 0)}\n")
            f.write(f"Fields Processed: {len(field_results.get('fields_added', []))}\n\n")
            
            # Validation
            validation = self.standardization_results.get('validation', {})
            f.write("DATA QUALITY VALIDATION\n")
            f.write("-" * 30 + "\n")
            f.write(f"Missing Job Numbers: {validation.get('missing_job_numbers', 0)}\n")
            f.write(f"Missing Firm Names: {validation.get('missing_firm_names', 0)}\n")
            f.write(f"Missing Subconsultants: {validation.get('missing_subconsultants', 0)}\n")
            f.write(f"Job Format Variations: {validation.get('inconsistent_formats', 0)}\n\n")
            
        print(f"✅ Standardization report saved: {report_file}")
        return report_file
        
    def run_phase1_standardization(self):
        """Run complete Phase 1 data standardization"""
        print("🚀 Starting Phase 1 Data Standardization...")
        
        # Load data
        self.load_data_files()
        
        # Create backups
        self.create_backup()
        
        # Run standardization steps
        self.standardize_job_numbers()
        self.fix_missing_subconsultants()
        self.normalize_firm_names()
        self.add_missing_fields()
        
        # Validate results
        self.validate_data_quality()
        
        # Save standardized data
        self.save_standardized_data()
        
        # Generate report
        report_file = self.generate_standardization_report()
        
        print(f"\n✅ Phase 1 Standardization Complete!")
        print(f"📄 Report: {report_file}")
        
        return self.standardization_results

if __name__ == "__main__":
    standardizer = Phase1DataStandardization()
    results = standardizer.run_phase1_standardization()
