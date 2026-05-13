#!/usr/bin/env python3
"""
Update Firm Data with Performance Metrics
Implements mathematical equation and performance evaluation framework
"""

import json
import re
from collections import defaultdict
from datetime import datetime

def parse_fee_estimate(fee_estimate):
    """Parse fee estimate and return average of range"""
    if not fee_estimate or fee_estimate == 'None':
        return 0
    
    # Extract numbers from fee estimate
    numbers = re.findall(r'\$?([0-9,]+)', fee_estimate)
    if not numbers:
        return 0
    
    # Convert to integers
    fee_values = []
    for num in numbers:
        try:
            fee_values.append(int(num.replace(',', '')))
        except:
            pass
    
    if not fee_values:
        return 0
    
    # Return average of range
    return sum(fee_values) / len(fee_values)

def normalize_district(district):
    """Normalize district format for consistent client identification"""
    if not district:
        return "Unknown"
    
    district_str = str(district).strip()
    
    # Handle various formats
    if '/' in district_str:
        # Format: "Region 1/District 1" or "1/1"
        parts = district_str.split('/')
        if len(parts) >= 2:
            return f"District_{parts[-1].strip()}"
    
    # Handle "District X" format
    if 'District' in district_str:
        match = re.search(r'District\s*(\d+)', district_str)
        if match:
            return f"District_{match.group(1)}"
    
    # Handle "R1/D1" format
    if district_str.startswith('R') and '/' in district_str:
        parts = district_str.split('/')
        if len(parts) >= 2:
            return f"District_{parts[-1].strip()}"
    
    # Handle bureau formats
    if 'Bureau' in district_str:
        return "Bureau"
    
    return f"District_{district_str}"

def calculate_capacity_category(max_project_capacity):
    """Determine capacity category based on maximum project capacity"""
    if max_project_capacity > 7000000:  # > $7M
        return "Large"
    elif max_project_capacity > 1000000:  # $1M - $7M
        return "Medium"
    else:
        return "Small"

def calculate_performance_score(firm_data):
    """Calculate performance score based on various metrics"""
    performance_score = 0
    
    # 1. Repeat Selection Rate (30% weight)
    if firm_data['total_awards'] > 0:
        repeat_rate = firm_data['unique_districts'] / firm_data['total_awards']
        performance_score += repeat_rate * 0.3
    
    # 2. Role Promotion Pattern (25% weight)
    if firm_data['total_awards'] > 0:
        prime_ratio = firm_data['prime_wins'] / firm_data['total_awards']
        performance_score += prime_ratio * 0.25
    
    # 3. Project Size Growth (25% weight)
    if firm_data['total_awards'] > 1:
        growth_rate = (firm_data['max_project_capacity'] - firm_data['min_project_capacity']) / max(firm_data['min_project_capacity'], 1)
        performance_score += min(growth_rate / 10, 1) * 0.25  # Normalize growth rate
    
    # 4. Symbolic Performance Tags (20% weight)
    symbolic_score = 0
    
    # Strong performance indicators
    if firm_data['total_awards'] >= 3:
        symbolic_score += 0.3
    if firm_data['max_project_capacity'] > 5000000:  # > $5M
        symbolic_score += 0.3
    if firm_data['unique_districts'] >= 2:
        symbolic_score += 0.2
    if firm_data['prime_wins'] > firm_data['sub_wins']:
        symbolic_score += 0.2
    
    performance_score += symbolic_score * 0.2
    
    return min(performance_score, 1.0)  # Cap at 1.0

def update_firm_data():
    """Update firm_data.json with performance metrics"""
    print("🔄 UPDATING FIRM_DATA.JSON WITH PERFORMANCE METRICS")
    print("="*60)
    
    # Load data
    with open('../data/award_structure.json', 'r') as f:
        award_data = json.load(f)
    
    with open('../data/firms_data.json', 'r') as f:
        firms_data = json.load(f)
    
    # Create firm lookup
    firm_lookup = {firm['firm_name']: firm for firm in firms_data}
    firm_names_set = set(firm['firm_name'] for firm in firms_data)
    
    print(f"📊 DATA LOADED:")
    print(f"  Awards: {len(award_data)}")
    print(f"  Firms in firm_data: {len(firms_data)}")
    
    # Initialize firm performance tracking
    firm_performance = defaultdict(lambda: {
        'total_awards': 0,
        'recent_awards': 0,
        'total_fee_earned': 0,
        'prime_wins': 0,
        'sub_wins': 0,
        'max_project_capacity': 0,
        'min_project_capacity': float('inf'),
        'avg_project_capacity': 0,
        'unique_districts': set(),
        'project_capacities': [],
        'first_project_date': None,
        'last_project_date': None
    })
    
    # Parameters for mathematical equation
    P_RATIO = 0.7  # Prime gets 70%
    S_RATIO = 0.3  # Subs get 30%
    
    print(f"\n🧮 APPLYING MATHEMATICAL EQUATION:")
    print(f"  Prime ratio: {P_RATIO} (70%)")
    print(f"  Sub ratio: {S_RATIO} (30%)")
    
    # Process awards
    processed_awards = 0
    fee_processed = 0
    sub_processed = 0
    firms_found = 0
    
    for award in award_data:
        selected_firm = award.get('SELECTED FIRM', '')
        subconsultants = award.get('SUBCONSULTANTS', '')
        fee_estimate = award.get('Fee Estimate', '')
        district = award.get('Region/District', '')
        selection_date = award.get('Selection Date', '')
        
        if not selected_firm:
            continue
        
        processed_awards += 1
        
        # Parse fee estimate
        project_fee = parse_fee_estimate(fee_estimate)
        if project_fee > 0:
            fee_processed += 1
        
        # Normalize district
        normalized_district = normalize_district(district)
        
        # Process prime firm
        if selected_firm in firm_names_set:
            firms_found += 1
            perf = firm_performance[selected_firm]
            perf['total_awards'] += 1
            perf['prime_wins'] += 1
            perf['unique_districts'].add(normalized_district)
            
            if project_fee > 0:
                prime_budget = project_fee * P_RATIO
                perf['total_fee_earned'] += prime_budget
                perf['project_capacities'].append(prime_budget)
                perf['max_project_capacity'] = max(perf['max_project_capacity'], prime_budget)
                perf['min_project_capacity'] = min(perf['min_project_capacity'], prime_budget)
            
            # Track dates
            if selection_date:
                try:
                    date_obj = datetime.strptime(selection_date, '%Y-%m-%d %H:%M:%S')
                    if not perf['first_project_date'] or date_obj < perf['first_project_date']:
                        perf['first_project_date'] = date_obj
                    if not perf['last_project_date'] or date_obj > perf['last_project_date']:
                        perf['last_project_date'] = date_obj
                except:
                    pass
        
        # Process subconsultants
        if subconsultants and subconsultants != 'None':
            sub_processed += 1
            subs = [s.strip() for s in subconsultants.split(';') if s.strip()]
            
            if project_fee > 0 and subs:
                sub_budget_each = (project_fee * S_RATIO) / len(subs)
                
                for sub in subs:
                    if sub in firm_names_set:
                        perf = firm_performance[sub]
                        perf['total_awards'] += 1
                        perf['sub_wins'] += 1
                        perf['unique_districts'].add(normalized_district)
                        perf['total_fee_earned'] += sub_budget_each
                        perf['project_capacities'].append(sub_budget_each)
                        perf['max_project_capacity'] = max(perf['max_project_capacity'], sub_budget_each)
                        perf['min_project_capacity'] = min(perf['min_project_capacity'], sub_budget_each)
    
    print(f"\n📊 PROCESSING RESULTS:")
    print(f"  Total awards processed: {processed_awards}")
    print(f"  Awards with fee data: {fee_processed}")
    print(f"  Awards with subconsultants: {sub_processed}")
    print(f"  Firms with performance data: {len(firm_performance)}")
    
    # Calculate recent awards (last 5 years)
    current_year = datetime.now().year
    for firm_name, perf in firm_performance.items():
        if perf['last_project_date']:
            years_since_last = current_year - perf['last_project_date'].year
            if years_since_last <= 5:
                perf['recent_awards'] = perf['total_awards']  # Simplified for now
    
    # Update firms_data with performance metrics
    updated_firms = 0
    for firm in firms_data:
        firm_name = firm['firm_name']
        if firm_name in firm_performance:
            perf = firm_performance[firm_name]
            
            # Calculate average project capacity
            if perf['project_capacities']:
                perf['avg_project_capacity'] = sum(perf['project_capacities']) / len(perf['project_capacities'])
            
            # Handle minimum project capacity
            if perf['min_project_capacity'] == float('inf'):
                perf['min_project_capacity'] = 0
            
            # Convert set to count
            perf['unique_districts'] = len(perf['unique_districts'])
            
            # Calculate capacity category
            capacity_category = calculate_capacity_category(perf['max_project_capacity'])
            
            # Calculate performance score
            performance_score = calculate_performance_score(perf)
            
            # Update firm data
            firm['total_awards'] = perf['total_awards']
            firm['recent_awards'] = perf['recent_awards']
            firm['total_fee_earned'] = perf['total_fee_earned']
            firm['prime_wins'] = perf['prime_wins']
            firm['sub_wins'] = perf['sub_wins']
            firm['max_project_capacity'] = perf['max_project_capacity']
            firm['min_project_capacity'] = perf['min_project_capacity']
            firm['avg_project_capacity'] = perf['avg_project_capacity']
            firm['unique_districts'] = perf['unique_districts']
            firm['capacity'] = capacity_category
            firm['performance_score'] = performance_score
            
            updated_firms += 1
        else:
            # Firms with no award history
            firm['total_awards'] = 0
            firm['recent_awards'] = 0
            firm['total_fee_earned'] = 0
            firm['prime_wins'] = 0
            firm['sub_wins'] = 0
            firm['max_project_capacity'] = 0
            firm['min_project_capacity'] = 0
            firm['avg_project_capacity'] = 0
            firm['unique_districts'] = 0
            firm['capacity'] = "Unknown"
            firm['performance_score'] = 0.0
    
    # Save updated firm_data.json
    with open('../data/firms_data_updated.json', 'w') as f:
        json.dump(firms_data, f, indent=2, default=str)
    
    print(f"\n✅ FIRM_DATA UPDATE COMPLETE:")
    print(f"  Firms updated with performance data: {updated_firms}")
    print(f"  Firms with no award history: {len(firms_data) - updated_firms}")
    print(f"  Updated file saved as: firms_data_updated.json")
    
    # Show sample results
    print(f"\n📋 SAMPLE UPDATED FIRMS:")
    firms_with_data = [f for f in firms_data if f['total_awards'] > 0]
    firms_with_data.sort(key=lambda x: x['total_fee_earned'], reverse=True)
    
    for i, firm in enumerate(firms_with_data[:5], 1):
        print(f"  {i}. {firm['firm_name']}")
        print(f"     📊 Total Awards: {firm['total_awards']}")
        print(f"     💰 Total Fees: ${firm['total_fee_earned']:,.0f}")
        print(f"     🏢 Capacity: {firm['capacity']}")
        print(f"     🏆 Performance Score: {firm['performance_score']:.3f}")
        print(f"     📍 Districts: {firm['unique_districts']}")
    
    return firms_data

if __name__ == "__main__":
    update_firm_data() 