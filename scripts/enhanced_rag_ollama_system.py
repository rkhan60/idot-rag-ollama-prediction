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

class EnhancedRAGOllamaSystem:
    def __init__(self):
        self.firms_data = {}
        self.prequal_lookup = {}
        self.district_mapping = {}
        self.award_structure = {}
        self.rag_knowledge_base = None
        self.vectorizer = None
        
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
        
    def extract_project_details_enhanced(self, project_text):
        """Enhanced extraction focusing on critical eligibility information for a single project"""
        
        # 1. Extract DBE requirements
        dbe_requirement = self.extract_dbe_requirement(project_text)
        
        # 2. Extract contract duration
        contract_duration = self.extract_contract_duration(project_text)
        
        # 3. Extract prequalification requirements ⭐ CRITICAL
        prequal_requirements = self.extract_prequalification_requirements(project_text)
        
        # 4. Extract personnel requirements
        personnel_requirements = self.extract_personnel_requirements(project_text)
        
        return {
            'dbe_requirement': dbe_requirement,
            'contract_duration': contract_duration,
            'prequalification_requirements': prequal_requirements,
            'personnel_requirements': personnel_requirements
        }
    
    def extract_all_projects(self, text):
        """Extract all projects from bulletin text"""
        # Pattern to match all job numbers and their content
        job_pattern = r'(\d+\.\s*Job No\.\s*([A-Z]-\d+-\d+-\d+[^.]*?)(?:\.|$).*?)(?=\d+\.\s*Job No\.|$)'
        matches = re.findall(job_pattern, text, re.DOTALL)
        
        projects = []
        for match in matches:
            full_text = match[0]
            job_number = match[1]
            
            # Extract description and region/district
            desc_pattern = r'Job No\.\s*[A-Z]-\d+-\d+-\d+[^,]*,\s*([^,]+)'
            desc_match = re.search(desc_pattern, full_text)
            description = desc_match.group(1).strip() if desc_match else ""
            
            # Extract region/district
            region_pattern = r'Region\s+(\w+),\s*District\s+(\w+)'
            region_match = re.search(region_pattern, full_text)
            region_district = f"Region {region_match.group(1)}, District {region_match.group(2)}" if region_match else ""
            
            projects.append({
                'job_number': job_number,
                'description': description,
                'region_district': region_district,
                'full_text': full_text
            })
        
        return projects
    
    def extract_dbe_requirement(self, text):
        """Extract DBE participation requirement"""
        dbe_patterns = [
            r'(\d+%)\s*DBE\s*participation',
            r'DBE\s*participation\s*of\s*(\d+%)',
            r'(\d+%)\s*Disadvantaged\s*Business\s*Enterprise'
        ]
        
        for pattern in dbe_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return "0%"
    
    def extract_contract_duration(self, text):
        """Extract contract duration"""
        duration_patterns = [
            r'completion\s+date.*?(\d+)\s*(?:months?|years?)',
            r'contract.*?(\d+)\s*(?:months?|years?)',
            r'(\d+)\s*(?:months?|years?).*?after\s+authorization'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"{match.group(1)} months"
        return "Unknown"
    
    def extract_prequalification_requirements(self, text):
        """Extract required prequalification categories"""
        prequal_patterns = [
            r'prime\s+firm\s+must\s+be\s+prequalified\s+in\s+(.*?)\s+category',
            r'must\s+be\s+prequalified\s+in\s+(.*?)\s+category',
            r'prequalified\s+in\s+(.*?)\s+category'
        ]
        
        required_prequals = []
        for pattern in prequal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean up the match
                clean_match = match.strip()
                if clean_match and len(clean_match) > 5:  # Filter out very short matches
                    # Remove common prefixes/suffixes
                    clean_match = re.sub(r'^the\s+', '', clean_match, flags=re.IGNORECASE)
                    clean_match = re.sub(r'\s+category$', '', clean_match, flags=re.IGNORECASE)
                    required_prequals.append(clean_match)
        
        # Also look for specific category mentions
        specific_categories = [
            'Special Services (Subsurface Utility Engineering)',
            'Special Services (Surveying)',
            'Special Services (Construction Inspection)',
            'Highways - Roads and Streets',
            'Structures - Highway: Typical',
            'Structures - Highway: Complex',
            'Environmental Reports - Environmental Assessment'
        ]
        
        for category in specific_categories:
            if category.lower() in text.lower():
                required_prequals.append(category)
        
        return list(set(required_prequals))  # Remove duplicates
    
    def extract_personnel_requirements(self, text):
        """Extract key personnel requirements"""
        personnel_pattern = r'Key\s+personnel.*?must\s+include:(.*?)(?=\n\n|\n[A-Z]|$)'
        match = re.search(personnel_pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        return ""
    
    def get_eligible_firms_by_prequalification(self, required_prequals):
        """Get all firms eligible for the required prequalifications"""
        eligible_firm_codes = set()
        
        for prequal in required_prequals:
            # Try exact match first
            if prequal in self.prequal_lookup:
                firm_data = self.prequal_lookup[prequal]
                # Extract firm codes from the list of dictionaries
                for firm in firm_data:
                    if isinstance(firm, dict) and 'firm_code' in firm:
                        eligible_firm_codes.add(firm['firm_code'])
                    elif isinstance(firm, str):
                        eligible_firm_codes.add(firm)
            else:
                # Try fuzzy matching for similar prequalifications
                for lookup_prequal in self.prequal_lookup.keys():
                    similarity = SequenceMatcher(None, prequal.lower(), lookup_prequal.lower()).ratio()
                    if similarity > 0.8:  # 80% similarity threshold
                        firm_data = self.prequal_lookup[lookup_prequal]
                        # Extract firm codes from the list of dictionaries
                        for firm in firm_data:
                            if isinstance(firm, dict) and 'firm_code' in firm:
                                eligible_firm_codes.add(firm['firm_code'])
                            elif isinstance(firm, str):
                                eligible_firm_codes.add(firm)
        
        return list(eligible_firm_codes)
    
    def filter_firms_by_distance(self, eligible_firm_codes, project_region_district):
        """Filter firms based on distance to project location"""
        # Extract district from region/district string
        district_match = re.search(r'District\s+(\w+)', project_region_district)
        if not district_match:
            # If no district found, return all eligible firms
            filtered_firms = []
            for firm_code in eligible_firm_codes:
                firm = self.firms_data.get(firm_code, {})
                filtered_firms.append({
                    'firm_code': firm_code,
                    'distance': 50,  # Default distance
                    'firm_data': firm
                })
            return filtered_firms
        
        project_district = f"district_{district_match.group(1)}"
        
        # Check if district exists in mapping
        districts = self.district_mapping.get('districts', {})
        district_info = districts.get(project_district, {})
        
        if not district_info:
            # If district not found, return all eligible firms
            filtered_firms = []
            for firm_code in eligible_firm_codes:
                firm = self.firms_data.get(firm_code, {})
                filtered_firms.append({
                    'firm_code': firm_code,
                    'distance': 50,  # Default distance
                    'firm_data': firm
                })
            return filtered_firms
        
        # Get district counties
        district_counties = district_info.get('counties', [])
        
        filtered_firms = []
        for firm_code in eligible_firm_codes:
            firm = self.firms_data.get(firm_code, {})
            firm_location = firm.get('location', '')
            
            if firm_location:
                # Simple distance calculation based on location
                distance = self.calculate_simple_distance(firm_location, district_counties)
                
                # Filter based on distance (within 100 miles)
                if distance <= 100:
                    filtered_firms.append({
                        'firm_code': firm_code,
                        'distance': distance,
                        'firm_data': firm
                    })
        
        return filtered_firms
    
    def calculate_simple_distance(self, firm_location, district_counties):
        """Simple distance calculation based on location strings and district counties"""
        # Extract city/state from firm location
        firm_city = firm_location.split(',')[0].strip() if ',' in firm_location else firm_location
        firm_state = firm_location.split(',')[1].strip() if ',' in firm_location and len(firm_location.split(',')) > 1 else ""
        
        # Check if firm is in the same district (same state and nearby)
        if firm_state == "IL":
            # For Illinois firms, use a simple distance calculation
            # District 1 (Chicago area) - closer distance for Chicago area firms
            if any(county in ['Cook', 'DuPage', 'Kane', 'Lake', 'McHenry', 'Will'] for county in district_counties):
                # Chicago area district
                chicago_area_cities = ['Chicago', 'Aurora', 'Naperville', 'Elgin', 'Joliet', 'Arlington Heights', 
                                     'Schaumburg', 'Palatine', 'Buffalo Grove', 'Evanston', 'Skokie', 
                                     'Des Plaines', 'Mount Prospect', 'Wheeling', 'Prospect Heights', 
                                     'Glenview', 'Northbrook', 'Highland Park', 'Lake Forest', 'Libertyville', 
                                     'Mundelein', 'Gurnee', 'Waukegan', 'Zion', 'Round Lake', 'Grayslake', 
                                     'Antioch', 'Fox Lake', 'McHenry', 'Crystal Lake', 'Woodstock', 'Huntley', 
                                     'Algonquin', 'Cary', 'Barrington', 'Lake Zurich', 'Hawthorn Woods', 
                                     'Long Grove', 'Vernon Hills', 'Lincolnshire', 'Riverwoods', 'Deerfield', 
                                     'Bannockburn', 'River Forest', 'Oak Park', 'Forest Park', 'Berwyn', 
                                     'Cicero', 'Stickney', 'Summit', 'Willow Springs', 'Burr Ridge', 
                                     'Willowbrook', 'Darien', 'Downers Grove', 'Lisle', 'Batavia', 'Geneva', 
                                     'St. Charles', 'Elburn', 'Sugar Grove', 'Yorkville', 'Plano', 'Sandwich']
                
                if firm_city in chicago_area_cities:
                    return 25  # Very close
                else:
                    return 75  # Moderate distance
            
            # Other Illinois districts - moderate distance
            return 50
        else:
            # Non-Illinois firms - longer distance
            return 100
    
    def build_rag_knowledge_base(self):
        """Build RAG knowledge base from historical project data"""
        print("Building RAG knowledge base...")
        
        # Extract project descriptions from award structure
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
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Fit and transform
        self.rag_knowledge_base = self.vectorizer.fit_transform(project_descriptions)
        self.project_metadata = project_metadata
        
        print(f"Built RAG knowledge base with {len(project_descriptions)} projects")
    
    def retrieve_similar_projects(self, project_description, top_k=5):
        """Retrieve similar historical projects using RAG"""
        if self.rag_knowledge_base is None or self.vectorizer is None:
            return []
        
        # Transform the query
        query_vector = self.vectorizer.transform([project_description])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.rag_knowledge_base).flatten()
        
        # Get top-k similar projects
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        similar_projects = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                similar_projects.append({
                    'metadata': self.project_metadata[idx],
                    'similarity': similarities[idx]
                })
        
        return similar_projects
    
    def query_ollama(self, prompt):
        """Query Ollama for enhanced understanding"""
        try:
            # Use subprocess to call Ollama
            result = subprocess.run([
                'ollama', 'run', 'llama3.2:latest', prompt
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Ollama query failed: {str(e)}"
    
    def enhance_project_understanding(self, project_details, bulletin_text):
        """Use Ollama to enhance project understanding"""
        
        # Create comprehensive prompt for Ollama
        prompt = f"""
        Analyze this construction project bulletin and provide insights:

        PROJECT DETAILS:
        - Job Number: {project_details.get('job_number', 'N/A')}
        - Description: {project_details.get('description', 'N/A')}
        - Region/District: {project_details.get('region_district', 'N/A')}
        - DBE Requirement: {project_details.get('dbe_requirement', 'N/A')}
        - Contract Duration: {project_details.get('contract_duration', 'N/A')}
        - Required Prequalifications: {project_details.get('prequalification_requirements', [])}
        - Personnel Requirements: {project_details.get('personnel_requirements', 'N/A')}

        BULLETIN TEXT:
        {bulletin_text[:2000]}...

        Please provide:
        1. Project complexity assessment (Low/Medium/High)
        2. Key technical challenges
        3. Recommended firm characteristics
        4. Potential risk factors
        5. Success indicators for this type of project

        Respond in a structured format.
        """
        
        ollama_response = self.query_ollama(prompt)
        return ollama_response
    
    def match_firms_to_project(self, bulletin_text, project_details):
        """Complete firm matching process for a project"""
        
        print(f"\n=== Processing Project: {project_details.get('job_number', 'Unknown')} ===")
        
        # Step 1: Extract prequalification requirements
        required_prequals = project_details.get('prequalification_requirements', [])
        print(f"Required Prequalifications: {required_prequals}")
        
        # Step 2: Get eligible firms from prequal lookup
        eligible_firm_codes = self.get_eligible_firms_by_prequalification(required_prequals)
        print(f"Eligible Firms (by prequal): {len(eligible_firm_codes)} firms")
        
        # Step 3: Filter by distance
        distance_filtered_firms = self.filter_firms_by_distance(
            eligible_firm_codes, 
            project_details.get('region_district', '')
        )
        print(f"Distance Filtered Firms: {len(distance_filtered_firms)} firms")
        
        # Step 4: Enhance with RAG
        similar_projects = self.retrieve_similar_projects(project_details.get('description', ''))
        print(f"Similar Historical Projects: {len(similar_projects)} found")
        
        # Step 5: Use Ollama for enhanced understanding
        ollama_insights = self.enhance_project_understanding(project_details, bulletin_text)
        print(f"Ollama Insights: {len(ollama_insights)} characters")
        
        return {
            'project_details': project_details,
            'eligible_firms': distance_filtered_firms,
            'similar_projects': similar_projects,
            'ollama_insights': ollama_insights
        }
    
    def predict_winners(self, matched_firms, project_details, similar_projects):
        """Predict top 5 winning firms"""
        
        if not matched_firms:
            return []
        
        # Calculate scores for each firm
        firm_scores = []
        
        for firm_info in matched_firms:
            firm_code = firm_info['firm_code']
            firm_data = firm_info['firm_data']
            distance = firm_info['distance']
            
            # Base score
            base_score = 100
            
            # Distance penalty (closer is better)
            distance_penalty = min(distance * 0.5, 25)
            
            # Capacity bonus
            capacity_bonus = 0
            if firm_data.get('capacity') == 'Large':
                capacity_bonus = 20
            elif firm_data.get('capacity') == 'Medium':
                capacity_bonus = 10
            
            # Historical performance bonus
            total_awards = firm_data.get('total_awards', 0)
            historical_bonus = min(total_awards * 2, 30)
            
            # Similar project experience bonus
            similar_project_bonus = 0
            for similar_project in similar_projects:
                if similar_project['metadata']['selected_firm'] == firm_data.get('firm_name', ''):
                    similar_project_bonus += 15
                    break
            
            # Calculate final score
            final_score = base_score - distance_penalty + capacity_bonus + historical_bonus + similar_project_bonus
            
            firm_scores.append({
                'firm_code': firm_code,
                'firm_name': firm_data.get('firm_name', ''),
                'score': final_score,
                'distance': distance,
                'capacity': firm_data.get('capacity', ''),
                'total_awards': total_awards,
                'similar_project_experience': similar_project_bonus > 0
            })
        
        # Sort by score and return top 5
        firm_scores.sort(key=lambda x: x['score'], reverse=True)
        return firm_scores[:5]
    
    def find_actual_winners(self, job_number):
        """Find actual winners from award structure"""
        actual_winners = []
        
        for award in self.award_structure:
            award_job = award.get('Job #', '')
            if award_job and self.clean_job_number(award_job) == self.clean_job_number(job_number):
                selected_firm = award.get('SELECTED FIRM', '')
                if selected_firm:
                    actual_winners.append(selected_firm)
        
        return actual_winners
    
    def clean_job_number(self, job_number):
        """Clean job number for comparison"""
        if not job_number:
            return ""
        return re.sub(r'[^A-Z0-9-]', '', job_number.upper())
    
    def calculate_accuracy(self, predictions, actual_winners):
        """Calculate prediction accuracy"""
        if not actual_winners:
            return 0.0
        
        predicted_firm_names = [pred['firm_name'] for pred in predictions]
        
        # Check if any actual winner is in top 5 predictions
        for actual_winner in actual_winners:
            if actual_winner in predicted_firm_names:
                return 1.0
        
        return 0.0
    
    def process_bulletin(self, bulletin_file):
        """Process a single bulletin file with multiple projects"""
        print(f"\nProcessing: {bulletin_file}")
        
        # Read bulletin text
        with open(bulletin_file, 'r', encoding='utf-8') as f:
            bulletin_text = f.read()
        
        # Extract all projects from bulletin
        projects = self.extract_all_projects(bulletin_text)
        
        if not projects:
            print("No projects found, skipping...")
            return None
        
        print(f"Found {len(projects)} projects in bulletin")
        
        # Process each project
        project_results = []
        for i, project in enumerate(projects, 1):
            print(f"\n--- Processing Project {i}: {project['job_number']} ---")
            
            # Extract project-specific details
            project_details = self.extract_project_details_enhanced(project['full_text'])
            
            # Combine with job header info
            complete_project_details = {
                'job_number': project['job_number'],
                'description': project['description'],
                'region_district': project['region_district'],
                'dbe_requirement': project_details['dbe_requirement'],
                'contract_duration': project_details['contract_duration'],
                'prequalification_requirements': project_details['prequalification_requirements'],
                'personnel_requirements': project_details['personnel_requirements']
            }
            
            # Match firms to project
            matching_results = self.match_firms_to_project(project['full_text'], complete_project_details)
            
            # Predict winners
            predictions = self.predict_winners(
                matching_results['eligible_firms'],
                complete_project_details,
                matching_results['similar_projects']
            )
            
            # Find actual winners
            actual_winners = self.find_actual_winners(complete_project_details['job_number'])
            
            # Calculate accuracy
            accuracy = self.calculate_accuracy(predictions, actual_winners)
            
            project_result = {
                'bulletin_file': bulletin_file,
                'project_number': i,
                'project_details': complete_project_details,
                'predictions': predictions,
                'actual_winners': actual_winners,
                'accuracy': accuracy,
                'eligible_firms_count': len(matching_results['eligible_firms']),
                'similar_projects_count': len(matching_results['similar_projects']),
                'ollama_insights': matching_results['ollama_insights']
            }
            
            project_results.append(project_result)
        
        return project_results
    
    def run_comprehensive_test(self):
        """Run comprehensive test on PTB160-170 (excluding PTB164)"""
        print("=== ENHANCED RAG + OLLAMA SYSTEM - COMPREHENSIVE TEST ===")
        
        # Load data
        self.load_data()
        
        # Build RAG knowledge base
        self.build_rag_knowledge_base()
        
        # Get bulletin files (PTB160-200, excluding PTB164)
        bulletin_files = []
        for i in range(160, 201):
            if i != 164:  # Skip PTB164
                file_pattern = f"../data/ptb{i}_docx_text.txt"
                matching_files = glob.glob(file_pattern)
                bulletin_files.extend(matching_files)
        
        print(f"Found {len(bulletin_files)} bulletin files to process")
        
        # Process each bulletin
        results = []
        total_accuracy = 0
        successful_predictions = 0
        
        for bulletin_file in sorted(bulletin_files):
            project_results = self.process_bulletin(bulletin_file)
            if project_results:
                # Add all projects from this bulletin
                for project_result in project_results:
                    results.append(project_result)
                    total_accuracy += project_result['accuracy']
                    if project_result['accuracy'] > 0:
                        successful_predictions += 1
        
        # Calculate overall metrics
        overall_accuracy = total_accuracy / len(results) if results else 0
        
        # Create comprehensive results
        comprehensive_results = {
            'overall_accuracy': overall_accuracy,
            'total_projects': len(results),
            'successful_predictions': successful_predictions,
            'results': results
        }
        
        # Export to Excel
        self.export_to_excel(comprehensive_results)
        
        # Print summary
        print(f"\n=== FINAL RESULTS ===")
        print(f"Overall Accuracy: {overall_accuracy:.1%}")
        print(f"Total Projects: {len(results)}")
        print(f"Successful Predictions: {successful_predictions}")
        print(f"Excel file exported: enhanced_rag_ollama_results.xlsx")
        
        return comprehensive_results
    
    def export_to_excel(self, results):
        """Export results to Excel with comprehensive formatting"""
        
        # Create Excel writer
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_rag_ollama_results_{timestamp}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            
            # Summary sheet
            summary_data = {
                'Metric': [
                    'Overall Accuracy',
                    'Total Projects',
                    'Successful Predictions',
                    'Success Rate',
                    'Average Eligible Firms per Project',
                    'Average Similar Projects Found'
                ],
                'Value': [
                    f"{results['overall_accuracy']:.1%}",
                    results['total_projects'],
                    results['successful_predictions'],
                    f"{results['successful_predictions']/results['total_projects']:.1%}" if results['total_projects'] > 0 else "0%",
                    f"{np.mean([r['eligible_firms_count'] for r in results['results']]):.1f}",
                    f"{np.mean([r['similar_projects_count'] for r in results['results']]):.1f}"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Detailed results sheet
            detailed_data = []
            for result in results['results']:
                project_details = result['project_details']
                
                # Get top 5 predictions
                predictions = result['predictions']
                for i, pred in enumerate(predictions, 1):
                    detailed_data.append({
                        'Bulletin File': result['bulletin_file'],
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
                        'Similar Project Experience': 'Yes' if pred['similar_project_experience'] else 'No',
                        'Actual Winners': ', '.join(result['actual_winners']),
                        'Accuracy': 'Yes' if result['accuracy'] > 0 else 'No',
                        'Eligible Firms Count': result['eligible_firms_count'],
                        'Similar Projects Count': result['similar_projects_count']
                    })
            
            detailed_df = pd.DataFrame(detailed_data)
            detailed_df.to_excel(writer, sheet_name='Detailed Results', index=False)
            
            # Ollama insights sheet
            insights_data = []
            for result in results['results']:
                insights_data.append({
                    'Bulletin File': result['bulletin_file'],
                    'Job Number': result['project_details'].get('job_number', ''),
                    'Ollama Insights': result['ollama_insights'][:500] + '...' if len(result['ollama_insights']) > 500 else result['ollama_insights']
                })
            
            insights_df = pd.DataFrame(insights_data)
            insights_df.to_excel(writer, sheet_name='Ollama Insights', index=False)
        
        print(f"Results exported to: {filename}")

def main():
    """Main function to run the enhanced RAG + Ollama system"""
    system = EnhancedRAGOllamaSystem()
    results = system.run_comprehensive_test()
    return results

if __name__ == "__main__":
    main() 