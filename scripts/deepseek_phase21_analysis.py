#!/usr/bin/env python3
"""
DeepSeek Analysis of Phase 2.1 System Structure
Comprehensive analysis using DeepSeek-r1:8b to identify problems and insights
"""

import subprocess
import time
import json
import os
from datetime import datetime

class DeepSeekPhase21Analyzer:
    def __init__(self):
        self.model = "deepseek-r1:8b"
        self.analysis_results = []
        
    def check_ollama_status(self):
        """Check if Ollama is running"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Ollama not available: {e}")
            return False
            
    def query_deepseek(self, prompt, timeout=60):
        """Query DeepSeek with timeout"""
        try:
            start_time = time.time()
            result = subprocess.run(
                ['ollama', 'run', self.model, prompt],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            end_time = time.time()
            
            return {
                'success': result.returncode == 0,
                'response': result.stdout.strip(),
                'error': result.stderr.strip(),
                'time': end_time - start_time
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'response': '',
                'error': f'Timeout after {timeout} seconds',
                'time': timeout
            }
        except Exception as e:
            return {
                'success': False,
                'response': '',
                'error': str(e),
                'time': 0
            }
            
    def analyze_system_structure(self):
        """Analyze the overall system structure"""
        print("🔍 Analyzing Phase 2.1 System Structure...")
        
        structure_analysis = """
        Analyze this PTB analysis system structure:

        CLASS: Phase21EnhancedSystem
        - Firms data management
        - Prequalification lookup system
        - District mapping
        - Award structure processing
        - RAG knowledge base
        - TF-IDF vectorizer
        - Temporal weights
        - Project complexity scores
        - Data quality flags

        KEY METHODS:
        1. load_data() - Loads all data files
        2. build_temporal_weights() - Builds time-based weights
        3. build_complexity_scores() - Calculates project complexity
        4. extract_all_projects_from_bulletin() - Extracts projects from text
        5. get_eligible_firms_by_prequalification_enhanced() - Filters firms
        6. calculate_phase2_score() - Calculates firm scores
        7. predict_winners() - Predicts winning firms
        8. run_test() - Runs complete test suite

        ENHANCEMENTS:
        - Enhanced prequalification synonyms
        - Geographic distance filtering
        - RAG-based similar project retrieval
        - Project type categorization
        - Data validation

        Analyze the system architecture and identify:
        1. Structural strengths
        2. Potential bottlenecks
        3. Data flow issues
        4. Scalability concerns
        5. Integration points
        6. Error handling mechanisms
        """
        
        result = self.query_deepseek(structure_analysis)
        return result
        
    def analyze_data_quality_issues(self):
        """Analyze data quality and validation issues"""
        print("🔍 Analyzing Data Quality Issues...")
        
        data_quality_analysis = """
        Analyze potential data quality issues in this PTB system:

        DATA SOURCES:
        - firms_data.json (415 firms)
        - prequal_lookup.json (prequalification categories)
        - district_mapping.json (district mappings)
        - award_structure.json (2166 award records)

        VALIDATION CHECKS:
        - validate_project_data() - Validates extracted project data
        - Data quality flags system
        - Enhanced job number normalization
        - Prequalification requirement extraction

        POTENTIAL ISSUES TO ANALYZE:
        1. Missing or inconsistent firm data
        2. Prequalification mapping errors
        3. District mapping inconsistencies
        4. Award structure data gaps
        5. Job number format variations
        6. Firm name duplications
        7. Missing subconsultant data
        8. Incomplete project descriptions

        Identify:
        1. Critical data quality problems
        2. Impact on system accuracy
        3. Root causes of data issues
        4. Recommended fixes
        5. Data validation improvements
        """
        
        result = self.query_deepseek(data_quality_analysis)
        return result
        
    def analyze_algorithm_issues(self):
        """Analyze algorithm and scoring issues"""
        print("🔍 Analyzing Algorithm Issues...")
        
        algorithm_analysis = """
        Analyze the scoring and prediction algorithms in this PTB system:

        SCORING COMPONENTS:
        - calculate_phase2_score() - Main scoring function
        - Geographic distance calculation
        - Project type similarity
        - Historical performance weights
        - RAG-based similar project analysis
        - Prequalification matching

        POTENTIAL ALGORITHM ISSUES:
        1. Scoring weight imbalances
        2. Distance calculation accuracy
        3. Similarity matching thresholds
        4. RAG knowledge base quality
        5. Project type categorization errors
        6. Historical data bias
        7. Prequalification fuzzy matching
        8. Temporal weight calculations

        ACCURACY ISSUES:
        - Current baseline: ~30.4%
        - Target: 50%+
        - Previous attempts failed to improve accuracy

        Analyze:
        1. Algorithm weaknesses
        2. Scoring formula problems
        3. RAG system issues
        4. Similarity calculation problems
        5. Weight optimization needs
        6. Prediction logic flaws
        """
        
        result = self.query_deepseek(algorithm_analysis)
        return result
        
    def analyze_extraction_issues(self):
        """Analyze project extraction issues"""
        print("🔍 Analyzing Project Extraction Issues...")
        
        extraction_analysis = """
        Analyze the project extraction process in this PTB system:

        EXTRACTION METHODS:
        - extract_all_projects_from_bulletin() - Main extraction function
        - extract_prequalification_requirements_enhanced() - Prequal extraction
        - enhanced_job_number_normalization() - Job number processing
        - Region/district extraction

        EXTRACTION PATTERNS:
        - Job number regex patterns
        - Project description parsing
        - Prequalification requirement identification
        - Region/district mapping

        POTENTIAL EXTRACTION ISSUES:
        1. Regex pattern limitations
        2. Inconsistent job number formats
        3. Missing prequalification requirements
        4. Region/district extraction errors
        5. Project description truncation
        6. Duplicate project extraction
        7. Context loss in extraction
        8. Edge case handling

        IMPACT ON ACCURACY:
        - Poor extraction leads to poor matching
        - Missing requirements affect firm eligibility
        - Incorrect regions affect distance calculations
        - Job number errors affect winner matching

        Analyze:
        1. Extraction accuracy problems
        2. Pattern matching issues
        3. Context preservation problems
        4. Edge case handling
        5. Data loss during extraction
        6. Recommended improvements
        """
        
        result = self.query_deepseek(extraction_analysis)
        return result
        
    def analyze_rag_system_issues(self):
        """Analyze RAG system issues"""
        print("🔍 Analyzing RAG System Issues...")
        
        rag_analysis = """
        Analyze the RAG (Retrieval Augmented Generation) system in this PTB analysis:

        RAG COMPONENTS:
        - build_rag_knowledge_base() - Builds TF-IDF knowledge base
        - retrieve_similar_projects_enhanced() - Retrieves similar projects
        - calculate_project_type_similarity() - Calculates project similarity
        - TF-IDF vectorizer for text similarity

        RAG PROCESS:
        1. Build knowledge base from historical projects
        2. Vectorize project descriptions
        3. Calculate cosine similarity
        4. Retrieve top-k similar projects
        5. Use similar projects for scoring

        POTENTIAL RAG ISSUES:
        1. Knowledge base quality
        2. TF-IDF vocabulary problems
        3. Similarity calculation accuracy
        4. Context relevance
        5. Historical data bias
        6. Vector space limitations
        7. Similarity threshold issues
        8. Knowledge base size limitations

        PREVIOUS ERRORS:
        - "empty vocabulary; perhaps the documents only contain stop words"
        - TF-IDF vectorizer failures
        - Similarity calculation errors

        Analyze:
        1. RAG system weaknesses
        2. Knowledge base problems
        3. Similarity calculation issues
        4. Context relevance problems
        5. Vectorization issues
        6. Recommended RAG improvements
        """
        
        result = self.query_deepseek(rag_analysis)
        return result
        
    def generate_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        print("\n📋 Generating Comprehensive Analysis Report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'deepseek_phase21_analysis_{timestamp}.txt'
        
        with open(report_file, 'w') as f:
            f.write("DEEPSEEK ANALYSIS OF PHASE 2.1 SYSTEM STRUCTURE\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("ANALYSIS OVERVIEW\n")
            f.write("-" * 20 + "\n")
            f.write(f"Model Used: {self.model}\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Analysis Areas: 5\n\n")
            
            for i, result in enumerate(self.analysis_results, 1):
                analysis_areas = [
                    "System Structure Analysis",
                    "Data Quality Issues",
                    "Algorithm Issues", 
                    "Project Extraction Issues",
                    "RAG System Issues"
                ]
                
                f.write(f"{analysis_areas[i-1].upper()}\n")
                f.write("-" * len(analysis_areas[i-1]) + "\n")
                f.write(f"Status: {'SUCCESS' if result['success'] else 'FAILED'}\n")
                f.write(f"Time: {result['time']:.1f}s\n")
                if result['success']:
                    f.write(f"Response:\n{result['response']}\n")
                else:
                    f.write(f"Error: {result['error']}\n")
                f.write("\n" + "="*60 + "\n\n")
                
        print(f"✅ Comprehensive analysis report saved: {report_file}")
        return report_file
        
    def run_complete_analysis(self):
        """Run complete Phase 2.1 analysis"""
        print("🚀 Starting DeepSeek Analysis of Phase 2.1 System...")
        
        if not self.check_ollama_status():
            print("❌ Ollama not available. Please start Ollama first.")
            return None
            
        # Run all analyses
        self.analysis_results.append(self.analyze_system_structure())
        self.analysis_results.append(self.analyze_data_quality_issues())
        self.analysis_results.append(self.analyze_algorithm_issues())
        self.analysis_results.append(self.analyze_extraction_issues())
        self.analysis_results.append(self.analyze_rag_system_issues())
        
        # Generate report
        report_file = self.generate_comprehensive_report()
        
        print(f"\n✅ DeepSeek Analysis Complete!")
        print(f"📄 Analysis Report: {report_file}")
        
        return self.analysis_results

if __name__ == "__main__":
    analyzer = DeepSeekPhase21Analyzer()
    results = analyzer.run_complete_analysis()
