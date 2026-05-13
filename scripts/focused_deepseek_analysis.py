#!/usr/bin/env python3
"""
Focused DeepSeek Analysis of Phase 2.1 System
Simplified analysis with shorter prompts to avoid timeouts
"""

import subprocess
import time
import json
import os
from datetime import datetime

class FocusedDeepSeekAnalyzer:
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
            
    def query_deepseek(self, prompt, timeout=30):
        """Query DeepSeek with shorter timeout"""
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
            
    def analyze_critical_issues(self):
        """Analyze the most critical issues"""
        print("🔍 Analyzing Critical Issues...")
        
        critical_analysis = """What are the top 3 critical problems in a PTB analysis system with 30% accuracy that needs 50%+ accuracy?

Focus on:
1. Data quality issues
2. Algorithm problems  
3. System bottlenecks

Keep response under 150 words."""
        
        result = self.query_deepseek(critical_analysis)
        return result
        
    def analyze_data_problems(self):
        """Analyze data quality problems"""
        print("🔍 Analyzing Data Problems...")
        
        data_analysis = """What are the main data quality issues in a system with:
- 2166 award records
- 415 firms
- 61 job format variations
- 630 missing subconsultants

List the top 3 data problems and their impact on accuracy."""
        
        result = self.query_deepseek(data_analysis)
        return result
        
    def analyze_algorithm_problems(self):
        """Analyze algorithm problems"""
        print("🔍 Analyzing Algorithm Problems...")
        
        algorithm_analysis = """What are the main algorithm problems in a scoring system that:
- Uses RAG for similar projects
- Calculates geographic distance
- Matches prequalifications
- Has 30% accuracy vs 50% target

List the top 3 algorithm issues."""
        
        result = self.query_deepseek(algorithm_analysis)
        return result
        
    def analyze_extraction_problems(self):
        """Analyze extraction problems"""
        print("🔍 Analyzing Extraction Problems...")
        
        extraction_analysis = """What are the main extraction problems in a system that:
- Extracts projects from bulletins
- Uses regex for job numbers
- Identifies prequalifications
- Maps regions/districts

List the top 3 extraction issues affecting accuracy."""
        
        result = self.query_deepseek(extraction_analysis)
        return result
        
    def analyze_rag_problems(self):
        """Analyze RAG system problems"""
        print("🔍 Analyzing RAG Problems...")
        
        rag_analysis = """What are the main RAG system problems when:
- TF-IDF vectorizer fails with "empty vocabulary"
- Similarity calculations are inaccurate
- Knowledge base quality is poor
- Context relevance is low

List the top 3 RAG issues."""
        
        result = self.query_deepseek(rag_analysis)
        return result
        
    def generate_focused_report(self):
        """Generate focused analysis report"""
        print("\n📋 Generating Focused Analysis Report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'focused_deepseek_analysis_{timestamp}.txt'
        
        with open(report_file, 'w') as f:
            f.write("FOCUSED DEEPSEEK ANALYSIS OF PHASE 2.1 SYSTEM\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("ANALYSIS OVERVIEW\n")
            f.write("-" * 20 + "\n")
            f.write(f"Model Used: {self.model}\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Analysis Areas: 5\n\n")
            
            analysis_areas = [
                "Critical Issues Analysis",
                "Data Quality Problems",
                "Algorithm Problems",
                "Extraction Problems", 
                "RAG System Problems"
            ]
            
            for i, result in enumerate(self.analysis_results):
                f.write(f"{analysis_areas[i].upper()}\n")
                f.write("-" * len(analysis_areas[i]) + "\n")
                f.write(f"Status: {'SUCCESS' if result['success'] else 'FAILED'}\n")
                f.write(f"Time: {result['time']:.1f}s\n")
                if result['success']:
                    f.write(f"Response:\n{result['response']}\n")
                else:
                    f.write(f"Error: {result['error']}\n")
                f.write("\n" + "="*50 + "\n\n")
                
        print(f"✅ Focused analysis report saved: {report_file}")
        return report_file
        
    def run_focused_analysis(self):
        """Run focused analysis"""
        print("🚀 Starting Focused DeepSeek Analysis...")
        
        if not self.check_ollama_status():
            print("❌ Ollama not available. Please start Ollama first.")
            return None
            
        # Run focused analyses
        self.analysis_results.append(self.analyze_critical_issues())
        self.analysis_results.append(self.analyze_data_problems())
        self.analysis_results.append(self.analyze_algorithm_problems())
        self.analysis_results.append(self.analyze_extraction_problems())
        self.analysis_results.append(self.analyze_rag_problems())
        
        # Generate report
        report_file = self.generate_focused_report()
        
        print(f"\n✅ Focused Analysis Complete!")
        print(f"📄 Analysis Report: {report_file}")
        
        return self.analysis_results

if __name__ == "__main__":
    analyzer = FocusedDeepSeekAnalyzer()
    results = analyzer.run_focused_analysis()
