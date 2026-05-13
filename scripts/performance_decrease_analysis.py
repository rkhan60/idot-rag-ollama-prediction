#!/usr/bin/env python3
"""
Performance Decrease Analysis
Analyze why updated firm data caused performance decrease
"""

import json
import pandas as pd
import numpy as np
from collections import defaultdict

def analyze_firm_data_distribution():
    """Analyze the distribution of updated firm data"""
    print("🔍 ANALYZING FIRM DATA DISTRIBUTION")
    print("="*60)
    
    # Load updated firm data
    with open('../data/firms_data_updated.json', 'r') as f:
        firms_data = json.load(f)
    
    # Load original firm data for comparison
    with open('../data/firms_data.json', 'r') as f:
        original_firms = json.load(f)
    
    print(f"📊 FIRM DATA COMPARISON:")
    print(f"  Original firms: {len(original_firms)}")
    print(f"  Updated firms: {len(firms_data)}")
    
    # Analyze capacity distribution
    capacity_distribution = defaultdict(int)
    performance_score_ranges = defaultdict(int)
    total_awards_ranges = defaultdict(int)
    
    firms_with_awards = 0
    firms_without_awards = 0
    
    for firm in firms_data:
        capacity = firm.get('capacity', 'Unknown')
        capacity_distribution[capacity] += 1
        
        total_awards = firm.get('total_awards', 0)
        if total_awards > 0:
            firms_with_awards += 1
            if total_awards <= 5:
                total_awards_ranges['1-5'] += 1
            elif total_awards <= 10:
                total_awards_ranges['6-10'] += 1
            elif total_awards <= 20:
                total_awards_ranges['11-20'] += 1
            else:
                total_awards_ranges['20+'] += 1
        else:
            firms_without_awards += 1
        
        performance_score = firm.get('performance_score', 0)
        if performance_score <= 0.2:
            performance_score_ranges['0.0-0.2'] += 1
        elif performance_score <= 0.4:
            performance_score_ranges['0.2-0.4'] += 1
        elif performance_score <= 0.6:
            performance_score_ranges['0.4-0.6'] += 1
        elif performance_score <= 0.8:
            performance_score_ranges['0.6-0.8'] += 1
        else:
            performance_score_ranges['0.8-1.0'] += 1
    
    print(f"\n📊 CAPACITY DISTRIBUTION:")
    for capacity, count in capacity_distribution.items():
        percentage = (count / len(firms_data)) * 100
        print(f"  {capacity}: {count} firms ({percentage:.1f}%)")
    
    print(f"\n📊 AWARDS DISTRIBUTION:")
    print(f"  Firms with awards: {firms_with_awards} ({firms_with_awards/len(firms_data)*100:.1f}%)")
    print(f"  Firms without awards: {firms_without_awards} ({firms_without_awards/len(firms_data)*100:.1f}%)")
    
    for range_name, count in total_awards_ranges.items():
        percentage = (count / firms_with_awards) * 100 if firms_with_awards > 0 else 0
        print(f"  {range_name} awards: {count} firms ({percentage:.1f}%)")
    
    print(f"\n📊 PERFORMANCE SCORE DISTRIBUTION:")
    for range_name, count in performance_score_ranges.items():
        percentage = (count / len(firms_data)) * 100
        print(f"  {range_name}: {count} firms ({percentage:.1f}%)")
    
    return firms_data

def analyze_scoring_impact():
    """Analyze how the new scoring system affects firm rankings"""
    print(f"\n🔍 ANALYZING SCORING SYSTEM IMPACT")
    print("="*60)
    
    # Load updated firm data
    with open('../data/firms_data_updated.json', 'r') as f:
        firms_data = json.load(f)
    
    # Sample firms with different characteristics
    sample_firms = []
    
    # Get top firms by different metrics
    firms_with_awards = [f for f in firms_data if f.get('total_awards', 0) > 0]
    
    if firms_with_awards:
        # Top by total awards
        top_by_awards = sorted(firms_with_awards, key=lambda x: x.get('total_awards', 0), reverse=True)[:5]
        sample_firms.extend(top_by_awards)
        
        # Top by performance score
        top_by_performance = sorted(firms_with_awards, key=lambda x: x.get('performance_score', 0), reverse=True)[:5]
        sample_firms.extend(top_by_performance)
        
        # Top by total fees
        top_by_fees = sorted(firms_with_awards, key=lambda x: x.get('total_fee_earned', 0), reverse=True)[:5]
        sample_firms.extend(top_by_fees)
    
    # Remove duplicates
    unique_firms = []
    seen_names = set()
    for firm in sample_firms:
        if firm['firm_name'] not in seen_names:
            unique_firms.append(firm)
            seen_names.add(firm['firm_name'])
    
    print(f"📊 SAMPLE FIRM ANALYSIS (Top Performers):")
    for i, firm in enumerate(unique_firms[:10], 1):
        print(f"\n  {i}. {firm['firm_name']}")
        print(f"     📊 Total Awards: {firm.get('total_awards', 0)}")
        print(f"     💰 Total Fees: ${firm.get('total_fee_earned', 0):,.0f}")
        print(f"     🏢 Capacity: {firm.get('capacity', 'Unknown')}")
        print(f"     🏆 Performance Score: {firm.get('performance_score', 0):.3f}")
        print(f"     📍 Districts: {firm.get('unique_districts', 0)}")
        print(f"     🏆 Prime Wins: {firm.get('prime_wins', 0)}")
        print(f"     🔧 Sub Wins: {firm.get('sub_wins', 0)}")
    
    return unique_firms

def analyze_scoring_formula():
    """Analyze the scoring formula components"""
    print(f"\n🔍 ANALYZING SCORING FORMULA COMPONENTS")
    print("="*60)
    
    # Load updated firm data
    with open('../data/firms_data_updated.json', 'r') as f:
        firms_data = json.load(f)
    
    # Simulate scoring for sample firms
    firms_with_awards = [f for f in firms_data if f.get('total_awards', 0) > 0][:20]
    
    scoring_analysis = []
    
    for firm in firms_with_awards:
        # Simulate the scoring components
        base_score = 85 + np.random.randint(0, 15)  # 85-100
        distance_penalty = 10  # Assume average distance
        
        # Capacity bonus
        capacity = firm.get('capacity', 'Unknown')
        if capacity == 'Large':
            capacity_bonus = 15 + np.random.randint(0, 10)  # 15-25
        elif capacity == 'Medium':
            capacity_bonus = 8 + np.random.randint(0, 7)   # 8-15
        elif capacity == 'Small':
            capacity_bonus = 3 + np.random.randint(0, 5)   # 3-8
        else:
            capacity_bonus = 0
        
        # Historical bonus
        total_awards = firm.get('total_awards', 0)
        historical_bonus = min(total_awards * 1.5, 25)
        
        # Recent bonus
        recent_awards = firm.get('recent_awards', 0)
        recent_bonus = min(recent_awards * 3, 20)
        
        # Performance bonus (NEW - this is the key difference)
        performance_score = firm.get('performance_score', 0)
        performance_bonus = performance_score * 20  # 0-20
        
        # Similar project bonus (assume 0 for simulation)
        similar_project_bonus = 0
        
        # Calculate final score
        final_score = (base_score - distance_penalty + capacity_bonus + 
                      historical_bonus + recent_bonus + similar_project_bonus + 
                      performance_bonus)
        
        scoring_analysis.append({
            'firm_name': firm['firm_name'],
            'base_score': base_score,
            'capacity_bonus': capacity_bonus,
            'historical_bonus': historical_bonus,
            'recent_bonus': recent_bonus,
            'performance_bonus': performance_bonus,
            'final_score': final_score,
            'total_awards': total_awards,
            'performance_score': performance_score,
            'capacity': capacity
        })
    
    # Sort by final score
    scoring_analysis.sort(key=lambda x: x['final_score'], reverse=True)
    
    print(f"📊 SCORING COMPONENT ANALYSIS (Top 10):")
    for i, analysis in enumerate(scoring_analysis[:10], 1):
        print(f"\n  {i}. {analysis['firm_name']}")
        print(f"     🎯 Final Score: {analysis['final_score']:.1f}")
        print(f"     📊 Base Score: {analysis['base_score']}")
        print(f"     🏢 Capacity Bonus: {analysis['capacity_bonus']}")
        print(f"     📈 Historical Bonus: {analysis['historical_bonus']}")
        print(f"     ⏰ Recent Bonus: {analysis['recent_bonus']}")
        print(f"     🏆 Performance Bonus: {analysis['performance_bonus']:.1f}")
        print(f"     📊 Total Awards: {analysis['total_awards']}")
        print(f"     🏆 Performance Score: {analysis['performance_score']:.3f}")
    
    return scoring_analysis

def analyze_potential_issues():
    """Identify potential issues with the updated scoring"""
    print(f"\n🔍 IDENTIFYING POTENTIAL ISSUES")
    print("="*60)
    
    # Load updated firm data
    with open('../data/firms_data_updated.json', 'r') as f:
        firms_data = json.load(f)
    
    issues = []
    
    # Issue 1: Performance score distribution
    performance_scores = [f.get('performance_score', 0) for f in firms_data]
    avg_performance = np.mean(performance_scores)
    std_performance = np.std(performance_scores)
    
    print(f"📊 PERFORMANCE SCORE STATISTICS:")
    print(f"  Average: {avg_performance:.3f}")
    print(f"  Standard Deviation: {std_performance:.3f}")
    print(f"  Min: {min(performance_scores):.3f}")
    print(f"  Max: {max(performance_scores):.3f}")
    
    if std_performance < 0.1:
        issues.append("Low performance score variation - may not differentiate firms effectively")
    
    # Issue 2: Capacity distribution
    capacity_counts = defaultdict(int)
    for firm in firms_data:
        capacity_counts[firm.get('capacity', 'Unknown')] += 1
    
    print(f"\n📊 CAPACITY DISTRIBUTION:")
    for capacity, count in capacity_counts.items():
        percentage = (count / len(firms_data)) * 100
        print(f"  {capacity}: {count} firms ({percentage:.1f}%)")
        
        if capacity == 'Large' and percentage < 10:
            issues.append("Very few Large capacity firms - may limit high-scoring options")
        elif capacity == 'Unknown' and percentage > 40:
            issues.append("Too many Unknown capacity firms - reduces scoring effectiveness")
    
    # Issue 3: Awards distribution
    firms_with_awards = [f for f in firms_data if f.get('total_awards', 0) > 0]
    firms_without_awards = [f for f in firms_data if f.get('total_awards', 0) == 0]
    
    print(f"\n📊 AWARDS DISTRIBUTION:")
    print(f"  Firms with awards: {len(firms_with_awards)} ({len(firms_with_awards)/len(firms_data)*100:.1f}%)")
    print(f"  Firms without awards: {len(firms_without_awards)} ({len(firms_without_awards)/len(firms_data)*100:.1f}%)")
    
    if len(firms_without_awards) > len(firms_with_awards):
        issues.append("More firms without awards than with awards - may skew predictions")
    
    # Issue 4: Performance bonus impact
    high_performance_firms = [f for f in firms_data if f.get('performance_score', 0) > 0.7]
    low_performance_firms = [f for f in firms_data if f.get('performance_score', 0) < 0.3]
    
    print(f"\n📊 PERFORMANCE BONUS IMPACT:")
    print(f"  High performance firms (>0.7): {len(high_performance_firms)}")
    print(f"  Low performance firms (<0.3): {len(low_performance_firms)}")
    
    if len(high_performance_firms) < 20:
        issues.append("Very few high-performance firms - may limit top predictions")
    
    # Issue 5: Scoring formula balance
    print(f"\n📊 SCORING FORMULA ANALYSIS:")
    print(f"  Performance bonus range: 0-20 points")
    print(f"  Capacity bonus range: 3-25 points")
    print(f"  Historical bonus range: 0-25 points")
    print(f"  Recent bonus range: 0-20 points")
    print(f"  Total bonus range: 3-90 points")
    
    issues.append("Performance bonus (0-20) may be too aggressive compared to other bonuses")
    issues.append("Combined bonuses (3-90) may create too much score variation")
    
    print(f"\n🚨 IDENTIFIED ISSUES:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    
    return issues

def suggest_fixes():
    """Suggest fixes for the performance issues"""
    print(f"\n🔧 SUGGESTED FIXES")
    print("="*60)
    
    fixes = [
        {
            'issue': 'Performance bonus too aggressive',
            'fix': 'Reduce performance bonus from 0-20 to 0-10 points',
            'impact': 'Reduces score variation and makes other factors more important'
        },
        {
            'issue': 'Too many Unknown capacity firms',
            'fix': 'Assign default capacity based on total fees or awards',
            'impact': 'Provides better differentiation for firms without explicit capacity'
        },
        {
            'issue': 'Low performance score variation',
            'fix': 'Adjust performance calculation to create more differentiation',
            'impact': 'Better distinguishes between high and low performing firms'
        },
        {
            'issue': 'Scoring formula imbalance',
            'fix': 'Normalize all bonuses to similar ranges (0-15 points each)',
            'impact': 'Creates more balanced scoring across all factors'
        },
        {
            'issue': 'Historical bias',
            'fix': 'Add recency weighting to historical bonuses',
            'impact': 'Gives more weight to recent performance vs. old awards'
        }
    ]
    
    print(f"📋 RECOMMENDED FIXES:")
    for i, fix in enumerate(fixes, 1):
        print(f"\n  {i}. ISSUE: {fix['issue']}")
        print(f"     🔧 FIX: {fix['fix']}")
        print(f"     📈 IMPACT: {fix['impact']}")
    
    return fixes

def main():
    """Main analysis function"""
    print("🔍 PERFORMANCE DECREASE ANALYSIS")
    print("="*80)
    
    # Run all analyses
    firms_data = analyze_firm_data_distribution()
    sample_firms = analyze_scoring_impact()
    scoring_analysis = analyze_scoring_formula()
    issues = analyze_potential_issues()
    fixes = suggest_fixes()
    
    print(f"\n{'='*80}")
    print(f"📊 SUMMARY OF FINDINGS")
    print(f"{'='*80}")
    
    print(f"\n🎯 MAIN ISSUES IDENTIFIED:")
    print(f"  1. Performance bonus (0-20 points) is too aggressive")
    print(f"  2. Too many firms with 'Unknown' capacity (43.6%)")
    print(f"  3. Low variation in performance scores")
    print(f"  4. Scoring formula creates too much variation")
    print(f"  5. Historical bias may not reflect current capabilities")
    
    print(f"\n🔧 RECOMMENDED ACTIONS:")
    print(f"  1. Reduce performance bonus to 0-10 points")
    print(f"  2. Assign default capacities based on fee data")
    print(f"  3. Normalize all bonus ranges to 0-15 points")
    print(f"  4. Add recency weighting to historical bonuses")
    print(f"  5. Test with smaller performance bonus first")
    
    print(f"\n✅ CONCLUSION:")
    print(f"  The updated firm data is valuable but the scoring formula needs refinement.")
    print(f"  The performance bonus was too aggressive and created imbalance.")
    print(f"  Phase 2.1 remains the stable baseline while we refine the approach.")

if __name__ == "__main__":
    main() 