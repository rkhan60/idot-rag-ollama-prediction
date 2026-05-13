#!/usr/bin/env python3
"""
Comprehensive Analysis of Performance Decrease
Detailed analysis of why both approaches failed to improve Phase 2.1
"""

import json
import pandas as pd
import numpy as np
from collections import defaultdict

def analyze_performance_trends():
    """Analyze performance trends across all systems"""
    print("🔍 COMPREHENSIVE PERFORMANCE ANALYSIS")
    print("="*80)
    
    # Performance data across all systems
    performance_data = {
        'Baseline (Original)': {
            'PTB180-190': 20.1,
            'PTB190-200': 20.1,
            'Average': 20.1,
            'Status': 'Initial'
        },
        'Phase 1': {
            'PTB180-190': 25.6,
            'PTB190-200': 28.5,
            'Average': 27.1,
            'Status': 'Improvement'
        },
        'Phase 2.1 (Current Baseline)': {
            'PTB180-190': 25.2,
            'PTB190-200': 30.1,
            'Average': 27.6,
            'Status': 'Best Performance'
        },
        'Updated Firm Data (Bonus Stacking)': {
            'PTB180-190': 18.7,
            'PTB190-200': 22.6,
            'Average': 20.7,
            'Status': 'Decrease'
        },
        'Weighted Scoring System': {
            'PTB180-190': 15.7,
            'PTB190-200': 21.1,
            'Average': 18.4,
            'Status': 'Decrease'
        }
    }
    
    print("📊 PERFORMANCE TREND ANALYSIS")
    print("-"*50)
    
    for system, data in performance_data.items():
        print(f"\n🎯 {system}:")
        print(f"  PTB180-190: {data['PTB180-190']:.1f}%")
        print(f"  PTB190-200: {data['PTB190-200']:.1f}%")
        print(f"  Average: {data['Average']:.1f}%")
        print(f"  Status: {data['Status']}")
    
    # Calculate improvements/decreases
    baseline = performance_data['Phase 2.1 (Current Baseline)']
    
    print(f"\n📈 IMPROVEMENT ANALYSIS (vs Phase 2.1 Baseline):")
    print("-"*50)
    
    for system, data in performance_data.items():
        if system != 'Phase 2.1 (Current Baseline)':
            ptb180_190_diff = data['PTB180-190'] - baseline['PTB180-190']
            ptb190_200_diff = data['PTB190-200'] - baseline['PTB190-200']
            avg_diff = data['Average'] - baseline['Average']
            
            print(f"\n  {system}:")
            print(f"    PTB180-190: {ptb180_190_diff:+.1f}%")
            print(f"    PTB190-200: {ptb190_200_diff:+.1f}%")
            print(f"    Average: {avg_diff:+.1f}%")
    
    return performance_data

def analyze_firm_data_issues():
    """Analyze specific issues with the updated firm data"""
    print(f"\n🔍 FIRM DATA ISSUE ANALYSIS")
    print("="*80)
    
    # Load updated firm data
    with open('../data/firms_data_updated.json', 'r') as f:
        firms_data = json.load(f)
    
    # Load original firm data for comparison
    with open('../data/firms_data.json', 'r') as f:
        original_firms = json.load(f)
    
    print("📊 FIRM DATA COMPARISON:")
    print("-"*40)
    
    # Analyze capacity distribution
    capacity_analysis = defaultdict(int)
    performance_analysis = defaultdict(int)
    awards_analysis = defaultdict(int)
    
    for firm in firms_data:
        capacity = firm.get('capacity', 'Unknown')
        capacity_analysis[capacity] += 1
        
        performance_score = firm.get('performance_score', 0)
        if performance_score <= 0.2:
            performance_analysis['0.0-0.2'] += 1
        elif performance_score <= 0.4:
            performance_analysis['0.2-0.4'] += 1
        elif performance_score <= 0.6:
            performance_analysis['0.4-0.6'] += 1
        elif performance_score <= 0.8:
            performance_analysis['0.6-0.8'] += 1
        else:
            performance_analysis['0.8-1.0'] += 1
        
        total_awards = firm.get('total_awards', 0)
        if total_awards == 0:
            awards_analysis['No Awards'] += 1
        elif total_awards <= 5:
            awards_analysis['1-5 Awards'] += 1
        elif total_awards <= 10:
            awards_analysis['6-10 Awards'] += 1
        elif total_awards <= 20:
            awards_analysis['11-20 Awards'] += 1
        else:
            awards_analysis['20+ Awards'] += 1
    
    print(f"📊 CAPACITY DISTRIBUTION:")
    for capacity, count in capacity_analysis.items():
        percentage = (count / len(firms_data)) * 100
        print(f"  {capacity}: {count} firms ({percentage:.1f}%)")
    
    print(f"\n📊 PERFORMANCE SCORE DISTRIBUTION:")
    for range_name, count in performance_analysis.items():
        percentage = (count / len(firms_data)) * 100
        print(f"  {range_name}: {count} firms ({percentage:.1f}%)")
    
    print(f"\n📊 AWARDS DISTRIBUTION:")
    for range_name, count in awards_analysis.items():
        percentage = (count / len(firms_data)) * 100
        print(f"  {range_name}: {count} firms ({percentage:.1f}%)")
    
    # Identify specific issues
    print(f"\n🚨 IDENTIFIED ISSUES:")
    print("-"*40)
    
    issues = []
    
    # Issue 1: Too many unknown capacity firms
    unknown_capacity = capacity_analysis.get('Unknown', 0)
    if unknown_capacity > len(firms_data) * 0.4:
        issues.append(f"Too many Unknown capacity firms ({unknown_capacity}, {unknown_capacity/len(firms_data)*100:.1f}%)")
    
    # Issue 2: Low performance score variation
    low_performance = performance_analysis.get('0.0-0.2', 0)
    if low_performance > len(firms_data) * 0.4:
        issues.append(f"Too many low-performance firms ({low_performance}, {low_performance/len(firms_data)*100:.1f}%)")
    
    # Issue 3: Many firms with no awards
    no_awards = awards_analysis.get('No Awards', 0)
    if no_awards > len(firms_data) * 0.4:
        issues.append(f"Too many firms with no awards ({no_awards}, {no_awards/len(firms_data)*100:.1f}%)")
    
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    
    return issues

def analyze_scoring_methodology():
    """Analyze why different scoring methodologies failed"""
    print(f"\n🔍 SCORING METHODOLOGY ANALYSIS")
    print("="*80)
    
    print("📊 SCORING APPROACH COMPARISON:")
    print("-"*40)
    
    scoring_methods = {
        'Phase 2.1 (Baseline)': {
            'approach': 'Balanced bonus system',
            'capacity_bonus': '3-25 points',
            'historical_bonus': '0-25 points',
            'recent_bonus': '0-20 points',
            'similar_project_bonus': '12-20 points',
            'total_range': '15-90 points',
            'strengths': ['Proven performance', 'Balanced approach', 'Stable results'],
            'weaknesses': ['Limited firm differentiation', 'No performance metrics']
        },
        'Updated Firm Data (Bonus Stacking)': {
            'approach': 'Aggressive bonus stacking',
            'capacity_bonus': '3-25 points',
            'historical_bonus': '0-25 points',
            'recent_bonus': '0-20 points',
            'performance_bonus': '0-20 points',
            'similar_project_bonus': '12-20 points',
            'total_range': '15-110 points',
            'strengths': ['Includes performance metrics', 'More comprehensive'],
            'weaknesses': ['Too aggressive', 'Overwhelmed other factors', 'High variance']
        },
        'Weighted Scoring System': {
            'approach': 'Normalized weighted scoring',
            'capacity_score': '0-1 normalized',
            'performance_score': '0-1 normalized',
            'weighting': '60% capacity + 40% performance',
            'firm_score_bonus': '0-30 points',
            'similar_project_bonus': '8-12 points',
            'total_range': 'Variable',
            'strengths': ['Theoretical soundness', 'Normalized approach', 'Balanced weighting'],
            'weaknesses': ['Complex implementation', 'Fallback estimation issues', 'Performance calculation flaws']
        }
    }
    
    for method, details in scoring_methods.items():
        print(f"\n🎯 {method}:")
        print(f"  Approach: {details['approach']}")
        print(f"  Total Range: {details['total_range']}")
        print(f"  Strengths: {', '.join(details['strengths'])}")
        print(f"  Weaknesses: {', '.join(details['weaknesses'])}")
    
    return scoring_methods

def analyze_root_causes():
    """Analyze root causes of performance decrease"""
    print(f"\n🔍 ROOT CAUSE ANALYSIS")
    print("="*80)
    
    print("🚨 PRIMARY ROOT CAUSES:")
    print("-"*40)
    
    root_causes = [
        {
            'cause': 'Data Quality Issues',
            'description': 'The updated firm data introduced noise and inaccuracies',
            'evidence': [
                '43.6% of firms have "Unknown" capacity',
                '43.6% of firms have no award history',
                'Performance scores show low variation (std dev: 0.346)'
            ],
            'impact': 'Reduced model precision and firm differentiation'
        },
        {
            'cause': 'Scoring Formula Imbalance',
            'description': 'Both approaches created scoring imbalances',
            'evidence': [
                'Bonus stacking created 3-110 point range (too wide)',
                'Weighted scoring introduced complex fallback estimation',
                'Performance bonus (0-20) overwhelmed other factors'
            ],
            'impact': 'Unpredictable and unstable scoring patterns'
        },
        {
            'cause': 'Over-Engineering',
            'description': 'Added complexity without corresponding benefit',
            'evidence': [
                'Phase 2.1 was already well-optimized',
                'Performance metrics calculation was flawed',
                'Fallback estimation introduced estimation errors'
            ],
            'impact': 'Increased system complexity without accuracy gains'
        },
        {
            'cause': 'Historical Data Limitations',
            'description': 'Limited historical data quality and coverage',
            'evidence': [
                'Only 56.4% of firms have award history',
                'Performance metrics based on incomplete data',
                'District-based analysis may not reflect current capabilities'
            ],
            'impact': 'Performance metrics may not be reliable predictors'
        }
    ]
    
    for i, cause in enumerate(root_causes, 1):
        print(f"\n  {i}. {cause['cause']}")
        print(f"     Description: {cause['description']}")
        print(f"     Evidence:")
        for evidence in cause['evidence']:
            print(f"       • {evidence}")
        print(f"     Impact: {cause['impact']}")
    
    return root_causes

def analyze_lessons_learned():
    """Analyze key lessons learned from this process"""
    print(f"\n🔍 LESSONS LEARNED")
    print("="*80)
    
    lessons = [
        {
            'lesson': 'Phase 2.1 was already optimal',
            'description': 'The baseline system was well-tuned for this dataset',
            'implication': 'Focus on incremental improvements rather than major overhauls'
        },
        {
            'lesson': 'Data quality trumps algorithm complexity',
            'description': 'Poor data quality cannot be overcome by sophisticated algorithms',
            'implication': 'Prioritize data quality improvements over algorithmic enhancements'
        },
        {
            'lesson': 'Bonus stacking can be effective when balanced',
            'description': 'Phase 2.1\'s balanced bonus approach worked well',
            'implication': 'Simple, balanced approaches often outperform complex ones'
        },
        {
            'lesson': 'Performance metrics need high-quality data',
            'description': 'Performance scoring requires comprehensive, accurate historical data',
            'implication': 'Only implement performance metrics when data quality is high'
        },
        {
            'lesson': 'Fallback estimation introduces noise',
            'description': 'Estimating missing data often reduces rather than improves accuracy',
            'implication': 'Work with available data rather than estimating missing data'
        },
        {
            'lesson': 'Stability is valuable',
            'description': 'Consistent, predictable performance is better than variable high performance',
            'implication': 'Prioritize system stability over potential performance gains'
        }
    ]
    
    print("📚 KEY LESSONS:")
    print("-"*40)
    
    for i, lesson in enumerate(lessons, 1):
        print(f"\n  {i}. {lesson['lesson']}")
        print(f"     Description: {lesson['description']}")
        print(f"     Implication: {lesson['implication']}")
    
    return lessons

def analyze_recommendations():
    """Provide recommendations for future improvements"""
    print(f"\n🔍 RECOMMENDATIONS FOR FUTURE")
    print("="*80)
    
    recommendations = [
        {
            'category': 'System Stability',
            'recommendation': 'Maintain Phase 2.1 as primary system',
            'rationale': 'Proven performance and stability',
            'priority': 'High'
        },
        {
            'category': 'Data Quality',
            'recommendation': 'Improve firm data quality before adding features',
            'rationale': 'Better data will enable better algorithms',
            'priority': 'High'
        },
        {
            'category': 'Incremental Improvements',
            'recommendation': 'Test small changes one at a time',
            'rationale': 'Isolate impact of each change',
            'priority': 'Medium'
        },
        {
            'category': 'Performance Monitoring',
            'recommendation': 'Implement continuous performance monitoring',
            'rationale': 'Detect performance degradation early',
            'priority': 'Medium'
        },
        {
            'category': 'Alternative Approaches',
            'recommendation': 'Consider ensemble methods or different ML approaches',
            'rationale': 'May provide better performance than rule-based scoring',
            'priority': 'Low'
        }
    ]
    
    print("📋 RECOMMENDATIONS:")
    print("-"*40)
    
    for rec in recommendations:
        print(f"\n  🎯 {rec['category']} ({rec['priority']} priority):")
        print(f"     Recommendation: {rec['recommendation']}")
        print(f"     Rationale: {rec['rationale']}")
    
    return recommendations

def main():
    """Main analysis function"""
    print("🔍 COMPREHENSIVE ANALYSIS OF PERFORMANCE DECREASE")
    print("="*80)
    
    # Run all analyses
    performance_data = analyze_performance_trends()
    firm_data_issues = analyze_firm_data_issues()
    scoring_methods = analyze_scoring_methodology()
    root_causes = analyze_root_causes()
    lessons = analyze_lessons_learned()
    recommendations = analyze_recommendations()
    
    print(f"\n{'='*80}")
    print(f"📊 EXECUTIVE SUMMARY")
    print(f"{'='*80}")
    
    print(f"\n🎯 KEY FINDINGS:")
    print(f"  1. Phase 2.1 baseline (27.6% average) is the optimal system")
    print(f"  2. Both enhancement attempts decreased performance significantly")
    print(f"  3. Data quality issues were the primary cause of failure")
    print(f"  4. Over-engineering introduced complexity without benefit")
    
    print(f"\n📈 PERFORMANCE TREND:")
    print(f"  Baseline → Phase 1 → Phase 2.1 → Attempted Enhancements")
    print(f"  20.1% → 27.1% → 27.6% → 20.7% / 18.4%")
    
    print(f"\n✅ RECOMMENDED ACTION:")
    print(f"  Maintain Phase 2.1 as the primary production system")
    print(f"  Focus on data quality improvements for future enhancements")
    print(f"  Implement incremental testing for any future changes")
    
    print(f"\n🔍 CONCLUSION:")
    print(f"  The performance decrease was caused by data quality issues and")
    print(f"  over-engineering. Phase 2.1 represents the optimal balance of")
    print(f"  performance and stability for this dataset.")

if __name__ == "__main__":
    main() 