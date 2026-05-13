#!/usr/bin/env python3
"""
DeepSeek Performance Investigation and Optimization
Analyzes timeout issues and implements solutions
"""

import subprocess
import time
import json
import psutil
import os
from datetime import datetime

class DeepSeekPerformanceInvestigator:
    def __init__(self):
        self.results = {}
        self.optimization_results = {}
        
    def check_system_resources(self):
        """Check current system resource usage"""
        print("🔍 CHECKING SYSTEM RESOURCES")
        print("=" * 50)
        
        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory Usage
        memory = psutil.virtual_memory()
        
        # Disk Usage
        disk = psutil.disk_usage('/')
        
        print(f"CPU Usage: {cpu_percent}% ({cpu_count} cores)")
        print(f"Memory Usage: {memory.percent}% ({memory.used / 1024**3:.1f}GB / {memory.total / 1024**3:.1f}GB)")
        print(f"Disk Usage: {disk.percent}% ({disk.used / 1024**3:.1f}GB / {disk.total / 1024**3:.1f}GB)")
        
        return {
            'cpu_percent': cpu_percent,
            'cpu_count': cpu_count,
            'memory_percent': memory.percent,
            'memory_used_gb': memory.used / 1024**3,
            'memory_total_gb': memory.total / 1024**3,
            'disk_percent': disk.percent
        }
    
    def test_prompt_complexity(self, model="deepseek-r1:8b"):
        """Test different prompt complexities to identify timeout causes"""
        print(f"\n🧪 TESTING PROMPT COMPLEXITY WITH {model}")
        print("=" * 50)
        
        # Simple prompt
        simple_prompt = "Analyze this PTB project briefly."
        
        # Medium prompt
        medium_prompt = """
        Analyze the PTB analysis system with focus on:
        1. Data quality assessment
        2. System performance
        3. Prediction accuracy
        Provide brief insights.
        """
        
        # Complex prompt (original)
        complex_prompt = """
        Analyze the PTB analysis system for PTB180-190 with focus on:
        
        1. DATA QUALITY ASSESSMENT:
        - Evaluate accuracy of firm matching
        - Check prequalification mapping precision
        - Assess district assignment accuracy
        
        2. SYSTEM PERFORMANCE:
        - Identify processing bottlenecks
        - Evaluate response times
        - Check resource utilization
        
        3. PREDICTION ACCURACY:
        - Analyze win prediction success rate
        - Evaluate firm ranking accuracy
        - Assess confidence scoring
        
        4. PROCESS OPTIMIZATION:
        - Identify workflow inefficiencies
        - Suggest automation opportunities
        - Recommend data pipeline improvements
        
        Provide specific, actionable insights for improving prediction accuracy.
        """
        
        prompts = [
            ("Simple", simple_prompt),
            ("Medium", medium_prompt),
            ("Complex", complex_prompt)
        ]
        
        results = {}
        
        for prompt_type, prompt in prompts:
            print(f"\nTesting {prompt_type} prompt...")
            
            start_time = time.time()
            try:
                cmd = f'echo "{prompt}" | ollama run {model}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                end_time = time.time()
                
                processing_time = end_time - start_time
                success = result.returncode == 0
                response_length = len(result.stdout.strip())
                
                print(f"  ✅ Success: {success}")
                print(f"  ⏱️  Time: {processing_time:.2f}s")
                print(f"  📝 Response Length: {response_length} characters")
                
                results[prompt_type] = {
                    'success': success,
                    'processing_time': processing_time,
                    'response_length': response_length,
                    'response': result.stdout.strip()[:200] + "..." if len(result.stdout.strip()) > 200 else result.stdout.strip()
                }
                
            except subprocess.TimeoutExpired:
                print(f"  ❌ TIMEOUT after 30s")
                results[prompt_type] = {
                    'success': False,
                    'processing_time': 30.0,
                    'response_length': 0,
                    'response': 'TIMEOUT'
                }
            except Exception as e:
                print(f"  ❌ ERROR: {str(e)}")
                results[prompt_type] = {
                    'success': False,
                    'processing_time': 0,
                    'response_length': 0,
                    'response': f'ERROR: {str(e)}'
                }
        
        return results
    
    def test_model_comparison(self):
        """Compare performance between different models"""
        print(f"\n🔄 COMPARING MODEL PERFORMANCE")
        print("=" * 50)
        
        models = ["deepseek-r1:8b", "deepseek-coder:latest", "llama2:13b"]
        test_prompt = "Briefly analyze this PTB project and provide 3 key insights."
        
        results = {}
        
        for model in models:
            print(f"\nTesting {model}...")
            
            start_time = time.time()
            try:
                cmd = f'echo "{test_prompt}" | ollama run {model}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=45)
                end_time = time.time()
                
                processing_time = end_time - start_time
                success = result.returncode == 0
                response_length = len(result.stdout.strip())
                
                print(f"  ✅ Success: {success}")
                print(f"  ⏱️  Time: {processing_time:.2f}s")
                print(f"  📝 Response Length: {response_length} characters")
                
                results[model] = {
                    'success': success,
                    'processing_time': processing_time,
                    'response_length': response_length,
                    'response': result.stdout.strip()[:200] + "..." if len(result.stdout.strip()) > 200 else result.stdout.strip()
                }
                
            except subprocess.TimeoutExpired:
                print(f"  ❌ TIMEOUT after 45s")
                results[model] = {
                    'success': False,
                    'processing_time': 45.0,
                    'response_length': 0,
                    'response': 'TIMEOUT'
                }
            except Exception as e:
                print(f"  ❌ ERROR: {str(e)}")
                results[model] = {
                    'success': False,
                    'processing_time': 0,
                    'response_length': 0,
                    'response': f'ERROR: {str(e)}'
                }
        
        return results
    
    def test_optimization_strategies(self):
        """Test different optimization strategies"""
        print(f"\n⚡ TESTING OPTIMIZATION STRATEGIES")
        print("=" * 50)
        
        strategies = {
            "Chunked_Prompt": "Analyze this PTB project. Focus on: 1) Data quality 2) Performance 3) Accuracy",
            "Shorter_Timeout": "Brief PTB analysis with key insights",
            "Simplified_Query": "What are the main issues in PTB analysis?",
            "Structured_Output": "Provide 3 bullet points about PTB optimization"
        }
        
        results = {}
        
        for strategy, prompt in strategies.items():
            print(f"\nTesting {strategy}...")
            
            start_time = time.time()
            try:
                cmd = f'echo "{prompt}" | ollama run deepseek-coder:latest'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
                end_time = time.time()
                
                processing_time = end_time - start_time
                success = result.returncode == 0
                response_length = len(result.stdout.strip())
                
                print(f"  ✅ Success: {success}")
                print(f"  ⏱️  Time: {processing_time:.2f}s")
                print(f"  📝 Response Length: {response_length} characters")
                
                results[strategy] = {
                    'success': success,
                    'processing_time': processing_time,
                    'response_length': response_length,
                    'response': result.stdout.strip()[:200] + "..." if len(result.stdout.strip()) > 200 else result.stdout.strip()
                }
                
            except subprocess.TimeoutExpired:
                print(f"  ❌ TIMEOUT after 20s")
                results[strategy] = {
                    'success': False,
                    'processing_time': 20.0,
                    'response_length': 0,
                    'response': 'TIMEOUT'
                }
            except Exception as e:
                print(f"  ❌ ERROR: {str(e)}")
                results[strategy] = {
                    'success': False,
                    'processing_time': 0,
                    'response_length': 0,
                    'response': f'ERROR: {str(e)}'
                }
        
        return results
    
    def generate_optimization_report(self):
        """Generate comprehensive optimization report"""
        print(f"\n📊 GENERATING OPTIMIZATION REPORT")
        print("=" * 50)
        
        # Collect all results
        system_resources = self.check_system_resources()
        prompt_complexity = self.test_prompt_complexity()
        model_comparison = self.test_model_comparison()
        optimization_strategies = self.test_optimization_strategies()
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_resources': system_resources,
            'prompt_complexity_analysis': prompt_complexity,
            'model_comparison': model_comparison,
            'optimization_strategies': optimization_strategies,
            'recommendations': self.generate_recommendations(system_resources, prompt_complexity, model_comparison, optimization_strategies)
        }
        
        # Save report
        report_filename = f"deepseek_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Optimization report saved: {report_filename}")
        return report
    
    def generate_recommendations(self, system_resources, prompt_complexity, model_comparison, optimization_strategies):
        """Generate specific recommendations based on analysis"""
        recommendations = {
            'immediate_actions': [],
            'model_selection': {},
            'prompt_optimization': {},
            'system_optimization': {}
        }
        
        # Analyze model performance
        successful_models = [model for model, data in model_comparison.items() if data['success']]
        fastest_model = min(successful_models, key=lambda x: model_comparison[x]['processing_time']) if successful_models else None
        
        if fastest_model:
            recommendations['model_selection'] = {
                'recommended_model': fastest_model,
                'reason': f"Fastest successful model with {model_comparison[fastest_model]['processing_time']:.2f}s response time"
            }
        
        # Analyze prompt complexity
        if 'Simple' in prompt_complexity and prompt_complexity['Simple']['success']:
            recommendations['prompt_optimization'] = {
                'strategy': 'Use shorter, focused prompts',
                'expected_improvement': f"Reduce processing time from {prompt_complexity.get('Complex', {}).get('processing_time', 'N/A')}s to {prompt_complexity['Simple']['processing_time']:.2f}s"
            }
        
        # System recommendations
        if system_resources['cpu_percent'] > 80:
            recommendations['system_optimization']['cpu'] = "High CPU usage detected. Consider reducing concurrent processes."
        
        if system_resources['memory_percent'] > 80:
            recommendations['system_optimization']['memory'] = "High memory usage detected. Consider closing unnecessary applications."
        
        # Immediate actions
        recommendations['immediate_actions'] = [
            f"Use {fastest_model} for optimal performance" if fastest_model else "Test different models for best performance",
            "Implement shorter, focused prompts",
            "Add timeout handling with fallback models",
            "Monitor system resources during processing"
        ]
        
        return recommendations

def main():
    """Main execution function"""
    print("🔍 DEEPSEEK PERFORMANCE INVESTIGATION")
    print("=" * 60)
    
    investigator = DeepSeekPerformanceInvestigator()
    report = investigator.generate_optimization_report()
    
    print("\n🎯 INVESTIGATION COMPLETE!")
    print("=" * 60)
    print("📋 Check the generated report for detailed analysis and recommendations.")
    
    # Print key findings
    if 'recommendations' in report:
        print("\n🚀 KEY RECOMMENDATIONS:")
        for action in report['recommendations'].get('immediate_actions', []):
            print(f"  • {action}")

if __name__ == "__main__":
    main()





