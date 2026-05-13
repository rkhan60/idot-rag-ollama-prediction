#!/usr/bin/env python3
"""
Test Phase 1 Improvements
Evaluate accuracy improvements from data standardization
"""

import json
import os
import sys
from datetime import datetime

# Add the current directory to path to import the Phase 2.1 system
sys.path.append('.')

class Phase1ImprovementTester:
    def __init__(self):
        self.data_dir = '../data'
        self.results = {}
        
    def load_standardized_data(self):
        """Load the standardized data files"""
        print("🔄 Loading standardized data...")
        
        # Load standardized award structure
        with open(f'{self.data_dir}/award_structure_standardized.json', 'r') as f:
            self.award_structure = json.load(f)
        print(f"✅ Loaded {len(self.award_structure)} standardized award records")
        
        # Load standardized firms data
        with open(f'{self.data_dir}/firms_data_standardized.json', 'r') as f:
            self.firms_data = json.load(f)
        print(f"✅ Loaded {len(self.firms_data)} standardized firm records")
        
    def compare_data_quality(self):
        """Compare data quality before and after standardization"""
        print("\n🔍 Comparing Data Quality...")
        
        # Load original data for comparison
        with open(f'{self.data_dir}/award_structure.json', 'r') as f:
            original_award_structure = json.load(f)
            
        with open(f'{self.data_dir}/firms_data.json', 'r') as f:
            original_firms_data = json.load(f)
            
        # Calculate improvements
        improvements = {
            'job_number_standardization': self.analyze_job_number_improvements(original_award_structure),
            'subconsultant_fixes': self.analyze_subconsultant_improvements(original_award_structure),
            'firm_name_normalization': self.analyze_firm_name_improvements(original_award_structure),
            'missing_field_fixes': self.analyze_missing_field_improvements(original_award_structure)
        }
        
        self.results['improvements'] = improvements
        return improvements
        
    def analyze_job_number_improvements(self, original_data):
        """Analyze job number standardization improvements"""
        original_formats = set()
        standardized_formats = set()
        
        for record in original_data:
            if record.get('Job #'):
                original_formats.add(str(record['Job #'])[:3])
                
        for record in self.award_structure:
            if record.get('Job #'):
                standardized_formats.add(str(record['Job #'])[:3])
                
        return {
            'original_variations': len(original_formats),
            'standardized_variations': len(standardized_formats),
            'reduction': len(original_formats) - len(standardized_formats),
            'improvement_percent': ((len(original_formats) - len(standardized_formats)) / len(original_formats) * 100) if original_formats else 0
        }
        
    def analyze_subconsultant_improvements(self, original_data):
        """Analyze subconsultant data improvements"""
        original_missing = sum(1 for record in original_data if not record.get('SUBCONSULTANTS') or record['SUBCONSULTANTS'] is None)
        standardized_missing = sum(1 for record in self.award_structure if not record.get('SUBCONSULTANTS') or record['SUBCONSULTANTS'] == [])
        
        return {
            'original_missing': original_missing,
            'standardized_missing': standardized_missing,
            'fixed_count': original_missing - standardized_missing,
            'improvement_percent': ((original_missing - standardized_missing) / original_missing * 100) if original_missing > 0 else 0
        }
        
    def analyze_firm_name_improvements(self, original_data):
        """Analyze firm name normalization improvements"""
        original_names = set()
        standardized_names = set()
        
        for record in original_data:
            if record.get('SELECTED FIRM'):
                original_names.add(record['SELECTED FIRM'].strip().upper())
                
        for record in self.award_structure:
            if record.get('SELECTED FIRM'):
                standardized_names.add(record['SELECTED FIRM'].strip().upper())
                
        return {
            'original_unique_names': len(original_names),
            'standardized_unique_names': len(standardized_names),
            'duplicates_removed': len(original_names) - len(standardized_names),
            'improvement_percent': ((len(original_names) - len(standardized_names)) / len(original_names) * 100) if original_names else 0
        }
        
    def analyze_missing_field_improvements(self, original_data):
        """Analyze missing field improvements"""
        fields_to_check = ['Fee Estimate', 'Submitted', 'Eligible', 'First Alternate', 'Second Alternate']
        
        original_missing = 0
        standardized_missing = 0
        
        for record in original_data:
            for field in fields_to_check:
                if field not in record or record[field] is None:
                    original_missing += 1
                    
        for record in self.award_structure:
            for field in fields_to_check:
                if field not in record or record[field] is None:
                    standardized_missing += 1
                    
        return {
            'original_missing_fields': original_missing,
            'standardized_missing_fields': standardized_missing,
            'fields_fixed': original_missing - standardized_missing,
            'improvement_percent': ((original_missing - standardized_missing) / original_missing * 100) if original_missing > 0 else 0
        }
        
    def estimate_accuracy_improvement(self):
        """Estimate accuracy improvement based on data quality fixes"""
        print("\n📊 Estimating Accuracy Improvement...")
        
        improvements = self.results['improvements']
        
        # Calculate weighted improvement based on DeepSeek analysis
        accuracy_improvement = 0
        
        # Job number standardization impact (10% weight)
        job_improvement = improvements['job_number_standardization']['improvement_percent']
        accuracy_improvement += (job_improvement * 0.1)
        
        # Subconsultant fixes impact (30% weight)
        sub_improvement = improvements['subconsultant_fixes']['improvement_percent']
        accuracy_improvement += (sub_improvement * 0.3)
        
        # Firm name normalization impact (20% weight)
        firm_improvement = improvements['firm_name_normalization']['improvement_percent']
        accuracy_improvement += (firm_improvement * 0.2)
        
        # Missing field fixes impact (10% weight)
        field_improvement = improvements['missing_field_fixes']['improvement_percent']
        accuracy_improvement += (field_improvement * 0.1)
        
        # Base improvement from data quality (30% weight)
        base_improvement = 5.0  # Conservative estimate
        accuracy_improvement += base_improvement
        
        self.results['estimated_accuracy_improvement'] = {
            'current_accuracy': 30.4,
            'estimated_new_accuracy': 30.4 + accuracy_improvement,
            'improvement_points': accuracy_improvement,
            'improvement_percent': (accuracy_improvement / 30.4) * 100
        }
        
        print(f"📈 Estimated Accuracy Improvement: {accuracy_improvement:.1f} points")
        print(f"🎯 New Estimated Accuracy: {30.4 + accuracy_improvement:.1f}%")
        
        return self.results['estimated_accuracy_improvement']
        
    def generate_improvement_report(self):
        """Generate comprehensive improvement report"""
        print("\n📋 Generating Improvement Report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'phase1_improvement_report_{timestamp}.txt'
        
        with open(report_file, 'w') as f:
            f.write("PHASE 1 IMPROVEMENT TEST REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("DATA QUALITY IMPROVEMENTS\n")
            f.write("-" * 30 + "\n")
            
            improvements = self.results['improvements']
            
            # Job Numbers
            job_imp = improvements['job_number_standardization']
            f.write(f"Job Number Standardization:\n")
            f.write(f"  Original Variations: {job_imp['original_variations']}\n")
            f.write(f"  Standardized Variations: {job_imp['standardized_variations']}\n")
            f.write(f"  Reduction: {job_imp['reduction']}\n")
            f.write(f"  Improvement: {job_imp['improvement_percent']:.1f}%\n\n")
            
            # Subconsultants
            sub_imp = improvements['subconsultant_fixes']
            f.write(f"Subconsultant Data Fixes:\n")
            f.write(f"  Original Missing: {sub_imp['original_missing']}\n")
            f.write(f"  Standardized Missing: {sub_imp['standardized_missing']}\n")
            f.write(f"  Fixed Count: {sub_imp['fixed_count']}\n")
            f.write(f"  Improvement: {sub_imp['improvement_percent']:.1f}%\n\n")
            
            # Firm Names
            firm_imp = improvements['firm_name_normalization']
            f.write(f"Firm Name Normalization:\n")
            f.write(f"  Original Unique Names: {firm_imp['original_unique_names']}\n")
            f.write(f"  Standardized Unique Names: {firm_imp['standardized_unique_names']}\n")
            f.write(f"  Duplicates Removed: {firm_imp['duplicates_removed']}\n")
            f.write(f"  Improvement: {firm_imp['improvement_percent']:.1f}%\n\n")
            
            # Missing Fields
            field_imp = improvements['missing_field_fixes']
            f.write(f"Missing Field Fixes:\n")
            f.write(f"  Original Missing: {field_imp['original_missing_fields']}\n")
            f.write(f"  Standardized Missing: {field_imp['standardized_missing_fields']}\n")
            f.write(f"  Fields Fixed: {field_imp['fields_fixed']}\n")
            f.write(f"  Improvement: {field_imp['improvement_percent']:.1f}%\n\n")
            
            # Accuracy Estimation
            acc_imp = self.results['estimated_accuracy_improvement']
            f.write("ACCURACY IMPROVEMENT ESTIMATION\n")
            f.write("-" * 35 + "\n")
            f.write(f"Current Accuracy: {acc_imp['current_accuracy']}%\n")
            f.write(f"Estimated New Accuracy: {acc_imp['estimated_new_accuracy']:.1f}%\n")
            f.write(f"Improvement Points: {acc_imp['improvement_points']:.1f}\n")
            f.write(f"Improvement Percent: {acc_imp['improvement_percent']:.1f}%\n\n")
            
            f.write("NEXT STEPS\n")
            f.write("-" * 10 + "\n")
            f.write("1. Test the standardized data with Phase 2.1 system\n")
            f.write("2. Measure actual accuracy improvements\n")
            f.write("3. Proceed to Phase 2 algorithm improvements\n")
            f.write("4. Implement RAG system fixes\n")
            
        print(f"✅ Improvement report saved: {report_file}")
        return report_file
        
    def run_improvement_test(self):
        """Run complete improvement test"""
        print("🚀 Starting Phase 1 Improvement Test...")
        
        # Load standardized data
        self.load_standardized_data()
        
        # Compare data quality
        improvements = self.compare_data_quality()
        
        # Estimate accuracy improvement
        accuracy_estimation = self.estimate_accuracy_improvement()
        
        # Generate report
        report_file = self.generate_improvement_report()
        
        print(f"\n✅ Phase 1 Improvement Test Complete!")
        print(f"📄 Report: {report_file}")
        
        return self.results

if __name__ == "__main__":
    tester = Phase1ImprovementTester()
    results = tester.run_improvement_test()
