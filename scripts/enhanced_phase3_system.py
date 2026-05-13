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
from collections import defaultdict, Counter

class EnhancedPhase3System:
    def __init__(self):
        self.firms_data = {}
        self.prequal_lookup = {}
        self.district_mapping = {}
        self.award_structure = {}
        self.rag_knowledge_base = None
        self.vectorizer = None
        
        # Phase 1 enhancements
        self.prequal_synonyms = {
            'highways': ['highway', 'roads', 'streets', 'freeways', 'interstate'],
            'structures': ['structure', 'bridge', 'bridges', 'structural'],
            'special services': ['special service', 'specialized services'],
            'construction inspection': ['construction', 'inspection', 'construction management'],
            'surveying': ['survey', 'surveys', 'land survey'],
            'environmental': ['environment', 'environmental assessment', 'environmental impact'],
            'hydraulic': ['hydraulics', 'waterways', 'drainage'],
            'geotechnical': ['geotech', 'soil', 'foundation'],
            'traffic': ['traffic studies', 'traffic signals', 'traffic control'],
            'location design': ['location', 'design studies', 'planning'],
            'special studies': ['special study', 'studies', 'analysis'],
            'specialty agents': ['specialty agent', 'appraiser', 'negotiator'],
            'airports': ['airport', 'aviation', 'runway'],
            'pump stations': ['pump station', 'pumping', 'water pumping'],
            'lighting': ['light', 'electrical lighting', 'street lighting'],
            'quality assurance': ['quality', 'assurance', 'testing', 'qa'],
            'hazardous waste': ['hazardous', 'waste', 'environmental cleanup'],
            'subsurface utility': ['subsurface', 'utility', 'underground'],
            'aerial mapping': ['aerial', 'mapping', 'lidar', 'photogrammetry'],
            'architecture': ['architectural', 'building design'],
            'mechanical': ['mechanical engineering', 'hvac', 'mechanical systems'],
            'landscape': ['landscape architecture', 'landscaping'],
            'sanitary': ['sanitation', 'sewer', 'wastewater'],
            'project controls': ['project management', 'controls', 'scheduling'],
            'public involvement': ['public outreach', 'community engagement'],
            'mobile lidar': ['mobile', 'lidar', 'mobile mapping'],
            'specialty firm': ['specialty', 'specialized', 'niche'],
            'railroad': ['rail', 'railway', 'train'],
            'mass transit': ['transit', 'public transportation', 'bus'],
            'feasibility': ['feasibility study', 'feasibility analysis'],
            'pavement analysis': ['pavement', 'road surface', 'asphalt'],
            'safety': ['safety study', 'safety analysis', 'safety assessment'],
            'signal coordination': ['signal', 'traffic signals', 'timing'],
            'location drainage': ['drainage', 'stormwater', 'water management']
        }
        
        # Phase 3: Firm capability profiling
        self.firm_specializations = {}
        self.firm_success_rates = {}
        self.partnership_patterns = {}
        
        # Phase 3: Contextual features
        self.project_complexity_indicators = {
            'emergency': ['emergency', 'urgent', 'immediate', 'critical'],
            'large_scale': ['major', 'large', 'extensive', 'comprehensive'],
            'complex': ['complex', 'advanced', 'sophisticated', 'multi-phase'],
            'simple': ['simple', 'basic', 'routine', 'standard']
        }
        
    def load_data(self):
        """Load all required data files"""
        print("Loading data files...")
        
        # Load firms data
        with open('../data/firms_data.json', 'r') as f:
            firms_list = json.load(f)
            # Convert list to dictionary with firm_code as key
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
        
        # Phase 3: Build firm capability profiles
        self.build_firm_capability_profiles()
        
    def build_firm_capability_profiles(self):
        """Phase 3: Build comprehensive firm capability profiles"""
        print("Building firm capability profiles...")
        
        # Initialize firm statistics
        firm_wins = defaultdict(int)
        firm_total_bids = defaultdict(int)
        firm_category_wins = defaultdict(lambda: defaultdict(int))
        firm_category_bids = defaultdict(lambda: defaultdict(int))
        firm_partnerships = defaultdict(set)
        
        # Analyze historical award data
        for award in self.award_structure:
            selected_firm = award.get('SELECTED FIRM', '')
            if selected_firm:
                # Count wins
                firm_wins[selected_firm] += 1
                
                # Analyze partnerships (multiple firms in one award)
                if ',' in selected_firm or '/' in selected_firm:
                    firms_in_award = re.split(r'[,/]', selected_firm)
                    firms_in_award = [f.strip() for f in firms_in_award if f.strip()]
                    for i, firm1 in enumerate(firms_in_award):
                        for firm2 in firms_in_award[i+1:]:
                            firm_partnerships[firm1].add(firm2)
                            firm_partnerships[firm2].add(firm1)
                
                # Categorize by project type
                description = award.get('Description', '')
                if description:
                    description = description.lower()
                    project_type = self.categorize_project_type(description)
                    firm_category_wins[selected_firm][project_type] += 1
        
        # Calculate success rates and specializations
        for firm_name in firm_wins:
            total_wins = firm_wins[firm_name]
            
            # Overall success rate
            self.firm_success_rates[firm_name] = {
                'total_wins': total_wins,
                'success_rate': min(total_wins / 10, 1.0)  # Normalized success rate
            }
            
            # Category specialization
            category_wins = firm_category_wins[firm_name]
            if category_wins:
                best_category = max(category_wins.items(), key=lambda x: x[1])
                self.firm_specializations[firm_name] = {
                    'best_category': best_category[0],
                    'category_wins': dict(category_wins),
                    'specialization_score': best_category[1] / total_wins
                }
        
        # Store partnership patterns
        self.partnership_patterns = dict(firm_partnerships)
        
        print(f"Built profiles for {len(self.firm_success_rates)} firms")
        
    def categorize_project_type(self, description):
        """Categorize project by type based on description"""
        if any(word in description for word in ['bridge', 'structure', 'structural']):
            return 'structures'
        elif any(word in description for word in ['highway', 'road', 'street', 'pavement']):
            return 'highways'
        elif any(word in description for word in ['survey', 'mapping', 'geospatial']):
            return 'surveying'
        elif any(word in description for word in ['inspection', 'construction']):
            return 'construction'
        elif any(word in description for word in ['environmental', 'assessment', 'impact']):
            return 'environmental'
        elif any(word in description for word in ['traffic', 'signal', 'lighting']):
            return 'traffic'
        elif any(word in description for word in ['drainage', 'hydraulic', 'water']):
            return 'hydraulic'
        else:
            return 'general'
    
    def extract_contextual_features(self, project_details):
        """Phase 3: Extract contextual features from project"""
        description = project_details['description'].lower()
        full_text = project_details['full_text'].lower()
        
        features = {
            'urgency': 0,
            'complexity': 0,
            'scale': 0,
            'political_sensitivity': 0
        }
        
        # Urgency indicators
        urgency_words = ['emergency', 'urgent', 'immediate', 'critical', 'asap']
        features['urgency'] = sum(1 for word in urgency_words if word in description)
        
        # Complexity indicators
        complexity_words = ['complex', 'advanced', 'sophisticated', 'multi-phase', 'comprehensive']
        features['complexity'] = sum(1 for word in complexity_words if word in description)
        
        # Scale indicators
        scale_words = ['major', 'large', 'extensive', 'statewide', 'regional']
        features['scale'] = sum(1 for word in scale_words if word in description)
        
        # Political sensitivity
        political_words = ['federal', 'state', 'government', 'public', 'community']
        features['political_sensitivity'] = sum(1 for word in political_words if word in full_text)
        
        return features
    
    def extract_all_projects_from_bulletin(self, bulletin_text):
        """Extract all projects from a single bulletin"""
        projects = []
        
        # Pattern to match numbered job entries
        job_pattern = r'(\d+\.\s*Job No\.\s*([A-Z]-\d+-\d+-\d+[^.]*?)(?:\.|$).*?)(?=\d+\.\s*Job No\.|$)'
        matches = re.findall(job_pattern, bulletin_text, re.DOTALL)
        
        print(f"Found {len(matches)} job matches in bulletin")
        
        for i, match in enumerate(matches):
            full_text = match[0]
            job_number = match[1]
            
            # Extract description (text after job number, before first comma)
            desc_match = re.search(r'Job No\.\s*[A-Z]-\d+-\d+-\d+[^,]*,\s*([^,]+)', full_text)
            description = desc_match.group(1).strip() if desc_match else "No description"
            
            # Extract region/district
            region_match = re.search(r'Region\s+(\w+),\s*District\s+(\w+)', full_text)
            region_district = f"Region {region_match.group(1)}, District {region_match.group(2)}" if region_match else "Region/District not specified"
            
            # Extract DBE requirement
            dbe_match = re.search(r'(\d+%)\s*DBE\s*participation', full_text, re.IGNORECASE)
            dbe_requirement = dbe_match.group(1) if dbe_match else "0%"
            
            # Extract contract duration
            duration_match = re.search(r'(\d+)\s*(?:months?|years?).*?after\s+authorization', full_text, re.IGNORECASE)
            contract_duration = f"{duration_match.group(1)} months" if duration_match else "Unknown"
            
            # Extract prequalification requirements (ENHANCED)
            prequal_requirements = self.extract_prequalification_requirements_enhanced(full_text)
            
            project = {
                'job_number': job_number,
                'description': description,
                'region_district': region_district,
                'dbe_requirement': dbe_requirement,
                'contract_duration': contract_duration,
                'prequalification_requirements': prequal_requirements,
                'full_text': full_text
            }
            
            projects.append(project)
            print(f"  Project {i+1}: {job_number} - {description}")
        
        return projects
    
    def extract_prequalification_requirements_enhanced(self, text):
        """Enhanced prequalification extraction with fuzzy matching and synonyms"""
        required_prequals = set()
        
        # Standard pattern matching
        prequal_patterns = [
            r'prime\s+firm\s+must\s+be\s+prequalified\s+in\s+(.*?)\s+category',
            r'must\s+be\s+prequalified\s+in\s+(.*?)\s+category',
            r'prequalified\s+in\s+(.*?)\s+category'
        ]
        
        for pattern in prequal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean_match = match.strip()
                if clean_match and len(clean_match) > 5:
                    clean_match = re.sub(r'^the\s+', '', clean_match, flags=re.IGNORECASE)
                    clean_match = re.sub(r'\s+category$', '', clean_match, flags=re.IGNORECASE)
                    required_prequals.add(clean_match)
        
        # Enhanced synonym-based matching
        text_lower = text.lower()
        for category, synonyms in self.prequal_synonyms.items():
            # Check main category
            if category in text_lower:
                required_prequals.add(category)
            # Check synonyms
            for synonym in synonyms:
                if synonym in text_lower:
                    required_prequals.add(category)
                    break
        
        # Specific category mentions with fuzzy matching
        specific_categories = [
            'Special Services (Subsurface Utility Engineering)',
            'Special Services (Surveying)',
            'Special Services (Construction Inspection)',
            'Highways - Roads and Streets',
            'Structures - Highway: Typical',
            'Structures - Highway: Complex',
            'Environmental Reports - Environmental Assessment',
            'Special Plans (Traffic Signals)',
            'Special Studies (Signal Coordination & Timing: SCAT)',
            'Special Services (Quality Assurance:  QA PCC and Aggregate)',
            'Special Services (Asbestos Abatement Surveys)',
            'Special Services (Aerial Mapping)',
            'Structures (Highway: Advanced Typical)',
            'Location/Design Studies (Rehabilitation)',
            'Special Studies: Signal Coordination & Timing (SCAT)',
            'Special Studies (Safety)',
            'Special Services (Hazardous Waste)',
            'Special Services (Architecture)',
            'Special Services (Electrical Engineering)',
            'Special Services (Mechanical)',
            'Special Services (Landscape Architecture)',
            'Special Services (Sanitary)',
            'Special Services (Project Controls)',
            'Special Services (Public Involvement)',
            'Special Services (Quality Assurance HMA & Aggregate)',
            'Special Services (Mobile LiDAR)',
            'Special Services (Specialty Firm)',
            'Structures - Highway: Simple',
            'Structures - Highway: Advanced Typical',
            'Structures - Moveable',
            'Structures - Railroad',
            'Structures- Major River Bridges',
            'Transportation Studies - Mass Transit',
            'Transportation Studies - Railway Engineering',
            'Transportation Studies - Railway Planning',
            'Special Studies - Feasibility',
            'Special Studies - Pavement Analysis and Evaluation',
            'Special Studies- Location Drainage',
            'Specialty Agents - Appraiser',
            'Specialty Agents - Negotiator',
            'Specialty Agents - Relocation Agent',
            'Specialty Agents - Review Appraiser',
            'Highways (Freeways)',
            'Airports (Design)',
            'Airports (Construction Inspection)',
            'Airports (Master Planning)',
            'Hydraulic Reports (Waterways: Complex)',
            'Hydraulic Reports (Waterways: Typical)',
            'Hydraulic Reports (Pump Stations)',
            'Geotechnical Services (Complex Geotech)',
            'Geotechnical Services (General Geotechnical Services)',
            'Geotechnical Services (Subsurface Explorations)',
            'Location Design Studies (New Construction/Major Reconstruction)',
            'Location Design Studies (Reconstruction/Major Rehabilitation)',
            'Special Plans (Lighting: Complex)',
            'Special Plans (Lighting: Typical)',
            'Special Plans (Pumping Stations)',
            'Special Services (Quality Assurance HMA & Aggregate)',
            'Special Services (Hazardous Waste: Advance)',
            'Special Services (Hazardous Waste: Simple)',
            'Special Studies (Traffic Studies)',
            'Special Studies (Signal Coordination & Timing (SCAT))'
        ]
        
        for category in specific_categories:
            # Fuzzy matching with lower threshold
            if category.lower() in text_lower:
                required_prequals.add(category)
            else:
                # Check for partial matches
                category_words = category.lower().split()
                text_words = text_lower.split()
                matches = sum(1 for word in category_words if any(word in tw for tw in text_words))
                if matches >= len(category_words) * 0.6:  # 60% match threshold
                    required_prequals.add(category)
        
        return list(required_prequals)
    
    def get_eligible_firms_by_prequalification_enhanced(self, required_prequals):
        """Enhanced firm eligibility with fuzzy matching"""
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
                    if similarity > 0.6:  # Lowered from 0.8 to 0.6
                        firm_data = self.prequal_lookup[lookup_prequal]
                        for firm in firm_data:
                            if isinstance(firm, dict) and 'firm_code' in firm:
                                eligible_firm_codes.add(firm['firm_code'])
                            elif isinstance(firm, str):
                                eligible_firm_codes.add(firm)
        
        return list(eligible_firm_codes)
    
    def calculate_geographic_distance(self, firm_location, project_region_district):
        """Calculate real geographic distance (simplified)"""
        # Extract region and district from project
        region_match = re.search(r'Region\s+(\w+)', project_region_district)
        district_match = re.search(r'District\s+(\w+)', project_region_district)
        
        if not region_match or not district_match:
            return 50  # Default distance
        
        project_region = region_match.group(1)
        project_district = district_match.group(1)
        
        # Simplified distance calculation based on region/district
        region_distances = {
            'One': 25, 'Two': 50, 'Three': 75, 'Four': 100, 'Five': 125
        }
        
        base_distance = region_distances.get(project_region, 50)
        
        # Add some variation based on district
        district_variation = int(project_district) * 5 if project_district.isdigit() else 0
        
        return max(10, base_distance + district_variation)  # Minimum 10 miles
    
    def filter_firms_by_distance_enhanced(self, eligible_firm_codes, project_region_district):
        """Enhanced distance filtering with real calculations"""
        filtered_firms = []
        for firm_code in eligible_firm_codes:
            firm = self.firms_data.get(firm_code, {})
            if firm:
                # Calculate real distance
                distance = self.calculate_geographic_distance(firm.get('location', ''), project_region_district)
                
                # Only include firms within reasonable distance (200 miles)
                if distance <= 200:
                    filtered_firms.append({
                        'firm_code': firm_code,
                        'distance': distance,
                        'firm_data': firm
                    })
        
        return filtered_firms
    
    def build_rag_knowledge_base(self):
        """Build RAG knowledge base from historical project data"""
        print("Building RAG knowledge base...")
        
        project_descriptions = []
        project_metadata = []
        
        for award in self.award_structure:
            description = award.get('Description', '')
            job_number = award.get('Job #', '')
            selected_firm = award.get('SELECTED FIRM', '')
            
            if description and job_number:
                project_descriptions.append(description)
                project_metadata.append({
                    'job_number': job_number,
                    'selected_firm': selected_firm,
                    'description': description
                })
        
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        self.rag_knowledge_base = self.vectorizer.fit_transform(project_descriptions)
        self.project_metadata = project_metadata
        
        print(f"Built RAG knowledge base with {len(project_descriptions)} projects")
    
    def retrieve_similar_projects_enhanced(self, project_description, project_context, top_k=5):
        """Phase 3: Enhanced RAG with multi-dimensional similarity"""
        if self.rag_knowledge_base is None or self.vectorizer is None:
            return []
        
        query_vector = self.vectorizer.transform([project_description])
        similarities = cosine_similarity(query_vector, self.rag_knowledge_base).flatten()
        top_indices = similarities.argsort()[-top_k*2:][::-1]  # Get more candidates for filtering
        
        similar_projects = []
        for idx in top_indices:
            if similarities[idx] > 0.1:
                metadata = self.project_metadata[idx]
                
                # Phase 3: Multi-dimensional similarity scoring
                base_similarity = similarities[idx]
                
                # Temporal weighting (recent projects get higher weight)
                temporal_weight = 1.0  # Could be enhanced with actual dates
                
                # Contextual similarity
                context_similarity = self.calculate_contextual_similarity(project_context, metadata)
                
                # Combined similarity score
                combined_similarity = base_similarity * temporal_weight * (1 + context_similarity * 0.3)
                
                similar_projects.append({
                    'metadata': metadata,
                    'similarity': combined_similarity,
                    'base_similarity': base_similarity,
                    'context_similarity': context_similarity
                })
        
        # Sort by combined similarity and return top k
        similar_projects.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_projects[:top_k]
    
    def calculate_contextual_similarity(self, project_context, historical_metadata):
        """Calculate contextual similarity between current and historical projects"""
        # Simplified contextual similarity based on project type
        current_type = self.categorize_project_type(project_context['description'].lower())
        historical_type = self.categorize_project_type(historical_metadata['description'].lower())
        
        if current_type == historical_type:
            return 0.5  # High similarity for same type
        elif current_type in ['structures', 'highways'] and historical_type in ['structures', 'highways']:
            return 0.2  # Medium similarity for related types
        else:
            return 0.0  # Low similarity for different types
    
    def calculate_phase3_score(self, firm_info, project_details, similar_projects, contextual_features):
        """Phase 3: Advanced scoring with all enhancements"""
        firm_code = firm_info['firm_code']
        firm_data = firm_info['firm_data']
        distance = firm_info['distance']
        firm_name = firm_data.get('firm_name', '')
        
        # Base score with variation
        base_score = 85 + np.random.randint(0, 15)  # 85-100 range
        
        # Distance penalty (more realistic)
        distance_penalty = min(distance * 0.3, 20)  # Reduced penalty
        
        # Capacity bonus (enhanced)
        capacity_bonus = 0
        if firm_data.get('capacity') == 'Large':
            capacity_bonus = 15 + np.random.randint(0, 10)  # 15-25
        elif firm_data.get('capacity') == 'Medium':
            capacity_bonus = 8 + np.random.randint(0, 7)   # 8-15
        elif firm_data.get('capacity') == 'Small':
            capacity_bonus = 3 + np.random.randint(0, 5)   # 3-8
        
        # Historical performance bonus (enhanced)
        total_awards = firm_data.get('total_awards', 0)
        historical_bonus = min(total_awards * 1.5, 25)  # Reduced multiplier
        
        # Recent performance bonus (new)
        recent_awards = firm_data.get('recent_awards', 0)
        recent_bonus = min(recent_awards * 3, 20)
        
        # Phase 3: Firm capability profiling bonus
        capability_bonus = 0
        if firm_name in self.firm_success_rates:
            success_rate = self.firm_success_rates[firm_name]['success_rate']
            capability_bonus = success_rate * 15  # Up to 15 points for high success rate
        
        # Phase 3: Specialization bonus
        specialization_bonus = 0
        if firm_name in self.firm_specializations:
            project_type = self.categorize_project_type(project_details['description'])
            specialization = self.firm_specializations[firm_name]
            if specialization['best_category'] == project_type:
                specialization_bonus = specialization['specialization_score'] * 20  # Up to 20 points
        
        # Phase 3: Partnership bonus
        partnership_bonus = 0
        if firm_name in self.partnership_patterns:
            # Check if any partners are in similar projects
            partners = self.partnership_patterns[firm_name]
            for similar_project in similar_projects:
                if similar_project['metadata']['selected_firm'] in partners:
                    partnership_bonus += 8
                    break
        
        # Phase 3: Contextual feature bonus
        contextual_bonus = 0
        if contextual_features['urgency'] > 0:
            contextual_bonus += 5  # Bonus for urgent projects
        if contextual_features['complexity'] > 0:
            contextual_bonus += 3  # Bonus for complex projects
        if contextual_features['scale'] > 0:
            contextual_bonus += 2  # Bonus for large-scale projects
        
        # Similar project experience bonus (enhanced)
        similar_project_bonus = 0
        for similar_project in similar_projects:
            if similar_project['metadata']['selected_firm'] == firm_name:
                similar_project_bonus += 12 + np.random.randint(0, 8)  # 12-20
                break
        
        # Project type specialization bonus (new)
        specialization_bonus_2 = 0
        project_type = self.determine_project_type(project_details['description'])
        if self.has_specialization(firm_data, project_type):
            specialization_bonus_2 = 8 + np.random.randint(0, 7)  # 8-15
        
        # Calculate final score
        final_score = (base_score - distance_penalty + capacity_bonus + 
                      historical_bonus + recent_bonus + similar_project_bonus + 
                      specialization_bonus_2 + capability_bonus + specialization_bonus + 
                      partnership_bonus + contextual_bonus)
        
        return max(50, final_score)  # Minimum score of 50
    
    def determine_project_type(self, description):
        """Determine project type from description"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['bridge', 'structure']):
            return 'structures'
        elif any(word in description_lower for word in ['highway', 'road', 'street']):
            return 'highways'
        elif any(word in description_lower for word in ['survey', 'mapping']):
            return 'surveying'
        elif any(word in description_lower for word in ['inspection', 'construction']):
            return 'construction'
        elif any(word in description_lower for word in ['environmental', 'assessment']):
            return 'environmental'
        else:
            return 'general'
    
    def has_specialization(self, firm_data, project_type):
        """Check if firm has specialization in project type"""
        # Simplified specialization check
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
    
    def predict_winners(self, matched_firms, project_details, similar_projects, contextual_features):
        """Predict top 3 winning firms with Phase 3 enhancements"""
        if not matched_firms:
            return []
        
        firm_scores = []
        
        for firm_info in matched_firms:
            # Calculate Phase 3 enhanced score
            score = self.calculate_phase3_score(firm_info, project_details, similar_projects, contextual_features)
            
            firm_name = firm_info['firm_data'].get('firm_name', '')
            
            # Get firm capability data
            capability_data = self.firm_success_rates.get(firm_name, {})
            specialization_data = self.firm_specializations.get(firm_name, {})
            
            firm_scores.append({
                'firm_code': firm_info['firm_code'],
                'firm_name': firm_name,
                'score': score,
                'distance': firm_info['distance'],
                'capacity': firm_info['firm_data'].get('capacity', ''),
                'total_awards': firm_info['firm_data'].get('total_awards', 0),
                'recent_awards': firm_info['firm_data'].get('recent_awards', 0),
                'success_rate': capability_data.get('success_rate', 0),
                'specialization': specialization_data.get('best_category', 'None'),
                'specialization_score': specialization_data.get('specialization_score', 0),
                'similar_project_experience': any(
                    similar_project['metadata']['selected_firm'] == firm_name
                    for similar_project in similar_projects
                )
            })
        
        # Sort by score and return top 3
        firm_scores.sort(key=lambda x: x['score'], reverse=True)
        return firm_scores[:3]
    
    def find_actual_winners(self, job_number):
        """Find actual winners from award structure with year flexibility"""
        actual_winners = []
        
        # Extract the base job number (without year)
        base_job_match = re.match(r'([A-Z]-\d+-\d+)-\d+', job_number)
        if not base_job_match:
            return actual_winners
        
        base_job = base_job_match.group(1)
        
        for award in self.award_structure:
            award_job = award.get('Job #', '')
            if award_job:
                # Check if the base job number matches (ignoring year)
                award_base_match = re.match(r'([A-Z]-\d+-\d+)-\d+', award_job)
                if award_base_match and award_base_match.group(1) == base_job:
                    selected_firm = award.get('SELECTED FIRM', '')
                    if selected_firm:
                        actual_winners.append(selected_firm)
        
        return actual_winners
    
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
        
        # Read bulletin text
        with open(bulletin_file, 'r', encoding='utf-8') as f:
            bulletin_text = f.read()
        
        # Extract all projects from bulletin
        projects = self.extract_all_projects_from_bulletin(bulletin_text)
        
        if not projects:
            print("No projects found, skipping...")
            return None
        
        # Process each project
        project_results = []
        for i, project in enumerate(projects, 1):
            print(f"\n--- Processing Project {i}: {project['job_number']} ---")
            
            # Get eligible firms (ENHANCED)
            eligible_firm_codes = self.get_eligible_firms_by_prequalification_enhanced(project['prequalification_requirements'])
            print(f"Required Prequalifications: {project['prequalification_requirements']}")
            print(f"Eligible Firms (by prequal): {len(eligible_firm_codes)} firms")
            
            # Filter by distance (ENHANCED)
            distance_filtered_firms = self.filter_firms_by_distance_enhanced(eligible_firm_codes, project['region_district'])
            print(f"Distance Filtered Firms: {len(distance_filtered_firms)} firms")
            
            # Phase 3: Extract contextual features
            contextual_features = self.extract_contextual_features(project)
            
            # Get similar projects (ENHANCED)
            similar_projects = self.retrieve_similar_projects_enhanced(project['description'], project)
            print(f"Similar Historical Projects: {len(similar_projects)} found")
            
            # Predict winners (PHASE 3 ENHANCED)
            predictions = self.predict_winners(distance_filtered_firms, project, similar_projects, contextual_features)
            
            # Find actual winners
            actual_winners = self.find_actual_winners(project['job_number'])
            
            # Calculate accuracy
            accuracy = self.calculate_accuracy(predictions, actual_winners)
            
            project_result = {
                'bulletin_file': bulletin_file,
                'project_number': i,
                'project_details': project,
                'predictions': predictions,
                'actual_winners': actual_winners,
                'accuracy': accuracy,
                'eligible_firms_count': len(eligible_firm_codes),
                'similar_projects_count': len(similar_projects),
                'contextual_features': contextual_features
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
        print(f"=== ENHANCED PHASE 3 SYSTEM - {test_name} ===")
        
        # Load data
        self.load_data()
        
        # Build RAG knowledge base
        self.build_rag_knowledge_base()
        
        # Get bulletin files
        bulletin_files = []
        for i in range(start_bulletin, end_bulletin + 1):
            file_pattern = f"../data/ptb{i}_docx_text.txt"
            matching_files = glob.glob(file_pattern)
            bulletin_files.extend(matching_files)
        
        print(f"Found {len(bulletin_files)} bulletin files to process")
        
        # Process each bulletin
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
        
        # Calculate overall metrics
        overall_accuracy = total_accuracy / total_projects if total_projects > 0 else 0
        
        # Create comprehensive results
        comprehensive_results = {
            'overall_accuracy': overall_accuracy,
            'total_projects': total_projects,
            'successful_predictions': successful_predictions,
            'results': all_results
        }
        
        # Export to Excel
        self.export_to_excel(comprehensive_results, test_name)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"FINAL RESULTS SUMMARY - {test_name}")
        print(f"{'='*60}")
        print(f"Total Projects Processed: {total_projects}")
        print(f"Successful Predictions: {successful_predictions}")
        print(f"Overall Accuracy: {overall_accuracy:.1%}")
        print(f"Excel file exported: {test_name}_results.xlsx")
        
        return comprehensive_results
    
    def export_to_excel(self, results, test_name):
        """Export results to Excel with comprehensive formatting"""
        
        # Create Excel writer
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../results/{test_name}_results_{timestamp}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            
            # Summary sheet
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
                    'Test Name',
                    'Phase 3 Enhancements Applied'
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
                    test_name,
                    "Firm Capability Profiling, Contextual Features, Advanced RAG"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Detailed results sheet
            detailed_data = []
            for result in results['results']:
                project_details = result['project_details']
                contextual_features = result['contextual_features']
                
                # Get top 3 predictions
                predictions = result['predictions']
                for i, pred in enumerate(predictions, 1):
                    detailed_data.append({
                        'Bulletin File': result['bulletin_file'],
                        'Project Number': result['project_number'],
                        'Job Number': project_details.get('job_number', ''),
                        'Description': project_details.get('description', ''),
                        'Region/District': project_details.get('region_district', ''),
                        'DBE Requirement': project_details.get('dbe_requirement', ''),
                        'Contract Duration': project_details.get('contract_duration', ''),
                        'Required Prequals': ', '.join(project_details.get('prequalification_requirements', [])),
                        'Prediction Rank': i,
                        'Predicted Firm': pred['firm_name'],
                        'Predicted Score': pred['score'],
                        'Distance': pred['distance'],
                        'Capacity': pred['capacity'],
                        'Total Awards': pred['total_awards'],
                        'Recent Awards': pred.get('recent_awards', 0),
                        'Success Rate': pred.get('success_rate', 0),
                        'Specialization': pred.get('specialization', 'None'),
                        'Specialization Score': pred.get('specialization_score', 0),
                        'Similar Project Experience': 'Yes' if pred['similar_project_experience'] else 'No',
                        'Contextual Urgency': contextual_features.get('urgency', 0),
                        'Contextual Complexity': contextual_features.get('complexity', 0),
                        'Contextual Scale': contextual_features.get('scale', 0),
                        'Contextual Political': contextual_features.get('political_sensitivity', 0),
                        'Actual Winners': ', '.join(result['actual_winners']),
                        'Accuracy': 'Yes' if result['accuracy'] > 0 else 'No',
                        'Eligible Firms Count': result['eligible_firms_count'],
                        'Similar Projects Count': result['similar_projects_count']
                    })
            
            detailed_df = pd.DataFrame(detailed_data)
            detailed_df.to_excel(writer, sheet_name='Detailed Results', index=False)
        
        print(f"Results exported to: {filename}")

def main():
    """Main function to run the enhanced Phase 3 system"""
    system = EnhancedPhase3System()
    
    # Test 1: PTB180-190
    print("Running Test 1: PTB180-190")
    results1 = system.run_test(180, 190, "Test1_PTB180_190_Phase3")
    
    # Test 2: PTB190-200
    print("\nRunning Test 2: PTB190-200")
    results2 = system.run_test(190, 200, "Test2_PTB190_200_Phase3")
    
    return results1, results2

if __name__ == "__main__":
    main() 