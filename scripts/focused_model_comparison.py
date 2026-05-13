#!/usr/bin/env python3
"""
Focused Model Comparison: DeepSeek-r1:8b vs GPT-OSS:20b
Simplified test with shorter timeouts to avoid memory issues
"""

import subprocess
import time
import json
import pandas as pd
from datetime import datetime

class FocusedModelComparison:
    def __init__(self):
        self.models = {
            'deepseek-r1:8b': {
                'name': 'DeepSeek-r1:8b',
                'size': '5.2 GB',
                'type': 'Fast Processing'
            },
            'gpt-oss:20b': {
                'name': 'GPT-OSS:20b',
                'size': '13 GB',
                'type': 'High Accuracy'
            }
        }
        self.test_results = []
        
    def check_ollama_status(self):
        """Check if Ollama is running"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Ollama not available: {e}")
            return False
            
    def query_ollama(self, model, prompt, timeout=30):
        """Query Ollama with shorter timeout"""
        try:
            start_time = time.time()
            result = subprocess.run(
                ['ollama', 'run', model, prompt],
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
            
    def create_simple_prompt(self, project_text):
        """Create a very simple analysis prompt"""
        return f"""Briefly analyze this PTB project:

{project_text}

List the main requirements in 3-4 bullet points."""

    def create_medium_prompt(self, project_text):
        """Create a medium complexity prompt"""
        return f"""Analyze this PTB project:

{project_text}

Provide:
1. Required qualifications
2. Key personnel needs
3. Main challenges
4. Estimated complexity

Keep response under 200 words."""

    def analyze_response_quality(self, response, expected_keywords=None):
        """Analyze the quality of a response"""
        if not response:
            return 0
            
        # Basic quality metrics
        word_count = len(response.split())
        sentence_count = len([s for s in response.split('.') if s.strip()])
        
        # Check for structured response
        has_numbers = any(char.isdigit() for char in response)
        has_bullet_points = '-' in response or '•' in response or '1.' in response
        
        # Check for technical depth
        technical_terms = ['prequalified', 'certification', 'engineering', 'construction', 
                          'inspection', 'assessment', 'compliance', 'requirements']
        technical_depth = sum(1 for term in technical_terms if term.lower() in response.lower())
        
        # Check for expected keywords if provided
        keyword_match = 0
        if expected_keywords:
            for keyword in expected_keywords:
                if keyword.lower() in response.lower():
                    keyword_match += 1
            keyword_match = keyword_match / len(expected_keywords) if expected_keywords else 0
        
        # Calculate quality score (0-100)
        quality_score = 0
        quality_score += min(word_count / 5, 20)  # Word count bonus (max 20)
        quality_score += min(sentence_count * 3, 20)  # Sentence structure (max 20)
        quality_score += 10 if has_numbers else 0  # Numerical content
        quality_score += 10 if has_bullet_points else 0  # Structured format
        quality_score += min(technical_depth * 5, 20)  # Technical depth (max 20)
        quality_score += keyword_match * 20  # Keyword relevance (max 20)
        
        return min(quality_score, 100)
        
    def test_model_performance(self):
        """Test both models on simplified PTB projects"""
        print("🚀 Starting Focused Model Comparison...")
        
        # Simplified PTB projects for testing
        test_projects = [
            {
                'name': 'Highway Construction',
                'text': 'Job No. V-91-010-25, Bureau of Construction - Various Hybrid Construction Engineering, Phase III Project, Various Counties, Region One/District One. This project requires 27% DBE participation. The Prime firm must be prequalified in the Special Services (Construction Inspection) category.',
                'expected_keywords': ['construction inspection', 'DBE', 'engineering']
            },
            {
                'name': 'Environmental Assessment',
                'text': 'Job No. E-91-516-11, Environmental Assessment for Highway Project, Cook County, Region One/District One. The Prime firm must be prequalified in Environmental Reports - Environmental Assessment. Key personnel must include Environmental Engineer and Field Technicians.',
                'expected_keywords': ['environmental assessment', 'environmental engineer']
            },
            {
                'name': 'Traffic Signal Design',
                'text': 'Job No. T-91-234-08, Traffic Signal Design and Installation, DuPage County, Region One/District One. The Prime firm must be prequalified in Special Plans - Traffic Signals. Project includes design, installation, and testing of traffic control systems.',
                'expected_keywords': ['traffic signals', 'design', 'installation']
            }
        ]
        
        for i, project in enumerate(test_projects, 1):
            print(f"\n📋 Test {i}: {project['name']}")
            
            for model_name in self.models.keys():
                print(f"  🔍 Testing {model_name}...")
                
                # Test simple prompt
                simple_result = self.query_ollama(model_name, self.create_simple_prompt(project['text']), timeout=20)
                simple_quality = self.analyze_response_quality(simple_result['response'], project['expected_keywords'])
                
                # Test medium prompt
                medium_result = self.query_ollama(model_name, self.create_medium_prompt(project['text']), timeout=30)
                medium_quality = self.analyze_response_quality(medium_result['response'], project['expected_keywords'])
                
                # Store results
                test_result = {
                    'project_name': project['name'],
                    'model': model_name,
                    'model_info': self.models[model_name],
                    'simple_success': simple_result['success'],
                    'simple_time': simple_result['time'],
                    'simple_quality': simple_quality,
                    'simple_response_length': len(simple_result['response']),
                    'medium_success': medium_result['success'],
                    'medium_time': medium_result['time'],
                    'medium_quality': medium_quality,
                    'medium_response_length': len(medium_result['response']),
                    'simple_error': simple_result['error'],
                    'medium_error': medium_result['error']
                }
                
                self.test_results.append(test_result)
                
                # Print results
                print(f"    Simple: {'✅' if simple_result['success'] else '❌'} ({simple_result['time']:.1f}s, Quality: {simple_quality:.1f})")
                print(f"    Medium: {'✅' if medium_result['success'] else '❌'} ({medium_result['time']:.1f}s, Quality: {medium_quality:.1f})")
                
    def calculate_model_statistics(self):
        """Calculate comprehensive statistics for each model"""
        print("\n📊 Calculating Model Statistics...")
        
        model_stats = {}
        
        for model_name in self.models.keys():
            model_results = [r for r in self.test_results if r['model'] == model_name]
            
            if not model_results:
                continue
                
            # Success rates
            simple_success_rate = sum(1 for r in model_results if r['simple_success']) / len(model_results)
            medium_success_rate = sum(1 for r in model_results if r['medium_success']) / len(model_results)
            
            # Average times
            simple_avg_time = sum(r['simple_time'] for r in model_results) / len(model_results)
            medium_avg_time = sum(r['medium_time'] for r in model_results) / len(model_results)
            
            # Average quality scores
            simple_avg_quality = sum(r['simple_quality'] for r in model_results) / len(model_results)
            medium_avg_quality = sum(r['medium_quality'] for r in model_results) / len(model_results)
            
            # Average response lengths
            simple_avg_length = sum(r['simple_response_length'] for r in model_results) / len(model_results)
            medium_avg_length = sum(r['medium_response_length'] for r in model_results) / len(model_results)
            
            model_stats[model_name] = {
                'simple_success_rate': simple_success_rate * 100,
                'medium_success_rate': medium_success_rate * 100,
                'simple_avg_time': simple_avg_time,
                'medium_avg_time': medium_avg_time,
                'simple_avg_quality': simple_avg_quality,
                'medium_avg_quality': medium_avg_quality,
                'simple_avg_length': simple_avg_length,
                'medium_avg_length': medium_avg_length
            }
            
        return model_stats
        
    def generate_comparison_report(self):
        """Generate focused comparison report"""
        print("\n📋 Generating Focused Comparison Report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'focused_model_comparison_{timestamp}.txt'
        
        model_stats = self.calculate_model_statistics()
        
        with open(report_file, 'w') as f:
            f.write("FOCUSED MODEL COMPARISON: DEEPSEEK-R1:8B vs GPT-OSS:20B\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("MODEL SPECIFICATIONS\n")
            f.write("-" * 20 + "\n")
            for model_name, info in self.models.items():
                f.write(f"{info['name']} ({model_name}):\n")
                f.write(f"  Size: {info['size']}\n")
                f.write(f"  Type: {info['type']}\n\n")
            
            f.write("PERFORMANCE SUMMARY\n")
            f.write("-" * 20 + "\n")
            for model_name, stats in model_stats.items():
                f.write(f"\n{self.models[model_name]['name']}:\n")
                f.write(f"  Simple Success Rate: {stats['simple_success_rate']:.1f}%\n")
                f.write(f"  Medium Success Rate: {stats['medium_success_rate']:.1f}%\n")
                f.write(f"  Simple Avg Time: {stats['simple_avg_time']:.1f}s\n")
                f.write(f"  Medium Avg Time: {stats['medium_avg_time']:.1f}s\n")
                f.write(f"  Simple Avg Quality: {stats['simple_avg_quality']:.1f}/100\n")
                f.write(f"  Medium Avg Quality: {stats['medium_avg_quality']:.1f}/100\n")
            
            f.write("\nDETAILED RESULTS\n")
            f.write("-" * 15 + "\n")
            for result in self.test_results:
                f.write(f"\nProject: {result['project_name']} - {result['model']}\n")
                f.write(f"  Simple: {'SUCCESS' if result['simple_success'] else 'FAILED'} ({result['simple_time']:.1f}s, Quality: {result['simple_quality']:.1f})\n")
                f.write(f"  Medium: {'SUCCESS' if result['medium_success'] else 'FAILED'} ({result['medium_time']:.1f}s, Quality: {result['medium_quality']:.1f})\n")
                
        print(f"✅ Focused comparison report saved: {report_file}")
        return report_file
        
    def run_complete_comparison(self):
        """Run the complete focused comparison test"""
        print("🚀 Starting Focused DeepSeek-r1:8b vs GPT-OSS:20b Test...")
        
        if not self.check_ollama_status():
            print("❌ Ollama not available. Please start Ollama first.")
            return None
            
        self.test_model_performance()
        report_file = self.generate_comparison_report()
        
        print(f"\n✅ Focused Comparison Complete!")
        print(f"📄 Text Report: {report_file}")
        
        return self.test_results

if __name__ == "__main__":
    comparer = FocusedModelComparison()
    results = comparer.run_complete_comparison()
