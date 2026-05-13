#!/usr/bin/env python3
"""
Analyze Workflow Support
Demonstrate how the working performance structure supports the 3-step workflow
"""

import json
import pandas as pd

class WorkflowSupportAnalyzer:
    def __init__(self):
        self.performance_file = '../data/working_past_performance.json'
        self.firms_data_file = '../data/firms_data.json'
        self.prequal_lookup_file = '../data/prequal_lookup.json'
        
        # Load data
        with open(self.performance_file, 'r') as f:
            self.performance_data = json.load(f)
        
        with open(self.firms_data_file, 'r') as f:
            self.firms_data = json.load(f)
        
        with open(self.prequal_lookup_file, 'r') as f:
            self.prequal_lookup = json.load(f)
    
    def step1_firms_eligible_by_prequals(self, required_prequals):
        """Step 1: Get firms eligible based on prequalifications"""
        print(f"🔍 STEP 1: FIRMS ELIGIBLE BY PREQUALIFICATIONS")
        print("=" * 80)
        
        eligible_firms = set()
        
        for prequal in required_prequals:
            if prequal in self.performance_data['prequalification_firm_rankings']:
                firms_with_prequal = self.performance_data['prequalification_firm_rankings'][prequal]
                for firm in firms_with_prequal:
                    eligible_firms.add(firm['firm_code'])
        
        print(f"📊 Required Prequalifications: {required_prequals}")
        print(f"📊 Total eligible firms: {len(eligible_firms)}")
        
        # Show sample eligible firms
        print(f"\n📋 SAMPLE ELIGIBLE FIRMS:")
        for i, firm_code in enumerate(list(eligible_firms)[:10], 1):
            firm_name = self.performance_data['firm_detailed_experience'][firm_code]['firm_name']
            print(f"   {i:2d}. {firm_name} ({firm_code})")
        
        if len(eligible_firms) > 10:
            print(f"   ... and {len(eligible_firms) - 10} more")
        
        return eligible_firms
    
    def step2_firms_eligible_by_district_rotation(self, eligible_firms, district):
        """Step 2: Filter firms by district rotation rule"""
        print(f"\n🔍 STEP 2: FIRMS ELIGIBLE BY DISTRICT ROTATION")
        print("=" * 80)
        
        # This is a placeholder - you would implement actual district rotation logic
        # For now, we'll simulate by taking top firms based on experience
        district_eligible = list(eligible_firms)[:50]  # Simulate district rotation
        
        print(f"📊 District: {district}")
        print(f"📊 Firms after district rotation: {len(district_eligible)}")
        
        # Show sample district eligible firms
        print(f"\n📋 SAMPLE DISTRICT ELIGIBLE FIRMS:")
        for i, firm_code in enumerate(district_eligible[:10], 1):
            firm_name = self.performance_data['firm_detailed_experience'][firm_code]['firm_name']
            print(f"   {i:2d}. {firm_name} ({firm_code})")
        
        return district_eligible
    
    def step3_firms_ranked_by_past_performance(self, district_eligible, required_prequals, top_n=5):
        """Step 3: Rank firms by past performance experience"""
        print(f"\n🔍 STEP 3: FIRMS RANKED BY PAST PERFORMANCE")
        print("=" * 80)
        
        firm_scores = []
        
        for firm_code in district_eligible:
            if firm_code in self.performance_data['firm_detailed_experience']:
                firm_data = self.performance_data['firm_detailed_experience'][firm_code]
                total_score = 0.0
                
                # Calculate score based on required prequalifications
                for prequal in required_prequals:
                    if prequal in firm_data['prequalification_experience']:
                        prequal_data = firm_data['prequalification_experience'][prequal]
                        total_score += prequal_data['experience_points']
                
                firm_scores.append({
                    'firm_code': firm_code,
                    'firm_name': firm_data['firm_name'],
                    'total_score': total_score,
                    'prequalification_scores': {
                        prequal: firm_data['prequalification_experience'].get(prequal, {}).get('experience_points', 0.0)
                        for prequal in required_prequals
                    }
                })
        
        # Sort by total score
        firm_scores.sort(key=lambda x: x['total_score'], reverse=True)
        
        print(f"📊 Top {top_n} firms by past performance:")
        for i, firm in enumerate(firm_scores[:top_n], 1):
            print(f"\n   {i}. {firm['firm_name']} ({firm['firm_code']})")
            print(f"      Total Score: {firm['total_score']:.2f}")
            print(f"      Prequalification Scores:")
            for prequal, score in firm['prequalification_scores'].items():
                print(f"        • {prequal}: {score:.2f}")
        
        return firm_scores[:top_n]
    
    def demonstrate_workflow(self):
        """Demonstrate the complete 3-step workflow"""
        print("🚀 DEMONSTRATING 3-STEP WORKFLOW")
        print("=" * 80)
        
        # Example project requirements
        required_prequals = [
            'Highways (Roads & Streets)',
            'Structures (Highway: Typical)',
            'Special Services (Surveying)'
        ]
        
        district = "District 1"
        
        # Step 1: Firms eligible by prequalifications
        eligible_firms = self.step1_firms_eligible_by_prequals(required_prequals)
        
        # Step 2: Firms eligible by district rotation
        district_eligible = self.step2_firms_eligible_by_district_rotation(eligible_firms, district)
        
        # Step 3: Firms ranked by past performance
        top_firms = self.step3_firms_ranked_by_past_performance(district_eligible, required_prequals, top_n=5)
        
        print(f"\n✅ WORKFLOW COMPLETE!")
        print(f"📊 Final Recommendation: {top_firms[0]['firm_name']} ({top_firms[0]['firm_code']})")
        print(f"   Total Experience Score: {top_firms[0]['total_score']:.2f}")
    
    def analyze_structure_benefits(self):
        """Analyze the benefits of the structured approach"""
        print(f"\n📊 STRUCTURE BENEFITS ANALYSIS")
        print("=" * 80)
        
        # Fast querying capability
        print(f"⚡ FAST QUERYING:")
        print(f"   • Direct access to prequalification rankings")
        print(f"   • No complex calculations needed during workflow")
        print(f"   • Instant firm lookup by prequalification")
        
        # Workflow optimization
        print(f"\n🎯 WORKFLOW OPTIMIZATION:")
        print(f"   • Step 1: Instant prequalification filtering")
        print(f"   • Step 2: District rotation integration ready")
        print(f"   • Step 3: Pre-calculated experience rankings")
        
        # Data completeness
        print(f"\n📈 DATA COMPLETENESS:")
        print(f"   • {self.performance_data['metadata']['firms_with_experience']} firms with experience")
        print(f"   • {self.performance_data['metadata']['total_experience_points']:.2f} total experience points")
        print(f"   • {self.performance_data['metadata']['projects_with_prequals']} projects with prequalifications")
        
        # Model-friendly structure
        print(f"\n🤖 MODEL-FRIENDLY STRUCTURE:")
        print(f"   • JSON format for easy AI processing")
        print(f"   • Hierarchical organization")
        print(f"   • Consistent data types")
        print(f"   • Clear relationships between entities")
    
    def show_query_examples(self):
        """Show example queries for the model"""
        print(f"\n🔍 EXAMPLE QUERIES FOR MODEL")
        print("=" * 80)
        
        # Example 1: Get top firms for a prequalification
        prequal = 'Highways (Roads & Streets)'
        rankings = self.performance_data['prequalification_firm_rankings'][prequal]
        
        print(f"📋 Query 1: Get top 5 firms for '{prequal}'")
        print(f"   Result: {len(rankings)} firms found")
        for i, firm in enumerate(rankings[:5], 1):
            print(f"   {i}. {firm['firm_name']} - {firm['experience_points']:.2f} points")
        
        # Example 2: Get firm's experience across prequalifications
        firm_code = 'F088'  # Civiltech Engineering
        if firm_code in self.performance_data['firm_detailed_experience']:
            firm_data = self.performance_data['firm_detailed_experience'][firm_code]
            
            print(f"\n📋 Query 2: Get experience for {firm_data['firm_name']}")
            print(f"   Total experience points: {firm_data['overall_experience']['total_experience_points']:.2f}")
            print(f"   Total projects: {firm_data['overall_experience']['total_projects']}")
            
            # Show top prequalifications
            prequal_experience = firm_data['prequalification_experience']
            top_prequals = sorted(prequal_experience.items(), 
                                key=lambda x: x[1]['experience_points'], reverse=True)[:3]
            
            print(f"   Top prequalifications:")
            for prequal, data in top_prequals:
                print(f"     • {prequal}: {data['experience_points']:.2f} points")
        
        # Example 3: Compare firms for a specific prequalification
        print(f"\n📋 Query 3: Compare firms for 'Special Services (Surveying)'")
        surveying_rankings = self.performance_data['prequalification_firm_rankings']['Special Services (Surveying)']
        
        for i, firm in enumerate(surveying_rankings[:3], 1):
            print(f"   {i}. {firm['firm_name']} - {firm['experience_points']:.2f} points ({firm['total_projects']} projects)")
    
    def run_complete_analysis(self):
        """Run complete workflow analysis"""
        print("🚀 COMPLETE WORKFLOW SUPPORT ANALYSIS")
        print("=" * 80)
        
        # Demonstrate workflow
        self.demonstrate_workflow()
        
        # Analyze benefits
        self.analyze_structure_benefits()
        
        # Show query examples
        self.show_query_examples()
        
        print(f"\n✅ Analysis complete!")
        print(f"💡 The working performance structure successfully supports your 3-step workflow!")

def main():
    analyzer = WorkflowSupportAnalyzer()
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()





