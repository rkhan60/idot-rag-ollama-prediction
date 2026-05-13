#!/usr/bin/env python3
"""
Create Proper Past Performance Structure
Build a well-structured past performance file optimized for workflow queries
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime
from collections import defaultdict
import re

class ProperPerformanceStructureBuilder:
    def __init__(self):
        self.award_file = '../data/award.xlsx'
        self.firms_data_file = '../data/firms_data.json'
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        self.output_file = '../data/proper_past_performance.json'
        
        # Load data
        self.award_df = pd.read_excel(self.award_file)
        
        with open(self.firms_data_file, 'r') as f:
            self.firms_data = json.load(f)
        
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
        
        # Create firm mappings
        self.firm_code_to_name = {firm['firm_code']: firm['firm_name'] for firm in self.firms_data}
        self.firm_name_to_code = {firm['firm_name']: firm['firm_code'] for firm in self.firms_data}
        
        # Get all prequalification categories from lookup
        self.all_prequals = set()
        for head_category, data in self.prequal_lookup.items():
            for sub_code, sub_data in data['sub_categories'].items():
                self.all_prequals.add(sub_data['full_prequal_name'])
        
        # Scoring weights
        self.role_weights = {
            'prime': 1.0,
            'subconsultant': 0.3,
            'first_alternate': 0.5,
            'second_alternate': 0.4
        }
        
        # Time decay weights
        self.time_weights = {
            'recent': 1.0,      # Within 5 years
            'medium': 0.7,      # 5-10 years
            'old': 0.3          # 10+ years
        }
    
    def clean_and_prepare_award_data(self):
        """Clean and prepare award data for analysis"""
        print("🔧 CLEANING AND PREPARING AWARD DATA")
        print("=" * 80)
        
        df = self.award_df.copy()
        
        # Clean job numbers and extract years
        df['Job #'] = df['Job #'].astype(str).str.strip()
        df['project_year'] = df['Job #'].str.extract(r'(\d{2})').astype(float)
        df['project_year'] = 2000 + df['project_year']
        
        # Clean firm names
        df['SELECTED FIRM'] = df['SELECTED FIRM'].astype(str).str.strip()
        df['SUBCONSULTANTS'] = df['SUBCONSULTANTS'].astype(str).str.strip()
        df['First Alternate'] = df['First Alternate'].astype(str).str.strip()
        df['Second Alternate'] = df['Second Alternate'].astype(str).str.strip()
        
        # Clean prequalifications
        df['Prequals'] = df['Prequals'].fillna('')
        
        print(f"✅ Award data cleaned and prepared")
        print(f"   Total projects: {len(df)}")
        print(f"   Projects with years: {df['project_year'].notna().sum()}")
        
        return df
    
    def extract_firms_from_text(self, text):
        """Extract firm names from text"""
        if pd.isna(text) or text == 'nan' or text == '':
            return []
        
        firms = [firm.strip() for firm in str(text).split(';') if firm.strip()]
        return firms
    
    def calculate_time_weight(self, project_year):
        """Calculate time weight based on project year"""
        current_year = datetime.now().year
        
        if pd.isna(project_year):
            return self.time_weights['medium']
        
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
        
        normalized = str(firm_name).strip().upper()
        
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
    
    def fuzzy_match_prequal(self, extracted_prequal, lookup_prequals):
        """Fuzzy match extracted prequalification to lookup categories"""
        extracted = extracted_prequal.lower().replace(':', '').replace('-', ' ').strip()
        
        for lookup_prequal in lookup_prequals:
            lookup = lookup_prequal.lower().replace(':', '').replace('-', ' ').strip()
            
            # Direct match
            if extracted == lookup:
                return lookup_prequal
            
            # Partial match
            if extracted in lookup or lookup in extracted:
                return lookup_prequal
            
            # Handle common variations
            variations = {
                'roads & streets': 'roads and streets',
                'roads and streets': 'roads & streets',
                'quality assurance: qa': 'quality assurance',
                'quality assurance qa': 'quality assurance',
                'location/design': 'location design',
                'location design': 'location/design',
            }
            
            if extracted in variations and variations[extracted] in lookup:
                return lookup_prequal
            if lookup in variations and variations[lookup] in extracted:
                return lookup_prequal
        
        return None
    
    def build_proper_structure(self):
        """Build the properly structured performance matrix"""
        print("🏗️  BUILDING PROPER PERFORMANCE STRUCTURE")
        print("=" * 80)
        
        # Clean award data
        df = self.clean_and_prepare_award_data()
        
        # Initialize structure
        structure = {
            'metadata': {
                'created_date': datetime.now().isoformat(),
                'total_projects': len(df),
                'scoring_weights': self.role_weights,
                'time_weights': self.time_weights,
                'total_prequalifications': len(self.all_prequals)
            },
            'prequalification_firm_rankings': {},
            'firm_detailed_experience': {},
            'prequalification_summary': {}
        }
        
        # Initialize prequalification rankings
        for prequal in self.all_prequals:
            structure['prequalification_firm_rankings'][prequal] = []
            structure['prequalification_summary'][prequal] = {
                'total_firms': 0,
                'total_experience_points': 0.0,
                'total_projects': 0
            }
        
        # Initialize firm experience tracking
        firm_experience = {}
        
        total_projects_processed = 0
        firms_with_experience = set()
        
        print("📊 Processing projects and building experience matrix...")
        
        for idx, row in df.iterrows():
            total_projects_processed += 1
            
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
            
            # Extract and match prequalifications
            extracted_prequals = self.extract_prequalifications(row['Prequals'])
            matched_prequals = []
            
            for extracted_prequal in extracted_prequals:
                matched_prequal = self.fuzzy_match_prequal(extracted_prequal, self.all_prequals)
                if matched_prequal:
                    matched_prequals.append(matched_prequal)
            
            # If no prequalifications found, skip this project
            if not matched_prequals:
                continue
            
            # Process each firm
            for firm_name, role in firms_roles:
                firm_code = self.match_firm_to_code(firm_name)
                
                if firm_code:
                    firms_with_experience.add(firm_code)
                    
                    # Initialize firm data if not exists
                    if firm_code not in firm_experience:
                        firm_experience[firm_code] = {}
                    
                    # Calculate experience points
                    role_weight = self.role_weights[role]
                    experience_points = role_weight * time_weight
                    
                    # Update experience for each prequalification
                    for prequal in matched_prequals:
                        # Initialize prequal data if not exists
                        if prequal not in firm_experience[firm_code]:
                            firm_experience[firm_code][prequal] = {
                                'experience_points': 0.0,
                                'total_projects': 0,
                                'prime_projects': 0,
                                'subconsultant_projects': 0,
                                'alternate_projects': 0,
                                'recent_experience': 0.0,
                                'medium_experience': 0.0,
                                'old_experience': 0.0,
                                'project_details': []
                            }
                        
                        # Update firm experience
                        firm_experience[firm_code][prequal]['experience_points'] += experience_points
                        firm_experience[firm_code][prequal]['total_projects'] += 1
                        
                        # Update role counts
                        if role == 'prime':
                            firm_experience[firm_code][prequal]['prime_projects'] += 1
                        elif role == 'subconsultant':
                            firm_experience[firm_code][prequal]['subconsultant_projects'] += 1
                        else:
                            firm_experience[firm_code][prequal]['alternate_projects'] += 1
                        
                        # Update time-based experience
                        if time_weight == self.time_weights['recent']:
                            firm_experience[firm_code][prequal]['recent_experience'] += experience_points
                        elif time_weight == self.time_weights['medium']:
                            firm_experience[firm_code][prequal]['medium_experience'] += experience_points
                        else:
                            firm_experience[firm_code][prequal]['old_experience'] += experience_points
                        
                        # Add project details
                        project_detail = {
                            'job_number': job_number,
                            'role': role,
                            'experience_points': experience_points,
                            'project_year': project_year,
                            'time_weight': time_weight,
                            'prequalifications': matched_prequals
                        }
                        firm_experience[firm_code][prequal]['project_details'].append(project_detail)
                        
                        # Update prequalification summary
                        structure['prequalification_summary'][prequal]['total_experience_points'] += experience_points
                        structure['prequalification_summary'][prequal]['total_projects'] += 1
        
        print(f"✅ Processed {total_projects_processed} projects")
        print(f"✅ Found experience for {len(firms_with_experience)} firms")
        
        # Build prequalification rankings
        print("📊 Building prequalification rankings...")
        
        for prequal in self.all_prequals:
            firms_with_prequal = []
            
            for firm_code, prequal_data in firm_experience.items():
                if prequal in prequal_data and prequal_data[prequal]['experience_points'] > 0:
                    firms_with_prequal.append({
                        'firm_code': firm_code,
                        'firm_name': self.firm_code_to_name.get(firm_code, 'Unknown'),
                        'experience_points': prequal_data[prequal]['experience_points'],
                        'total_projects': prequal_data[prequal]['total_projects'],
                        'prime_projects': prequal_data[prequal]['prime_projects'],
                        'subconsultant_projects': prequal_data[prequal]['subconsultant_projects'],
                        'alternate_projects': prequal_data[prequal]['alternate_projects'],
                        'recent_experience': prequal_data[prequal]['recent_experience'],
                        'medium_experience': prequal_data[prequal]['medium_experience'],
                        'old_experience': prequal_data[prequal]['old_experience']
                    })
            
            # Sort by experience points and add ranking
            firms_with_prequal.sort(key=lambda x: x['experience_points'], reverse=True)
            
            for i, firm_data in enumerate(firms_with_prequal, 1):
                firm_data['ranking'] = i
            
            structure['prequalification_firm_rankings'][prequal] = firms_with_prequal
            structure['prequalification_summary'][prequal]['total_firms'] = len(firms_with_prequal)
        
        # Build detailed firm experience
        print("📊 Building detailed firm experience...")
        
        for firm_code, prequal_data in firm_experience.items():
            if firm_code in self.firm_code_to_name:
                structure['firm_detailed_experience'][firm_code] = {
                    'firm_name': self.firm_code_to_name[firm_code],
                    'firm_code': firm_code,
                    'prequalification_experience': dict(prequal_data),
                    'overall_experience': {
                        'total_experience_points': sum(data['experience_points'] for data in prequal_data.values()),
                        'total_projects': sum(data['total_projects'] for data in prequal_data.values()),
                        'total_prime_projects': sum(data['prime_projects'] for data in prequal_data.values()),
                        'total_subconsultant_projects': sum(data['subconsultant_projects'] for data in prequal_data.values()),
                        'total_alternate_projects': sum(data['alternate_projects'] for data in prequal_data.values())
                    }
                }
        
        # Update metadata
        structure['metadata']['firms_with_experience'] = len(firms_with_experience)
        structure['metadata']['total_experience_points'] = sum(
            data['total_experience_points'] for data in structure['prequalification_summary'].values()
        )
        
        print(f"✅ Proper performance structure built successfully!")
        
        return structure
    
    def save_structure(self, structure):
        """Save the properly structured performance data"""
        print(f"💾 Saving properly structured performance data to {self.output_file}")
        
        with open(self.output_file, 'w') as f:
            json.dump(structure, f, indent=2)
        
        print(f"✅ Performance structure saved successfully!")
    
    def generate_structure_summary(self, structure):
        """Generate summary of the properly structured data"""
        print("📊 PROPER STRUCTURE SUMMARY")
        print("=" * 80)
        
        print(f"📋 STRUCTURE METADATA:")
        print(f"   Created: {structure['metadata']['created_date']}")
        print(f"   Total projects: {structure['metadata']['total_projects']}")
        print(f"   Firms with experience: {structure['metadata']['firms_with_experience']}")
        print(f"   Total prequalifications: {structure['metadata']['total_prequalifications']}")
        print(f"   Total experience points: {structure['metadata']['total_experience_points']:.2f}")
        print()
        
        # Show top prequalifications by firm count
        prequal_firm_counts = []
        for prequal, summary in structure['prequalification_summary'].items():
            prequal_firm_counts.append((prequal, summary['total_firms'], summary['total_experience_points']))
        
        prequal_firm_counts.sort(key=lambda x: x[1], reverse=True)
        
        print(f"🏆 TOP 10 PREQUALIFICATIONS BY FIRM COUNT:")
        for i, (prequal, firm_count, total_points) in enumerate(prequal_firm_counts[:10], 1):
            print(f"   {i:2d}. {prequal}")
            print(f"       Firms with experience: {firm_count}")
            print(f"       Total experience points: {total_points:.2f}")
            print()
        
        # Show sample rankings for a few prequalifications
        print(f"📈 SAMPLE RANKINGS:")
        for prequal in list(structure['prequalification_firm_rankings'].keys())[:3]:
            rankings = structure['prequalification_firm_rankings'][prequal]
            if rankings:
                print(f"   {prequal}:")
                for i, firm in enumerate(rankings[:3], 1):
                    print(f"     {i}. {firm['firm_name']} ({firm['firm_code']}) - {firm['experience_points']:.2f} points")
                print()
    
    def run_complete_build(self):
        """Run complete proper structure build process"""
        print("🚀 BUILDING PROPERLY STRUCTURED PAST PERFORMANCE DATA")
        print("=" * 80)
        
        # Build structure
        structure = self.build_proper_structure()
        
        # Generate summary
        self.generate_structure_summary(structure)
        
        # Save structure
        self.save_structure(structure)
        
        print(f"\n✅ Proper performance structure build complete!")
        print(f"Structure saved to: {self.output_file}")
        
        return structure

def main():
    builder = ProperPerformanceStructureBuilder()
    structure = builder.run_complete_build()

if __name__ == "__main__":
    main()
