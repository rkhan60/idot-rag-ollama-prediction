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

class PTB190200Top3System:
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
        
    def extract_all_projects_from_bulletin(self, bulletin_text):
        """Extract all projects from a single bulletin"""
        projects = []
        
        # Pattern to match numbered job entries
        # This will match: "1. Job No. D-91-516-11, ..." and similar patterns
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
            
            # Extract prequalification requirements
            prequal_requirements = self.extract_prequalification_requirements(full_text)
            
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
                clean_match = match.strip()
                if clean_match and len(clean_match) > 5:
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
            if category.lower() in text.lower():
                required_prequals.append(category)
        
        return list(set(required_prequals))
    
    def get_eligible_firms_by_prequalification(self, required_prequals):
        """Get all firms eligible for the required prequalifications"""
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
                # Try fuzzy matching
                for lookup_prequal in self.prequal_lookup.keys():
                    similarity = SequenceMatcher(None, prequal.lower(), lookup_prequal.lower()).ratio()
                    if similarity > 0.8:
                        firm_data = self.prequal_lookup[lookup_prequal]
                        for firm in firm_data:
                            if isinstance(firm, dict) and 'firm_code' in firm:
                                eligible_firm_codes.add(firm['firm_code'])
                            elif isinstance(firm, str):
                                eligible_firm_codes.add(firm)
        
        return list(eligible_firm_codes)
    
    def filter_firms_by_distance(self, eligible_firm_codes, project_region_district):
        """Filter firms based on distance to project location"""
        # For now, return all eligible firms (simplified)
        filtered_firms = []
        for firm_code in eligible_firm_codes:
            firm = self.firms_data.get(firm_code, {})
            if firm:
                filtered_firms.append({
                    'firm_code': firm_code,
                    'distance': 50,  # Default distance
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
    
    def retrieve_similar_projects(self, project_description, top_k=5):
        """Retrieve similar historical projects using RAG"""
        if self.rag_knowledge_base is None or self.vectorizer is None:
            return []
        
        query_vector = self.vectorizer.transform([project_description])
        similarities = cosine_similarity(query_vector, self.rag_knowledge_base).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        similar_projects = []
        for idx in top_indices:
            if similarities[idx] > 0.1:
                similar_projects.append({
                    'metadata': self.project_metadata[idx],
                    'similarity': similarities[idx]
                })
        
        return similar_projects
    
    def predict_winners(self, matched_firms, project_details, similar_projects):
        """Predict top 3 winning firms (MODIFIED FROM TOP 5)"""
        if not matched_firms:
            return []
        
        firm_scores = []
        
        for firm_info in matched_firms:
            firm_code = firm_info['firm_code']
            firm_data = firm_info['firm_data']
            distance = firm_info['distance']
            
            # Base score
            base_score = 100
            
            # Distance penalty
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
        
        # Sort by score and return top 3 (MODIFIED FROM TOP 5)
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
            
            # Get eligible firms
            eligible_firm_codes = self.get_eligible_firms_by_prequalification(project['prequalification_requirements'])
            print(f"Required Prequalifications: {project['prequalification_requirements']}")
            print(f"Eligible Firms (by prequal): {len(eligible_firm_codes)} firms")
            
            # Filter by distance
            distance_filtered_firms = self.filter_firms_by_distance(eligible_firm_codes, project['region_district'])
            print(f"Distance Filtered Firms: {len(distance_filtered_firms)} firms")
            
            # Get similar projects
            similar_projects = self.retrieve_similar_projects(project['description'])
            print(f"Similar Historical Projects: {len(similar_projects)} found")
            
            # Predict winners (TOP 3)
            predictions = self.predict_winners(distance_filtered_firms, project, similar_projects)
            
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
                'similar_projects_count': len(similar_projects)
            }
            
            project_results.append(project_result)
            
            print(f"Accuracy: {accuracy:.1%}")
            print(f"Actual Winners: {actual_winners}")
            if predictions:
                print(f"Top Prediction: {predictions[0]['firm_name']} (Score: {predictions[0]['score']:.1f})")
                print(f"Top 3 Predictions: {[p['firm_name'] for p in predictions]}")
        
        return project_results
    
    def run_ptb190_200_top3_test(self):
        """Run test on PTB190-200 with TOP 3 predictions"""
        print("=== PTB190-200 SYSTEM - TOP 3 PREDICTIONS TEST ===")
        
        # Load data
        self.load_data()
        
        # Build RAG knowledge base
        self.build_rag_knowledge_base()
        
        # Get bulletin files (PTB190-200)
        bulletin_files = []
        for i in range(190, 201):
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
        self.export_to_excel(comprehensive_results)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"FINAL RESULTS SUMMARY - TOP 3 PREDICTIONS")
        print(f"{'='*60}")
        print(f"Total Projects Processed: {total_projects}")
        print(f"Successful Predictions: {successful_predictions}")
        print(f"Overall Accuracy: {overall_accuracy:.1%}")
        print(f"Excel file exported: ptb190_200_top3_results.xlsx")
        
        return comprehensive_results
    
    def export_to_excel(self, results):
        """Export results to Excel with comprehensive formatting"""
        
        # Create Excel writer
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../results/ptb190_200_top3_results_{timestamp}.xlsx"
        
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
                    'Theoretical Random Accuracy'
                ],
                'Value': [
                    f"{results['overall_accuracy']:.1%}",
                    results['total_projects'],
                    results['successful_predictions'],
                    f"{results['successful_predictions']/results['total_projects']:.1%}" if results['total_projects'] > 0 else "0%",
                    f"{np.mean([r['eligible_firms_count'] for r in results['results']]):.1f}",
                    f"{np.mean([r['similar_projects_count'] for r in results['results']]):.1f}",
                    "Top 3",
                    "33.3% (1/3)"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Detailed results sheet
            detailed_data = []
            for result in results['results']:
                project_details = result['project_details']
                
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
                        'Similar Project Experience': 'Yes' if pred['similar_project_experience'] else 'No',
                        'Actual Winners': ', '.join(result['actual_winners']),
                        'Accuracy': 'Yes' if result['accuracy'] > 0 else 'No',
                        'Eligible Firms Count': result['eligible_firms_count'],
                        'Similar Projects Count': result['similar_projects_count']
                    })
            
            detailed_df = pd.DataFrame(detailed_data)
            detailed_df.to_excel(writer, sheet_name='Detailed Results', index=False)
        
        print(f"Results exported to: {filename}")

def main():
    """Main function to run the PTB190-200 Top 3 system"""
    system = PTB190200Top3System()
    results = system.run_ptb190_200_top3_test()
    return results

if __name__ == "__main__":
    main() 