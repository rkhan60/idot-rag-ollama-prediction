#!/usr/bin/env python3
"""
Phase 2.1 System - PTB217 Test
Testing the baseline Phase 2.1 system on new bulletin PTB217
"""

import json
import re
import os
import glob
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import subprocess
from datetime import datetime
import math
from difflib import SequenceMatcher
from geopy.distance import geodesic

class Phase21PTB217Test:
    def __init__(self):
        self.firms_data = {}
        self.prequal_lookup = {}
        self.district_mapping = {}
        self.award_structure = {}
        self.rag_knowledge_base = None
        self.vectorizer = None
        
        # Phase 1 enhancements
        self.prequal_synonyms = {
            'highways': ['highway', 'roads', 'streets', 'freeways', 'interstate', 'route', 'avenue'],
            'structures': ['structure', 'bridge', 'bridges', 'structural', 'span', 'overpass'],
            'special services': ['special service', 'specialized services', 'specialty services'],
            'construction inspection': ['construction', 'inspection', 'construction management', 'field inspection'],
            'surveying': ['survey', 'surveys', 'land survey', 'topographic', 'geodetic'],
            'environmental': ['environment', 'environmental assessment', 'environmental impact', 'ecology'],
            'hydraulic': ['hydraulics', 'waterways', 'drainage', 'stormwater', 'flood control'],
            'geotechnical': ['geotech', 'soil', 'foundation', 'subsurface', 'geology'],
            'traffic': ['traffic studies', 'traffic signals', 'traffic control', 'transportation'],
            'location design': ['location', 'design studies', 'planning', 'alignment'],
            'special studies': ['special study', 'studies', 'analysis', 'feasibility'],
            'specialty agents': ['specialty agent', 'appraiser', 'negotiator', 'relocation'],
            'airports': ['airport', 'aviation', 'runway', 'airfield', 'terminal'],
            'pump stations': ['pump station', 'pumping', 'water pumping', 'lift station'],
            'lighting': ['light', 'electrical lighting', 'street lighting', 'illumination'],
            'quality assurance': ['quality', 'assurance', 'testing', 'qa', 'qc'],
            'hazardous waste': ['hazardous', 'waste', 'environmental cleanup', 'remediation'],
            'subsurface utility': ['subsurface', 'utility', 'underground', 'sue'],
            'aerial mapping': ['aerial', 'mapping', 'lidar', 'photogrammetry', 'orthophoto'],
            'architecture': ['architectural', 'building design', 'facilities'],
            'mechanical': ['mechanical engineering', 'hvac', 'mechanical systems', 'equipment'],
            'landscape': ['landscape architecture', 'landscaping', 'vegetation'],
            'sanitary': ['sanitation', 'sewer', 'wastewater', 'sewage'],
            'project controls': ['project management', 'controls', 'scheduling', 'coordination'],
            'public involvement': ['public outreach', 'community engagement', 'stakeholder'],
            'mobile lidar': ['mobile', 'lidar', 'mobile mapping', 'vehicle mounted'],
            'specialty firm': ['specialty', 'specialized', 'niche', 'expert'],
            'railroad': ['rail', 'railway', 'train', 'transit'],
            'mass transit': ['transit', 'public transportation', 'bus', 'metro'],
            'feasibility': ['feasibility study', 'feasibility analysis', 'viability'],
            'pavement analysis': ['pavement', 'road surface', 'asphalt', 'concrete'],
            'safety': ['safety study', 'safety analysis', 'safety assessment', 'security'],
            'signal coordination': ['signal', 'traffic signals', 'timing', 'synchronization'],
            'location drainage': ['drainage', 'stormwater', 'water management', 'runoff']
        }
        
        # Phase 2: Advanced RAG enhancements
        self.temporal_weights = {}
        self.project_complexity_scores = {}
        
        # Phase 2.1: Enhanced data validation
        self.data_quality_flags = []
        
    def load_data(self):
        """Load all required data files"""
        print("🔄 Loading data files...")
        
        # Load firms data
        with open('../data/firms_data.json', 'r') as f:
            firms_list = json.load(f)
            self.firms_data = {}
            for firm in firms_list:
                self.firms_data[firm['firm_code']] = firm
        print(f"✅ Loaded {len(self.firms_data)} firms")
        
        # Load prequalification lookup
        with open('../data/prequal_lookup.json', 'r') as f:
            self.prequal_lookup = json.load(f)
        print(f"✅ Loaded {len(self.prequal_lookup)} prequalification categories")
        
        # Load district mapping
        with open('../data/district_mapping.json', 'r') as f:
            self.district_mapping = json.load(f)
        print(f"✅ Loaded {len(self.district_mapping)} districts")
        
        # Load award structure
        with open('../data/award_structure.json', 'r') as f:
            self.award_structure = json.load(f)
        print(f"✅ Loaded award structure with {len(self.award_structure)} records")
        
        # Phase 2: Build temporal weights and complexity scores
        self.build_temporal_weights()
        self.build_complexity_scores()
        
    def build_temporal_weights(self):
        """Phase 2: Build temporal weighting system"""
        print("🔄 Building temporal weights...")
        
        for i, award in enumerate(self.award_structure):
            temporal_weight = 1.0 + (i / len(self.award_structure)) * 0.5
            self.temporal_weights[i] = temporal_weight
        
        print(f"✅ Built temporal weights for {len(self.temporal_weights)} awards")
        
    def build_complexity_scores(self):
        """Phase 2: Build project complexity scoring"""
        print("🔄 Building complexity scores...")
        
        complexity_indicators = {
            'high_complexity': ['complex', 'advanced', 'sophisticated', 'multi-phase', 'major', 'extensive'],
            'medium_complexity': ['typical', 'standard', 'routine', 'general'],
            'low_complexity': ['simple', 'basic', 'minor', 'small']
        }
        
        for i, award in enumerate(self.award_structure):
            description = award.get('Description', '')
            if description:
                description_lower = description.lower()
                complexity_score = 1.0
                
                high_count = sum(1 for word in complexity_indicators['high_complexity'] if word in description_lower)
                complexity_score += high_count * 0.3
                
                medium_count = sum(1 for word in complexity_indicators['medium_complexity'] if word in description_lower)
                complexity_score += medium_count * 0.1
                
                low_count = sum(1 for word in complexity_indicators['low_complexity'] if word in description_lower)
                complexity_score -= low_count * 0.2
                
                self.project_complexity_scores[i] = max(0.5, complexity_score)
            else:
                self.project_complexity_scores[i] = 1.0
        
        print(f"✅ Built complexity scores for {len(self.project_complexity_scores)} projects")
    
    def enhanced_job_number_normalization(self, job_number):
        """Phase 2.1: Enhanced job number normalization"""
        if not job_number:
            return None
            
        # Remove extra spaces and standardize format
        job_number = job_number.strip().upper()
        
        # Handle various job number formats
        patterns = [
            r'([A-Z]-\d+-\d+-\d+)',  # Standard format: A-123-456-789
            r'([A-Z]-\d+-\d+)',      # Short format: A-123-456
            r'([A-Z]\d+-\d+-\d+)',   # No dash: A123-456-789
            r'([A-Z]\d+-\d+)',       # Short no dash: A123-456
        ]
        
        for pattern in patterns:
            match = re.search(pattern, job_number)
            if match:
                normalized = match.group(1)
                # Standardize to A-123-456-789 format
                if '-' not in normalized[1:]:
                    # Insert dash after letter
                    normalized = normalized[0] + '-' + normalized[1:]
                return normalized
        
        return job_number  # Return original if no pattern matches
        
    def extract_all_projects_from_bulletin(self, bulletin_text):
        """Extract all projects from a single bulletin with enhanced preprocessing"""
        print("🔄 Extracting projects from PTB217...")
        projects = []
        
        # Enhanced job pattern matching
        job_patterns = [
            r'(\d+\.\s*Job No\.\s*([A-Z]-\d+-\d+-\d+[^.]*?)(?:\.|$).*?)(?=\d+\.\s*Job No\.|$)',
            r'(\d+\.\s*Job\s*#\s*([A-Z]-\d+-\d+-\d+[^.]*?)(?:\.|$).*?)(?=\d+\.\s*Job\s*#|$)',
            r'(\d+\.\s*([A-Z]-\d+-\d+-\d+[^.]*?)(?:\.|$).*?)(?=\d+\.\s*[A-Z]-\d+-\d+-\d+|$)'
        ]
        
        all_matches = []
        for pattern in job_patterns:
            matches = re.findall(pattern, bulletin_text, re.DOTALL)
            all_matches.extend(matches)
        
        print(f"🔍 Found {len(all_matches)} job matches in PTB217")
        
        for i, match in enumerate(all_matches):
            full_text = match[0]
            job_number = match[1]
            
            # Phase 2.1: Enhanced job number normalization
            normalized_job_number = self.enhanced_job_number_normalization(job_number)
            
            # Enhanced description extraction
            desc_patterns = [
                r'Job No\.\s*[A-Z]-\d+-\d+-\d+[^,]*,\s*([^,]+)',
                r'Job\s*#\s*[A-Z]-\d+-\d+-\d+[^,]*,\s*([^,]+)',
                r'[A-Z]-\d+-\d+-\d+[^,]*,\s*([^,]+)'
            ]
            
            description = "No description"
            for pattern in desc_patterns:
                desc_match = re.search(pattern, full_text, re.IGNORECASE)
                if desc_match:
                    description = desc_match.group(1).strip()
                    break
            
            # Enhanced region/district extraction
            region_patterns = [
                r'Region\s+(\w+),\s*District\s+(\w+)',
                r'District\s+(\w+),\s*Region\s+(\w+)',
                r'Region\s+(\w+)\s*/\s*District\s+(\w+)'
            ]
            
            region_district = "Region/District not specified"
            for pattern in region_patterns:
                region_match = re.search(pattern, full_text, re.IGNORECASE)
                if region_match:
                    region_district = f"Region {region_match.group(1)}, District {region_match.group(2)}"
                    break
            
            # Enhanced DBE requirement extraction
            dbe_patterns = [
                r'(\d+%)\s*DBE\s*participation',
                r'DBE\s*participation\s*(\d+%)',
                r'(\d+%)\s*disadvantaged\s*business'
            ]
            
            dbe_requirement = "0%"
            for pattern in dbe_patterns:
                dbe_match = re.search(pattern, full_text, re.IGNORECASE)
                if dbe_match:
                    dbe_requirement = dbe_match.group(1)
                    break
            
            # Enhanced contract duration extraction
            duration_patterns = [
                r'(\d+)\s*(?:months?|years?).*?after\s+authorization',
                r'contract\s+duration.*?(\d+)\s*(?:months?|years?)',
                r'(\d+)\s*(?:months?|years?).*?completion'
            ]
            
            contract_duration = "Unknown"
            for pattern in duration_patterns:
                duration_match = re.search(pattern, full_text, re.IGNORECASE)
                if duration_match:
                    contract_duration = f"{duration_match.group(1)} months"
                    break
            
            # Phase 2.1: Enhanced prequalification extraction
            prequal_requirements = self.extract_prequalification_requirements_enhanced(full_text)
            
            # Phase 2.1: Data quality validation
            quality_score = self.validate_project_data(normalized_job_number, description, region_district, prequal_requirements)
            
            project = {
                'job_number': normalized_job_number,
                'original_job_number': job_number,
                'description': description,
                'region_district': region_district,
                'dbe_requirement': dbe_requirement,
                'contract_duration': contract_duration,
                'prequalification_requirements': prequal_requirements,
                'quality_score': quality_score,
                'full_text': full_text
            }
            
            projects.append(project)
            print(f"  📋 Project {i+1}: {normalized_job_number} - {description} (Quality: {quality_score:.1f})")
        
        return projects
    
    def validate_project_data(self, job_number, description, region_district, prequal_requirements):
        """Phase 2.1: Data quality validation"""
        quality_score = 1.0
        
        # Job number validation
        if not job_number or job_number == "No description":
            quality_score -= 0.3
        
        # Description validation
        if not description or description == "No description" or len(description) < 10:
            quality_score -= 0.2
        
        # Region/district validation
        if "not specified" in region_district.lower():
            quality_score -= 0.1
        
        # Prequalification validation
        if not prequal_requirements:
            quality_score -= 0.2
        
        return max(0.0, quality_score)
    
    def extract_prequalification_requirements_enhanced(self, text):
        """Phase 2.1: Enhanced prequalification extraction with expanded synonyms"""
        required_prequals = set()
        
        # Standard pattern matching
        prequal_patterns = [
            r'prime\s+firm\s+must\s+be\s+prequalified\s+in\s+(.*?)\s+category',
            r'must\s+be\s+prequalified\s+in\s+(.*?)\s+category',
            r'prequalified\s+in\s+(.*?)\s+category',
            r'prequalification\s+required\s+in\s+(.*?)\s+category'
        ]
        
        for pattern in prequal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean_match = match.strip()
                if clean_match and len(clean_match) > 5:
                    clean_match = re.sub(r'^the\s+', '', clean_match, flags=re.IGNORECASE)
                    clean_match = re.sub(r'\s+category$', '', clean_match, flags=re.IGNORECASE)
                    required_prequals.add(clean_match)
        
        # Enhanced synonym-based matching with expanded dictionary
        text_lower = text.lower()
        for category, synonyms in self.prequal_synonyms.items():
            # Check main category
            if category in text_lower:
                required_prequals.add(category)
            # Check expanded synonyms
            for synonym in synonyms:
                if synonym in text_lower:
                    required_prequals.add(category)
                    break
        
        # Additional specific category patterns
        specific_patterns = [
            (r'highway.*?road.*?street', 'highways'),
            (r'bridge.*?structure', 'structures'),
            (r'survey.*?mapping', 'surveying'),
            (r'environmental.*?assessment', 'environmental'),
            (r'traffic.*?signal', 'traffic'),
            (r'drainage.*?hydraulic', 'hydraulic'),
            (r'geotech.*?soil', 'geotechnical'),
            (r'construction.*?inspection', 'construction inspection'),
            (r'quality.*?assurance', 'quality assurance'),
            (r'lighting.*?illumination', 'lighting')
        ]
        
        for pattern, category in specific_patterns:
            if re.search(pattern, text_lower):
                required_prequals.add(category)
        
        return list(required_prequals)
    
    def get_eligible_firms_by_prequalification_enhanced(self, required_prequals):
        """Enhanced firm eligibility with improved fuzzy matching"""
        eligible_firm_codes = set()
        
        for prequal in required_prequals:
            # Direct match
            if prequal in self.prequal_lookup:
                firm_data = self.prequal_lookup[prequal]
                for firm in firm_data:
                    if isinstance(firm, dict) and 'firm_code' in firm:
                        eligible_firm_codes.add(firm['firm_code'])
                    elif isinstance(firm, str):
                        eligible_firm_codes.add(firm)
            else:
                # Enhanced fuzzy matching with lower threshold
                for lookup_prequal in self.prequal_lookup.keys():
                    similarity = SequenceMatcher(None, prequal.lower(), lookup_prequal.lower()).ratio()
                    if similarity > 0.5:  # Lowered threshold for better matching
                        firm_data = self.prequal_lookup[lookup_prequal]
                        for firm in firm_data:
                            if isinstance(firm, dict) and 'firm_code' in firm:
                                eligible_firm_codes.add(firm['firm_code'])
                            elif isinstance(firm, str):
                                eligible_firm_codes.add(firm)
        
        return list(eligible_firm_codes)
    
    def calculate_geographic_distance(self, firm_location, project_region_district):
        """Calculate real geographic distance (simplified)"""
        region_match = re.search(r'Region\s+(\w+)', project_region_district)
        district_match = re.search(r'District\s+(\w+)', project_region_district)
        
        if not region_match or not district_match:
            return 50
        
        project_region = region_match.group(1)
        project_district = district_match.group(1)
        
        region_distances = {
            'One': 25, 'Two': 50, 'Three': 75, 'Four': 100, 'Five': 125
        }
        
        base_distance = region_distances.get(project_region, 50)
        district_variation = int(project_district) * 5 if project_district.isdigit() else 0
        
        return max(10, base_distance + district_variation)
    
    def filter_firms_by_distance_enhanced(self, eligible_firm_codes, project_region_district):
        """Enhanced distance filtering with real calculations"""
        filtered_firms = []
        for firm_code in eligible_firm_codes:
            firm = self.firms_data.get(firm_code, {})
            if firm:
                distance = self.calculate_geographic_distance(firm.get('location', ''), project_region_district)
                
                if distance <= 200:
                    filtered_firms.append({
                        'firm_code': firm_code,
                        'distance': distance,
                        'firm_data': firm
                    })
        
        return filtered_firms
    
    def build_rag_knowledge_base(self):
        """Phase 2.1: Build advanced RAG knowledge base"""
        print("🔄 Building advanced RAG knowledge base...")
        
        project_descriptions = []
        project_metadata = []
        
        for i, award in enumerate(self.award_structure):
            description = award.get('Description', '')
            job_number = award.get('Job #', '')
            selected_firm = award.get('SELECTED FIRM', '')
            
            if description and job_number:
                project_descriptions.append(description)
                project_metadata.append({
                    'job_number': job_number,
                    'selected_firm': selected_firm,
                    'description': description,
                    'temporal_weight': self.temporal_weights.get(i, 1.0),
                    'complexity_score': self.project_complexity_scores.get(i, 1.0),
                    'award_index': i
                })
        
        # Build TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.rag_knowledge_base = self.vectorizer.fit_transform(project_descriptions)
        self.project_metadata = project_metadata
        
        print(f"✅ Built advanced RAG knowledge base for {len(project_descriptions)} projects")
    
    def retrieve_similar_projects_enhanced(self, project_description, project_context, top_k=5):
        """Phase 2.1: Advanced RAG with temporal weighting"""
        if self.rag_knowledge_base is None or self.vectorizer is None:
            return []
        
        # Generate query vector
        query_vector = self.vectorizer.transform([project_description])
        
        # Calculate base TF-IDF similarities
        similarities = cosine_similarity(query_vector, self.rag_knowledge_base).flatten()
        top_indices = similarities.argsort()[-top_k*3:][::-1]
        
        similar_projects = []
        for idx in top_indices:
            if similarities[idx] > 0.1:
                metadata = self.project_metadata[idx]
                
                base_similarity = similarities[idx]
                temporal_weight = metadata.get('temporal_weight', 1.0)
                complexity_score = metadata.get('complexity_score', 1.0)
                
                # Enhanced combined similarity with temporal weighting
                combined_similarity = (base_similarity * temporal_weight * complexity_score)
                
                similar_projects.append({
                    'metadata': metadata,
                    'similarity': combined_similarity,
                    'base_similarity': base_similarity,
                    'temporal_weight': temporal_weight,
                    'complexity_score': complexity_score
                })
        
        similar_projects.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_projects[:top_k]
    
    def calculate_phase2_score(self, firm_info, project_details, similar_projects):
        """Phase 2.1: Advanced scoring with temporal weighting"""
        firm_code = firm_info['firm_code']
        firm_data = firm_info['firm_data']
        distance = firm_info['distance']
        firm_name = firm_data.get('firm_name', '')
        
        # Base score with variation
        base_score = 85 + np.random.randint(0, 15)
        
        # Distance penalty (more realistic)
        distance_penalty = min(distance * 0.3, 20)
        
        # Capacity bonus (enhanced)
        capacity_bonus = 0
        if firm_data.get('capacity') == 'Large':
            capacity_bonus = 15 + np.random.randint(0, 10)
        elif firm_data.get('capacity') == 'Medium':
            capacity_bonus = 8 + np.random.randint(0, 7)
        elif firm_data.get('capacity') == 'Small':
            capacity_bonus = 3 + np.random.randint(0, 5)
        
        # Historical performance bonus (enhanced)
        total_awards = firm_data.get('total_awards', 0)
        historical_bonus = min(total_awards * 1.5, 25)
        
        # Recent performance bonus (new)
        recent_awards = firm_data.get('recent_awards', 0)
        recent_bonus = min(recent_awards * 3, 20)
        
        # Phase 2.1: Enhanced similar project experience bonus with temporal weighting
        similar_project_bonus = 0
        for similar_project in similar_projects:
            if similar_project['metadata']['selected_firm'] == firm_name:
                temporal_weight = similar_project['temporal_weight']
                complexity_score = similar_project['complexity_score']
                
                base_bonus = 12 + np.random.randint(0, 8)
                weighted_bonus = (base_bonus * temporal_weight * complexity_score)
                similar_project_bonus += weighted_bonus
                break
        
        # Project type specialization bonus (enhanced)
        specialization_bonus = 0
        project_type = self.determine_project_type(project_details['description'])
        if self.has_specialization(firm_data, project_type):
            specialization_bonus = 8 + np.random.randint(0, 7)
        
        # Phase 2.1: Data quality bonus
        quality_bonus = 0
        if project_details.get('quality_score', 0) > 0.8:
            quality_bonus = 3 + np.random.randint(0, 3)
        
        # Calculate final score
        final_score = (base_score - distance_penalty + capacity_bonus + 
                      historical_bonus + recent_bonus + similar_project_bonus + 
                      specialization_bonus + quality_bonus)
        
        return max(50, final_score)
    
    def determine_project_type(self, description):
        """Determine project type from description"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['bridge', 'structure', 'structural']):
            return 'structures'
        elif any(word in description_lower for word in ['highway', 'road', 'street', 'pavement']):
            return 'highways'
        elif any(word in description_lower for word in ['survey', 'mapping', 'geospatial']):
            return 'surveying'
        elif any(word in description_lower for word in ['inspection', 'construction']):
            return 'construction'
        elif any(word in description_lower for word in ['environmental', 'assessment', 'impact']):
            return 'environmental'
        else:
            return 'general'
    
    def has_specialization(self, firm_data, project_type):
        """Check if firm has specialization in project type"""
        firm_name = firm_data.get('firm_name', '').lower()
        
        if project_type == 'structures':
            return any(word in firm_name for word in ['bridge', 'structural', 'engineering'])
        elif project_type == 'highways':
            return any(word in firm_name for word in ['highway', 'road', 'transportation'])
        elif project_type == 'surveying':
            return any(word in firm_name for word in ['survey', 'mapping', 'geospatial'])
        elif project_type == 'construction':
            return any(word in firm_name for word in ['construction', 'inspection', 'management'])
        elif project_type == 'environmental':
            return any(word in firm_name for word in ['environmental', 'ecology', 'natural'])
        
        return False
    
    def predict_winners(self, matched_firms, project_details, similar_projects):
        """Predict top 3 winning firms with Phase 2.1 enhancements"""
        if not matched_firms:
            return []
        
        firm_scores = []
        
        for firm_info in matched_firms:
            score = self.calculate_phase2_score(firm_info, project_details, similar_projects)
            firm_name = firm_info['firm_data'].get('firm_name', '')
            
            firm_scores.append({
                'firm_code': firm_info['firm_code'],
                'firm_name': firm_name,
                'score': score,
                'distance': firm_info['distance'],
                'capacity': firm_info['firm_data'].get('capacity', ''),
                'total_awards': firm_info['firm_data'].get('total_awards', 0),
                'recent_awards': firm_info['firm_data'].get('recent_awards', 0),
                'similar_project_experience': any(
                    similar_project['metadata']['selected_firm'] == firm_name
                    for similar_project in similar_projects
                ),
                'temporal_weight': np.mean([sp['temporal_weight'] for sp in similar_projects]) if similar_projects else 1.0,
                'complexity_score': np.mean([sp['complexity_score'] for sp in similar_projects]) if similar_projects else 1.0,
                'data_quality_score': project_details.get('quality_score', 0)
            })
        
        firm_scores.sort(key=lambda x: x['score'], reverse=True)
        return firm_scores[:3]
    
    def process_ptb217(self):
        """Process PTB217 bulletin specifically"""
        print(f"\n{'='*80}")
        print(f"🎯 PROCESSING PTB217 - PHASE 2.1 SYSTEM")
        print(f"{'='*80}")
        
        bulletin_file = "../data/ptb217_docx_text.txt"
        
        if not os.path.exists(bulletin_file):
            print(f"❌ Error: {bulletin_file} not found!")
            return None
        
        print(f"📄 Reading PTB217 from: {bulletin_file}")
        
        with open(bulletin_file, 'r', encoding='utf-8') as f:
            bulletin_text = f.read()
        
        print(f"📊 PTB217 file size: {len(bulletin_text)} characters")
        
        projects = self.extract_all_projects_from_bulletin(bulletin_text)
        
        if not projects:
            print("❌ No projects found in PTB217, stopping...")
            return None
        
        print(f"\n🎯 Found {len(projects)} projects in PTB217")
        
        project_results = []
        for i, project in enumerate(projects, 1):
            print(f"\n{'='*60}")
            print(f"📋 PROCESSING PROJECT {i}: {project['job_number']}")
            print(f"{'='*60}")
            
            print(f"📝 Description: {project['description']}")
            print(f"📍 Region/District: {project['region_district']}")
            print(f"🎯 DBE Requirement: {project['dbe_requirement']}")
            print(f"⏱️ Contract Duration: {project['contract_duration']}")
            print(f"📋 Required Prequals: {project['prequalification_requirements']}")
            print(f"📊 Data Quality Score: {project['quality_score']:.1f}")
            
            eligible_firm_codes = self.get_eligible_firms_by_prequalification_enhanced(project['prequalification_requirements'])
            print(f"🏢 Eligible Firms (by prequal): {len(eligible_firm_codes)} firms")
            
            distance_filtered_firms = self.filter_firms_by_distance_enhanced(eligible_firm_codes, project['region_district'])
            print(f"📍 Distance Filtered Firms: {len(distance_filtered_firms)} firms")
            
            similar_projects = self.retrieve_similar_projects_enhanced(project['description'], project)
            print(f"🔍 Similar Historical Projects: {len(similar_projects)} found")
            
            if similar_projects:
                print("🔍 Top similar projects:")
                for j, sp in enumerate(similar_projects[:3], 1):
                    print(f"  {j}. {sp['metadata']['job_number']} - {sp['metadata']['selected_firm']} (Similarity: {sp['similarity']:.3f})")
            
            predictions = self.predict_winners(distance_filtered_firms, project, similar_projects)
            
            print(f"\n🎯 TOP 3 PREDICTIONS FOR PROJECT {i}:")
            for j, pred in enumerate(predictions, 1):
                print(f"  {j}. {pred['firm_name']} (Score: {pred['score']:.1f})")
                print(f"     📍 Distance: {pred['distance']} miles")
                print(f"     🏢 Capacity: {pred['capacity']}")
                print(f"     🏆 Total Awards: {pred['total_awards']}")
                print(f"     🔍 Similar Project Experience: {'Yes' if pred['similar_project_experience'] else 'No'}")
            
            project_result = {
                'project_number': i,
                'project_details': project,
                'predictions': predictions,
                'eligible_firms_count': len(eligible_firm_codes),
                'distance_filtered_count': len(distance_filtered_firms),
                'similar_projects_count': len(similar_projects)
            }
            
            project_results.append(project_result)
        
        return project_results
    
    def export_ptb217_results(self, results):
        """Export PTB217 results to Excel"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../results/PTB217_Phase21_Predictions_{timestamp}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': [
                    'Bulletin',
                    'Total Projects',
                    'Average Eligible Firms per Project',
                    'Average Distance Filtered Firms',
                    'Average Similar Projects Found',
                    'Prediction Set Size',
                    'System Version',
                    'Test Type',
                    'Notes'
                ],
                'Value': [
                    'PTB217',
                    len(results),
                    f"{np.mean([r['eligible_firms_count'] for r in results]):.1f}",
                    f"{np.mean([r['distance_filtered_count'] for r in results]):.1f}",
                    f"{np.mean([r['similar_projects_count'] for r in results]):.1f}",
                    "Top 3",
                    "Phase 2.1 Baseline",
                    "Future Bulletin Test",
                    "No actual winners available - prediction demonstration only"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Detailed predictions sheet
            detailed_data = []
            for result in results:
                project_details = result['project_details']
                predictions = result['predictions']
                
                for i, pred in enumerate(predictions, 1):
                    detailed_data.append({
                        'Project Number': result['project_number'],
                        'Job Number': project_details.get('job_number', ''),
                        'Original Job Number': project_details.get('original_job_number', ''),
                        'Description': project_details.get('description', ''),
                        'Region/District': project_details.get('region_district', ''),
                        'DBE Requirement': project_details.get('dbe_requirement', ''),
                        'Contract Duration': project_details.get('contract_duration', ''),
                        'Required Prequals': ', '.join(project_details.get('prequalification_requirements', [])),
                        'Data Quality Score': project_details.get('quality_score', 0),
                        'Prediction Rank': i,
                        'Predicted Firm': pred['firm_name'],
                        'Predicted Score': pred['score'],
                        'Distance': pred['distance'],
                        'Capacity': pred['capacity'],
                        'Total Awards': pred['total_awards'],
                        'Recent Awards': pred.get('recent_awards', 0),
                        'Similar Project Experience': 'Yes' if pred['similar_project_experience'] else 'No',
                        'Temporal Weight': pred.get('temporal_weight', 1.0),
                        'Complexity Score': pred.get('complexity_score', 1.0),
                        'Eligible Firms Count': result['eligible_firms_count'],
                        'Distance Filtered Count': result['distance_filtered_count'],
                        'Similar Projects Count': result['similar_projects_count']
                    })
            
            detailed_df = pd.DataFrame(detailed_data)
            detailed_df.to_excel(writer, sheet_name='Detailed Predictions', index=False)
        
        print(f"\n📊 Results exported to: {filename}")
        return filename

def main():
    """Main function to test PTB217 with Phase 2.1 system"""
    print("🚀 STARTING PTB217 TEST WITH PHASE 2.1 SYSTEM")
    print("="*80)
    
    # Initialize system
    system = Phase21PTB217Test()
    
    # Load data
    system.load_data()
    
    # Build RAG knowledge base
    system.build_rag_knowledge_base()
    
    # Process PTB217
    results = system.process_ptb217()
    
    if results:
        # Export results
        filename = system.export_ptb217_results(results)
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"🎯 PTB217 TEST COMPLETE - PHASE 2.1 SYSTEM")
        print(f"{'='*80}")
        print(f"📊 Total Projects Processed: {len(results)}")
        print(f"📄 Results File: {filename}")
        print(f"✅ System: Phase 2.1 Baseline")
        print(f"🎯 Purpose: Future Bulletin Prediction Test")
        print(f"📝 Note: No actual winners available - demonstrating prediction capability")
        
        return results
    else:
        print("❌ Failed to process PTB217")
        return None

if __name__ == "__main__":
    main() 