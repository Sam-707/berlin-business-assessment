#!/usr/bin/env python3
"""
Simple Berlin Business Finder - Quick version to get started
"""

import requests
import pandas as pd
import time
import os

def search_berlin_restaurants(api_key):
    """Find Berlin restaurants with GMB issues"""
    
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        'query': 'restaurants in Berlin Germany',
        'key': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('status') == 'OK':
            return data.get('results', [])
        else:
            print(f"API Error: {data.get('status')} - {data.get('error_message', '')}")
            return []
            
    except Exception as e:
        print(f"Request error: {e}")
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
        print(f"Details error: {e}")
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
    if len(photos) >= 10:
        score += 20
    elif len(photos) >= 5:
        score += 15
    elif len(photos) >= 1:
        score += 10
    else:
        issues.append("No photos")
    
    if len(photos) < 10:
        issues.append("Need more photos")
    
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
    
    if review_count < 10:
        issues.append("Need more reviews")
    
    # Assume average for description and activity (30 points)
    score += 15
    
    # Suggest package based on score
    if score < 40:
        package = "Premium Package (€700)"
    elif score < 60:
        package = "Standard Package (€400)"
    else:
        package = "Basic Package (€200)"
    
    return {
        'score': score,
        'issues': issues,
        'package': package,
        'photo_count': len(photos),
        'rating': rating,
        'review_count': review_count
    }

def main():
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    if not api_key:
        print("No API key found")
        return
    
    print("🔍 Finding Berlin restaurants with GMB opportunities...")
    
    # Search for restaurants
    restaurants = search_berlin_restaurants(api_key)
    print(f"Found {len(restaurants)} restaurants")
    
    opportunities = []
    
    # Analyze first 10 to avoid API limits
    for i, restaurant in enumerate(restaurants[:10]):
        print(f"Analyzing {i+1}/10: {restaurant.get('name', 'Unknown')}")
        
        place_id = restaurant.get('place_id')
        if not place_id:
            continue
            
        # Get detailed info
        details = get_business_details(place_id, api_key)
        if not details:
            continue
        
        # Score the listing
        analysis = score_gmb_listing(details)
        
        # Only include if score suggests opportunity (30-70 range)
        if 30 <= analysis['score'] <= 70:
            opportunity = {
                'name': details.get('name', 'Unknown'),
                'address': details.get('formatted_address', ''),
                'phone': details.get('formatted_phone_number', 'Missing'),
                'website': details.get('website', 'Missing'),
                'score': analysis['score'],
                'package': analysis['package'],
                'photos': analysis['photo_count'],
                'rating': analysis['rating'],
                'reviews': analysis['review_count'],
                'top_issues': ', '.join(analysis['issues'][:3])
            }
            opportunities.append(opportunity)
        
        time.sleep(0.5)  # Be nice to API
    
    # Results
    if opportunities:
        print(f"\n✅ Found {len(opportunities)} GMB optimization opportunities!")
        
        # Save to CSV
        df = pd.DataFrame(opportunities)
        filename = "berlin_restaurant_opportunities.csv"
        df.to_csv(filename, index=False)
        print(f"📊 Results saved to: {filename}")
        
        # Show top 5
        print("\n🎯 TOP OPPORTUNITIES:")
        for i, opp in enumerate(sorted(opportunities, key=lambda x: x['score'])[:5], 1):
            print(f"\n{i}. {opp['name']}")
            print(f"   GMB Score: {opp['score']}/100")
            print(f"   Package: {opp['package']}")
            print(f"   Issues: {opp['top_issues']}")
            print(f"   Address: {opp['address']}")
    else:
        print("No opportunities found in this sample. Try expanding search.")

if __name__ == "__main__":
    main()