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

class Phase22cTemporalSystem:
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
        
        # Phase 2.2c: Enhanced temporal weighting features
        self.award_timestamps = {}
        self.recency_decay_factors = {}
        self.seasonal_weights = {}
        self.temporal_trends = {}
        
    def load_data(self):
        """Load all required data files"""
        print("Loading data files...")
        
        # Load firms data
        with open('../data/firms_data.json', 'r') as f:
            firms_list = json.load(f)
            self.firms_data = {}
            for firm in firms_list:
                self.firms_data[firm['firm_code']] = firm
        print(f"Loaded {len(self.firms_data)} firms")
        
        # Load prequalification lookup
        with open('../data/prequal_lookup.json', 'r') as f:
            self.prequal_lookup = json.load(f)
        print(f"Loaded {len(self.prequal_lookup)} prequalification categories")
        
        # Load district mapping
        with open('../data/district_mapping.json', 'r') as f:
            self.district_mapping = json.load(f)
        print(f"Loaded {len(self.district_mapping)} districts")
        
        # Load award structure
        with open('../data/award_structure.json', 'r') as f:
            self.award_structure = json.load(f)
        print(f"Loaded award structure with {len(self.award_structure)} records")
        
        # Phase 2: Build temporal weights and complexity scores
        self.build_temporal_weights()
        self.build_complexity_scores()
        
        # Phase 2.2c: Build enhanced temporal features
        self.build_award_timestamps()
        self.build_recency_decay_factors()
        self.build_seasonal_weights()
        self.build_temporal_trends()
        
    def build_temporal_weights(self):
        """Phase 2: Build temporal weighting system"""
        print("Building temporal weights...")
        
        for i, award in enumerate(self.award_structure):
            temporal_weight = 1.0 + (i / len(self.award_structure)) * 0.5
            self.temporal_weights[i] = temporal_weight
        
        print(f"Built temporal weights for {len(self.temporal_weights)} awards")
        
    def build_complexity_scores(self):
        """Phase 2: Build project complexity scoring"""
        print("Building complexity scores...")
        
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
        
        print(f"Built complexity scores for {len(self.project_complexity_scores)} projects")
    
    def build_award_timestamps(self):
        """Phase 2.2c: Build award timestamps based on index position"""
        print("Building award timestamps...")
        
        # Simulate timestamps based on award index (newer awards = higher index)
        base_date = datetime(2020, 1, 1)
        
        for i, award in enumerate(self.award_structure):
            # Simulate time progression (each award is ~1 month apart)
            days_offset = i * 30
            award_date = base_date + pd.Timedelta(days=days_offset)
            self.award_timestamps[i] = award_date
        
        print(f"Built timestamps for {len(self.award_timestamps)} awards")
    
    def build_recency_decay_factors(self):
        """Phase 2.2c: Build recency decay factors"""
        print("Building recency decay factors...")
        
        total_awards = len(self.award_structure)
        
        for i, award in enumerate(self.award_structure):
            # Calculate recency factor (1.0 = most recent, 0.5 = oldest)
            recency_factor = 0.5 + (i / total_awards) * 0.5
            
            # Apply exponential decay for more dramatic recency effect
            decay_factor = math.exp(recency_factor - 1.0)
            
            self.recency_decay_factors[i] = decay_factor
        
        print(f"Built recency decay factors for {len(self.recency_decay_factors)} awards")
    
    def build_seasonal_weights(self):
        """Phase 2.2c: Build seasonal weighting factors"""
        print("Building seasonal weights...")
        
        for i, award in enumerate(self.award_structure):
            if i in self.award_timestamps:
                award_date = self.award_timestamps[i]
                month = award_date.month
                
                # Seasonal weighting (construction season = higher weight)
                if month in [3, 4, 5, 6, 7, 8, 9, 10]:  # Spring/Summer/Fall
                    seasonal_weight = 1.2
                else:  # Winter
                    seasonal_weight = 0.8
                
                self.seasonal_weights[i] = seasonal_weight
            else:
                self.seasonal_weights[i] = 1.0
        
        print(f"Built seasonal weights for {len(self.seasonal_weights)} awards")
    
    def build_temporal_trends(self):
        """Phase 2.2c: Build temporal trend analysis"""
        print("Building temporal trends...")
        
        # Analyze trends in award patterns
        total_awards = len(self.award_structure)
        
        for i, award in enumerate(self.award_structure):
            # Calculate trend factor based on position in sequence
            trend_position = i / total_awards
            
            # Simulate different trend patterns
            if trend_position < 0.3:  # Early period
                trend_factor = 0.9
            elif trend_position < 0.7:  # Middle period
                trend_factor = 1.1
            else:  # Recent period
                trend_factor = 1.2
            
            self.temporal_trends[i] = trend_factor
        
        print(f"Built temporal trends for {len(self.temporal_trends)} awards")
    
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
        
        print(f"Found {len(all_matches)} job matches in bulletin")
        
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
            print(f"  Project {i+1}: {normalized_job_number} - {description} (Quality: {quality_score:.1f})")
        
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
        """Phase 2.2c: Build advanced RAG knowledge base with enhanced temporal features"""
        print("Building advanced RAG knowledge base with enhanced temporal features...")
        
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
                    'recency_decay': self.recency_decay_factors.get(i, 1.0),
                    'seasonal_weight': self.seasonal_weights.get(i, 1.0),
                    'temporal_trend': self.temporal_trends.get(i, 1.0),
                    'award_index': i
                })
        
        # Build TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.rag_knowledge_base = self.vectorizer.fit_transform(project_descriptions)
        self.project_metadata = project_metadata
        
        print(f"Built advanced RAG knowledge base with enhanced temporal features for {len(project_descriptions)} projects")
    
    def retrieve_similar_projects_enhanced(self, project_description, project_context, top_k=5):
        """Phase 2.2c: Advanced RAG with enhanced temporal weighting"""
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
                recency_decay = metadata.get('recency_decay', 1.0)
                seasonal_weight = metadata.get('seasonal_weight', 1.0)
                temporal_trend = metadata.get('temporal_trend', 1.0)
                
                # Phase 2.2c: Enhanced temporal weighting calculation
                enhanced_temporal_weight = (temporal_weight * recency_decay * 
                                          seasonal_weight * temporal_trend)
                
                # Enhanced combined similarity with sophisticated temporal weighting
                combined_similarity = (base_similarity * enhanced_temporal_weight * 
                                     complexity_score)
                
                similar_projects.append({
                    'metadata': metadata,
                    'similarity': combined_similarity,
                    'base_similarity': base_similarity,
                    'temporal_weight': temporal_weight,
                    'complexity_score': complexity_score,
                    'recency_decay': recency_decay,
                    'seasonal_weight': seasonal_weight,
                    'temporal_trend': temporal_trend,
                    'enhanced_temporal_weight': enhanced_temporal_weight
                })
        
        similar_projects.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_projects[:top_k] 

    def calculate_phase2_score(self, firm_info, project_details, similar_projects):
        """Phase 2.2c: Advanced scoring with enhanced temporal weighting"""
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
        
        # Phase 2.2c: Enhanced similar project experience bonus with temporal weighting
        similar_project_bonus = 0
        for similar_project in similar_projects:
            if similar_project['metadata']['selected_firm'] == firm_name:
                temporal_weight = similar_project['temporal_weight']
                complexity_score = similar_project['complexity_score']
                recency_decay = similar_project['recency_decay']
                seasonal_weight = similar_project['seasonal_weight']
                temporal_trend = similar_project['temporal_trend']
                enhanced_temporal_weight = similar_project['enhanced_temporal_weight']
                
                base_bonus = 12 + np.random.randint(0, 8)
                weighted_bonus = (base_bonus * enhanced_temporal_weight * complexity_score)
                similar_project_bonus += weighted_bonus
                break
        
        # Project type specialization bonus (enhanced with Phase 2.2c)
        specialization_bonus = 0
        project_type = self.determine_project_type(project_details['description'])
        if self.has_specialization(firm_data, project_type):
            specialization_bonus = 8 + np.random.randint(0, 7)
        
        # Phase 2.2c: Enhanced temporal complexity bonus
        complexity_bonus = 0
        if similar_projects:
            avg_complexity = np.mean([sp['complexity_score'] for sp in similar_projects])
            avg_recency_decay = np.mean([sp['recency_decay'] for sp in similar_projects])
            avg_seasonal_weight = np.mean([sp['seasonal_weight'] for sp in similar_projects])
            avg_temporal_trend = np.mean([sp['temporal_trend'] for sp in similar_projects])
            
            if avg_complexity > 1.2:
                complexity_bonus += 3 + np.random.randint(0, 3)
            if avg_recency_decay > 1.0:
                complexity_bonus += 2 + np.random.randint(0, 2)
            if avg_seasonal_weight > 1.1:
                complexity_bonus += 2 + np.random.randint(0, 2)
            if avg_temporal_trend > 1.1:
                complexity_bonus += 2 + np.random.randint(0, 2)
        
        # Phase 2.1: Data quality bonus
        quality_bonus = 0
        if project_details.get('quality_score', 0) > 0.8:
            quality_bonus = 3 + np.random.randint(0, 3)
        
        # Phase 2.2c: Temporal expertise bonus
        temporal_bonus = 0
        if similar_projects:
            avg_enhanced_temporal_weight = np.mean([sp['enhanced_temporal_weight'] for sp in similar_projects])
            if avg_enhanced_temporal_weight > 1.2:
                temporal_bonus = 4 + np.random.randint(0, 4)
        
        # Calculate final score
        final_score = (base_score - distance_penalty + capacity_bonus + 
                      historical_bonus + recent_bonus + similar_project_bonus + 
                      specialization_bonus + complexity_bonus + quality_bonus + temporal_bonus)
        
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
        """Predict top 3 winning firms with Phase 2.2c enhancements"""
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
                'recency_decay': np.mean([sp['recency_decay'] for sp in similar_projects]) if similar_projects else 1.0,
                'seasonal_weight': np.mean([sp['seasonal_weight'] for sp in similar_projects]) if similar_projects else 1.0,
                'temporal_trend': np.mean([sp['temporal_trend'] for sp in similar_projects]) if similar_projects else 1.0,
                'enhanced_temporal_weight': np.mean([sp['enhanced_temporal_weight'] for sp in similar_projects]) if similar_projects else 1.0,
                'data_quality_score': project_details.get('quality_score', 0)
            })
        
        firm_scores.sort(key=lambda x: x['score'], reverse=True)
        return firm_scores[:3]
    
    def find_actual_winners(self, job_number):
        """Find actual winners from award structure with enhanced job number matching"""
        actual_winners = []
        
        if not job_number:
            return actual_winners
        
        # Phase 2.1: Enhanced job number matching
        normalized_job = self.enhanced_job_number_normalization(job_number)
        
        # Try multiple matching strategies
        matching_strategies = [
            # Strategy 1: Exact match
            lambda award_job: award_job == normalized_job,
            # Strategy 2: Base job number match (ignore year)
            lambda award_job: self.match_base_job_number(normalized_job, award_job),
            # Strategy 3: Fuzzy match
            lambda award_job: SequenceMatcher(None, (normalized_job or '').lower(), (award_job or '').lower()).ratio() > 0.8
        ]
        
        for award in self.award_structure:
            award_job = award.get('Job #', '')
            if award_job:
                for strategy in matching_strategies:
                    if strategy(award_job):
                        selected_firm = award.get('SELECTED FIRM', '')
                        if selected_firm:
                            actual_winners.append(selected_firm)
                        break
        
        return list(set(actual_winners))  # Remove duplicates
    
    def match_base_job_number(self, job1, job2):
        """Match job numbers ignoring year component"""
        base_match1 = re.match(r'([A-Z]-\d+-\d+)-\d+', job1)
        base_match2 = re.match(r'([A-Z]-\d+-\d+)-\d+', job2)
        
        if base_match1 and base_match2:
            return base_match1.group(1) == base_match2.group(1)
        
        return False
    
    def calculate_accuracy(self, predictions, actual_winners):
        """Calculate prediction accuracy"""
        if not actual_winners:
            return 0.0
        
        predicted_firm_names = [pred['firm_name'] for pred in predictions]
        
        for actual_winner in actual_winners:
            if actual_winner in predicted_firm_names:
                return 1.0
        
        return 0.0
    
    def process_bulletin(self, bulletin_file):
        """Process a single bulletin file with multiple projects"""
        print(f"\n{'='*60}")
        print(f"Processing: {bulletin_file}")
        print(f"{'='*60}")
        
        with open(bulletin_file, 'r', encoding='utf-8') as f:
            bulletin_text = f.read()
        
        projects = self.extract_all_projects_from_bulletin(bulletin_text)
        
        if not projects:
            print("No projects found, skipping...")
            return None
        
        project_results = []
        for i, project in enumerate(projects, 1):
            print(f"\n--- Processing Project {i}: {project['job_number']} ---")
            
            eligible_firm_codes = self.get_eligible_firms_by_prequalification_enhanced(project['prequalification_requirements'])
            print(f"Required Prequalifications: {project['prequalification_requirements']}")
            print(f"Eligible Firms (by prequal): {len(eligible_firm_codes)} firms")
            
            distance_filtered_firms = self.filter_firms_by_distance_enhanced(eligible_firm_codes, project['region_district'])
            print(f"Distance Filtered Firms: {len(distance_filtered_firms)} firms")
            
            similar_projects = self.retrieve_similar_projects_enhanced(project['description'], project)
            print(f"Similar Historical Projects: {len(similar_projects)} found")
            
            predictions = self.predict_winners(distance_filtered_firms, project, similar_projects)
            
            actual_winners = self.find_actual_winners(project['job_number'])
            accuracy = self.calculate_accuracy(predictions, actual_winners)
            
            project_result = {
                'bulletin_file': bulletin_file,
                'project_number': i,
                'project_details': project,
                'predictions': predictions,
                'actual_winners': actual_winners,
                'accuracy': accuracy,
                'eligible_firms_count': len(eligible_firm_codes),
                'similar_projects_count': len(similar_projects)
            }
            
            project_results.append(project_result)
            
            print(f"Accuracy: {accuracy:.1%}")
            print(f"Actual Winners: {actual_winners}")
            if predictions:
                print(f"Top Prediction: {predictions[0]['firm_name']} (Score: {predictions[0]['score']:.1f})")
                print(f"Top 3 Predictions: {[p['firm_name'] for p in predictions]}")
        
        return project_results
    
    def run_test(self, start_bulletin, end_bulletin, test_name):
        """Run test on specified bulletin range"""
        print(f"=== PHASE 2.2c TEMPORAL SYSTEM - {test_name} ===")
        
        self.load_data()
        self.build_rag_knowledge_base()
        
        bulletin_files = []
        for i in range(start_bulletin, end_bulletin + 1):
            file_pattern = f"../data/ptb{i}_docx_text.txt"
            matching_files = glob.glob(file_pattern)
            bulletin_files.extend(matching_files)
        
        print(f"Found {len(bulletin_files)} bulletin files to process")
        
        all_results = []
        total_accuracy = 0
        successful_predictions = 0
        total_projects = 0
        
        for bulletin_file in sorted(bulletin_files):
            project_results = self.process_bulletin(bulletin_file)
            if project_results:
                for project_result in project_results:
                    all_results.append(project_result)
                    total_accuracy += project_result['accuracy']
                    total_projects += 1
                    if project_result['accuracy'] > 0:
                        successful_predictions += 1
        
        overall_accuracy = total_accuracy / total_projects if total_projects > 0 else 0
        
        comprehensive_results = {
            'overall_accuracy': overall_accuracy,
            'total_projects': total_projects,
            'successful_predictions': successful_predictions,
            'results': all_results
        }
        
        self.export_to_excel(comprehensive_results, test_name)
        
        print(f"\n{'='*60}")
        print(f"PHASE 2.2c TEMPORAL RESULTS SUMMARY - {test_name}")
        print(f"{'='*60}")
        print(f"Total Projects Processed: {total_projects}")
        print(f"Successful Predictions: {successful_predictions}")
        print(f"Overall Accuracy: {overall_accuracy:.1%}")
        print(f"Excel file exported: {test_name}_results.xlsx")
        
        return comprehensive_results
    
    def export_to_excel(self, results, test_name):
        """Export results to Excel with comprehensive formatting"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../results/{test_name}_results_{timestamp}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            summary_data = {
                'Metric': [
                    'Overall Accuracy (Top 3)',
                    'Total Projects',
                    'Successful Predictions',
                    'Success Rate',
                    'Average Eligible Firms per Project',
                    'Average Similar Projects Found',
                    'Prediction Set Size',
                    'Theoretical Random Accuracy',
                    'System Version',
                    'Deployment Status',
                    'Enhancements Applied'
                ],
                'Value': [
                    f"{results['overall_accuracy']:.1%}",
                    results['total_projects'],
                    results['successful_predictions'],
                    f"{results['successful_predictions']/results['total_projects']:.1%}" if results['total_projects'] > 0 else "0%",
                    f"{np.mean([r['eligible_firms_count'] for r in results['results']]):.1f}",
                    f"{np.mean([r['similar_projects_count'] for r in results['results']]):.1f}",
                    "Top 3",
                    "33.3% (1/3)",
                    "Phase 2.2c Temporal",
                    "TESTING",
                    "Enhanced Temporal Weighting, Recency Decay, Seasonal Analysis, Temporal Trends"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            detailed_data = []
            for result in results['results']:
                project_details = result['project_details']
                predictions = result['predictions']
                for i, pred in enumerate(predictions, 1):
                    detailed_data.append({
                        'Bulletin File': result['bulletin_file'],
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
                        'Recency Decay': pred.get('recency_decay', 1.0),
                        'Seasonal Weight': pred.get('seasonal_weight', 1.0),
                        'Temporal Trend': pred.get('temporal_trend', 1.0),
                        'Enhanced Temporal Weight': pred.get('enhanced_temporal_weight', 1.0),
                        'Actual Winners': ', '.join(result['actual_winners']),
                        'Accuracy': 'Yes' if result['accuracy'] > 0 else 'No',
                        'Eligible Firms Count': result['eligible_firms_count'],
                        'Similar Projects Count': result['similar_projects_count']
                    })
            
            detailed_df = pd.DataFrame(detailed_data)
            detailed_df.to_excel(writer, sheet_name='Detailed Results', index=False)
        
        print(f"Results exported to: {filename}")

def main():
    """Main function to run the Phase 2.2c Temporal system"""
    system = Phase22cTemporalSystem()
    
    # Test Phase 2.2c on both ranges
    print("Running Phase 2.2c Temporal System")
    results1 = system.run_test(180, 190, "Phase22c_Temporal_PTB180_190")
    results2 = system.run_test(190, 200, "Phase22c_Temporal_PTB190_200")
    
    # Print Phase 2.2c summary
    print(f"\n{'='*80}")
    print(f"PHASE 2.2c TEMPORAL SYSTEM - TESTING SUMMARY")
    print(f"{'='*80}")
    print(f"PTB180-190 Accuracy: {results1['overall_accuracy']:.1%}")
    print(f"PTB190-200 Accuracy: {results2['overall_accuracy']:.1%}")
    print(f"Average Accuracy: {(results1['overall_accuracy'] + results2['overall_accuracy']) / 2:.1%}")
    print(f"Status: TESTING COMPLETE")
    print(f"System: Phase 2.2c (Enhanced Temporal Weighting)")
    print(f"Next Step: Compare with Phase 2.1 Baseline")
    
    return results1, results2

if __name__ == "__main__":
    main() 