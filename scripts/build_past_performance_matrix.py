#!/usr/bin/env python3
"""
Build Past Performance Matrix
Create a comprehensive firm experience matrix based on historical award data
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import re

class PastPerformanceMatrixBuilder:
    def __init__(self):
        self.award_file = '../data/award.xlsx'
        self.firms_data_file = '../data/firms_data.json'
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.output_file = '../data/past_performance_matrix.json'
        
        # Load data
        self.award_df = pd.read_excel(self.award_file)
        
        with open(self.firms_data_file, 'r') as f:
            self.firms_data = json.load(f)
        
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        # Create firm mappings
        self.firm_code_to_name = {firm['firm_code']: firm['firm_name'] for firm in self.firms_data}
        self.firm_name_to_code = {firm['firm_name']: firm['firm_code'] for firm in self.firms_data}
        
        # Scoring weights
        self.role_weights = {
            'prime': 1.0,           # Selected firm
            'subconsultant': 0.3,   # Subconsultant
            'first_alternate': 0.5,  # First alternate
            'second_alternate': 0.4  # Second alternate
        }
        
        # Time decay weights
        self.time_weights = {
            'recent': 1.0,      # Within 5 years
            'medium': 0.7,      # 5-10 years
            'old': 0.3          # 10+ years
        }
        
        # Results storage
        self.performance_matrix = {}
        self.analysis_results = {
            'total_projects': 0,
            'firms_with_experience': 0,
            'total_experience_points': 0,
            'matrix_created': False
        }
    
    def clean_and_prepare_award_data(self):
        """Clean and prepare award data for analysis"""
        print("🔧 CLEANING AND PREPARING AWARD DATA")
        print("=" * 80)
        
        # Create a copy for cleaning
        df = self.award_df.copy()
        
        # Clean job numbers
        df['Job #'] = df['Job #'].astype(str).str.strip()
        
        # Clean firm names
        df['SELECTED FIRM'] = df['SELECTED FIRM'].astype(str).str.strip()
        df['SUBCONSULTANTS'] = df['SUBCONSULTANTS'].astype(str).str.strip()
        df['First Alternate'] = df['First Alternate'].astype(str).str.strip()
        df['Second Alternate'] = df['Second Alternate'].astype(str).str.strip()
        
        # Clean dates
        df['Selection Date'] = pd.to_datetime(df['Selection Date'], errors='coerce')
        
        # Extract year from job numbers for time weighting
        df['project_year'] = df['Job #'].str.extract(r'(\d{2})').astype(float)
        df['project_year'] = 2000 + df['project_year']  # Convert to full year
        
        # Clean prequalifications
        df['Prequals'] = df['Prequals'].fillna('')
        
        print(f"✅ Award data cleaned and prepared")
        print(f"   Total projects: {len(df)}")
        print(f"   Projects with dates: {df['Selection Date'].notna().sum()}")
        print(f"   Projects with years: {df['project_year'].notna().sum()}")
        
        return df
    
    def extract_firms_from_text(self, text):
        """Extract firm names from text (handles multiple firms separated by semicolons)"""
        if pd.isna(text) or text == 'nan' or text == '':
            return []
        
        # Split by semicolon and clean
        firms = [firm.strip() for firm in str(text).split(';') if firm.strip()]
        return firms
    
    def calculate_time_weight(self, project_year):
        """Calculate time weight based on project year"""
        current_year = datetime.now().year
        
        if pd.isna(project_year):
            return self.time_weights['medium']  # Default to medium weight
        
        years_ago = current_year - project_year
        
        if years_ago <= 5:
            return self.time_weights['recent']
        elif years_ago <= 10:
            return self.time_weights['medium']
        else:
            return self.time_weights['old']
    
    def normalize_firm_name(self, firm_name):
        """Normalize firm name for matching"""
        if pd.isna(firm_name) or firm_name == 'nan':
            return None
        
        # Basic normalization
        normalized = str(firm_name).strip().upper()
        
        # Remove common suffixes
        suffixes = [' INC', ' LLC', ' P.C.', ' CORP', ' CORPORATION', ' LTD', ' CO', ' COMPANY']
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
        
        return normalized.strip()
    
    def match_firm_to_code(self, firm_name):
        """Match firm name to firm code"""
        if not firm_name or firm_name == 'nan':
            return None
        
        # Direct match
        if firm_name in self.firm_name_to_code:
            return self.firm_name_to_code[firm_name]
        
        # Normalized match
        normalized_name = self.normalize_firm_name(firm_name)
        for name, code in self.firm_name_to_code.items():
            if self.normalize_firm_name(name) == normalized_name:
                return code
        
        return None
    
    def extract_prequalifications(self, prequal_text):
        """Extract prequalifications from text"""
        if pd.isna(prequal_text) or prequal_text == '':
            return []
        
        prequals = []
        lines = str(prequal_text).split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('nan'):
                # Remove numbering (e.g., "1.", "2.")
                line = re.sub(r'^\d+\.', '', line).strip()
                if line:
                    prequals.append(line)
        
        return prequals
    
    def build_experience_matrix(self):
        """Build the past performance matrix"""
        print("🏗️  BUILDING PAST PERFORMANCE MATRIX")
        print("=" * 80)
        
        # Clean award data
        df = self.clean_and_prepare_award_data()
        
        # Initialize matrix
        matrix = {}
        
        total_projects = 0
        firms_with_experience = 0
        
        for idx, row in df.iterrows():
            total_projects += 1
            
            # Extract project information
            job_number = row['Job #']
            project_year = row['project_year']
            time_weight = self.calculate_time_weight(project_year)
            
            # Extract firms and their roles
            firms_roles = []
            
            # Selected firm (Prime)
            selected_firm = row['SELECTED FIRM']
            if selected_firm and selected_firm != 'nan':
                firms_roles.append((selected_firm, 'prime'))
            
            # Subconsultants
            subconsultants_text = row['SUBCONSULTANTS']
            if subconsultants_text and subconsultants_text != 'nan':
                subconsultants = self.extract_firms_from_text(subconsultants_text)
                for firm in subconsultants:
                    firms_roles.append((firm, 'subconsultant'))
            
            # First Alternate
            first_alt = row['First Alternate']
            if first_alt and first_alt != 'nan':
                firms_roles.append((first_alt, 'first_alternate'))
            
            # Second Alternate
            second_alt = row['Second Alternate']
            if second_alt and second_alt != 'nan':
                firms_roles.append((second_alt, 'second_alternate'))
            
            # Extract prequalifications
            prequals = self.extract_prequalifications(row['Prequals'])
            
            # Process each firm
            for firm_name, role in firms_roles:
                firm_code = self.match_firm_to_code(firm_name)
                
                if firm_code:
                    # Initialize firm data if not exists
                    if firm_code not in matrix:
                        matrix[firm_code] = {
                            'total_experience_points': 0.0,
                            'total_projects': 0,
                            'prime_projects': 0,
                            'subconsultant_projects': 0,
                            'alternate_projects': 0,
                            'project_details': [],
                            'prequalification_experience': defaultdict(float),
                            'recent_experience': 0.0,
                            'medium_experience': 0.0,
                            'old_experience': 0.0
                        }
                    
                    # Calculate experience points
                    role_weight = self.role_weights[role]
                    experience_points = role_weight * time_weight
                    
                    # Update matrix
                    matrix[firm_code]['total_experience_points'] += experience_points
                    matrix[firm_code]['total_projects'] += 1
                    
                    # Update role counts
                    if role == 'prime':
                        matrix[firm_code]['prime_projects'] += 1
                    elif role == 'subconsultant':
                        matrix[firm_code]['subconsultant_projects'] += 1
                    else:
                        matrix[firm_code]['alternate_projects'] += 1
                    
                    # Update time-based experience
                    if time_weight == self.time_weights['recent']:
                        matrix[firm_code]['recent_experience'] += experience_points
                    elif time_weight == self.time_weights['medium']:
                        matrix[firm_code]['medium_experience'] += experience_points
                    else:
                        matrix[firm_code]['old_experience'] += experience_points
                    
                    # Add project details
                    project_detail = {
                        'job_number': job_number,
                        'role': role,
                        'experience_points': experience_points,
                        'project_year': project_year,
                        'time_weight': time_weight,
                        'prequalifications': prequals
                    }
                    matrix[firm_code]['project_details'].append(project_detail)
                    
                    # Update prequalification experience
                    for prequal in prequals:
                        matrix[firm_code]['prequalification_experience'][prequal] += experience_points
        
        # Convert defaultdict to regular dict and add firm names
        final_matrix = {}
        for firm_code, data in matrix.items():
            if firm_code in self.firm_code_to_name:
                final_matrix[firm_code] = {
                    'firm_name': self.firm_code_to_name[firm_code],
                    'firm_code': firm_code,
                    **data
                }
                firms_with_experience += 1
        
        self.performance_matrix = final_matrix
        
        # Update analysis results
        self.analysis_results['total_projects'] = total_projects
        self.analysis_results['firms_with_experience'] = firms_with_experience
        self.analysis_results['total_experience_points'] = sum(data['total_experience_points'] for data in final_matrix.values())
        self.analysis_results['matrix_created'] = True
        
        print(f"✅ Past performance matrix built successfully!")
        print(f"   Total projects analyzed: {total_projects}")
        print(f"   Firms with experience: {firms_with_experience}")
        print(f"   Total experience points: {self.analysis_results['total_experience_points']:.2f}")
        
        return final_matrix
    
    def save_matrix(self):
        """Save the performance matrix to JSON file"""
        if not self.performance_matrix:
            print("❌ No matrix to save. Build matrix first.")
            return
        
        print(f"💾 Saving performance matrix to {self.output_file}")
        
        output_data = {
            'metadata': {
                'created_date': datetime.now().isoformat(),
                'total_firms': len(self.performance_matrix),
                'total_projects': self.analysis_results['total_projects'],
                'total_experience_points': self.analysis_results['total_experience_points'],
                'scoring_weights': self.role_weights,
                'time_weights': self.time_weights
            },
            'performance_matrix': self.performance_matrix
        }
        
        with open(self.output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"✅ Performance matrix saved successfully!")
    
    def generate_summary_report(self):
        """Generate summary report of the performance matrix"""
        if not self.performance_matrix:
            print("❌ No matrix to analyze. Build matrix first.")
            return
        
        print("📊 PAST PERFORMANCE MATRIX SUMMARY")
        print("=" * 80)
        
        # Top performing firms
        sorted_firms = sorted(
            self.performance_matrix.items(),
            key=lambda x: x[1]['total_experience_points'],
            reverse=True
        )
        
        print(f"🏆 TOP 10 FIRMS BY EXPERIENCE POINTS:")
        for i, (firm_code, data) in enumerate(sorted_firms[:10], 1):
            print(f"   {i:2d}. {data['firm_name']} ({firm_code})")
            print(f"       Experience Points: {data['total_experience_points']:.2f}")
            print(f"       Total Projects: {data['total_projects']}")
            print(f"       Prime Projects: {data['prime_projects']}")
            print()
        
        # Experience distribution
        experience_points = [data['total_experience_points'] for data in self.performance_matrix.values()]
        
        print(f"📈 EXPERIENCE DISTRIBUTION:")
        print(f"   Average experience points: {np.mean(experience_points):.2f}")
        print(f"   Median experience points: {np.median(experience_points):.2f}")
        print(f"   Max experience points: {np.max(experience_points):.2f}")
        print(f"   Min experience points: {np.min(experience_points):.2f}")
        print()
        
        # Role distribution
        total_prime = sum(data['prime_projects'] for data in self.performance_matrix.values())
        total_sub = sum(data['subconsultant_projects'] for data in self.performance_matrix.values())
        total_alt = sum(data['alternate_projects'] for data in self.performance_matrix.values())
        
        print(f"🎭 ROLE DISTRIBUTION:")
        print(f"   Prime projects: {total_prime}")
        print(f"   Subconsultant projects: {total_sub}")
        print(f"   Alternate projects: {total_alt}")
        print()
        
        # Time distribution
        total_recent = sum(data['recent_experience'] for data in self.performance_matrix.values())
        total_medium = sum(data['medium_experience'] for data in self.performance_matrix.values())
        total_old = sum(data['old_experience'] for data in self.performance_matrix.values())
        
        print(f"⏰ TIME DISTRIBUTION:")
        print(f"   Recent experience (≤5 years): {total_recent:.2f} points")
        print(f"   Medium experience (5-10 years): {total_medium:.2f} points")
        print(f"   Old experience (>10 years): {total_old:.2f} points")
    
    def run_complete_build(self):
        """Run complete past performance matrix build process"""
        print("🚀 BUILDING COMPREHENSIVE PAST PERFORMANCE MATRIX")
        print("=" * 80)
        
        # Build matrix
        matrix = self.build_experience_matrix()
        
        # Generate summary
        self.generate_summary_report()
        
        # Save matrix
        self.save_matrix()
        
        print(f"\n✅ Past performance matrix build complete!")
        print(f"Matrix saved to: {self.output_file}")
        
        return self.performance_matrix

def main():
    builder = PastPerformanceMatrixBuilder()
    matrix = builder.run_complete_build()

if __name__ == "__main__":
    main()
