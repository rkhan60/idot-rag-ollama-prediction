#!/usr/bin/env python3
"""
Bulletin Structure Analysis with DeepSeek
Analyze bulletin structure and extract key patterns for model training
"""

import json
import subprocess
import sys
from datetime import datetime

class BulletinStructureAnalyzer:
    def __init__(self):
        self.data_dir = '../data'
        
    def analyze_with_deepseek(self, bulletin_text):
        """Analyze bulletin structure using DeepSeek"""
        print("🔍 ANALYZING BULLETIN STRUCTURE WITH DEEPSEEK")
        print("=" * 60)
        
        # Create analysis prompt
        prompt = f"""
ANALYZE THIS IDOT PUBLIC TENDER BULLETIN STRUCTURE:

{bulletin_text}

TASK: Analyze the bulletin structure and extract key patterns for model training.

REQUIRED ANALYSIS:

1. PROJECT STRUCTURE PATTERNS:
   - Job Number format and location
   - Project title format
   - Location information format
   - District information format
   - Phase type identification

2. PREQUALIFICATION REQUIREMENTS:
   - How are prequalifications stated in the bulletin?
   - Exact format and location of prequalification requirements
   - Multiple prequalification patterns
   - Single prequalification patterns

3. KEY PERSONNEL REQUIREMENTS:
   - How are key personnel requirements stated?
   - Format of Exhibit A references
   - Required qualifications and certifications

4. PROJECT DETAILS:
   - DBE participation requirements
   - Complexity factor information
   - Project scope and description patterns
   - Timeline and completion requirements

5. MAPPING PATTERNS:
   - How to map bulletin prequalifications to lookup categories
   - Format variations between bulletin and lookup
   - Standardization rules needed

PROVIDE A DETAILED ANALYSIS WITH:
- Specific examples from the bulletin
- Pattern recognition
- Format standardization rules
- Model training recommendations
- Data extraction strategies

Focus on making the model understand how to extract the 5 critical details:
1. Project Number (Job No.)
2. Project Exact Location
3. District
4. Phase Type
5. Exhibit A (Prequalification Requirements)
"""
        
        # Call DeepSeek for analysis
        try:
            print("🤖 Calling DeepSeek for analysis...")
            result = subprocess.run([
                'ollama', 'run', 'deepseek-r1:8b',
                prompt
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                analysis = result.stdout
                print("✅ DeepSeek analysis completed successfully!")
                return analysis
            else:
                print(f"❌ DeepSeek analysis failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ DeepSeek analysis timed out")
            return None
        except Exception as e:
            print(f"❌ Error calling DeepSeek: {e}")
            return None
            
    def extract_bulletin_patterns(self, bulletin_text):
        """Extract key patterns from bulletin text"""
        print("\n🔍 EXTRACTING BULLETIN PATTERNS")
        print("=" * 50)
        
        patterns = {
            'job_number_patterns': [],
            'location_patterns': [],
            'district_patterns': [],
            'phase_patterns': [],
            'prequalification_patterns': [],
            'personnel_patterns': []
        }
        
        lines = bulletin_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Job Number patterns
            if 'Job No.' in line:
                patterns['job_number_patterns'].append(line)
                
            # Location patterns
            if any(word in line for word in ['County', 'Counties', 'Route', 'Routes']):
                patterns['location_patterns'].append(line)
                
            # District patterns
            if 'District' in line:
                patterns['district_patterns'].append(line)
                
            # Phase patterns
            if 'Phase' in line:
                patterns['phase_patterns'].append(line)
                
            # Prequalification patterns
            if 'prequalified' in line.lower() or 'prequalification' in line.lower():
                patterns['prequalification_patterns'].append(line)
                
            # Personnel patterns
            if 'Exhibit A' in line or 'Key personnel' in line:
                patterns['personnel_patterns'].append(line)
                
        return patterns
        
    def analyze_prequalification_formats(self, bulletin_text):
        """Analyze prequalification format variations"""
        print("\n🔍 ANALYZING PREQUALIFICATION FORMATS")
        print("=" * 50)
        
        prequal_formats = []
        
        # Extract prequalification statements
        lines = bulletin_text.split('\n')
        for line in lines:
            if 'prequalified' in line.lower() or 'prequalification' in line.lower():
                prequal_formats.append(line.strip())
                
        # Analyze format variations
        format_analysis = {
            'parentheses_format': [],
            'hyphen_format': [],
            'colon_format': [],
            'other_formats': []
        }
        
        for prequal in prequal_formats:
            if '(' in prequal and ')' in prequal:
                format_analysis['parentheses_format'].append(prequal)
            elif ' - ' in prequal:
                format_analysis['hyphen_format'].append(prequal)
            elif ':' in prequal:
                format_analysis['colon_format'].append(prequal)
            else:
                format_analysis['other_formats'].append(prequal)
                
        return format_analysis
        
    def generate_mapping_rules(self, format_analysis):
        """Generate mapping rules for prequalification formats"""
        print("\n🔍 GENERATING MAPPING RULES")
        print("=" * 50)
        
        mapping_rules = {
            'parentheses_to_hyphen': {},
            'colon_to_hyphen': {},
            'standardization_rules': []
        }
        
        # Analyze parentheses format
        for prequal in format_analysis['parentheses_format']:
            # Extract category and service from parentheses format
            # Example: "Special Services (Quality Assurance HMA & Aggregate)"
            if '(' in prequal and ')' in prequal:
                category = prequal.split('(')[0].strip()
                service = prequal.split('(')[1].split(')')[0].strip()
                hyphen_format = f"{category} - {service}"
                mapping_rules['parentheses_to_hyphen'][prequal] = hyphen_format
                
        # Analyze colon format
        for prequal in format_analysis['colon_format']:
            # Extract category and service from colon format
            # Example: "Special Services: Quality Assurance HMA & Aggregate"
            if ':' in prequal:
                parts = prequal.split(':')
                if len(parts) >= 2:
                    category = parts[0].strip()
                    service = parts[1].strip()
                    hyphen_format = f"{category} - {service}"
                    mapping_rules['colon_to_hyphen'][prequal] = hyphen_format
                    
        # Generate standardization rules
        mapping_rules['standardization_rules'] = [
            "Replace parentheses () with hyphens -",
            "Replace colons : with hyphens -",
            "Standardize spacing around hyphens",
            "Maintain category and service separation"
        ]
        
        return mapping_rules
        
    def create_training_recommendations(self, patterns, format_analysis, mapping_rules):
        """Create model training recommendations"""
        print("\n🔍 CREATING TRAINING RECOMMENDATIONS")
        print("=" * 50)
        
        recommendations = {
            'data_extraction_strategies': [],
            'format_standardization': [],
            'model_training_approach': [],
            'validation_strategies': []
        }
        
        # Data extraction strategies
        recommendations['data_extraction_strategies'] = [
            "Extract Job Number using regex pattern: 'Job No\\. [A-Z]-\\d+-\\d+-\\d+'",
            "Extract Location from lines containing 'County' or 'Route'",
            "Extract District from lines containing 'District'",
            "Extract Phase from lines containing 'Phase'",
            "Extract Prequalifications from lines containing 'prequalified' or 'prequalification'"
        ]
        
        # Format standardization
        recommendations['format_standardization'] = [
            "Convert bulletin parentheses format to hyphen format",
            "Standardize spacing and punctuation",
            "Map to prequal_lookup.json categories",
            "Handle multiple prequalifications per project"
        ]
        
        # Model training approach
        recommendations['model_training_approach'] = [
            "Train on bulletin text extraction",
            "Train on format standardization",
            "Train on category mapping",
            "Train on multi-label classification for prequalifications"
        ]
        
        # Validation strategies
        recommendations['validation_strategies'] = [
            "Cross-validate with IDOT Excel data",
            "Validate against known project requirements",
            "Test format standardization accuracy",
            "Verify category mapping completeness"
        ]
        
        return recommendations
        
    def generate_comprehensive_report(self, bulletin_text):
        """Generate comprehensive bulletin analysis report"""
        print("🚀 GENERATING COMPREHENSIVE BULLETIN ANALYSIS REPORT")
        print("=" * 70)
        
        # Extract patterns
        patterns = self.extract_bulletin_patterns(bulletin_text)
        
        # Analyze prequalification formats
        format_analysis = self.analyze_prequalification_formats(bulletin_text)
        
        # Generate mapping rules
        mapping_rules = self.generate_mapping_rules(format_analysis)
        
        # Create training recommendations
        recommendations = self.create_training_recommendations(patterns, format_analysis, mapping_rules)
        
        # Get DeepSeek analysis
        deepseek_analysis = self.analyze_with_deepseek(bulletin_text)
        
        # Generate report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'bulletin_structure_analysis_{timestamp}.txt'
        
        with open(report_file, 'w') as f:
            f.write("BULLETIN STRUCTURE ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Purpose: Analyze IDOT bulletin structure for model training\n")
            f.write("Focus: Extract 5 critical project details and prequalification mapping\n\n")
            
            f.write("DEEPSEEK ANALYSIS\n")
            f.write("-" * 20 + "\n")
            if deepseek_analysis:
                f.write(deepseek_analysis)
            else:
                f.write("DeepSeek analysis not available\n")
            f.write("\n")
            
            f.write("PATTERN ANALYSIS\n")
            f.write("-" * 20 + "\n")
            for pattern_type, pattern_list in patterns.items():
                f.write(f"\n{pattern_type.upper()}:\n")
                for pattern in pattern_list[:5]:  # Show first 5 examples
                    f.write(f"  - {pattern}\n")
            f.write("\n")
            
            f.write("PREQUALIFICATION FORMAT ANALYSIS\n")
            f.write("-" * 35 + "\n")
            for format_type, format_list in format_analysis.items():
                f.write(f"\n{format_type.upper()}:\n")
                for fmt in format_list[:3]:  # Show first 3 examples
                    f.write(f"  - {fmt}\n")
            f.write("\n")
            
            f.write("MAPPING RULES\n")
            f.write("-" * 15 + "\n")
            for rule_type, rule_dict in mapping_rules.items():
                f.write(f"\n{rule_type.upper()}:\n")
                if isinstance(rule_dict, dict):
                    for key, value in list(rule_dict.items())[:3]:  # Show first 3
                        f.write(f"  {key} -> {value}\n")
                elif isinstance(rule_dict, list):
                    for rule in rule_dict:
                        f.write(f"  - {rule}\n")
            f.write("\n")
            
            f.write("TRAINING RECOMMENDATIONS\n")
            f.write("-" * 25 + "\n")
            for rec_type, rec_list in recommendations.items():
                f.write(f"\n{rec_type.upper()}:\n")
                for rec in rec_list:
                    f.write(f"  - {rec}\n")
            f.write("\n")
            
            f.write("NEXT STEPS\n")
            f.write("-" * 12 + "\n")
            f.write("1. Standardize prequal_lookup.json to match bulletin format\n")
            f.write("2. Create bulletin text extraction model\n")
            f.write("3. Implement format standardization pipeline\n")
            f.write("4. Train category mapping model\n")
            f.write("5. Validate with real bulletin data\n")
            
        print(f"✅ Comprehensive report saved: {report_file}")
        
        return {
            'patterns': patterns,
            'format_analysis': format_analysis,
            'mapping_rules': mapping_rules,
            'recommendations': recommendations,
            'deepseek_analysis': deepseek_analysis,
            'report_file': report_file
        }

def main():
    # Sample bulletin text (you can replace with actual bulletin)
    bulletin_text = """
    Job No. D-91-516-11, Various Subsurface Utility Engineering Projects, Various Routes, Various Counties, Region One, District One.
    
    The prime firm must be prequalified in the Special Services (Subsurface Utility Engineering) category to be considered for this project.
    
    Job No. C-91-390-11, US-30 – Briarcliff Rd. to US 34 & West of IL 31 (West Lake St.) to East of BNSF RR, Phase III Project, Kane and Kendall Counties, Region One/District One.
    
    The prime firm must be prequalified in the Special Services (Construction Inspection) category to be considered for this project.
    
    Job No. D-91-506-11, Various Phase II Projects, Various Routes, Various Counties, Region One, District One.
    
    The prime firm must be prequalified in the following categories to be considered for this project:
    Highways (Roads & Streets)
    Structures (Highway: Typical)
    Special Services (Surveying)
    """
    
    analyzer = BulletinStructureAnalyzer()
    results = analyzer.generate_comprehensive_report(bulletin_text)
    
    print(f"\n🎯 ANALYSIS COMPLETE!")
    print(f"   Report saved: {results['report_file']}")
    print(f"   Patterns found: {len(results['patterns'])}")
    print(f"   Format variations: {len(results['format_analysis'])}")
    print(f"   Mapping rules: {len(results['mapping_rules'])}")

if __name__ == "__main__":
    main()
