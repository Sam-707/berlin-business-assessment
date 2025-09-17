#!/usr/bin/env python3
"""
Realistic Berlin Business Opportunity Finder
Adjusted scoring to find real optimization opportunities
"""

import requests
import pandas as pd
import time
import os

def search_businesses(query, api_key):
    """Search for businesses in Berlin"""
    
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        'query': query,
        'key': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('status') == 'OK':
            return data.get('results', [])
        else:
            print("API Error:", data.get('status', 'Unknown error'))
            return []
            
    except Exception as e:
        print("Request error:", str(e))
        return []

def get_business_details(place_id, api_key):
    """Get detailed info for a business"""
    
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'place_id': place_id,
        'fields': 'name,formatted_address,formatted_phone_number,website,opening_hours,photos,reviews,rating,user_ratings_total',
        'key': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('status') == 'OK':
            return data.get('result', {})
        else:
            return {}
            
    except Exception as e:
        return {}

def analyze_gmb_opportunity(business):
    """Analyze real optimization opportunities"""
    
    issues = []
    improvements = []
    
    # Check what's missing or could be improved
    phone = business.get('formatted_phone_number', '')
    website = business.get('website', '')
    hours = business.get('opening_hours', {})
    photos = business.get('photos', [])
    rating = business.get('rating', 0)
    review_count = business.get('user_ratings_total', 0)
    
    # Identify specific opportunities
    if not phone:
        issues.append("No phone number listed")
        improvements.append("Add phone number")
    
    if not website:
        issues.append("No website listed") 
        improvements.append("Add website URL")
    
    if not hours:
        issues.append("Business hours not specified")
        improvements.append("Add complete business hours")
    
    photo_count = len(photos)
    if photo_count < 5:
        issues.append("Only {} photos".format(photo_count))
        improvements.append("Add more photos (need 10+ for best results)")
    elif photo_count < 10:
        improvements.append("Add more photos (currently {} - aim for 15+)".format(photo_count))
    
    if review_count < 5:
        issues.append("Only {} reviews".format(review_count))
        improvements.append("Implement review generation strategy")
    elif review_count < 15:
        improvements.append("Could benefit from more reviews (currently {})".format(review_count))
    
    if rating > 0 and rating < 4.0:
        issues.append("Low rating: {} stars".format(rating))
        improvements.append("Address review management and customer service")
    
    # Determine if this is a good prospect
    issue_count = len(issues)
    improvement_count = len(improvements)
    
    if issue_count >= 2:
        opportunity_level = "HIGH"
        package = "Premium Package (€700)"
        priority = 1
    elif issue_count >= 1 or improvement_count >= 3:
        opportunity_level = "MEDIUM"
        package = "Standard Package (€400)"
        priority = 2
    elif improvement_count >= 1:
        opportunity_level = "LOW"
        package = "Basic Optimization (€250)"
        priority = 3
    else:
        return None  # Already well optimized
    
    return {
        'opportunity_level': opportunity_level,
        'package': package,
        'priority': priority,
        'issues': issues,
        'improvements': improvements,
        'photo_count': photo_count,
        'rating': rating,
        'review_count': review_count,
        'missing_phone': not bool(phone),
        'missing_website': not bool(website),
        'missing_hours': not bool(hours)
    }

def main():
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    if not api_key:
        print("No API key found")
        return
    
    # Focus on business types more likely to need help
    search_queries = [
        "family restaurant Berlin",
        "local cafe Berlin", 
        "hair salon Berlin",
        "auto repair shop Berlin",
        "dental practice Berlin",
        "small gym Berlin",
        "local bakery Berlin",
        "barber shop Berlin"
    ]
    
    all_opportunities = []
    
    for query in search_queries:
        print("\n🔍 Searching:", query)
        businesses = search_businesses(query, api_key)
        print("Found {} businesses".format(len(businesses)))
        
        # Analyze each business for opportunities
        for i, business in enumerate(businesses[:3]):  # Limit to 3 per search
            name = business.get('name', 'Unknown')
            print("  Analyzing {}/3: {}".format(i+1, name))
            
            place_id = business.get('place_id')
            if not place_id:
                continue
                
            # Get detailed info
            details = get_business_details(place_id, api_key)
            if not details:
                continue
            
            # Analyze opportunities
            analysis = analyze_gmb_opportunity(details)
            
            if analysis:  # Only include if there are opportunities
                opportunity = {
                    'name': details.get('name', 'Unknown'),
                    'address': details.get('formatted_address', ''),
                    'phone': details.get('formatted_phone_number', 'MISSING - OPPORTUNITY!'),
                    'website': details.get('website', 'MISSING - OPPORTUNITY!'),
                    'opportunity_level': analysis['opportunity_level'],
                    'package': analysis['package'],
                    'priority': analysis['priority'],
                    'photos': analysis['photo_count'],
                    'rating': analysis['rating'],
                    'reviews': analysis['review_count'],
                    'main_issues': ' | '.join(analysis['issues']),
                    'improvements': ' | '.join(analysis['improvements'][:2]),
                    'category': query.split()[0]
                }
                all_opportunities.append(opportunity)
                print("    ✅ OPPORTUNITY FOUND: {} - {}".format(analysis['opportunity_level'], analysis['package']))
            else:
                print("    ❌ Already well optimized")
            
            time.sleep(0.5)  # Be nice to API
    
    # Results
    if all_opportunities:
        print("\n" + "="*60)
        print("🎯 FOUND {} REAL GMB OPTIMIZATION OPPORTUNITIES!".format(len(all_opportunities)))
        print("="*60)
        
        # Save to CSV
        df = pd.DataFrame(all_opportunities)
        filename = "berlin_gmb_prospects.csv"
        df.to_csv(filename, index=False)
        print("\n📊 Complete prospect list saved to: {}".format(filename))
        
        # Summary by priority
        high_priority = [o for o in all_opportunities if o['priority'] == 1]
        medium_priority = [o for o in all_opportunities if o['priority'] == 2]
        low_priority = [o for o in all_opportunities if o['priority'] == 3]
        
        print("\n📈 OPPORTUNITY SUMMARY:")
        print("🔥 HIGH Priority:   {} prospects - €700 packages = €{:,} potential".format(
            len(high_priority), len(high_priority) * 700))
        print("🔶 MEDIUM Priority: {} prospects - €400 packages = €{:,} potential".format(
            len(medium_priority), len(medium_priority) * 400))
        print("🔸 LOW Priority:    {} prospects - €250 packages = €{:,} potential".format(
            len(low_priority), len(low_priority) * 250))
        
        total_revenue = len(high_priority) * 700 + len(medium_priority) * 400 + len(low_priority) * 250
        print("\n💰 TOTAL REVENUE POTENTIAL: €{:,}".format(total_revenue))
        
        # Show actionable prospects
        print("\n🚀 YOUR FIRST 5 PROSPECTS TO CONTACT:")
        top_prospects = sorted(all_opportunities, key=lambda x: x['priority'])[:5]
        
        for i, prospect in enumerate(top_prospects, 1):
            print("\n{}. {} [{}]".format(i, prospect['name'], prospect['opportunity_level']))
            print("   📍 {}".format(prospect['address']))
            print("   📞 {}".format(prospect['phone']))
            print("   🌐 {}".format(prospect['website']))
            print("   💶 {}".format(prospect['package']))
            print("   ❗ Issues: {}".format(prospect['main_issues']))
            print("   ✅ Pitch: \"{}\"".format(prospect['improvements']))
        
        print("\n" + "="*60)
        print("📋 WHAT TO DO NEXT:")
        print("1. Call the HIGH priority prospects first")
        print("2. Mention their specific missing elements (phone, website, photos)")
        print("3. Offer free audit: 'I noticed your GMB listing is missing...'")
        print("4. Use the improvements as your value proposition")
        print("5. Start with a €250-400 package to get testimonials")
        print("="*60)
        
        # Open the CSV file to show them
        try:
            os.system("open {}".format(filename))
            print("\n📂 Opening your prospect list now...")
        except:
            print("\n📂 Open {} to see your complete prospect list".format(filename))
        
    else:
        print("\n❌ No clear opportunities found in this sample.")
        print("This could mean:")
        print("- Berlin businesses are well-optimized")
        print("- Need to try different neighborhoods/business types")
        print("- Consider expanding to other German cities")

if __name__ == "__main__":
    main()