#!/usr/bin/env python3
"""
Test Bulletin Format Standardization
Test the standardized prequal_lookup.json by finding firms for a specific category
"""

import json
from datetime import datetime

def test_bulletin_format():
    """Test bulletin format standardization"""
    print("🧪 TESTING BULLETIN FORMAT STANDARDIZATION")
    print("=" * 60)
    
    # Load standardized prequal_lookup.json
    print("📂 Loading standardized prequal_lookup.json...")
    with open('../data/prequal_lookup.json', 'r') as f:
        prequal_lookup = json.load(f)
        
    print(f"✅ Loaded {len(prequal_lookup)} categories")
    
    # Test category: Airports (Construction Inspection)
    test_category = "Airports (Construction Inspection)"
    
    print(f"\n🔍 TESTING CATEGORY: {test_category}")
    print("=" * 50)
    
    # Check if category exists
    if test_category in prequal_lookup:
        print(f"✅ CATEGORY FOUND: {test_category}")
        
        firms = prequal_lookup[test_category]
        print(f"📊 Number of Firms: {len(firms)}")
        
        print(f"\n📋 FIRMS PREQUALIFIED FOR {test_category}:")
        print("=" * 60)
        
        # Display firms with their codes
        for i, firm_dict in enumerate(firms, 1):
            firm_code = firm_dict.get('firm_code', 'N/A')
            firm_name = firm_dict.get('firm_name', 'N/A')
            print(f"{i:3d}. {firm_code} - {firm_name}")
            
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"   Category: {test_category}")
        print(f"   Total Firms: {len(firms)}")
        print(f"   Format: Bulletin Format (Parentheses) ✅")
        
        # Test other related categories
        print(f"\n🔍 RELATED CATEGORIES:")
        print("=" * 40)
        
        related_categories = [
            "Airports (Construction Inspection: Complex Electrical)",
            "Airports (Design)",
            "Airports (Design: Complex Electrical)",
            "Airports (Master Planning: Airport Layout Plans (ALP))"
        ]
        
        for related_cat in related_categories:
            if related_cat in prequal_lookup:
                firm_count = len(prequal_lookup[related_cat])
                print(f"✅ {related_cat}: {firm_count} firms")
            else:
                print(f"❌ {related_cat}: Not found")
                
    else:
        print(f"❌ CATEGORY NOT FOUND: {test_category}")
        
        # Show available airport categories
        print(f"\n🔍 AVAILABLE AIRPORT CATEGORIES:")
        print("=" * 50)
        
        airport_categories = [cat for cat in prequal_lookup.keys() if 'Airport' in cat]
        
        if airport_categories:
            for cat in airport_categories:
                firm_count = len(prequal_lookup[cat])
                print(f"  • {cat}: {firm_count} firms")
        else:
            print("  No airport categories found")
            
    # Test bulletin format examples
    print(f"\n🧪 BULLETIN FORMAT TEST:")
    print("=" * 40)
    
    bulletin_examples = [
        "Special Services (Subsurface Utility Engineering)",
        "Special Services (Construction Inspection)",
        "Special Studies (Traffic)",
        "Highways (Roads & Streets)",
        "Structures (Highway: Typical)",
        "Location Design Studies (Reconstruction/Major Rehabilitation)",
        "Structures (Highway: Complex)"
    ]
    
    for example in bulletin_examples:
        if example in prequal_lookup:
            firm_count = len(prequal_lookup[example])
            print(f"✅ {example}: {firm_count} firms")
        else:
            print(f"❌ {example}: Not found")
            
    # Generate test report
    generate_test_report(test_category, prequal_lookup)
    
def generate_test_report(test_category, prequal_lookup):
    """Generate test report"""
    print(f"\n📄 GENERATING TEST REPORT")
    print("=" * 40)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f'bulletin_format_test_{timestamp}.txt'
    
    with open(report_file, 'w') as f:
        f.write("BULLETIN FORMAT STANDARDIZATION TEST REPORT\n")
        f.write("=" * 55 + "\n\n")
        
        f.write("EXECUTIVE SUMMARY\n")
        f.write("-" * 20 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Purpose: Test bulletin format standardization\n")
        f.write(f"Test Category: {test_category}\n\n")
        
        # Test category results
        if test_category in prequal_lookup:
            firms = prequal_lookup[test_category]
            f.write("TEST CATEGORY RESULTS\n")
            f.write("-" * 25 + "\n")
            f.write(f"Category: {test_category}\n")
            f.write(f"Status: FOUND ✅\n")
            f.write(f"Number of Firms: {len(firms)}\n\n")
            
            f.write("FIRMS LIST:\n")
            f.write("-" * 12 + "\n")
            for i, firm_dict in enumerate(firms, 1):
                firm_code = firm_dict.get('firm_code', 'N/A')
                firm_name = firm_dict.get('firm_name', 'N/A')
                f.write(f"{i:3d}. {firm_code} - {firm_name}\n")
        else:
            f.write("TEST CATEGORY RESULTS\n")
            f.write("-" * 25 + "\n")
            f.write(f"Category: {test_category}\n")
            f.write(f"Status: NOT FOUND ❌\n\n")
            
        # Bulletin format test results
        f.write("\nBULLETIN FORMAT TEST RESULTS\n")
        f.write("-" * 30 + "\n")
        
        bulletin_examples = [
            "Special Services (Subsurface Utility Engineering)",
            "Special Services (Construction Inspection)",
            "Special Studies (Traffic)",
            "Highways (Roads & Streets)",
            "Structures (Highway: Typical)",
            "Location Design Studies (Reconstruction/Major Rehabilitation)",
            "Structures (Highway: Complex)"
        ]
        
        matches = 0
        for example in bulletin_examples:
            if example in prequal_lookup:
                firm_count = len(prequal_lookup[example])
                f.write(f"✅ {example}: {firm_count} firms\n")
                matches += 1
            else:
                f.write(f"❌ {example}: Not found\n")
                
        accuracy = (matches / len(bulletin_examples)) * 100
        f.write(f"\nBulletin Format Accuracy: {accuracy:.2f}%\n")
        
        # Overall statistics
        f.write("\nOVERALL STATISTICS\n")
        f.write("-" * 20 + "\n")
        f.write(f"Total Categories: {len(prequal_lookup)}\n")
        f.write(f"Categories with Firms: {sum(1 for firms in prequal_lookup.values() if firms)}\n")
        f.write(f"Total Firms: {sum(len(firms) for firms in prequal_lookup.values())}\n")
        
        # Final recommendation
        f.write("\nFINAL RECOMMENDATION\n")
        f.write("-" * 20 + "\n")
        
        if accuracy == 100:
            f.write("🎉 PERFECT BULLETIN FORMAT STANDARDIZATION!\n")
            f.write("✅ All bulletin examples match perfectly\n")
            f.write("✅ Ready for model training\n")
            f.write("✅ Format standardization successful\n")
        else:
            f.write("⚠️  BULLETIN FORMAT NEEDS IMPROVEMENT\n")
            f.write("❌ Some bulletin examples don't match\n")
            f.write("❌ Need to fix remaining mismatches\n")
            
    print(f"✅ Test report saved: {report_file}")

if __name__ == "__main__":
    test_bulletin_format()


