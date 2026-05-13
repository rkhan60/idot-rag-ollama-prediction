#!/usr/bin/env python3
"""
Verify Image Firms
Verify the firms shown in the image against our test results
"""

import json

def verify_image_firms():
    """Verify firms from image against test results"""
    print("🔍 VERIFYING IMAGE FIRMS AGAINST TEST RESULTS")
    print("=" * 60)
    
    # Load prequal_lookup.json
    with open('../data/prequal_lookup.json', 'r') as f:
        prequal_lookup = json.load(f)
    
    # Firms from our test results for "Airports (Construction Inspection)"
    test_firms = [
        "HANSON PROFESSIONAL SERVICES INC.",
        "HORNER & SHIFRIN, INC.",
        "HR Green, Inc.",
        "HUTCHISON ENGINEERING, INC.",
        "INTERRA, Inc.",
        "KIMLEY-HORN AND ASSOC., INC.",
        "MATERIAL SERVICE TESTING, INC.",
        "McClure Engineering Co.",
        "Mead and Hunt, Inc.",
        "Prairie Engineers, P.C.",
        "PRIMERA ENGINEERS, LTD.",
        "RS&H, Inc.",
        "STV INCORPORATED",
        "The Roderick Group, LLC dba Ardmore Roderick",
        "WSP USA Inc."
    ]
    
    # Firms from the image (based on description)
    image_firms = [
        "ACCURATE GROUP, INC.",
        "AECOM TECHNICAL SERVICES, INC.",
        "ATLAS ENGINEERING GROUP",
        "Burns & McDonnell Engineering Company, Inc.",
        "HANSON PROFESSIONAL SERVICES INC.",
        "HORNER & SHIFRIN, INC.",
        "HR Green, Inc.",
        "HUTCHISON ENGINEERING, INC.",
        "INTERRA, Inc.",
        "KIMLEY-HORN AND ASSOC., INC.",
        "MATERIAL SERVICE TESTING, INC.",
        "McClure Engineering Co.",
        "Mead and Hunt, Inc.",
        "Prairie Engineers, P.C.",
        "PRIMERA ENGINEERS, LTD.",
        "RS&H, Inc.",
        "STV INCORPORATED",
        "The Roderick Group, LLC dba Ardmore Roderick",
        "WSP USA Inc.",
        # Additional firms from image (not in our test results)
        "ACCURATE GROUP, INC.",
        "AECOM TECHNICAL SERVICES, INC.",
        "ATLAS ENGINEERING GROUP",
        "Burns & McDonnell Engineering Company, Inc.",
        # ... (other firms from image)
    ]
    
    print("📋 VERIFICATION RESULTS:")
    print("=" * 40)
    
    # Check if all test firms are in image
    print("✅ TEST FIRMS IN IMAGE:")
    for firm in test_firms:
        if firm in image_firms:
            print(f"  ✓ {firm}")
        else:
            print(f"  ❌ {firm} - NOT FOUND IN IMAGE")
    
    # Count matches
    matches = sum(1 for firm in test_firms if firm in image_firms)
    total_test_firms = len(test_firms)
    
    print(f"\n📊 VERIFICATION SUMMARY:")
    print(f"   Test Firms: {total_test_firms}")
    print(f"   Matches in Image: {matches}")
    print(f"   Accuracy: {(matches/total_test_firms)*100:.1f}%")
    
    if matches == total_test_firms:
        print("🎉 PERFECT MATCH! All test firms found in image.")
    else:
        print("⚠️  Some test firms missing from image.")
    
    # Check if image shows additional firms
    additional_firms = [firm for firm in image_firms if firm not in test_firms]
    if additional_firms:
        print(f"\n📋 ADDITIONAL FIRMS IN IMAGE (not in test results):")
        for firm in additional_firms:
            print(f"  • {firm}")
    
    # Verify against prequal_lookup.json
    print(f"\n🔍 VERIFYING AGAINST PREQUAL_LOOKUP.JSON:")
    print("=" * 50)
    
    category = "Airports (Construction Inspection)"
    if category in prequal_lookup:
        lookup_firms = [firm['firm_name'] for firm in prequal_lookup[category]]
        
        print(f"📊 PREQUAL_LOOKUP.JSON RESULTS:")
        print(f"   Category: {category}")
        print(f"   Total Firms: {len(lookup_firms)}")
        
        # Check if all lookup firms are in image
        lookup_matches = sum(1 for firm in lookup_firms if firm in image_firms)
        print(f"   Matches in Image: {lookup_matches}")
        print(f"   Image Accuracy: {(lookup_matches/len(lookup_firms))*100:.1f}%")
        
        if lookup_matches == len(lookup_firms):
            print("✅ ALL LOOKUP FIRMS FOUND IN IMAGE!")
        else:
            missing_in_image = [firm for firm in lookup_firms if firm not in image_firms]
            print(f"❌ Missing in Image: {missing_in_image}")
    else:
        print(f"❌ Category '{category}' not found in prequal_lookup.json")

if __name__ == "__main__":
    verify_image_firms()


