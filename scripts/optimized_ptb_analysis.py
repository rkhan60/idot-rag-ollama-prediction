#!/usr/bin/env python3
"""
Optimized PTB Analysis System
Implements immediate optimizations from DeepSeek analysis
"""

import json
import subprocess
import time
import pandas as pd
from datetime import datetime
import os

class OptimizedPTBAnalysis:
    def __init__(self):
        self.results = {}
        self.optimization_config = {
            'primary_model': 'deepseek-coder:latest',
            'fallback_model': 'llama2:13b',
            'timeout_primary': 30,
            'timeout_fallback': 45,
            'max_retries': 2,
            'chunk_size': 1000  # characters per prompt chunk
        }
        
    def query_model_with_fallback(self, prompt, model=None, timeout=None):
        """Query model with automatic fallback on timeout"""
        if model is None:
            model = self.optimization_config['primary_model']
        if timeout is None:
            timeout = self.optimization_config['timeout_primary']
        
        print(f"🔍 Querying {model} (timeout: {timeout}s)...")
        
        try:
            cmd = f'echo "{prompt}" | ollama run {model}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'model': model,
                    'response': result.stdout.strip(),
                    'processing_time': 0  # Will be set by caller
                }
            else:
                raise Exception(f"Model returned error code: {result.returncode}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {model} timed out, trying fallback...")
            return self.try_fallback_model(prompt)
        except Exception as e:
            print(f"❌ {model} failed: {str(e)}, trying fallback...")
            return self.try_fallback_model(prompt)
    
    def try_fallback_model(self, prompt):
        """Try fallback model if primary fails"""
        fallback_model = self.optimization_config['fallback_model']
        fallback_timeout = self.optimization_config['timeout_fallback']
        
        print(f"🔄 Trying fallback: {fallback_model}")
        
        try:
            cmd = f'echo "{prompt}" | ollama run {fallback_model}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=fallback_timeout)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'model': fallback_model,
                    'response': result.stdout.strip(),
                    'processing_time': 0  # Will be set by caller
                }
            else:
                return {
                    'success': False,
                    'model': fallback_model,
                    'response': f"Fallback model failed with error code: {result.returncode}",
                    'processing_time': 0
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'model': fallback_model,
                'response': f"Fallback model timed out after {fallback_timeout}s",
                'processing_time': fallback_timeout
            }
        except Exception as e:
            return {
                'success': False,
                'model': fallback_model,
                'response': f"Fallback model error: {str(e)}",
                'processing_time': 0
            }
    
    def optimize_prompt(self, original_prompt):
        """Optimize prompt for better performance"""
        # Split complex prompts into smaller chunks
        if len(original_prompt) > self.optimization_config['chunk_size']:
            return self.chunk_prompt(original_prompt)
        
        # Simplify complex prompts
        simplified_prompt = self.simplify_prompt(original_prompt)
        return simplified_prompt
    
    def chunk_prompt(self, prompt):
        """Split long prompts into manageable chunks"""
        words = prompt.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > self.optimization_config['chunk_size']:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def simplify_prompt(self, prompt):
        """Simplify complex prompts for faster processing"""
        # Remove excessive formatting and instructions
        simplified = prompt.replace('\n\n', '\n')
        simplified = simplified.replace('  ', ' ')
        
        # Focus on key points
        if 'DATA QUALITY ASSESSMENT' in simplified:
            simplified = simplified.replace('DATA QUALITY ASSESSMENT:', 'Data Quality:')
        if 'SYSTEM PERFORMANCE' in simplified:
            simplified = simplified.replace('SYSTEM PERFORMANCE:', 'Performance:')
        if 'PREDICTION ACCURACY' in simplified:
            simplified = simplified.replace('PREDICTION ACCURACY:', 'Accuracy:')
        if 'PROCESS OPTIMIZATION' in simplified:
            simplified = simplified.replace('PROCESS OPTIMIZATION:', 'Optimization:')
        
        return simplified
    
    def run_optimized_ptb_test(self, ptb_range, test_number):
        """Run optimized PTB test with improved performance"""
        print(f"\n🚀 Running Optimized Test {test_number}: {ptb_range}")
        print("=" * 60)
        
        # Create optimized prompt
        original_prompt = f"""
        Analyze the PTB analysis system for {ptb_range} with focus on:
        
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
        
        optimized_prompt = self.optimize_prompt(original_prompt)
        
        # Handle chunked prompts
        if isinstance(optimized_prompt, list):
            print(f"📝 Processing {len(optimized_prompt)} prompt chunks...")
            responses = []
            
            for i, chunk in enumerate(optimized_prompt):
                print(f"  Processing chunk {i+1}/{len(optimized_prompt)}...")
                start_time = time.time()
                result = self.query_model_with_fallback(chunk)
                end_time = time.time()
                
                result['processing_time'] = end_time - start_time
                result['chunk_number'] = i + 1
                responses.append(result)
            
            # Combine responses
            combined_response = "\n\n".join([r['response'] for r in responses if r['success']])
            total_time = sum(r['processing_time'] for r in responses)
            
            final_result = {
                'ptb_range': ptb_range,
                'test_number': test_number,
                'success': any(r['success'] for r in responses),
                'model': responses[0]['model'] if responses else 'unknown',
                'response': combined_response,
                'processing_time': total_time,
                'chunks_processed': len(responses),
                'timestamp': datetime.now().isoformat()
            }
        else:
            # Single optimized prompt
            print("📝 Processing optimized prompt...")
            start_time = time.time()
            result = self.query_model_with_fallback(optimized_prompt)
            end_time = time.time()
            
            result['processing_time'] = end_time - start_time
            result['ptb_range'] = ptb_range
            result['test_number'] = test_number
            result['timestamp'] = datetime.now().isoformat()
            
            final_result = result
        
        # Print results
        print(f"✅ Test completed in {final_result['processing_time']:.2f}s")
        print(f"🎯 Model used: {final_result['model']}")
        print(f"📊 Success: {final_result['success']}")
        
        return final_result
    
    def run_comprehensive_optimized_tests(self):
        """Run comprehensive optimized tests"""
        print("🎯 STARTING OPTIMIZED PTB ANALYSIS")
        print("=" * 80)
        
        test_results = []
        
        # Test Set 1: PTB180-190 (3 tests)
        print("\n📊 OPTIMIZED TEST SET 1: PTB180-190 ANALYSIS")
        for i in range(1, 4):
            result = self.run_optimized_ptb_test("PTB180-190", i)
            test_results.append(result)
            time.sleep(1)  # Brief pause between tests
        
        # Test Set 2: PTB190-200 (3 tests)
        print("\n📊 OPTIMIZED TEST SET 2: PTB190-200 ANALYSIS")
        for i in range(1, 4):
            result = self.run_optimized_ptb_test("PTB190-200", i)
            test_results.append(result)
            time.sleep(1)
        
        # Test Set 3: PTB217 (3 tests)
        print("\n📊 OPTIMIZED TEST SET 3: PTB217 ANALYSIS")
        for i in range(1, 4):
            result = self.run_optimized_ptb_test("PTB217", i)
            test_results.append(result)
            time.sleep(1)
        
        return test_results
    
    def generate_performance_comparison(self, original_results, optimized_results):
        """Compare performance between original and optimized tests"""
        print("\n📊 PERFORMANCE COMPARISON")
        print("=" * 60)
        
        # Calculate statistics
        original_times = [r.get('processing_time', 0) for r in original_results]
        optimized_times = [r.get('processing_time', 0) for r in optimized_results]
        
        original_success_rate = sum(1 for r in original_results if r.get('success', False)) / len(original_results) * 100
        optimized_success_rate = sum(1 for r in optimized_results if r.get('success', False)) / len(optimized_results) * 100
        
        original_avg_time = sum(original_times) / len(original_times) if original_times else 0
        optimized_avg_time = sum(optimized_times) / len(optimized_times) if optimized_times else 0
        
        improvement_percentage = ((original_avg_time - optimized_avg_time) / original_avg_time * 100) if original_avg_time > 0 else 0
        
        comparison = {
            'original': {
                'total_tests': len(original_results),
                'success_rate': original_success_rate,
                'average_time': original_avg_time,
                'total_time': sum(original_times)
            },
            'optimized': {
                'total_tests': len(optimized_results),
                'success_rate': optimized_success_rate,
                'average_time': optimized_avg_time,
                'total_time': sum(optimized_times)
            },
            'improvement': {
                'time_reduction_percentage': improvement_percentage,
                'success_rate_improvement': optimized_success_rate - original_success_rate,
                'total_time_saved': sum(original_times) - sum(optimized_times)
            }
        }
        
        print(f"📈 ORIGINAL PERFORMANCE:")
        print(f"  • Success Rate: {original_success_rate:.1f}%")
        print(f"  • Average Time: {original_avg_time:.2f}s")
        print(f"  • Total Time: {sum(original_times):.2f}s")
        
        print(f"\n🚀 OPTIMIZED PERFORMANCE:")
        print(f"  • Success Rate: {optimized_success_rate:.1f}%")
        print(f"  • Average Time: {optimized_avg_time:.2f}s")
        print(f"  • Total Time: {sum(optimized_times):.2f}s")
        
        print(f"\n🎯 IMPROVEMENTS:")
        print(f"  • Time Reduction: {improvement_percentage:.1f}%")
        print(f"  • Success Rate Improvement: {optimized_success_rate - original_success_rate:.1f}%")
        print(f"  • Total Time Saved: {sum(original_times) - sum(optimized_times):.2f}s")
        
        return comparison
    
    def save_optimized_results(self, test_results, comparison):
        """Save optimized results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save test results
        results_filename = f"optimized_ptb_results_{timestamp}.json"
        with open(results_filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'test_results': test_results,
                'performance_comparison': comparison,
                'optimization_config': self.optimization_config
            }, f, indent=2)
        
        # Create Excel report
        excel_filename = f"optimized_ptb_analysis_{timestamp}.xlsx"
        
        # Prepare data for Excel
        test_data = []
        for result in test_results:
            test_data.append({
                'PTB_Range': result.get('ptb_range', ''),
                'Test_Number': result.get('test_number', ''),
                'Success': result.get('success', False),
                'Model_Used': result.get('model', ''),
                'Processing_Time': result.get('processing_time', 0),
                'Chunks_Processed': result.get('chunks_processed', 1),
                'Timestamp': result.get('timestamp', '')
            })
        
        df = pd.DataFrame(test_data)
        
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Test_Results', index=False)
            
            # Add performance comparison
            comparison_data = {
                'Metric': ['Total Tests', 'Success Rate (%)', 'Average Time (s)', 'Total Time (s)'],
                'Original': [
                    comparison['original']['total_tests'],
                    comparison['original']['success_rate'],
                    comparison['original']['average_time'],
                    comparison['original']['total_time']
                ],
                'Optimized': [
                    comparison['optimized']['total_tests'],
                    comparison['optimized']['success_rate'],
                    comparison['optimized']['average_time'],
                    comparison['optimized']['total_time']
                ],
                'Improvement': [
                    'N/A',
                    f"{comparison['improvement']['success_rate_improvement']:.1f}%",
                    f"{comparison['improvement']['time_reduction_percentage']:.1f}%",
                    f"{comparison['improvement']['total_time_saved']:.2f}s"
                ]
            }
            
            comparison_df = pd.DataFrame(comparison_data)
            comparison_df.to_excel(writer, sheet_name='Performance_Comparison', index=False)
        
        print(f"\n✅ Results saved:")
        print(f"  📄 JSON: {results_filename}")
        print(f"  📊 Excel: {excel_filename}")
        
        return results_filename, excel_filename

def main():
    """Main execution function"""
    print("🚀 OPTIMIZED PTB ANALYSIS SYSTEM")
    print("=" * 80)
    
    # Load original results for comparison
    original_results = []
    try:
        with open('comprehensive_analysis_report_20250812_094109.md', 'r') as f:
            # Extract test results from the markdown file
            # This is a simplified approach - in practice, you'd parse the actual results
            original_results = [
                {'processing_time': 60.01, 'success': False},  # Test 1
                {'processing_time': 12.40, 'success': True},   # Test 2
                {'processing_time': 60.01, 'success': False},  # Test 3
                {'processing_time': 5.40, 'success': True},    # Test 4
                {'processing_time': 60.01, 'success': False},  # Test 5
                {'processing_time': 60.01, 'success': False},  # Test 6
                {'processing_time': 60.01, 'success': False},  # Test 7
                {'processing_time': 6.71, 'success': True},    # Test 8
                {'processing_time': 60.01, 'success': False}   # Test 9
            ]
    except:
        print("⚠️  Could not load original results for comparison")
    
    # Run optimized analysis
    analyzer = OptimizedPTBAnalysis()
    optimized_results = analyzer.run_comprehensive_optimized_tests()
    
    # Compare performance
    if original_results:
        comparison = analyzer.generate_performance_comparison(original_results, optimized_results)
    else:
        comparison = None
    
    # Save results
    json_file, excel_file = analyzer.save_optimized_results(optimized_results, comparison)
    
    print("\n🎉 OPTIMIZED ANALYSIS COMPLETE!")
    print("=" * 80)
    print("📋 Check the generated files for detailed results and performance improvements.")

if __name__ == "__main__":
    main()





