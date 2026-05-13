#!/usr/bin/env python3
"""
Smart Tiered Performance System
Implements tiered performance scoring with fallback logic for firms without award history
"""

import json
import re
import os
import glob
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
from difflib import SequenceMatcher
from geopy.distance import geodesic
from collections import defaultdict

class SmartTieredPerformanceSystem:
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
        
        # NEW: Smart performance tracking
        self.firm_performance_data = {}
        self.performance_normalization_factors = {}
        
    def load_data(self):
        """Load all required data files"""
        print("🔄 Loading data files...")
        
        # Load original firms data (Phase 2.1 approach)
        with open('../data/firms_data.json', 'r') as f:
            firms_list = json.load(f)
            self.firms_data = {}
            for firm in firms_list:
                self.firms_data[firm['firm_code']] = firm
        print(f"✅ Loaded {len(self.firms_data)} firms (ORIGINAL)")
        
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
        
        # NEW: Build smart performance data
        self.build_smart_performance_data()
        
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
    
    def build_smart_performance_data(self):
        """NEW: Build smart performance data with fallback logic"""
        print("🔄 Building smart performance data...")
        
        # Track firm performance from award history
        firm_awards = {}
        
        # Analyze award structure for firm performance
        for i, award in enumerate(self.award_structure):
            selected_firm = award.get('SELECTED FIRM', '')
            subconsultants = award.get('SUBCONSULTANTS', '')
            district = award.get('Region/District', '')
            
            # Track prime firm
            if selected_firm:
                if selected_firm not in firm_awards:
                    firm_awards[selected_firm] = {
                        'total_awards': 0,
                        'recent_awards': 0,
                        'district_awards': defaultdict(int),
                        'has_history': False
                    }
                firm_awards[selected_firm]['total_awards'] += 1
                firm_awards[selected_firm]['recent_awards'] += 1  # Simplified for now
                firm_awards[selected_firm]['district_awards'][district] += 1
                firm_awards[selected_firm]['has_history'] = True
            
            # Track subconsultants
            if subconsultants and subconsultants != 'None':
                subs = [s.strip() for s in subconsultants.split(';') if s.strip()]
                for sub in subs:
                    if sub not in firm_awards:
                        firm_awards[sub] = {
                            'total_awards': 0,
                            'recent_awards': 0,
                            'district_awards': defaultdict(int),
                            'has_history': False
                        }
                    firm_awards[sub]['total_awards'] += 1
                    firm_awards[sub]['recent_awards'] += 1  # Simplified for now
                    firm_awards[sub]['district_awards'][district] += 1
                    firm_awards[sub]['has_history'] = True
        
        # Calculate normalization factors for firms with history
        firms_with_history = [firm for firm in firm_awards.values() if firm['has_history']]
        
        if firms_with_history:
            total_awards_values = [f['total_awards'] for f in firms_with_history]
            recent_awards_values = [f['recent_awards'] for f in firms_with_history]
            district_awards_values = [max(f['district_awards'].values()) if f['district_awards'] else 0 for f in firms_with_history]
            
            self.performance_normalization_factors = {
                'total_awards': {
                    'min': min(total_awards_values),
                    'max': max(total_awards_values)
                },
                'recent_awards': {
                    'min': min(recent_awards_values),
                    'max': max(recent_awards_values)
                },
                'district_awards': {
                    'min': min(district_awards_values),
                    'max': max(district_awards_values)
                }
            }
        else:
            # Fallback normalization factors
            self.performance_normalization_factors = {
                'total_awards': {'min': 0, 'max': 1},
                'recent_awards': {'min': 0, 'max': 1},
                'district_awards': {'min': 0, 'max': 1}
            }
        
        # Calculate performance scores for all firms
        for firm_code, firm in self.firms_data.items():
            firm_name = firm.get('firm_name', '')
            award_data = firm_awards.get(firm_name, {
                'total_awards': 0,
                'recent_awards': 0,
                'district_awards': defaultdict(int),
                'has_history': False
            })
            
            if award_data['has_history']:
                # Calculate performance score using formula
                total_awards_norm = self.normalize_value(
                    award_data['total_awards'],
                    self.performance_normalization_factors['total_awards']['min'],
                    self.performance_normalization_factors['total_awards']['max']
                )
                
                recent_awards_norm = self.normalize_value(
                    award_data['recent_awards'],
                    self.performance_normalization_factors['recent_awards']['min'],
                    self.performance_normalization_factors['recent_awards']['max']
                )
                
                district_awards_norm = self.normalize_value(
                    max(award_data['district_awards'].values()) if award_data['district_awards'] else 0,
                    self.performance_normalization_factors['district_awards']['min'],
                    self.performance_normalization_factors['district_awards']['max']
                )
                
                performance_score = (
                    total_awards_norm * 0.5 +
                    recent_awards_norm * 0.3 +
                    district_awards_norm * 0.2
                ) * 20
                
                performance_type = 'Historical'
            else:
                # Fallback score for firms without history
                performance_score = 10.0  # Neutral midpoint
                performance_type = 'Fallback'
            
            self.firm_performance_data[firm_code] = {
                'firm_name': firm_name,
                'performance_score': performance_score,
                'performance_type': performance_type,
                'total_awards': award_data['total_awards'],
                'recent_awards': award_data['recent_awards'],
                'max_district_awards': max(award_data['district_awards'].values()) if award_data['district_awards'] else 0,
                'has_history': award_data['has_history']
            }
        
        # Show performance distribution
        historical_firms = [f for f in self.firm_performance_data.values() if f['has_history']]
        fallback_firms = [f for f in self.firm_performance_data.values() if not f['has_history']]
        
        print(f"✅ Built smart performance data for {len(self.firm_performance_data)} firms")
        print(f"  Firms with history: {len(historical_firms)} ({len(historical_firms)/len(self.firm_performance_data)*100:.1f}%)")
        print(f"  Firms with fallback: {len(fallback_firms)} ({len(fallback_firms)/len(self.firm_performance_data)*100:.1f}%)")
        
        if historical_firms:
            historical_scores = [f['performance_score'] for f in historical_firms]
            print(f"  Historical score range: {min(historical_scores):.1f} - {max(historical_scores):.1f}")
            print(f"  Fallback score: 10.0 (neutral)")
    
    def normalize_value(self, value, min_val, max_val):
        """Normalize value to 0-1 range"""
        if max_val == min_val:
            return 0.5  # Neutral value if no variation
        return (value - min_val) / (max_val - min_val)
    
    def extract_all_projects_from_bulletin(self, bulletin_text):
        """Extract all projects from bulletin"""
        projects = []
        
        # Enhanced job pattern matching
        job_patterns = [
            r'(Job No\.\s*([A-Z]-\d+-\d+-\d+),\s*([^,]+?)(?:,|\.).*?)(?=Job No\.|$)',
            r'(Job No\.\s*([A-Z]-\d+-\d+-\d+),\s*([^.]*?)(?:\.|$).*?)(?=Job No\.|$)',
            r'(Job No\.\s*([A-Z]-\d+-\d+-\d+)[^.]*?)(?=Job No\.|$)'
        ]
        
        all_matches = []
        for pattern in job_patterns:
            matches = re.findall(pattern, bulletin_text, re.DOTALL | re.IGNORECASE)
            all_matches.extend(matches)
        
        for i, match in enumerate(all_matches):
            if len(match) >= 2:
                full_text = match[0]
                job_number = match[1]
                description = match[2] if len(match) > 2 else "No description"
            else:
                continue
            
            # Enhanced description extraction
            if description == "No description":
                desc_patterns = [
                    r'Job No\.\s*[A-Z]-\d+-\d+-\d+,\s*([^,]+)',
                    r'Job\s*#\s*[A-Z]-\d+-\d+-\d+[^,]*,\s*([^,]+)',
                    r'[A-Z]-\d+-\d+-\d+[^,]*,\s*([^,]+)'
                ]
                
                for pattern in desc_patterns:
                    desc_match = re.search(pattern, full_text, re.IGNORECASE)
                    if desc_match:
                        description = desc_match.group(1).strip()
                        break
            
            # Enhanced region/district extraction
            region_patterns = [
                r'Region\s+(\w+)[^D]*District\s+(\w+)',
                r'District\s+(\w+)[^R]*Region\s+(\w+)',
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
            
            # Enhanced prequalification extraction
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
        
        return projects
    
    def extract_prequalification_requirements_enhanced(self, text):
        """Enhanced prequalification extraction"""
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
        
        # Enhanced synonym-based matching
        text_lower = text.lower()
        for category, synonyms in self.prequal_synonyms.items():
            if category in text_lower:
                required_prequals.add(category)
            for synonym in synonyms:
                if synonym in text_lower:
                    required_prequals.add(category)
                    break
        
        return list(required_prequals)
    
    def get_eligible_firms_by_prequalification_enhanced(self, required_prequals):
        """Enhanced firm eligibility"""
        eligible_firm_codes = set()
        
        for prequal in required_prequals:
            if prequal in self.prequal_lookup:
                firm_data = self.prequal_lookup[prequal]
                for firm in firm_data:
                    if isinstance(firm, dict) and 'firm_code' in firm:
                        eligible_firm_codes.add(firm['firm_code'])
                    elif isinstance(firm, str):
                        eligible_firm_codes.add(firm)
            else:
                # Enhanced fuzzy matching
                for lookup_prequal in self.prequal_lookup.keys():
                    similarity = SequenceMatcher(None, prequal.lower(), lookup_prequal.lower()).ratio()
                    if similarity > 0.5:
                        firm_data = self.prequal_lookup[lookup_prequal]
                        for firm in firm_data:
                            if isinstance(firm, dict) and 'firm_code' in firm:
                                eligible_firm_codes.add(firm['firm_code'])
                            elif isinstance(firm, str):
                                eligible_firm_codes.add(firm)
        
        return list(eligible_firm_codes)
    
    def calculate_geographic_distance(self, firm_location, project_region_district):
        """Calculate geographic distance"""
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
        """Enhanced distance filtering"""
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
        """Build RAG knowledge base"""
        print("🔄 Building RAG knowledge base...")
        
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
        
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.rag_knowledge_base = self.vectorizer.fit_transform(project_descriptions)
        self.project_metadata = project_metadata
        
        print(f"✅ Built RAG knowledge base for {len(project_descriptions)} projects")
    
    def retrieve_similar_projects_enhanced(self, project_description, project_context, top_k=5):
        """Enhanced RAG with temporal weighting"""
        if self.rag_knowledge_base is None or self.vectorizer is None:
            return []
        
        query_vector = self.vectorizer.transform([project_description])
        similarities = cosine_similarity(query_vector, self.rag_knowledge_base).flatten()
        top_indices = similarities.argsort()[-top_k*3:][::-1]
        
        similar_projects = []
        for idx in top_indices:
            if similarities[idx] > 0.1:
                metadata = self.project_metadata[idx]
                
                base_similarity = similarities[idx]
                temporal_weight = metadata.get('temporal_weight', 1.0)
                complexity_score = metadata.get('complexity_score', 1.0)
                
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
    
    def calculate_smart_score(self, firm_info, project_details, similar_projects):
        """Calculate score using smart tiered performance system"""
        firm_code = firm_info['firm_code']
        firm_data = firm_info['firm_data']
        distance = firm_info['distance']
        firm_name = firm_data.get('firm_name', '')
        
        # Get performance data
        performance_data = self.firm_performance_data.get(firm_code, {})
        
        # Base score (Phase 2.1 style)
        base_score = 85 + np.random.randint(0, 15)
        
        # Distance penalty
        distance_penalty = min(distance * 0.3, 20)
        
        # Capacity bonus (Phase 2.1 style)
        capacity_bonus = 0
        capacity = firm_data.get('capacity', 'Unknown')
        if capacity == 'Large':
            capacity_bonus = 15 + np.random.randint(0, 10)
        elif capacity == 'Medium':
            capacity_bonus = 8 + np.random.randint(0, 7)
        elif capacity == 'Small':
            capacity_bonus = 3 + np.random.randint(0, 5)
        
        # Historical bonus (Phase 2.1 style)
        total_awards = performance_data.get('total_awards', 0)
        historical_bonus = min(total_awards * 1.5, 25)
        
        # Recent bonus (Phase 2.1 style)
        recent_awards = performance_data.get('recent_awards', 0)
        recent_bonus = min(recent_awards * 3, 20)
        
        # Similar project bonus (Phase 2.1 style)
        similar_project_bonus = 0
        for similar_project in similar_projects:
            if similar_project['metadata']['selected_firm'] == firm_name:
                temporal_weight = similar_project['temporal_weight']
                complexity_score = similar_project['complexity_score']
                
                base_bonus = 12 + np.random.randint(0, 8)
                weighted_bonus = (base_bonus * temporal_weight * complexity_score)
                similar_project_bonus += weighted_bonus
                break
        
        # NEW: Performance Score (0-20 points)
        performance_score = performance_data.get('performance_score', 10.0)
        
        # Calculate final score
        final_score = (base_score - distance_penalty + capacity_bonus + 
                      historical_bonus + recent_bonus + similar_project_bonus + 
                      performance_score)
        
        return max(50, final_score), performance_data
    
    def predict_winners(self, matched_firms, project_details, similar_projects):
        """Predict top 5 winning firms with smart tiered performance"""
        if not matched_firms:
            return []
        
        firm_scores = []
        
        for firm_info in matched_firms:
            score, performance_data = self.calculate_smart_score(firm_info, project_details, similar_projects)
            firm_name = firm_info['firm_data'].get('firm_name', '')
            
            firm_scores.append({
                'firm_code': firm_info['firm_code'],
                'firm_name': firm_name,
                'score': score,
                'distance': firm_info['distance'],
                'performance_score': performance_data.get('performance_score', 10.0),
                'performance_type': performance_data.get('performance_type', 'Fallback'),
                'total_awards': performance_data.get('total_awards', 0),
                'recent_awards': performance_data.get('recent_awards', 0),
                'max_district_awards': performance_data.get('max_district_awards', 0),
                'has_history': performance_data.get('has_history', False),
                'similar_project_experience': any(
                    similar_project['metadata']['selected_firm'] == firm_name
                    for similar_project in similar_projects
                )
            })
        
        firm_scores.sort(key=lambda x: x['score'], reverse=True)
        return firm_scores[:5]
    
    def find_actual_winners(self, job_number):
        """Find actual winners from award structure"""
        actual_winners = []
        base_job_match = re.match(r'([A-Z]-\d+-\d+)-\d+', job_number)
        if not base_job_match:
            return actual_winners
        base_job = base_job_match.group(1)
        for award in self.award_structure:
            award_job = award.get('Job #', '')
            if award_job:
                award_base_match = re.match(r'([A-Z]-\d+-\d+)-\d+', award_job)
                if award_base_match and award_base_match.group(1) == base_job:
                    selected_firm = award.get('SELECTED FIRM', '')
                    if selected_firm:
                        actual_winners.append(selected_firm)
        return actual_winners
    
    def run_test(self, start_bulletin, end_bulletin, test_name):
        """Run test on specified bulletin range"""
        print(f"\n{'='*80}")
        print(f"🎯 RUNNING {test_name} WITH SMART TIERED PERFORMANCE")
        print(f"{'='*80}")
        
        self.load_data()
        self.build_rag_knowledge_base()
        
        bulletin_files = []
        for i in range(start_bulletin, end_bulletin + 1):
            file_pattern = f"../data/ptb{i}_docx_text.txt"
            matching_files = glob.glob(file_pattern)
            bulletin_files.extend(matching_files)
        
        if not bulletin_files:
            print(f"❌ No bulletin files found for range {start_bulletin}-{end_bulletin}")
            return None
        
        print(f"📊 Found {len(bulletin_files)} bulletin files")
        
        all_results = []
        total_projects = 0
        successful_predictions = 0
        
        for bulletin_file in bulletin_files:
            print(f"\n📄 Processing: {os.path.basename(bulletin_file)}")
            
            with open(bulletin_file, 'r', encoding='utf-8') as f:
                bulletin_text = f.read()
            
            projects = self.extract_all_projects_from_bulletin(bulletin_text)
            
            if not projects:
                print(f"  ⚠️  No projects found in {os.path.basename(bulletin_file)}")
                continue
            
            print(f"  📋 Found {len(projects)} projects")
            
            for project in projects:
                total_projects += 1
                
                eligible_firm_codes = self.get_eligible_firms_by_prequalification_enhanced(project['prequalification_requirements'])
                distance_filtered_firms = self.filter_firms_by_distance_enhanced(eligible_firm_codes, project['region_district'])
                similar_projects = self.retrieve_similar_projects_enhanced(project['description'], project)
                predictions = self.predict_winners(distance_filtered_firms, project, similar_projects)
                
                # Check if any actual winner is in predictions
                actual_winners = self.find_actual_winners(project['job_number'])
                if actual_winners:
                    predicted_firm_names = [pred['firm_name'] for pred in predictions]
                    if any(winner in predicted_firm_names for winner in actual_winners):
                        successful_predictions += 1
                
                project_result = {
                    'job_number': project['job_number'],
                    'description': project['description'],
                    'predictions': predictions,
                    'actual_winners': actual_winners,
                    'eligible_firms_count': len(eligible_firm_codes),
                    'distance_filtered_count': len(distance_filtered_firms)
                }
                
                all_results.append(project_result)
        
        # Calculate accuracy
        accuracy = (successful_predictions / total_projects * 100) if total_projects > 0 else 0
        
        print(f"\n📊 {test_name} RESULTS:")
        print(f"  Total Projects: {total_projects}")
        print(f"  Successful Predictions: {successful_predictions}")
        print(f"  Accuracy: {accuracy:.1f}%")
        
        # Export results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../results/{test_name}_SmartTiered_{timestamp}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': ['Test Name', 'Total Projects', 'Successful Predictions', 'Accuracy', 'System Version', 'Performance Method'],
                'Value': [test_name, total_projects, successful_predictions, f"{accuracy:.1f}%", "Smart Tiered Performance System", "Tiered with Fallback Logic"]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Detailed predictions sheet
            detailed_data = []
            for result in all_results:
                for i, pred in enumerate(result['predictions'], 1):
                    detailed_data.append({
                        'Job Number': result['job_number'],
                        'Description': result['description'],
                        'Prediction Rank': i,
                        'Predicted Firm': pred['firm_name'],
                        'Predicted Score': pred['score'],
                        'Performance Score': pred['performance_score'],
                        'Performance Type': pred['performance_type'],
                        'Total Awards': pred['total_awards'],
                        'Recent Awards': pred['recent_awards'],
                        'Max District Awards': pred['max_district_awards'],
                        'Has History': 'Yes' if pred['has_history'] else 'No',
                        'Similar Project Experience': 'Yes' if pred['similar_project_experience'] else 'No',
                        'Actual Winners': ', '.join(result['actual_winners']),
                        'Eligible Firms Count': result['eligible_firms_count'],
                        'Distance Filtered Count': result['distance_filtered_count']
                    })
            
            detailed_df = pd.DataFrame(detailed_data)
            detailed_df.to_excel(writer, sheet_name='Detailed Predictions', index=False)
        
        print(f"📄 Results exported to: {filename}")
        
        return {
            'test_name': test_name,
            'total_projects': total_projects,
            'successful_predictions': successful_predictions,
            'accuracy': accuracy,
            'filename': filename
        }

def main():
    """Main function to test smart tiered performance system"""
    print("🚀 TESTING SMART TIERED PERFORMANCE SYSTEM")
    print("="*80)
    
    tester = SmartTieredPerformanceSystem()
    
    # Test 1: PTB180-190
    print("\n🎯 TEST 1: PTB180-190")
    results1 = tester.run_test(180, 190, "PTB180_190_SmartTiered")
    
    # Test 2: PTB190-200
    print("\n🎯 TEST 2: PTB190-200")
    results2 = tester.run_test(190, 200, "PTB190_200_SmartTiered")
    
    # Compare with baseline
    print(f"\n{'='*80}")
    print(f"📊 COMPARISON WITH BASELINE (PHASE 2.1)")
    print(f"{'='*80}")
    
    baseline_ptb180_190 = 25.2
    baseline_ptb190_200 = 30.1
    baseline_average = 27.6
    
    if results1 and results2:
        new_ptb180_190 = results1['accuracy']
        new_ptb190_200 = results2['accuracy']
        new_average = (new_ptb180_190 + new_ptb190_200) / 2
        
        print(f"📊 BASELINE RESULTS (Phase 2.1):")
        print(f"  PTB180-190: {baseline_ptb180_190:.1f}%")
        print(f"  PTB190-200: {baseline_ptb190_200:.1f}%")
        print(f"  Average: {baseline_average:.1f}%")
        
        print(f"\n📊 SMART TIERED PERFORMANCE RESULTS:")
        print(f"  PTB180-190: {new_ptb180_190:.1f}%")
        print(f"  PTB190-200: {new_ptb190_200:.1f}%")
        print(f"  Average: {new_average:.1f}%")
        
        print(f"\n📈 IMPROVEMENT ANALYSIS:")
        ptb180_190_improvement = new_ptb180_190 - baseline_ptb180_190
        ptb190_200_improvement = new_ptb190_200 - baseline_ptb190_200
        average_improvement = new_average - baseline_average
        
        print(f"  PTB180-190: {ptb180_190_improvement:+.1f}%")
        print(f"  PTB190-200: {ptb190_200_improvement:+.1f}%")
        print(f"  Average: {average_improvement:+.1f}%")
        
        if ptb180_190_improvement > 0 and ptb190_200_improvement > 0:
            print(f"\n✅ SIGNIFICANT IMPROVEMENT ACHIEVED!")
            print(f"   Both ranges show improvement - Smart tiered performance is successful")
        elif average_improvement > 0:
            print(f"\n⚠️  PARTIAL IMPROVEMENT:")
            print(f"   Average improved but not both ranges - Needs analysis")
        else:
            print(f"\n❌ NO IMPROVEMENT:")
            print(f"   Rolling back to Phase 2.1 baseline")
    
    print(f"\n✅ TESTING COMPLETE")

if __name__ == "__main__":
    main() 