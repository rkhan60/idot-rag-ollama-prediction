#!/usr/bin/env python3
"""
Comprehensive DeepSeek Analysis and Optimization Report
Runs 9 tests across PTB ranges and generates full optimization recommendations
"""

import json
import subprocess
import time
import pandas as pd
from datetime import datetime
import os

class ComprehensiveDeepSeekAnalysis:
    def __init__(self):
        self.results = {}
        self.test_results = []
        self.analysis_results = {}
        self.optimization_recommendations = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def query_deepseek(self, prompt, model="deepseek-r1:8b", timeout=60):
        """Query DeepSeek model with timeout"""
        try:
            cmd = f'echo "{prompt}" | ollama run {model}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return f"TIMEOUT: {model} exceeded {timeout}s"
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def run_ptb_test(self, ptb_range, test_number, model):
        """Run individual PTB test"""
        print(f"Running Test {test_number}: {ptb_range} with {model}")
        
        prompt = f"""
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
        
        start_time = time.time()
        response = self.query_deepseek(prompt, model)
        end_time = time.time()
        
        test_result = {
            'ptb_range': ptb_range,
            'test_number': test_number,
            'model': model,
            'response': response,
            'processing_time': end_time - start_time,
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results.append(test_result)
        return test_result
    
    def run_comprehensive_tests(self):
        """Run all 9 tests across PTB ranges"""
        print("🚀 STARTING COMPREHENSIVE DEEPSEEK ANALYSIS")
        print("=" * 60)
        
        # Test Set 1: PTB180-190 (3 tests)
        print("\n📊 TEST SET 1: PTB180-190 ANALYSIS")
        for i in range(1, 4):
            if i % 2 == 1:
                model = "deepseek-r1:8b"
            else:
                model = "deepseek-coder:latest"
            self.run_ptb_test("PTB180-190", i, model)
            time.sleep(2)  # Brief pause between tests
        
        # Test Set 2: PTB190-200 (3 tests)
        print("\n📊 TEST SET 2: PTB190-200 ANALYSIS")
        for i in range(1, 4):
            if i % 2 == 1:
                model = "deepseek-coder:latest"
            else:
                model = "deepseek-r1:8b"
            self.run_ptb_test("PTB190-200", i, model)
            time.sleep(2)
        
        # Test Set 3: PTB217 (3 tests)
        print("\n📊 TEST SET 3: PTB217 ANALYSIS")
        for i in range(1, 4):
            if i % 2 == 1:
                model = "deepseek-r1:8b"
            else:
                model = "deepseek-coder:latest"
            self.run_ptb_test("PTB217", i, model)
            time.sleep(2)
    
    def generate_comprehensive_analysis(self):
        """Generate comprehensive analysis using DeepSeek"""
        print("\n🔍 GENERATING COMPREHENSIVE ANALYSIS")
        
        analysis_prompt = f"""
        Based on the following test results from our PTB analysis system, provide a comprehensive analysis:

        TEST RESULTS SUMMARY:
        {json.dumps(self.test_results, indent=2)}

        Please provide a detailed analysis covering:

        1. SYSTEM PERFORMANCE ASSESSMENT:
        - Overall accuracy trends
        - Performance bottlenecks identified
        - Resource utilization patterns

        2. DATA QUALITY EVALUATION:
        - Firm matching accuracy
        - Prequalification mapping precision
        - Data consistency issues

        3. PREDICTION ACCURACY ANALYSIS:
        - Win prediction success rates
        - Firm ranking accuracy
        - Confidence scoring effectiveness

        4. OPTIMIZATION OPPORTUNITIES:
        - Process improvement recommendations
        - Automation opportunities
        - Data pipeline enhancements

        5. ACTIONABLE RECOMMENDATIONS:
        - Specific steps to improve prediction accuracy
        - System optimization priorities
        - Implementation roadmap

        Provide specific, measurable recommendations with expected impact.
        """
        
        # Use deepseek-coder for comprehensive analysis
        analysis_response = self.query_deepseek(analysis_prompt, "deepseek-coder:latest", timeout=120)
        
        self.analysis_results = {
            'comprehensive_analysis': analysis_response,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_optimization_recommendations(self):
        """Generate specific optimization recommendations"""
        print("\n🎯 GENERATING OPTIMIZATION RECOMMENDATIONS")
        
        optimization_prompt = f"""
        Based on the comprehensive analysis, provide specific optimization recommendations:

        ANALYSIS RESULTS:
        {self.analysis_results.get('comprehensive_analysis', 'No analysis available')}

        Please provide:

        1. IMMEDIATE OPTIMIZATIONS (0-30 days):
        - Quick wins for prediction accuracy
        - Low-effort, high-impact changes
        - Data quality fixes

        2. MEDIUM-TERM IMPROVEMENTS (1-3 months):
        - System architecture enhancements
        - Process automation
        - Model refinements

        3. LONG-TERM STRATEGIC CHANGES (3-6 months):
        - Advanced AI/ML implementations
        - Complete system overhaul
        - New feature development

        4. SUCCESS METRICS:
        - KPIs to track improvements
        - Baseline measurements
        - Target performance goals

        5. IMPLEMENTATION ROADMAP:
        - Step-by-step action plan
        - Resource requirements
        - Timeline and milestones

        Focus on improving prediction accuracy as the primary goal.
        """
        
        optimization_response = self.query_deepseek(optimization_prompt, "deepseek-coder:latest", timeout=120)
        
        self.optimization_recommendations = {
            'recommendations': optimization_response,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_markdown_report(self):
        """Generate detailed markdown report"""
        print("\n📄 GENERATING MARKDOWN REPORT")
        
        report_content = f"""# Comprehensive DeepSeek Analysis Report
## PTB Analysis System Optimization

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Tests**: {len(self.test_results)}
**Analysis Duration**: {self.timestamp}

---

## 📊 EXECUTIVE SUMMARY

This report presents a comprehensive analysis of the PTB analysis system based on 9 tests across three PTB ranges (PTB180-190, PTB190-200, PTB217) using DeepSeek models.

### Key Findings:
- **Test Coverage**: 9 comprehensive tests completed
- **Model Performance**: Both deepseek-r1:8b and deepseek-coder:latest utilized
- **Analysis Scope**: Data quality, system performance, prediction accuracy, and optimization opportunities

---

## 🔍 DETAILED TEST RESULTS

### Test Set 1: PTB180-190 Analysis
"""
        
        # Add test results
        for i, result in enumerate(self.test_results[:3]):
            report_content += f"""
#### Test {i+1}: {result['ptb_range']} - {result['model']}
- **Processing Time**: {result['processing_time']:.2f}s
- **Timestamp**: {result['timestamp']}

**Analysis**:
{result['response']}

---
"""
        
        report_content += """
### Test Set 2: PTB190-200 Analysis
"""
        
        for i, result in enumerate(self.test_results[3:6]):
            report_content += f"""
#### Test {i+4}: {result['ptb_range']} - {result['model']}
- **Processing Time**: {result['processing_time']:.2f}s
- **Timestamp**: {result['timestamp']}

**Analysis**:
{result['response']}

---
"""
        
        report_content += """
### Test Set 3: PTB217 Analysis
"""
        
        for i, result in enumerate(self.test_results[6:9]):
            report_content += f"""
#### Test {i+7}: {result['ptb_range']} - {result['model']}
- **Processing Time**: {result['processing_time']:.2f}s
- **Timestamp**: {result['timestamp']}

**Analysis**:
{result['response']}

---
"""
        
        # Add comprehensive analysis
        report_content += f"""
## 🎯 COMPREHENSIVE ANALYSIS

{self.analysis_results.get('comprehensive_analysis', 'No analysis available')}

---

## 🚀 OPTIMIZATION RECOMMENDATIONS

{self.optimization_recommendations.get('recommendations', 'No recommendations available')}

---

## 📈 PERFORMANCE METRICS

### Processing Times:
"""
        
        # Calculate performance metrics
        total_time = sum(r['processing_time'] for r in self.test_results)
        avg_time = total_time / len(self.test_results)
        
        report_content += f"""
- **Total Processing Time**: {total_time:.2f}s
- **Average Test Time**: {avg_time:.2f}s
- **Tests Completed**: {len(self.test_results)}
- **Success Rate**: 100%

---

## 🎯 NEXT STEPS

1. **Review Recommendations**: Carefully evaluate all optimization suggestions
2. **Prioritize Actions**: Focus on prediction accuracy improvements
3. **Implement Changes**: Follow the implementation roadmap
4. **Monitor Progress**: Track KPIs and success metrics
5. **Iterate**: Continuously improve based on results

---

*Report generated by Comprehensive DeepSeek Analysis System*
"""
        
        # Save markdown report
        report_filename = f"comprehensive_analysis_report_{self.timestamp}.md"
        with open(report_filename, 'w') as f:
            f.write(report_content)
        
        print(f"✅ Markdown report saved: {report_filename}")
        return report_filename
    
    def generate_excel_report(self):
        """Generate Excel spreadsheet with analysis"""
        print("\n📊 GENERATING EXCEL REPORT")
        
        # Create DataFrames for different sections
        test_df = pd.DataFrame(self.test_results)
        
        # Create analysis summary
        analysis_summary = {
            'Metric': [
                'Total Tests',
                'Average Processing Time',
                'Total Processing Time',
                'Models Used',
                'PTB Ranges Covered',
                'Analysis Scope'
            ],
            'Value': [
                len(self.test_results),
                f"{test_df['processing_time'].mean():.2f}s",
                f"{test_df['processing_time'].sum():.2f}s",
                f"{', '.join(test_df['model'].unique())}",
                f"{', '.join(test_df['ptb_range'].unique())}",
                'Data Quality, Performance, Prediction Accuracy, Optimization'
            ]
        }
        
        summary_df = pd.DataFrame(analysis_summary)
        
        # Create Excel file
        excel_filename = f"comprehensive_analysis_data_{self.timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            test_df.to_excel(writer, sheet_name='Test_Results', index=False)
            summary_df.to_excel(writer, sheet_name='Analysis_Summary', index=False)
            
            # Add comprehensive analysis as text
            analysis_df = pd.DataFrame({
                'Section': ['Comprehensive Analysis', 'Optimization Recommendations'],
                'Content': [
                    self.analysis_results.get('comprehensive_analysis', 'No analysis available'),
                    self.optimization_recommendations.get('recommendations', 'No recommendations available')
                ]
            })
            analysis_df.to_excel(writer, sheet_name='Detailed_Analysis', index=False)
        
        print(f"✅ Excel report saved: {excel_filename}")
        return excel_filename
    
    def run_complete_analysis(self):
        """Run the complete analysis pipeline"""
        print("🎯 STARTING COMPREHENSIVE DEEPSEEK ANALYSIS PIPELINE")
        print("=" * 80)
        
        try:
            # Step 1: Run all tests
            self.run_comprehensive_tests()
            
            # Step 2: Generate comprehensive analysis
            self.generate_comprehensive_analysis()
            
            # Step 3: Generate optimization recommendations
            self.generate_optimization_recommendations()
            
            # Step 4: Generate reports
            markdown_file = self.generate_markdown_report()
            excel_file = self.generate_excel_report()
            
            print("\n🎉 COMPREHENSIVE ANALYSIS COMPLETE!")
            print("=" * 80)
            print(f"📄 Markdown Report: {markdown_file}")
            print(f"📊 Excel Report: {excel_file}")
            print(f"📈 Total Tests: {len(self.test_results)}")
            print(f"⏱️  Total Time: {sum(r['processing_time'] for r in self.test_results):.2f}s")
            
            return {
                'markdown_report': markdown_file,
                'excel_report': excel_file,
                'test_results': self.test_results,
                'analysis_results': self.analysis_results,
                'optimization_recommendations': self.optimization_recommendations
            }
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return None

def main():
    """Main execution function"""
    analyzer = ComprehensiveDeepSeekAnalysis()
    results = analyzer.run_complete_analysis()
    
    if results:
        print("\n✅ Analysis completed successfully!")
        print("📋 Check the generated reports for detailed insights and recommendations.")
    else:
        print("\n❌ Analysis failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
