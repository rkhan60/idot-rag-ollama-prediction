#!/usr/bin/env python3
"""
Analyze Past Performance Matrix
Comprehensive analysis of the built performance matrix
"""

import json
import pandas as pd
import numpy as np
from collections import defaultdict

class PerformanceMatrixAnalyzer:
    def __init__(self):
        self.matrix_file = '../data/past_performance_matrix.json'
        self.firms_data_file = '../data/firms_data.json'
        
        # Load data
        with open(self.matrix_file, 'r') as f:
            self.matrix_data = json.load(f)
        
        with open(self.firms_data_file, 'r') as f:
            self.firms_data = json.load(f)
        
        self.matrix = self.matrix_data['performance_matrix']
        self.metadata = self.matrix_data['metadata']
    
    def analyze_overall_statistics(self):
        """Analyze overall statistics of the performance matrix"""
        print("📊 OVERALL PERFORMANCE MATRIX STATISTICS")
        print("=" * 80)
        
        print(f"📋 MATRIX METADATA:")
        print(f"   Created: {self.metadata['created_date']}")
        print(f"   Total firms: {self.metadata['total_firms']}")
        print(f"   Total projects: {self.metadata['total_projects']}")
        print(f"   Total experience points: {self.metadata['total_experience_points']:.2f}")
        print()
        
        print(f"📈 SCORING WEIGHTS:")
        print(f"   Role weights: {self.metadata['scoring_weights']}")
        print(f"   Time weights: {self.metadata['time_weights']}")
        print()
        
        # Experience distribution
        experience_points = [data['total_experience_points'] for data in self.matrix.values()]
        
        print(f"📊 EXPERIENCE DISTRIBUTION:")
        print(f"   Average: {np.mean(experience_points):.2f}")
        print(f"   Median: {np.median(experience_points):.2f}")
        print(f"   Standard deviation: {np.std(experience_points):.2f}")
        print(f"   Min: {np.min(experience_points):.2f}")
        print(f"   Max: {np.max(experience_points):.2f}")
        print()
        
        # Percentiles
        percentiles = [25, 50, 75, 90, 95, 99]
        print(f"📈 PERCENTILES:")
        for p in percentiles:
            value = np.percentile(experience_points, p)
            print(f"   {p}th percentile: {value:.2f}")
        print()
    
    def analyze_top_performers(self, top_n=20):
        """Analyze top performing firms"""
        print(f"🏆 TOP {top_n} PERFORMING FIRMS")
        print("=" * 80)
        
        sorted_firms = sorted(
            self.matrix.items(),
            key=lambda x: x[1]['total_experience_points'],
            reverse=True
        )
        
        for i, (firm_code, data) in enumerate(sorted_firms[:top_n], 1):
            print(f"{i:2d}. {data['firm_name']} ({firm_code})")
            print(f"    Experience Points: {data['total_experience_points']:.2f}")
            print(f"    Total Projects: {data['total_projects']}")
            print(f"    Prime: {data['prime_projects']}, Sub: {data['subconsultant_projects']}, Alt: {data['alternate_projects']}")
            print(f"    Recent: {data['recent_experience']:.2f}, Medium: {data['medium_experience']:.2f}, Old: {data['old_experience']:.2f}")
            print()
    
    def analyze_role_distribution(self):
        """Analyze distribution of roles across firms"""
        print("🎭 ROLE DISTRIBUTION ANALYSIS")
        print("=" * 80)
        
        # Collect role data
        prime_counts = [data['prime_projects'] for data in self.matrix.values()]
        sub_counts = [data['subconsultant_projects'] for data in self.matrix.values()]
        alt_counts = [data['alternate_projects'] for data in self.matrix.values()]
        
        print(f"📊 ROLE STATISTICS:")
        print(f"   Prime projects:")
        print(f"     Total: {sum(prime_counts)}")
        print(f"     Average per firm: {np.mean(prime_counts):.2f}")
        print(f"     Max per firm: {max(prime_counts)}")
        print(f"     Firms with prime experience: {sum(1 for x in prime_counts if x > 0)}")
        print()
        
        print(f"   Subconsultant projects:")
        print(f"     Total: {sum(sub_counts)}")
        print(f"     Average per firm: {np.mean(sub_counts):.2f}")
        print(f"     Max per firm: {max(sub_counts)}")
        print(f"     Firms with subconsultant experience: {sum(1 for x in sub_counts if x > 0)}")
        print()
        
        print(f"   Alternate projects:")
        print(f"     Total: {sum(alt_counts)}")
        print(f"     Average per firm: {np.mean(alt_counts):.2f}")
        print(f"     Max per firm: {max(alt_counts)}")
        print(f"     Firms with alternate experience: {sum(1 for x in alt_counts if x > 0)}")
        print()
        
        # Role specialization analysis
        print(f"🎯 ROLE SPECIALIZATION:")
        prime_specialists = [(code, data) for code, data in self.matrix.items() 
                           if data['prime_projects'] > data['subconsultant_projects'] + data['alternate_projects']]
        sub_specialists = [(code, data) for code, data in self.matrix.items() 
                          if data['subconsultant_projects'] > data['prime_projects'] + data['alternate_projects']]
        
        print(f"   Prime specialists: {len(prime_specialists)} firms")
        print(f"   Subconsultant specialists: {len(sub_specialists)} firms")
        print()
    
    def analyze_time_distribution(self):
        """Analyze time-based experience distribution"""
        print("⏰ TIME-BASED EXPERIENCE ANALYSIS")
        print("=" * 80)
        
        recent_exp = [data['recent_experience'] for data in self.matrix.values()]
        medium_exp = [data['medium_experience'] for data in self.matrix.values()]
        old_exp = [data['old_experience'] for data in self.matrix.values()]
        
        print(f"📊 TIME DISTRIBUTION:")
        print(f"   Recent experience (≤5 years):")
        print(f"     Total: {sum(recent_exp):.2f} points")
        print(f"     Average per firm: {np.mean(recent_exp):.2f}")
        print(f"     Firms with recent experience: {sum(1 for x in recent_exp if x > 0)}")
        print()
        
        print(f"   Medium experience (5-10 years):")
        print(f"     Total: {sum(medium_exp):.2f} points")
        print(f"     Average per firm: {np.mean(medium_exp):.2f}")
        print(f"     Firms with medium experience: {sum(1 for x in medium_exp if x > 0)}")
        print()
        
        print(f"   Old experience (>10 years):")
        print(f"     Total: {sum(old_exp):.2f} points")
        print(f"     Average per firm: {np.mean(old_exp):.2f}")
        print(f"     Firms with old experience: {sum(1 for x in old_exp if x > 0)}")
        print()
    
    def analyze_prequalification_experience(self):
        """Analyze prequalification-specific experience"""
        print("🔧 PREQUALIFICATION EXPERIENCE ANALYSIS")
        print("=" * 80)
        
        # Collect all prequalifications
        all_prequals = set()
        for data in self.matrix.values():
            all_prequals.update(data['prequalification_experience'].keys())
        
        print(f"📋 PREQUALIFICATION COVERAGE:")
        print(f"   Total unique prequalifications: {len(all_prequals)}")
        print()
        
        # Analyze top prequalifications by total experience
        prequal_totals = defaultdict(float)
        for data in self.matrix.values():
            for prequal, points in data['prequalification_experience'].items():
                prequal_totals[prequal] += points
        
        sorted_prequals = sorted(prequal_totals.items(), key=lambda x: x[1], reverse=True)
        
        print(f"🏆 TOP 15 PREQUALIFICATIONS BY EXPERIENCE:")
        for i, (prequal, total_points) in enumerate(sorted_prequals[:15], 1):
            firm_count = sum(1 for data in self.matrix.values() 
                           if prequal in data['prequalification_experience'])
            print(f"   {i:2d}. {prequal}")
            print(f"       Total points: {total_points:.2f}")
            print(f"       Firms with experience: {firm_count}")
            print()
    
    def analyze_firm_comparison(self, firm_codes):
        """Compare specific firms"""
        print("🔍 FIRM COMPARISON ANALYSIS")
        print("=" * 80)
        
        for firm_code in firm_codes:
            if firm_code in self.matrix:
                data = self.matrix[firm_code]
                print(f"🏢 {data['firm_name']} ({firm_code})")
                print(f"   Total Experience Points: {data['total_experience_points']:.2f}")
                print(f"   Total Projects: {data['total_projects']}")
                print(f"   Prime Projects: {data['prime_projects']}")
                print(f"   Subconsultant Projects: {data['subconsultant_projects']}")
                print(f"   Alternate Projects: {data['alternate_projects']}")
                print(f"   Recent Experience: {data['recent_experience']:.2f}")
                print(f"   Medium Experience: {data['medium_experience']:.2f}")
                print(f"   Old Experience: {data['old_experience']:.2f}")
                
                # Top prequalifications
                top_prequals = sorted(data['prequalification_experience'].items(), 
                                    key=lambda x: x[1], reverse=True)[:5]
                print(f"   Top Prequalifications:")
                for prequal, points in top_prequals:
                    print(f"     • {prequal}: {points:.2f} points")
                print()
            else:
                print(f"❌ Firm {firm_code} not found in matrix")
                print()
    
    def generate_insights(self):
        """Generate key insights from the analysis"""
        print("💡 KEY INSIGHTS")
        print("=" * 80)
        
        # Calculate insights
        total_firms = len(self.matrix)
        firms_with_prime = sum(1 for data in self.matrix.values() if data['prime_projects'] > 0)
        firms_with_sub = sum(1 for data in self.matrix.values() if data['subconsultant_projects'] > 0)
        firms_with_recent = sum(1 for data in self.matrix.values() if data['recent_experience'] > 0)
        
        experience_points = [data['total_experience_points'] for data in self.matrix.values()]
        high_performers = sum(1 for points in experience_points if points > np.percentile(experience_points, 75))
        
        print(f"🎯 MARKET INSIGHTS:")
        print(f"   • {firms_with_prime}/{total_firms} firms ({firms_with_prime/total_firms*100:.1f}%) have prime contractor experience")
        print(f"   • {firms_with_sub}/{total_firms} firms ({firms_with_sub/total_firms*100:.1f}%) have subconsultant experience")
        print(f"   • {firms_with_recent}/{total_firms} firms ({firms_with_recent/total_firms*100:.1f}%) have recent experience (≤5 years)")
        print(f"   • {high_performers} firms are in the top 25% by experience points")
        print()
        
        print(f"📈 PERFORMANCE INSIGHTS:")
        print(f"   • Experience points range from {min(experience_points):.2f} to {max(experience_points):.2f}")
        print(f"   • Median firm has {np.median(experience_points):.2f} experience points")
        print(f"   • Top 10% of firms have >{np.percentile(experience_points, 90):.2f} experience points")
        print()
        
        print(f"⏰ TEMPORAL INSIGHTS:")
        recent_total = sum(data['recent_experience'] for data in self.matrix.values())
        medium_total = sum(data['medium_experience'] for data in self.matrix.values())
        old_total = sum(data['old_experience'] for data in self.matrix.values())
        total_exp = recent_total + medium_total + old_total
        
        print(f"   • {recent_total/total_exp*100:.1f}% of experience is recent (≤5 years)")
        print(f"   • {medium_total/total_exp*100:.1f}% of experience is medium (5-10 years)")
        print(f"   • {old_total/total_exp*100:.1f}% of experience is old (>10 years)")
        print()
    
    def run_complete_analysis(self):
        """Run complete analysis"""
        print("🚀 COMPREHENSIVE PERFORMANCE MATRIX ANALYSIS")
        print("=" * 80)
        
        # Run all analyses
        self.analyze_overall_statistics()
        self.analyze_top_performers()
        self.analyze_role_distribution()
        self.analyze_time_distribution()
        self.analyze_prequalification_experience()
        
        # Compare some specific firms
        sample_firms = ['F001', 'F008', 'F302', 'F230']  # Top performers
        self.analyze_firm_comparison(sample_firms)
        
        # Generate insights
        self.generate_insights()
        
        print("✅ Performance matrix analysis complete!")

def main():
    analyzer = PerformanceMatrixAnalyzer()
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()





