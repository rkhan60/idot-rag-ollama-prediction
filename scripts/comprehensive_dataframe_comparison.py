#!/usr/bin/env python3
"""
Comprehensive Dataframe Comparison
=================================
Compare Book2.xlsx with our existing data frames to identify:
- Firm overlaps and gaps
- Category naming convention differences
- Geographic coverage comparison
- Data quality insights
"""

import pandas as pd
import json
import re
from collections import defaultdict

class DataframeComparator:
    def __init__(self):
        self.book2_data = None
        self.award_data = None
        self.firms_data = None
        self.district_mapping = None
        self.prequal_lookup = None
        
    def load_all_data(self):
        """Load all data sources for comparison"""
        print("🔄 Loading all data sources...")
        
        # Load Book2.xlsx
        try:
            self.book2_data = pd.read_excel('../data/Book2.xlsx')
            print("✅ Book2.xlsx loaded successfully")
        except Exception as e:
            print(f"❌ Error loading Book2.xlsx: {e}")
            return False
            
        # Load award_structure.json
        try:
            with open('../data/award_structure.json', 'r') as f:
                self.award_data = json.load(f)
            print("✅ award_structure.json loaded successfully")
        except Exception as e:
            print(f"❌ Error loading award_structure.json: {e}")
            return False
            
        # Load firms_data.json
        try:
            with open('../data/firms_data.json', 'r') as f:
                self.firms_data = json.load(f)
            print("✅ firms_data.json loaded successfully")
        except Exception as e:
            print(f"❌ Error loading firms_data.json: {e}")
            return False
            
        # Load district_mapping_clean.json
        try:
            with open('../data/district_mapping_clean.json', 'r') as f:
                self.district_mapping = json.load(f)
            print("✅ district_mapping_clean.json loaded successfully")
        except Exception as e:
            print(f"❌ Error loading district_mapping_clean.json: {e}")
            return False
            
        # Load prequal_lookup.json
        try:
            with open('../data/prequal_lookup.json', 'r') as f:
                self.prequal_lookup = json.load(f)
            print("✅ prequal_lookup.json loaded successfully")
        except Exception as e:
            print(f"❌ Error loading prequal_lookup.json: {e}")
            return False
            
        return True
    
    def extract_book2_firms(self):
        """Extract firm information from Book2 hierarchical structure"""
        if self.book2_data is None:
            return {}
            
        firms = {}
        current_state = None
        current_city = None
        
        for idx, row in self.book2_data.iterrows():
            state = row['STATE']
            city = row['CITY']
            firm = row['FIRM']
            email = row['EMAIL']
            is_dbe = row['IS DBE']
            categories = row['PRE-QUAL CATEGORIES']
            
            if pd.notna(state):
                current_state = state
            if pd.notna(city):
                current_city = city
            if pd.notna(firm):
                firm_key = f"{firm}_{current_city}_{current_state}"
                firms[firm_key] = {
                    'firm_name': firm,
                    'city': current_city,
                    'state': current_state,
                    'email': email,
                    'is_dbe': is_dbe,
                    'categories': []
                }
            
            if pd.notna(categories) and firm_key in firms:
                category = str(categories).strip()
                if category and category != 'nan':
                    firms[firm_key]['categories'].append(category)
        
        return firms
    
    def extract_award_firms(self):
        """Extract unique firms from award data"""
        if self.award_data is None:
            return set()
            
        firms = set()
        for award in self.award_data:
            if 'SELECTED FIRM' in award and award['SELECTED FIRM']:
                firms.add(award['SELECTED FIRM'])
            if 'SUBCONSULTANTS' in award and award['SUBCONSULTANTS']:
                if isinstance(award['SUBCONSULTANTS'], str):
                    subconsultants = award['SUBCONSULTANTS'].split(',')
                    for sub in subconsultants:
                        firms.add(sub.strip())
        return firms
    
    def extract_district_firms(self):
        """Extract firms from district mapping"""
        if self.district_mapping is None:
            return {}
            
        firms = {}
        for district, district_firms in self.district_mapping.items():
            if isinstance(district_firms, list):
                for firm in district_firms:
                    if isinstance(firm, dict) and 'firm_name' in firm:
                        firm_key = f"{firm['firm_name']}_{firm.get('city', 'Unknown')}_{firm.get('state', 'IL')}"
                        firms[firm_key] = {
                            'firm_name': firm['firm_name'],
                            'city': firm.get('city', 'Unknown'),
                            'state': firm.get('state', 'IL'),
                            'district': district,
                            'status': firm.get('status', 'Unknown')
                        }
        return firms
    
    def normalize_category_name(self, category):
        """Convert Book2 category format to lookup format"""
        # Replace " - " with " (" and add ")"
        normalized = category.replace(" - ", " (")
        if not normalized.endswith(")"):
            normalized += ")"
        return normalized
    
    def compare_firms(self):
        """Compare firms across all data sources"""
        print("\n🔍 FIRM COMPARISON ANALYSIS")
        print("=" * 60)
        
        book2_firms = self.extract_book2_firms()
        award_firms = self.extract_award_firms()
        district_firms = self.extract_district_firms()
        
        print(f"📊 Firm Counts:")
        print(f"   Book2.xlsx: {len(book2_firms)} firms")
        print(f"   Award Data: {len(award_firms)} firms")
        print(f"   District Mapping: {len(district_firms)} firms")
        print()
        
        # Find overlaps
        book2_firm_names = {firm['firm_name'] for firm in book2_firms.values()}
        award_firm_names = award_firms
        district_firm_names = {firm['firm_name'] for firm in district_firms.values()}
        
        # Book2 vs Award overlap
        book2_award_overlap = book2_firm_names.intersection(award_firm_names)
        print(f"🔗 Book2 vs Award Data Overlap:")
        print(f"   Overlapping firms: {len(book2_award_overlap)}")
        print(f"   Overlap rate: {len(book2_award_overlap)/len(book2_firm_names)*100:.1f}%")
        
        if book2_award_overlap:
            print(f"   Sample overlaps: {list(book2_award_overlap)[:5]}")
        print()
        
        # Book2 vs District overlap
        book2_district_overlap = book2_firm_names.intersection(district_firm_names)
        print(f"🔗 Book2 vs District Mapping Overlap:")
        print(f"   Overlapping firms: {len(book2_district_overlap)}")
        print(f"   Overlap rate: {len(book2_district_overlap)/len(book2_firm_names)*100:.1f}%")
        
        if book2_district_overlap:
            print(f"   Sample overlaps: {list(book2_district_overlap)[:5]}")
        print()
        
        # All three overlap
        all_overlap = book2_firm_names.intersection(award_firm_names).intersection(district_firm_names)
        print(f"🔗 All Three Sources Overlap:")
        print(f"   Firms in all sources: {len(all_overlap)}")
        print(f"   Complete coverage rate: {len(all_overlap)/len(book2_firm_names)*100:.1f}%")
        print()
        
        return {
            'book2_firms': book2_firms,
            'award_firms': award_firms,
            'district_firms': district_firms,
            'overlaps': {
                'book2_award': book2_award_overlap,
                'book2_district': book2_district_overlap,
                'all_three': all_overlap
            }
        }
    
    def compare_categories(self):
        """Compare prequalification categories across sources"""
        print("🔍 CATEGORY COMPARISON ANALYSIS")
        print("=" * 60)
        
        # Extract Book2 categories
        book2_categories = set()
        book2_firms = self.extract_book2_firms()
        for firm_data in book2_firms.values():
            book2_categories.update(firm_data['categories'])
        
        # Extract lookup categories
        lookup_categories = set()
        for main_cat, subcats_data in self.prequal_lookup.items():
            lookup_categories.add(main_cat)
            if 'sub_categories' in subcats_data:
                for subcat_key, subcat_info in subcats_data['sub_categories'].items():
                    full_name = subcat_info.get('full_prequal_name', '')
                    if full_name:
                        lookup_categories.add(full_name)
        
        print(f"📊 Category Counts:")
        print(f"   Book2.xlsx: {len(book2_categories)} categories")
        print(f"   Prequal Lookup: {len(lookup_categories)} categories")
        print()
        
        # Test normalization
        normalized_book2 = {self.normalize_category_name(cat) for cat in book2_categories}
        
        # Find matches after normalization
        exact_matches = normalized_book2.intersection(lookup_categories)
        print(f"🔗 Category Matching (After Normalization):")
        print(f"   Exact matches: {len(exact_matches)}")
        print(f"   Match rate: {len(exact_matches)/len(book2_categories)*100:.1f}%")
        print()
        
        # Show some matches
        if exact_matches:
            print(f"✅ Sample Exact Matches:")
            for category in sorted(list(exact_matches))[:10]:
                print(f"   ✅ {category}")
            print()
        
        # Show some mismatches
        book2_only = normalized_book2 - lookup_categories
        if book2_only:
            print(f"⚠️  Categories in Book2 only (first 10):")
            for category in sorted(list(book2_only))[:10]:
                print(f"   ❌ {category}")
            print()
        
        lookup_only = lookup_categories - normalized_book2
        if lookup_only:
            print(f"⚠️  Categories in Lookup only (first 10):")
            for category in sorted(list(lookup_only))[:10]:
                print(f"   ❌ {category}")
            print()
        
        return {
            'book2_categories': book2_categories,
            'lookup_categories': lookup_categories,
            'normalized_book2': normalized_book2,
            'exact_matches': exact_matches,
            'book2_only': book2_only,
            'lookup_only': lookup_only
        }
    
    def compare_geographic_coverage(self):
        """Compare geographic coverage across sources"""
        print("🔍 GEOGRAPHIC COVERAGE COMPARISON")
        print("=" * 60)
        
        # Book2 geographic coverage
        book2_firms = self.extract_book2_firms()
        book2_states = set()
        book2_cities = set()
        
        for firm_data in book2_firms.values():
            if firm_data['state']:
                book2_states.add(firm_data['state'])
            if firm_data['city']:
                book2_cities.add(firm_data['city'])
        
        # District mapping geographic coverage
        district_states = set()
        district_cities = set()
        
        for district, district_firms in self.district_mapping.items():
            if isinstance(district_firms, list):
                for firm in district_firms:
                    if isinstance(firm, dict):
                        if firm.get('state'):
                            district_states.add(firm['state'])
                        if firm.get('city'):
                            district_cities.add(firm['city'])
        
        print(f"📊 Geographic Coverage:")
        print(f"   Book2.xlsx:")
        print(f"     States: {len(book2_states)} - {sorted(list(book2_states))}")
        print(f"     Cities: {len(book2_cities)}")
        print()
        print(f"   District Mapping:")
        print(f"     States: {len(district_states)} - {sorted(list(district_states))}")
        print(f"     Cities: {len(district_cities)}")
        print()
        
        # Illinois focus comparison
        book2_il_cities = {city for city in book2_cities if any(firm['state'] == 'IL' for firm in book2_firms.values() if firm['city'] == city)}
        district_il_cities = {city for city in district_cities if any(firm.get('state') == 'IL' for firm in district_firms if isinstance(firm, dict) and firm.get('city') == city)}
        
        print(f"🌍 Illinois Focus:")
        print(f"   Book2 IL Cities: {len(book2_il_cities)}")
        print(f"   District IL Cities: {len(district_il_cities)}")
        print(f"   Common IL Cities: {len(book2_il_cities.intersection(district_il_cities))}")
        print()
        
        return {
            'book2_states': book2_states,
            'book2_cities': book2_cities,
            'district_states': district_states,
            'district_cities': district_cities,
            'book2_il_cities': book2_il_cities,
            'district_il_cities': district_il_cities
        }
    
    def generate_recommendations(self, firm_comparison, category_comparison, geo_comparison):
        """Generate actionable recommendations based on comparison"""
        print("🎯 RECOMMENDATIONS & ACTION ITEMS")
        print("=" * 60)
        
        print("📋 1. FIRM DATA INTEGRATION:")
        book2_firms = len(firm_comparison['book2_firms'])
        award_overlap = len(firm_comparison['overlaps']['book2_award'])
        district_overlap = len(firm_comparison['overlaps']['book2_district'])
        
        print(f"   • Book2.xlsx adds {book2_firms - award_overlap} new firms to award data")
        print(f"   • Book2.xlsx adds {book2_firms - district_overlap} new firms to district mapping")
        print(f"   • Consider merging Book2 firm data into existing databases")
        print()
        
        print("📋 2. CATEGORY NAMING STANDARDIZATION:")
        total_categories = len(category_comparison['book2_categories'])
        matched_categories = len(category_comparison['exact_matches'])
        match_rate = matched_categories/total_categories*100
        
        if match_rate > 80:
            print(f"   ✅ Excellent category match rate: {match_rate:.1f}%")
        elif match_rate > 60:
            print(f"   ⚠️  Good category match rate: {match_rate:.1f}% - minor standardization needed")
        else:
            print(f"   ❌ Low category match rate: {match_rate:.1f}% - major standardization needed")
        
        print(f"   • {total_categories - matched_categories} categories need naming conversion")
        print(f"   • Implement automatic category name normalization")
        print()
        
        print("📋 3. GEOGRAPHIC EXPANSION:")
        book2_states = len(geo_comparison['book2_states'])
        district_states = len(geo_comparison['district_states'])
        
        if book2_states > district_states:
            print(f"   🌍 Book2 expands geographic coverage by {book2_states - district_states} states")
            print(f"   • Consider expanding district mapping beyond Illinois")
        else:
            print(f"   🏠 District mapping covers more states ({district_states} vs {book2_states})")
        
        print()
        
        print("📋 4. DATA QUALITY IMPROVEMENTS:")
        print(f"   • Book2.xlsx provides email addresses for {book2_firms} firms")
        print(f"   • Book2.xlsx tracks DBE status for compliance")
        print(f"   • Consider adding these fields to existing databases")
        print()
        
        print("📋 5. IMMEDIATE ACTIONS:")
        print(f"   • Create category name conversion mapping")
        print(f"   • Merge Book2 firm data into firms_data.json")
        print(f"   • Update district_mapping with Book2 geographic data")
        print(f"   • Validate category matches with manual review")
        print()
        
        return {
            'firm_integration_potential': book2_firms - award_overlap,
            'category_standardization_needed': total_categories - matched_categories,
            'geographic_expansion': book2_states - district_states,
            'overall_data_quality_score': (match_rate + (award_overlap/book2_firms*100) + (district_overlap/book2_firms*100)) / 3
        }
    
    def run_comprehensive_comparison(self):
        """Run the complete comparison analysis"""
        print("🚀 COMPREHENSIVE DATAFRAME COMPARISON")
        print("=" * 80)
        print("Comparing Book2.xlsx with our existing data frames...")
        print()
        
        if not self.load_all_data():
            print("❌ Failed to load data sources. Exiting.")
            return
        
        # Run all comparisons
        firm_comparison = self.compare_firms()
        category_comparison = self.compare_categories()
        geo_comparison = self.compare_geographic_coverage()
        
        # Generate recommendations
        recommendations = self.generate_recommendations(firm_comparison, category_comparison, geo_comparison)
        
        # Final summary
        print("📊 FINAL COMPARISON SUMMARY")
        print("=" * 60)
        print(f"🎯 Overall Data Quality Score: {recommendations['overall_data_quality_score']:.1f}%")
        print(f"🏢 New Firms to Integrate: {recommendations['firm_integration_potential']}")
        print(f"📋 Categories to Standardize: {recommendations['category_standardization_needed']}")
        print(f"🌍 Geographic Expansion: {recommendations['geographic_expansion']} states")
        print()
        print("✅ Book2.xlsx is an excellent complement to our existing data!")
        print("🚀 Integration will significantly enhance our system's coverage and quality.")

if __name__ == "__main__":
    comparator = DataframeComparator()
    comparator.run_comprehensive_comparison()
