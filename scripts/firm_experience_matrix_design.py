#!/usr/bin/env python3
"""
Firm Experience Matrix Design Document
Comprehensive system for calculating firm experience based on prequalifications and historical data
"""

import json
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

class FirmExperienceMatrixDesign:
    def __init__(self):
        self.design_config = {
            'time_weighting': {
                'recent_5_years': {'prime': 1.0, 'sub': 0.5},
                'recent_10_years': {'prime': 0.5, 'sub': 0.25},
                'beyond_10_years': {'prime': 0.1, 'sub': 0.01}
            },
            'prequal_categories': 61,  # Total prequalification categories
            'experience_thresholds': {
                'expert': 10,      # 10+ projects in category
                'experienced': 5,   # 5-9 projects in category
                'intermediate': 2,  # 2-4 projects in category
                'beginner': 1      # 1 project in category
            }
        }
    
    def analyze_data_structure(self):
        """Analyze current data structure and requirements"""
        print("🔍 ANALYZING DATA STRUCTURE FOR FIRM EXPERIENCE MATRIX")
        print("=" * 70)
        
        # Data sources analysis
        data_sources = {
            'award_data': {
                'file': 'award_structure_standardized.json',
                'purpose': 'Historical project awards and firm roles',
                'key_fields': ['job_number', 'prime_firm', 'subconsultants', 'award_date', 'project_value']
            },
            'firm_data': {
                'file': 'firms_data.json',
                'purpose': 'Current firm information and prequalifications',
                'key_fields': ['firm_code', 'firm_name', 'prequalifications', 'location']
            },
            'prequal_lookup': {
                'file': 'prequal_lookup.json',
                'purpose': 'Prequalification categories and firm mappings',
                'key_fields': ['category_name', 'firm_list']
            }
        }
        
        print("📊 DATA SOURCES REQUIRED:")
        for source, details in data_sources.items():
            print(f"  • {source.upper()}: {details['file']}")
            print(f"    Purpose: {details['purpose']}")
            print(f"    Key Fields: {', '.join(details['key_fields'])}")
        
        return data_sources
    
    def design_experience_calculation(self):
        """Design the experience calculation methodology"""
        print("\n🎯 EXPERIENCE CALCULATION METHODOLOGY")
        print("=" * 70)
        
        methodology = {
            'scoring_system': {
                'prime_contractor': {
                    'recent_5_years': 1.0,
                    'recent_10_years': 0.5,
                    'beyond_10_years': 0.1
                },
                'subconsultant': {
                    'recent_5_years': 0.5,
                    'recent_10_years': 0.25,
                    'beyond_10_years': 0.01
                }
            },
            'time_periods': {
                'recent_5_years': '2020-2025',
                'recent_10_years': '2015-2019',
                'beyond_10_years': 'Pre-2015'
            },
            'calculation_formula': {
                'base_score': 'project_count * role_weight * time_weight',
                'total_experience': 'sum(base_scores) for all projects in category',
                'experience_level': 'categorized based on total_experience score'
            }
        }
        
        print("📈 SCORING SYSTEM:")
        print("  Prime Contractor:")
        for period, weight in methodology['scoring_system']['prime_contractor'].items():
            print(f"    • {period}: {weight} points")
        
        print("  Subconsultant:")
        for period, weight in methodology['scoring_system']['subconsultant'].items():
            print(f"    • {period}: {weight} points")
        
        print("\n⏰ TIME PERIODS:")
        for period, years in methodology['time_periods'].items():
            print(f"  • {period}: {years}")
        
        print("\n🧮 CALCULATION FORMULA:")
        print(f"  • Base Score: {methodology['calculation_formula']['base_score']}")
        print(f"  • Total Experience: {methodology['calculation_formula']['total_experience']}")
        print(f"  • Experience Level: {methodology['calculation_formula']['experience_level']}")
        
        return methodology
    
    def design_matrix_structure(self):
        """Design the experience matrix structure"""
        print("\n📊 EXPERIENCE MATRIX STRUCTURE")
        print("=" * 70)
        
        matrix_structure = {
            'dimensions': {
                'firms': 'All firms from firms_data.json (F1-F415)',
                'prequal_categories': '61 prequalification categories',
                'experience_metrics': ['total_score', 'project_count', 'experience_level', 'last_project_date']
            },
            'matrix_format': {
                'rows': 'Firms (415 total)',
                'columns': 'Prequalification Categories (61 total)',
                'cells': 'Experience scores and metrics'
            },
            'output_format': {
                'json': 'Structured data for programmatic access',
                'excel': 'Spreadsheet format for analysis',
                'csv': 'Comma-separated values for import'
            }
        }
        
        print("📐 MATRIX DIMENSIONS:")
        print(f"  • Firms: {matrix_structure['dimensions']['firms']}")
        print(f"  • Prequal Categories: {matrix_structure['dimensions']['prequal_categories']}")
        print(f"  • Experience Metrics: {', '.join(matrix_structure['dimensions']['experience_metrics'])}")
        
        print("\n📋 MATRIX FORMAT:")
        print(f"  • Rows: {matrix_structure['matrix_format']['rows']}")
        print(f"  • Columns: {matrix_structure['matrix_format']['columns']}")
        print(f"  • Cells: {matrix_structure['matrix_format']['cells']}")
        
        print("\n💾 OUTPUT FORMATS:")
        for format_type, description in matrix_structure['output_format'].items():
            print(f"  • {format_type.upper()}: {description}")
        
        return matrix_structure
    
    def design_implementation_phases(self):
        """Design implementation phases"""
        print("\n🚀 IMPLEMENTATION PHASES")
        print("=" * 70)
        
        phases = {
            'phase_1': {
                'name': 'Data Preparation and Validation',
                'duration': '1-2 days',
                'tasks': [
                    'Load and validate award data',
                    'Load and validate firm data',
                    'Load and validate prequalification data',
                    'Cross-reference data consistency',
                    'Handle missing or inconsistent data'
                ],
                'deliverables': ['Validated data sources', 'Data quality report']
            },
            'phase_2': {
                'name': 'Experience Calculation Engine',
                'duration': '2-3 days',
                'tasks': [
                    'Implement time-weighted scoring system',
                    'Calculate experience scores for each firm-category combination',
                    'Handle edge cases and data anomalies',
                    'Implement experience level categorization',
                    'Add data validation and error handling'
                ],
                'deliverables': ['Experience calculation engine', 'Scoring validation report']
            },
            'phase_3': {
                'name': 'Matrix Generation and Optimization',
                'duration': '1-2 days',
                'tasks': [
                    'Generate complete experience matrix',
                    'Optimize matrix for performance and storage',
                    'Implement multiple output formats',
                    'Add matrix analysis and statistics',
                    'Create visualization capabilities'
                ],
                'deliverables': ['Complete experience matrix', 'Analysis reports', 'Visualizations']
            },
            'phase_4': {
                'name': 'Integration and Testing',
                'duration': '1-2 days',
                'tasks': [
                    'Integrate with prediction system',
                    'Test matrix accuracy and performance',
                    'Validate against known firm capabilities',
                    'Performance optimization',
                    'Documentation and user guides'
                ],
                'deliverables': ['Integrated system', 'Test results', 'Documentation']
            }
        }
        
        total_duration = 0
        for phase_id, phase in phases.items():
            print(f"\n📅 {phase['name'].upper()}:")
            print(f"  Duration: {phase['duration']}")
            print(f"  Tasks:")
            for task in phase['tasks']:
                print(f"    • {task}")
            print(f"  Deliverables: {', '.join(phase['deliverables'])}")
            
            # Extract duration for total calculation
            duration_str = phase['duration']
            if '1-2' in duration_str:
                total_duration += 1.5
            elif '2-3' in duration_str:
                total_duration += 2.5
        
        print(f"\n⏱️  TOTAL ESTIMATED DURATION: {total_duration} days")
        
        return phases
    
    def design_technical_architecture(self):
        """Design technical architecture for the system"""
        print("\n🏗️  TECHNICAL ARCHITECTURE")
        print("=" * 70)
        
        architecture = {
            'core_components': {
                'data_loader': {
                    'purpose': 'Load and validate data sources',
                    'inputs': ['award_data.json', 'firms_data.json', 'prequal_lookup.json'],
                    'outputs': ['validated_dataframes', 'data_quality_report']
                },
                'experience_calculator': {
                    'purpose': 'Calculate time-weighted experience scores',
                    'inputs': ['validated_award_data', 'firm_data', 'time_weights'],
                    'outputs': ['experience_scores', 'project_counts', 'experience_levels']
                },
                'matrix_generator': {
                    'purpose': 'Generate complete experience matrix',
                    'inputs': ['experience_scores', 'firm_list', 'prequal_categories'],
                    'outputs': ['experience_matrix', 'matrix_statistics']
                },
                'output_formatter': {
                    'purpose': 'Format matrix for different output types',
                    'inputs': ['experience_matrix'],
                    'outputs': ['json_output', 'excel_output', 'csv_output']
                }
            },
            'data_flow': [
                'Data Sources → Data Loader → Experience Calculator → Matrix Generator → Output Formatter → Final Matrix'
            ],
            'performance_considerations': {
                'memory_optimization': 'Process data in chunks for large datasets',
                'caching': 'Cache intermediate results for faster processing',
                'parallel_processing': 'Use multiprocessing for large calculations',
                'storage_optimization': 'Use efficient data structures and compression'
            }
        }
        
        print("🔧 CORE COMPONENTS:")
        for component, details in architecture['core_components'].items():
            print(f"  • {component.replace('_', ' ').title()}:")
            print(f"    Purpose: {details['purpose']}")
            print(f"    Inputs: {', '.join(details['inputs'])}")
            print(f"    Outputs: {', '.join(details['outputs'])}")
        
        print("\n🔄 DATA FLOW:")
        for flow in architecture['data_flow']:
            print(f"  {flow}")
        
        print("\n⚡ PERFORMANCE CONSIDERATIONS:")
        for consideration, description in architecture['performance_considerations'].items():
            print(f"  • {consideration.replace('_', ' ').title()}: {description}")
        
        return architecture
    
    def generate_implementation_plan(self):
        """Generate comprehensive implementation plan"""
        print("\n📋 COMPREHENSIVE IMPLEMENTATION PLAN")
        print("=" * 70)
        
        plan = {
            'overview': 'Build firm experience matrix based on historical award data and prequalifications',
            'objectives': [
                'Calculate time-weighted experience scores for each firm-category combination',
                'Generate comprehensive experience matrix (415 firms × 61 categories)',
                'Provide multiple output formats for different use cases',
                'Integrate with prediction system for improved accuracy'
            ],
            'success_criteria': [
                '100% data coverage (all firms and categories)',
                'Accurate time-weighted scoring',
                'Performance: Generate matrix in <5 minutes',
                'Integration: Seamless connection with prediction system'
            ],
            'risks_and_mitigation': {
                'data_quality': {
                    'risk': 'Inconsistent or missing data',
                    'mitigation': 'Robust data validation and cleaning'
                },
                'performance': {
                    'risk': 'Slow processing for large matrix',
                    'mitigation': 'Optimized algorithms and parallel processing'
                },
                'accuracy': {
                    'risk': 'Incorrect experience calculations',
                    'mitigation': 'Comprehensive testing and validation'
                }
            }
        }
        
        print("🎯 OBJECTIVES:")
        for i, objective in enumerate(plan['objectives'], 1):
            print(f"  {i}. {objective}")
        
        print("\n✅ SUCCESS CRITERIA:")
        for i, criterion in enumerate(plan['success_criteria'], 1):
            print(f"  {i}. {criterion}")
        
        print("\n⚠️  RISKS AND MITIGATION:")
        for risk, details in plan['risks_and_mitigation'].items():
            print(f"  • {risk.replace('_', ' ').title()}:")
            print(f"    Risk: {details['risk']}")
            print(f"    Mitigation: {details['mitigation']}")
        
        return plan

def main():
    """Main function to generate design document"""
    print("🎯 FIRM EXPERIENCE MATRIX DESIGN DOCUMENT")
    print("=" * 80)
    
    designer = FirmExperienceMatrixDesign()
    
    # Generate all design components
    data_sources = designer.analyze_data_structure()
    methodology = designer.design_experience_calculation()
    matrix_structure = designer.design_matrix_structure()
    phases = designer.design_implementation_phases()
    architecture = designer.design_technical_architecture()
    plan = designer.generate_implementation_plan()
    
    # Save design document
    design_document = {
        'timestamp': datetime.now().isoformat(),
        'data_sources': data_sources,
        'methodology': methodology,
        'matrix_structure': matrix_structure,
        'implementation_phases': phases,
        'technical_architecture': architecture,
        'implementation_plan': plan
    }
    
    filename = f"firm_experience_matrix_design_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(design_document, f, indent=2)
    
    print(f"\n✅ Design document saved: {filename}")
    print("\n🎯 READY TO PROCEED WITH IMPLEMENTATION!")

if __name__ == "__main__":
    main()





