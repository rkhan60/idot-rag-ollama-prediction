
# Updated fuzzy_match_prequal function with bulletin format support

def fuzzy_match_prequal(extracted_prequal):
    """Fuzzy match extracted prequalification to lookup category with bulletin format support"""
    extracted = extracted_prequal.lower().replace(':', '').replace('-', ' ').strip()
    
    for lookup_category in prequal_lookup.keys():
        lookup = lookup_category.lower().replace(':', '').replace('-', ' ').strip()
        
        # Direct match
        if extracted == lookup:
            return lookup_category
        
        # Partial match
        if extracted in lookup or lookup in extracted:
            return lookup_category
        
        # Handle common variations
        variations = {
            'roads & streets': 'roads and streets',
            'roads and streets': 'roads & streets',
            'quality assurance: qa': 'quality assurance',
            'quality assurance qa': 'quality assurance',
            'location/design': 'location design',
            'location design': 'location/design',
        }
        
        if extracted in variations and variations[extracted] == lookup:
            return lookup_category
        if lookup in variations and variations[lookup] == extracted:
            return lookup_category
        
        # NEW: Handle bulletin format variations
        # Brackets vs parentheses
        if '[' in extracted and '(' in lookup:
            extracted_clean = extracted.replace('[', '(').replace(']', ')')
            if extracted_clean == lookup:
                return lookup_category
        
        # Slash vs space
        if '/' in extracted and ' ' in lookup:
            extracted_clean = extracted.replace('/', ' ')
            if extracted_clean == lookup:
                return lookup_category
        
        # Colon vs hyphen
        if ':' in extracted and '-' in lookup:
            extracted_clean = extracted.replace(':', '-')
            if extracted_clean == lookup:
                return lookup_category
        
        # Dash vs hyphen
        if '–' in extracted and '-' in lookup:
            extracted_clean = extracted.replace('–', '-')
            if extracted_clean == lookup:
                return lookup_category
        
        # Space after colon
        if '  ' in extracted and ' ' in lookup:
            extracted_clean = ' '.join(extracted.split())
            lookup_clean = ' '.join(lookup.split())
            if extracted_clean == lookup_clean:
                return lookup_category
        
        # Special handling for Quality Assurance variations
        if 'quality assurance' in extracted and 'quality assurance' in lookup:
            extracted_clean = extracted.replace('qa', '').replace(':', '').strip()
            lookup_clean = lookup.replace('qa', '').replace(':', '').strip()
            extracted_clean = ' '.join(extracted_clean.split())
            lookup_clean = ' '.join(lookup_clean.split())
            if extracted_clean == lookup_clean:
                return lookup_category
        
        # Special handling for Aerial Mapping variations
        if 'aerial mapping' in extracted and 'aerial mapping' in lookup:
            extracted_has_lidar = 'lidar' in extracted
            lookup_has_lidar = 'lidar' in lookup
            
            if extracted_has_lidar != lookup_has_lidar:
                extracted_clean = extracted.replace('lidar', '').strip()
                lookup_clean = lookup.replace('lidar', '').strip()
                extracted_clean = ' '.join(extracted_clean.split()).strip()
                lookup_clean = ' '.join(lookup_clean.split()).strip()
                extracted_clean = extracted_clean.replace(' )', ')')
                lookup_clean = lookup_clean.replace(' )', ')')
                
                if extracted_clean == lookup_clean:
                    return lookup_category
        
        # Special handling for Structures variations
        if 'structures' in extracted and 'structures' in lookup:
            if 'advanced typical' in extracted and 'advanced typical' in lookup:
                extracted_clean = extracted.replace(':', '-')
                lookup_clean = lookup.replace(':', '-')
                extracted_clean = ' '.join(extracted_clean.split())
                lookup_clean = ' '.join(lookup_clean.split())
                
                if extracted_clean == lookup_clean:
                    return lookup_category
    
    return None
