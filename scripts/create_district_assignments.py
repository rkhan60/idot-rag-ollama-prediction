#!/usr/bin/env python3
"""
Create District Assignments
Assign districts to firms based on location data
"""

import json
import os
from collections import defaultdict
from datetime import datetime

class DistrictAssignmentCreator:
    def __init__(self):
        self.data_dir = '../data'
        self.backup_dir = '../data/backups'
        
        # Illinois IDOT District Mapping
        self.district_mapping = {
            'District 1': {
                'cities': ['Chicago', 'Evanston', 'Oak Park', 'Skokie', 'Arlington Heights', 'Palatine', 'Schaumburg', 'Naperville', 'Aurora', 'Elgin', 'Waukegan', 'Highland Park', 'Deerfield', 'Northbrook', 'Glenview', 'Mount Prospect', 'Des Plaines', 'Park Ridge', 'Morton Grove', 'Niles', 'Rolling Meadows', 'Hoffman Estates', 'Barrington', 'Buffalo Grove', 'Libertyville', 'Gurnee', 'Mundelein', 'Vernon Hills', 'Lake Forest', 'Lake Bluff', 'Wilmette', 'Glencoe', 'Winnetka', 'Kenilworth', 'Hinsdale', 'Oak Brook', 'Downers Grove', 'Lisle', 'Wheaton', 'Glen Ellyn', 'Lombard', 'Villa Park', 'Elmhurst', 'Addison', 'Itasca', 'Roselle', 'Bloomingdale', 'Carol Stream', 'Hanover Park', 'Streamwood', 'Bartlett', 'West Chicago', 'St. Charles', 'Geneva', 'Batavia', 'Warrenville', 'Winfield', 'Wayne', 'South Elgin', 'Carpentersville', 'Algonquin', 'Crystal Lake', 'McHenry', 'Woodstock', 'Harvard', 'Marengo', 'Huntley', 'Lake in the Hills', 'Fox River Grove', 'Cary', 'Fox Lake', 'Round Lake', 'Grayslake', 'Antioch', 'Lindenhurst', 'Zion', 'Beach Park', 'Wadsworth', 'Gurnee', 'Mundelein', 'Libertyville', 'Vernon Hills', 'Lake Forest', 'Lake Bluff', 'Highland Park', 'Deerfield', 'Northbrook', 'Glenview', 'Mount Prospect', 'Des Plaines', 'Park Ridge', 'Morton Grove', 'Niles', 'Rolling Meadows', 'Hoffman Estates', 'Barrington', 'Buffalo Grove'],
                'counties': ['Cook', 'Lake', 'McHenry', 'DuPage', 'Kane', 'Will', 'Kendall']
            },
            'District 2': {
                'cities': ['Rockford', 'DeKalb', 'Sycamore', 'Geneva', 'St. Charles', 'Batavia', 'Aurora', 'Naperville', 'Elgin', 'Carpentersville', 'Algonquin', 'Crystal Lake', 'McHenry', 'Woodstock', 'Harvard', 'Marengo', 'Huntley', 'Lake in the Hills', 'Fox River Grove', 'Cary', 'Fox Lake', 'Round Lake', 'Grayslake', 'Antioch', 'Lindenhurst', 'Zion', 'Beach Park', 'Wadsworth', 'Gurnee', 'Mundelein', 'Libertyville', 'Vernon Hills', 'Lake Forest', 'Lake Bluff', 'Highland Park', 'Deerfield', 'Northbrook', 'Glenview', 'Mount Prospect', 'Des Plaines', 'Park Ridge', 'Morton Grove', 'Niles', 'Rolling Meadows', 'Hoffman Estates', 'Barrington', 'Buffalo Grove'],
                'counties': ['Winnebago', 'DeKalb', 'Kane', 'Kendall', 'LaSalle', 'Lee', 'Ogle']
            },
            'District 3': {
                'cities': ['Joliet', 'Kankakee', 'Bourbonnais', 'Bradley', 'Pontiac', 'Ottawa', 'Streator', 'Morris', 'Coal City', 'Minooka', 'Channahon', 'Shorewood', 'Plainfield', 'Bolingbrook', 'Romeoville', 'Lockport', 'New Lenox', 'Frankfort', 'Mokena', 'Orland Park', 'Tinley Park', 'Oak Forest', 'Oak Lawn', 'Burbank', 'Bridgeview', 'Hickory Hills', 'Palos Heights', 'Palos Park', 'Palos Hills', 'Worth', 'Summit Argo', 'Forest View', 'Bedford Park', 'Hodgkins', 'Willow Springs', 'Burr Ridge', 'Willowbrook', 'Woodridge', 'Downers Grove', 'Lisle', 'Naperville', 'Aurora', 'Batavia', 'Geneva', 'St. Charles', 'Elgin', 'Carpentersville', 'Algonquin', 'Crystal Lake', 'McHenry', 'Woodstock', 'Harvard', 'Marengo', 'Huntley', 'Lake in the Hills', 'Fox River Grove', 'Cary', 'Fox Lake', 'Round Lake', 'Grayslake', 'Antioch', 'Lindenhurst', 'Zion', 'Beach Park', 'Wadsworth', 'Gurnee', 'Mundelein', 'Libertyville', 'Vernon Hills', 'Lake Forest', 'Lake Bluff', 'Highland Park', 'Deerfield', 'Northbrook', 'Glenview', 'Mount Prospect', 'Des Plaines', 'Park Ridge', 'Morton Grove', 'Niles', 'Rolling Meadows', 'Hoffman Estates', 'Barrington', 'Buffalo Grove'],
                'counties': ['Will', 'Kankakee', 'Bureau', 'Grundy', 'Iroquois', 'Livingston', 'Vermilion']
            },
            'District 4': {
                'cities': ['Peoria', 'East Peoria', 'Morton', 'Washington', 'Metamora', 'Germantown Hills', 'Dunlap', 'Chillicothe', 'Lacon', 'Henry', 'Kewanee', 'Princeton', 'Peru', 'LaSalle', 'Ottawa', 'Streator', 'Pontiac', 'Bloomington', 'Normal', 'Champaign', 'Urbana', 'Danville', 'Decatur', 'Springfield', 'Jacksonville', 'Quincy', 'Macomb', 'Galesburg', 'Monmouth', 'Rock Island', 'Moline', 'East Moline', 'Silvis', 'Rock Island', 'Milan', 'Colona', 'Geneseo', 'Kewanee', 'Galva', 'Cambridge', 'Altona', 'Oneida', 'Rio', 'Cambridge', 'Galva', 'Kewanee', 'Geneseo', 'Colona', 'Milan', 'Rock Island', 'Silvis', 'East Moline', 'Moline', 'Rock Island', 'Monmouth', 'Galesburg', 'Macomb', 'Quincy', 'Jacksonville', 'Springfield', 'Decatur', 'Danville', 'Urbana', 'Champaign', 'Normal', 'Bloomington', 'Streator', 'Ottawa', 'LaSalle', 'Peru', 'Princeton', 'Kewanee', 'Henry', 'Lacon', 'Chillicothe', 'Dunlap', 'Germantown Hills', 'Metamora', 'Washington', 'Morton', 'East Peoria', 'Peoria'],
                'counties': ['Peoria', 'Tazewell', 'Woodford', 'Mercer', 'Rock Island', 'Henry', 'Stark', 'Bureau', 'Putnam', 'Marshall', 'Knox', 'Warren', 'Henderson', 'McDonough', 'Fulton', 'Schuyler', 'Adams', 'Brown', 'Cass', 'Mason', 'Hancock']
            },
            'District 5': {
                'cities': ['Champaign', 'Urbana', 'Danville', 'Decatur', 'Springfield', 'Jacksonville', 'Quincy', 'Macomb', 'Galesburg', 'Monmouth', 'Rock Island', 'Moline', 'East Moline', 'Silvis', 'Rock Island', 'Milan', 'Colona', 'Geneseo', 'Kewanee', 'Galva', 'Cambridge', 'Altona', 'Oneida', 'Rio', 'Cambridge', 'Galva', 'Kewanee', 'Geneseo', 'Colona', 'Milan', 'Rock Island', 'Silvis', 'East Moline', 'Moline', 'Rock Island', 'Monmouth', 'Galesburg', 'Macomb', 'Quincy', 'Jacksonville', 'Springfield', 'Decatur', 'Danville', 'Urbana', 'Champaign'],
                'counties': ['Champaign', 'Vermilion', 'Douglas', 'Coles', 'Moultrie', 'Shelby', 'Fayette', 'Effingham', 'Jasper', 'Crawford', 'Clark', 'Cumberland', 'Edgar', 'Piatt', 'DeWitt', 'Macon', 'Ford', 'Iroquois']
            },
            'District 6': {
                'cities': ['Carbondale', 'Marion', 'Mount Vernon', 'Centralia', 'Belleville', 'East St. Louis', 'Collinsville', 'Edwardsville', 'Glen Carbon', 'Maryville', 'Troy', 'O\'Fallon', 'Shiloh', 'Fairview Heights', 'Swansea', 'Cahokia', 'Granite City', 'Madison', 'Venice', 'Alton', 'Godfrey', 'Jerseyville', 'Carrollton', 'White Hall', 'Pittsfield', 'Jacksonville', 'Beardstown', 'Rushville', 'Macomb', 'Carthage', 'Hamilton', 'McLeansboro', 'Carmi', 'Harrisburg', 'Eldorado', 'Marion', 'Herrin', 'West Frankfort', 'Benton', 'Du Quoin', 'Pinckneyville', 'Murphysboro', 'Carbondale', 'Anna', 'Jonesboro', 'Cairo', 'Metropolis', 'Vienna', 'Golconda', 'Shawneetown', 'Carmi', 'McLeansboro', 'Hamilton', 'Carthage', 'Rushville', 'Beardstown', 'Jacksonville', 'White Hall', 'Carrollton', 'Jerseyville', 'Godfrey', 'Alton', 'Venice', 'Madison', 'Granite City', 'Cahokia', 'Swansea', 'Fairview Heights', 'Shiloh', 'O\'Fallon', 'Troy', 'Maryville', 'Glen Carbon', 'Edwardsville', 'Collinsville', 'East St. Louis', 'Belleville', 'Centralia', 'Mount Vernon', 'Marion', 'Carbondale'],
                'counties': ['Jackson', 'Williamson', 'Saline', 'Franklin', 'Perry', 'Randolph', 'Monroe', 'St. Clair', 'Madison', 'Clinton', 'Bond', 'Washington', 'Jefferson', 'Marion', 'Fayette', 'Effingham', 'Clay', 'Richland', 'Lawrence', 'Wabash', 'Edwards', 'Wayne', 'White', 'Hamilton', 'Gallatin', 'Hardin', 'Pope', 'Johnson', 'Massac', 'Pulaski', 'Alexander', 'Union']
            },
            'District 7': {
                'cities': ['Springfield', 'Decatur', 'Danville', 'Urbana', 'Champaign', 'Normal', 'Bloomington', 'Pontiac', 'Streator', 'Ottawa', 'LaSalle', 'Peru', 'Princeton', 'Kewanee', 'Henry', 'Lacon', 'Chillicothe', 'Dunlap', 'Germantown Hills', 'Metamora', 'Washington', 'Morton', 'East Peoria', 'Peoria', 'East Peoria', 'Morton', 'Washington', 'Metamora', 'Germantown Hills', 'Dunlap', 'Chillicothe', 'Lacon', 'Henry', 'Kewanee', 'Princeton', 'Peru', 'LaSalle', 'Ottawa', 'Streator', 'Pontiac', 'Bloomington', 'Normal', 'Champaign', 'Urbana', 'Danville', 'Decatur', 'Springfield'],
                'counties': ['Sangamon', 'Macon', 'Vermilion', 'Champaign', 'Douglas', 'Coles', 'Moultrie', 'Shelby', 'Fayette', 'Effingham', 'Jasper', 'Crawford', 'Clark', 'Cumberland', 'Edgar', 'Piatt', 'DeWitt', 'Ford', 'Iroquois', 'Bond', 'Montgomery', 'Christian', 'Macoupin', 'Greene', 'Jersey', 'Calhoun', 'Morgan', 'Scott']
            },
            'District 8': {
                'cities': ['Rockford', 'DeKalb', 'Sycamore', 'Geneva', 'St. Charles', 'Batavia', 'Aurora', 'Naperville', 'Elgin', 'Carpentersville', 'Algonquin', 'Crystal Lake', 'McHenry', 'Woodstock', 'Harvard', 'Marengo', 'Huntley', 'Lake in the Hills', 'Fox River Grove', 'Cary', 'Fox Lake', 'Round Lake', 'Grayslake', 'Antioch', 'Lindenhurst', 'Zion', 'Beach Park', 'Wadsworth', 'Gurnee', 'Mundelein', 'Libertyville', 'Vernon Hills', 'Lake Forest', 'Lake Bluff', 'Highland Park', 'Deerfield', 'Northbrook', 'Glenview', 'Mount Prospect', 'Des Plaines', 'Park Ridge', 'Morton Grove', 'Niles', 'Rolling Meadows', 'Hoffman Estates', 'Barrington', 'Buffalo Grove'],
                'counties': ['Winnebago', 'Boone', 'Carroll', 'Jo Daviess', 'Stephenson', 'Ogle', 'Whiteside']
            },
            'District 9': {
                'cities': ['Champaign', 'Urbana', 'Danville', 'Decatur', 'Springfield', 'Jacksonville', 'Quincy', 'Macomb', 'Galesburg', 'Monmouth', 'Rock Island', 'Moline', 'East Moline', 'Silvis', 'Rock Island', 'Milan', 'Colona', 'Geneseo', 'Kewanee', 'Galva', 'Cambridge', 'Altona', 'Oneida', 'Rio', 'Cambridge', 'Galva', 'Kewanee', 'Geneseo', 'Colona', 'Milan', 'Rock Island', 'Silvis', 'East Moline', 'Moline', 'Rock Island', 'Monmouth', 'Galesburg', 'Macomb', 'Quincy', 'Jacksonville', 'Springfield', 'Decatur', 'Danville', 'Urbana', 'Champaign'],
                'counties': ['Champaign', 'Vermilion', 'Douglas', 'Coles', 'Moultrie', 'Shelby', 'Fayette', 'Effingham', 'Jasper', 'Crawford', 'Clark', 'Cumberland', 'Edgar', 'Piatt', 'DeWitt', 'Macon', 'Ford', 'Iroquois']
            }
        }
        
    def assign_district_by_location(self, city, state):
        """Assign district based on city and state"""
        if state != 'IL':
            return 'Out of State'
            
        city_lower = city.lower().strip()
        
        for district, info in self.district_mapping.items():
            # Check cities
            for district_city in info['cities']:
                if city_lower == district_city.lower():
                    return district
                    
        # If no exact match, try partial matches
        for district, info in self.district_mapping.items():
            for district_city in info['cities']:
                if city_lower in district_city.lower() or district_city.lower() in city_lower:
                    return district
                    
        return 'Unknown'
        
    def create_district_assignments(self):
        """Create district assignments for all firms"""
        print("🚀 CREATING DISTRICT ASSIGNMENTS")
        print("=" * 50)
        
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Load firms_data.json
        print("📂 Loading firms_data.json...")
        with open(f'{self.data_dir}/firms_data.json', 'r') as f:
            firms_data = json.load(f)
            
        print(f"✅ Loaded {len(firms_data)} firms from firms_data.json")
        
        # Create backup of existing district_mapping.json if it exists
        district_mapping_path = f'{self.data_dir}/district_mapping.json'
        if os.path.exists(district_mapping_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f'{self.backup_dir}/district_mapping_backup_{timestamp}.json'
            
            print(f"📦 Creating backup: {backup_path}")
            with open(district_mapping_path, 'r') as f:
                existing_data = json.load(f)
            with open(backup_path, 'w') as f:
                json.dump(existing_data, f, indent=2)
            print("✅ Backup created successfully")
        
        # Assign districts to firms
        print("\n🔍 Assigning districts to firms...")
        district_assignments = defaultdict(list)
        
        for firm in firms_data:
            firm_name = firm.get('firm_name', '').strip()
            if not firm_name:
                continue
                
            city = firm.get('city', '').strip()
            state = firm.get('state', '').strip()
            
            # Assign district
            district = self.assign_district_by_location(city, state)
            
            # Create firm entry
            firm_entry = {
                'firm_code': firm.get('firm_code', ''),
                'firm_name': firm_name,
                'district': district,
                'city': city,
                'state': state
            }
            
            # Add to district mapping
            district_assignments[district].append(firm_entry)
            
        # Convert defaultdict to regular dict
        district_assignments = dict(district_assignments)
        
        # Print summary
        print(f"\n📊 DISTRICT ASSIGNMENT SUMMARY:")
        print(f"   Total Districts: {len(district_assignments)}")
        total_firms = sum(len(firms) for firms in district_assignments.values())
        print(f"   Total Firms: {total_firms}")
        
        # Show district breakdown
        print(f"\n📋 DISTRICT BREAKDOWN:")
        for district, firms in sorted(district_assignments.items()):
            print(f"   {district}: {len(firms)} firms")
            
        # Save the populated district_mapping.json
        print(f"\n💾 Saving district_mapping.json...")
        with open(district_mapping_path, 'w') as f:
            json.dump(district_assignments, f, indent=2)
            
        print("✅ district_mapping.json populated successfully!")
        
        # Analyze assignment quality
        self.analyze_assignment_quality(district_assignments)
        
        return district_assignments
        
    def analyze_assignment_quality(self, district_assignments):
        """Analyze the quality of district assignments"""
        print(f"\n🔍 ANALYZING ASSIGNMENT QUALITY")
        print("=" * 50)
        
        # Count firms by district
        district_counts = {district: len(firms) for district, firms in district_assignments.items()}
        
        # Find districts with most firms
        sorted_districts = sorted(district_counts.items(), key=lambda x: x[1], reverse=True)
        
        print(f"📊 FIRMS BY DISTRICT:")
        for district, count in sorted_districts:
            print(f"   {district}: {count} firms")
            
        # Check for unknown districts
        unknown_firms = len(district_assignments.get('Unknown', []))
        out_of_state_firms = len(district_assignments.get('Out of State', []))
        total_firms = sum(district_counts.values())
        
        known_firms = total_firms - unknown_firms - out_of_state_firms
        quality_score = (known_firms / total_firms) * 100 if total_firms > 0 else 0
        
        print(f"\n📈 ASSIGNMENT QUALITY:")
        print(f"   Total Firms: {total_firms}")
        print(f"   Known Districts: {known_firms}")
        print(f"   Unknown Districts: {unknown_firms}")
        print(f"   Out of State: {out_of_state_firms}")
        print(f"   Quality Score: {quality_score:.2f}%")
        
        if quality_score >= 80:
            print("✅ Good assignment quality!")
        elif quality_score >= 60:
            print("⚠️  Fair assignment quality, some improvements needed")
        else:
            print("❌ Poor assignment quality, significant improvements needed")
            
        return quality_score

def main():
    creator = DistrictAssignmentCreator()
    
    # Create district assignments
    district_assignments = creator.create_district_assignments()
    
    print(f"\n🎯 FINAL SUMMARY:")
    print(f"   District Assignments: CREATED")
    print(f"   Total Firms: {sum(len(firms) for firms in district_assignments.values())}")
    print(f"   Total Districts: {len(district_assignments)}")
    
    # Calculate quality score
    total_firms = sum(len(firms) for firms in district_assignments.values())
    known_firms = total_firms - len(district_assignments.get('Unknown', [])) - len(district_assignments.get('Out of State', []))
    quality_score = (known_firms / total_firms) * 100 if total_firms > 0 else 0
    
    print(f"   Quality Score: {quality_score:.2f}%")
    
    if quality_score >= 60:
        print("✅ Ready for next verification step!")
    else:
        print("⚠️  Assignment quality needs improvement before proceeding")

if __name__ == "__main__":
    main()
