#!/usr/bin/env python3
"""
Berlin Business GMB Opportunity Finder
Automatically finds and scores businesses for GMB optimization potential
"""

import requests
import pandas as pd
import time
from typing import List, Dict, Optional
import json
from datetime import datetime
import os

class BerlinBusinessFinder:
    def __init__(self, google_api_key: str):
        self.api_key = google_api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.session = requests.Session()
        
        # Business categories to target
        self.target_categories = {
            'restaurants': ['restaurant', 'cafe', 'bakery'],
            'health_wellness': ['gym', 'spa', 'beauty_salon', 'hair_care'],
            'professional': ['lawyer', 'dentist', 'doctor', 'accounting'],
            'retail': ['clothing_store', 'electronics_store', 'jewelry_store'],
            'services': ['car_repair', 'plumber', 'electrician']
        }
        
    def search_businesses_by_category(self, category: str, location: str = "Berlin, Germany", radius: int = 50000) -> List[Dict]:
        """Search for businesses in Berlin by category"""
        
        search_url = f"{self.base_url}/textsearch/json"
        params = {
            'query': f"{category} in {location}",
            'key': self.api_key,
            'radius': radius
        }
        
        all_businesses = []
        
        try:
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'OK':
                all_businesses.extend(data.get('results', []))
                
                # Handle pagination
                while 'next_page_token' in data:
                    time.sleep(2)  # Required delay for next_page_token
                    params['pagetoken'] = data['next_page_token']
                    response = self.session.get(search_url, params=params)
                    data = response.json()
                    
                    if data.get('status') == 'OK':
                        all_businesses.extend(data.get('results', []))
                    else:
                        break
                        
        except requests.RequestException as e:
            print(f"Error searching for {category}: {e}")
            
        return all_businesses
    
    def get_business_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information about a specific business"""
        
        details_url = f"{self.base_url}/details/json"
        params = {
            'place_id': place_id,
            'fields': 'name,formatted_address,formatted_phone_number,website,opening_hours,photos,reviews,rating,user_ratings_total,url',
            'key': self.api_key
        }
        
        try:
            response = self.session.get(details_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'OK':
                return data.get('result', {})
                
        except requests.RequestException as e:
            print(f"Error getting details for place_id {place_id}: {e}")
            
        return None
    
    def score_gmb_listing(self, business_details: Dict) -> Dict:
        """Score a business's GMB listing completeness (0-100)"""
        
        score = 0
        scoring_details = {}
        
        # Basic Information (25 points)
        if business_details.get('name'):
            score += 5
            scoring_details['has_name'] = True
        
        if business_details.get('formatted_address'):
            score += 5
            scoring_details['has_address'] = True
            
        if business_details.get('formatted_phone_number'):
            score += 5
            scoring_details['has_phone'] = True
            
        if business_details.get('website'):
            score += 5
            scoring_details['has_website'] = True
            
        if business_details.get('opening_hours'):
            score += 5
            scoring_details['has_hours'] = True
        
        # Photos (20 points)
        photos = business_details.get('photos', [])
        if len(photos) >= 10:
            score += 20
            scoring_details['sufficient_photos'] = True
        elif len(photos) >= 5:
            score += 15
            scoring_details['some_photos'] = True
        elif len(photos) >= 1:
            score += 10
            scoring_details['few_photos'] = True
        
        # Reviews and Engagement (25 points)
        rating = business_details.get('rating', 0)
        review_count = business_details.get('user_ratings_total', 0)
        
        if rating >= 4.5 and review_count >= 20:
            score += 25
            scoring_details['excellent_reviews'] = True
        elif rating >= 4.0 and review_count >= 10:
            score += 20
            scoring_details['good_reviews'] = True
        elif rating >= 3.5 and review_count >= 5:
            score += 15
            scoring_details['average_reviews'] = True
        elif review_count > 0:
            score += 10
            scoring_details['some_reviews'] = True
        
        # Business Description & Categories (15 points)
        # Note: Google Places API doesn't provide business description directly
        # This would need additional scraping or manual assessment
        score += 10  # Assume average for now
        scoring_details['description_assumed'] = True
        
        # Recent Activity (15 points)
        # This would require additional API calls to check for recent posts, updates
        # For now, we'll estimate based on review recency
        reviews = business_details.get('reviews', [])
        if reviews:
            # Check if any reviews are recent (simplified approach)
            score += 10
            scoring_details['some_activity'] = True
        
        scoring_details['total_score'] = score
        scoring_details['scoring_breakdown'] = {
            'basic_info': min(25, score),
            'photos': len(photos),
            'rating': rating,
            'review_count': review_count
        }
        
        return scoring_details
    
    def find_gmb_opportunities(self, niche: str = None, min_score: int = 30, max_score: int = 70) -> pd.DataFrame:
        """Find businesses with GMB optimization opportunities"""
        
        if niche and niche in self.target_categories:
            categories_to_search = {niche: self.target_categories[niche]}
        else:
            categories_to_search = self.target_categories
        
        all_opportunities = []
        
        for category_group, categories in categories_to_search.items():
            print(f"Searching {category_group} businesses...")
            
            for category in categories:
                print(f"  - Searching {category}...")
                businesses = self.search_businesses_by_category(category)
                
                for business in businesses[:20]:  # Limit to prevent API quota issues
                    place_id = business.get('place_id')
                    if not place_id:
                        continue
                    
                    details = self.get_business_details(place_id)
                    if not details:
                        continue
                    
                    scoring = self.score_gmb_listing(details)
                    score = scoring['total_score']
                    
                    if min_score <= score <= max_score:
                        opportunity = {
                            'business_name': details.get('name', 'Unknown'),
                            'address': details.get('formatted_address', ''),
                            'phone': details.get('formatted_phone_number', ''),
                            'website': details.get('website', ''),
                            'category_group': category_group,
                            'category': category,
                            'gmb_score': score,
                            'rating': details.get('rating', 0),
                            'review_count': details.get('user_ratings_total', 0),
                            'photo_count': len(details.get('photos', [])),
                            'google_url': details.get('url', ''),
                            'place_id': place_id,
                            'opportunity_level': self._get_opportunity_level(score),
                            'estimated_package': self._suggest_package(scoring),
                            'priority_fixes': self._identify_priority_fixes(scoring)
                        }
                        all_opportunities.append(opportunity)
                
                time.sleep(1)  # Be respectful to API limits
        
        return pd.DataFrame(all_opportunities)
    
    def _get_opportunity_level(self, score: int) -> str:
        """Categorize opportunity level based on score"""
        if score < 40:
            return "High Opportunity"
        elif score < 60:
            return "Medium Opportunity"
        else:
            return "Low Opportunity"
    
    def _suggest_package(self, scoring: Dict) -> str:
        """Suggest appropriate service package based on scoring"""
        score = scoring['total_score']
        
        if score < 40:
            return "Premium Package (€700)"
        elif score < 60:
            return "Standard Package (€400)"
        else:
            return "Basic Touch-up (€200)"
    
    def _identify_priority_fixes(self, scoring: Dict) -> List[str]:
        """Identify what needs to be fixed first"""
        fixes = []
        
        if not scoring.get('has_hours'):
            fixes.append("Add business hours")
        if not scoring.get('has_phone'):
            fixes.append("Add phone number")
        if not scoring.get('has_website'):
            fixes.append("Add website")
        if scoring.get('few_photos') or not scoring.get('sufficient_photos'):
            fixes.append("Add more photos")
        if scoring.get('average_reviews') or not scoring.get('good_reviews'):
            fixes.append("Improve review strategy")
        
        return fixes

def main():
    """Example usage of the Berlin Business Finder"""
    
    # You'll need to get a Google Places API key from Google Cloud Console
    api_key = os.getenv('GOOGLE_PLACES_API_KEY', 'YOUR_API_KEY_HERE')
    
    if api_key == 'YOUR_API_KEY_HERE':
        print("Please set your Google Places API key in GOOGLE_PLACES_API_KEY environment variable")
        print("Get one at: https://console.cloud.google.com/apis/credentials")
        return
    
    finder = BerlinBusinessFinder(api_key)
    
    # Find opportunities in restaurants niche
    print("Finding GMB optimization opportunities in Berlin restaurants...")
    opportunities = finder.find_gmb_opportunities(niche='restaurants')
    
    if not opportunities.empty:
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"berlin_gmb_opportunities_{timestamp}.csv"
        opportunities.to_csv(filename, index=False)
        
        print(f"\nFound {len(opportunities)} opportunities!")
        print(f"Results saved to: {filename}")
        
        # Show summary
        print("\n=== OPPORTUNITY SUMMARY ===")
        print(f"High Opportunity (Score < 40): {len(opportunities[opportunities['gmb_score'] < 40])}")
        print(f"Medium Opportunity (Score 40-60): {len(opportunities[(opportunities['gmb_score'] >= 40) & (opportunities['gmb_score'] < 60)])}")
        print(f"Low Opportunity (Score 60+): {len(opportunities[opportunities['gmb_score'] >= 60])}")
        
        print("\n=== TOP 5 OPPORTUNITIES ===")
        top_opportunities = opportunities.nsmallest(5, 'gmb_score')
        for _, opp in top_opportunities.iterrows():
            print(f"\n{opp['business_name']}")
            print(f"  Score: {opp['gmb_score']}/100")
            print(f"  Package: {opp['estimated_package']}")
            print(f"  Priority Fixes: {', '.join(opp['priority_fixes'])}")
            print(f"  Address: {opp['address']}")
    
    else:
        print("No opportunities found. Try adjusting score range or different niche.")

if __name__ == "__main__":
    main()