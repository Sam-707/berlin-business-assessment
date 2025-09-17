#!/usr/bin/env python3
"""
Find Berlin businesses with GMB optimization opportunities
Focus on smaller, local businesses more likely to need help
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

def score_gmb_listing(business):
    """Score a business GMB listing 0-100"""
    
    score = 0
    issues = []
    
    # Basic info (25 points)
    if business.get('name'):
        score += 5
    if business.get('formatted_address'):
        score += 5
    if business.get('formatted_phone_number'):
        score += 5
    else:
        issues.append("Missing phone number")
    if business.get('website'):
        score += 5
    else:
        issues.append("Missing website")
    if business.get('opening_hours'):
        score += 5
    else:
        issues.append("Missing business hours")
    
    # Photos (20 points)
    photos = business.get('photos', [])
    photo_count = len(photos)
    if photo_count >= 10:
        score += 20
    elif photo_count >= 5:
        score += 15
    elif photo_count >= 1:
        score += 10
    else:
        issues.append("No photos")
        score += 0
    
    if photo_count < 8:
        issues.append("Need more photos ({} currently)".format(photo_count))
    
    # Reviews (25 points) 
    rating = business.get('rating', 0)
    review_count = business.get('user_ratings_total', 0)
    
    if rating >= 4.5 and review_count >= 20:
        score += 25
    elif rating >= 4.0 and review_count >= 10:
        score += 20
    elif rating >= 3.5 and review_count >= 5:
        score += 15
    elif review_count > 0:
        score += 10
    else:
        issues.append("No reviews")
        score += 0
    
    if review_count < 10:
        issues.append("Need more reviews ({} currently)".format(review_count))
    
    # Description and activity (30 points) - assume average since we can't check easily
    score += 15
    
    # Suggest package based on score
    if score < 40:
        package = "Premium Package (€700)"
        opportunity_level = "HIGH"
    elif score < 60:
        package = "Standard Package (€400)"  
        opportunity_level = "MEDIUM"
    else:
        package = "Basic Package (€200)"
        opportunity_level = "LOW"
    
    return {
        'score': score,
        'issues': issues,
        'package': package,
        'opportunity_level': opportunity_level,
        'photo_count': photo_count,
        'rating': rating,
        'review_count': review_count
    }

def main():
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    if not api_key:
        print("No API key found")
        return
    
    # Search different types of businesses more likely to need help
    search_queries = [
        "small restaurants Berlin Kreuzberg",
        "hair salon Berlin Prenzlauer Berg", 
        "fitness studio Berlin Friedrichshain",
        "cafe Berlin Mitte",
        "auto repair Berlin"
    ]
    
    all_opportunities = []
    
    for query in search_queries:
        print("\n🔍 Searching:", query)
        businesses = search_businesses(query, api_key)
        print("Found {} businesses".format(len(businesses)))
        
        # Analyze first 5 from each search to avoid API limits
        for i, business in enumerate(businesses[:5]):
            name = business.get('name', 'Unknown')
            print("  Analyzing {}/5: {}".format(i+1, name))
            
            place_id = business.get('place_id')
            if not place_id:
                continue
                
            # Get detailed info
            details = get_business_details(place_id, api_key)
            if not details:
                continue
            
            # Score the listing
            analysis = score_gmb_listing(details)
            
            # Include all opportunities, especially those needing help
            if analysis['score'] <= 70:  # Focus on businesses that need optimization
                opportunity = {
                    'name': details.get('name', 'Unknown'),
                    'address': details.get('formatted_address', ''),
                    'phone': details.get('formatted_phone_number', 'Missing'),
                    'website': details.get('website', 'Missing'),
                    'score': analysis['score'],
                    'opportunity_level': analysis['opportunity_level'],
                    'package': analysis['package'],
                    'photos': analysis['photo_count'],
                    'rating': analysis['rating'],
                    'reviews': analysis['review_count'],
                    'top_issues': ' | '.join(analysis['issues'][:3]),
                    'search_category': query.split()[0]  # restaurant, hair, fitness, etc.
                }
                all_opportunities.append(opportunity)
            
            time.sleep(0.5)  # Be nice to API
    
    # Results
    if all_opportunities:
        print("\n" + "="*50)
        print("✅ FOUND {} GMB OPTIMIZATION OPPORTUNITIES!".format(len(all_opportunities)))
        print("="*50)
        
        # Save to CSV
        df = pd.DataFrame(all_opportunities)
        filename = "berlin_gmb_opportunities.csv"
        df.to_csv(filename, index=False)
        print("📊 Full results saved to: {}".format(filename))
        
        # Show summary by opportunity level
        high_opp = [o for o in all_opportunities if o['opportunity_level'] == 'HIGH']
        medium_opp = [o for o in all_opportunities if o['opportunity_level'] == 'MEDIUM']
        low_opp = [o for o in all_opportunities if o['opportunity_level'] == 'LOW']
        
        print("\n📈 OPPORTUNITY BREAKDOWN:")
        print("🎯 HIGH Priority (Score <40):   {} businesses - €700 packages".format(len(high_opp)))
        print("🔶 MEDIUM Priority (Score 40-60): {} businesses - €400 packages".format(len(medium_opp))) 
        print("🔸 LOW Priority (Score 60+):     {} businesses - €200 packages".format(len(low_opp)))
        
        # Calculate revenue potential
        total_revenue = len(high_opp) * 700 + len(medium_opp) * 400 + len(low_opp) * 200
        print("\n💰 TOTAL REVENUE POTENTIAL: €{:,}".format(total_revenue))
        
        # Show top 5 best opportunities
        print("\n🏆 TOP 5 OPPORTUNITIES TO CONTACT FIRST:")
        top_opportunities = sorted(all_opportunities, key=lambda x: x['score'])[:5]
        
        for i, opp in enumerate(top_opportunities, 1):
            print("\n{}. {}".format(i, opp['name']))
            print("   📍 {}".format(opp['address']))
            print("   📊 GMB Score: {}/100 ({})".format(opp['score'], opp['opportunity_level']))
            print("   💶 Package: {}".format(opp['package']))
            print("   📞 Phone: {}".format(opp['phone']))
            print("   🌐 Website: {}".format(opp['website']))
            print("   ❗ Issues: {}".format(opp['top_issues']))
            
        print("\n" + "="*50)
        print("🚀 NEXT STEPS:")
        print("1. Open the CSV file to see all prospects")
        print("2. Start with the HIGH priority businesses above") 
        print("3. Call/visit them with specific audit results")
        print("4. Use the issues identified as talking points")
        print("="*50)
        
    else:
        print("No opportunities found. This might mean:")
        print("- Businesses are already well-optimized")
        print("- Need to search different areas/types")
        print("- API limits reached")

if __name__ == "__main__":
    main()