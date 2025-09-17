#!/usr/bin/env python3
"""
Berlin Business Niche Analyzer
Determines which niches have the most GMB optimization opportunities
"""

import pandas as pd
from berlin_business_finder import BerlinBusinessFinder
import os
from typing import Dict, List
import json

class NicheAnalyzer:
    def __init__(self, api_key: str):
        self.finder = BerlinBusinessFinder(api_key)
        
    def analyze_all_niches(self, sample_size: int = 50) -> Dict:
        """Analyze opportunity potential across all niches"""
        
        niche_analysis = {}
        
        for niche_name, categories in self.finder.target_categories.items():
            print(f"\nAnalyzing {niche_name} niche...")
            
            niche_data = {
                'total_businesses': 0,
                'opportunities': 0,
                'high_opportunity': 0,
                'medium_opportunity': 0,
                'low_opportunity': 0,
                'avg_score': 0,
                'revenue_potential': 0,
                'avg_review_count': 0,
                'avg_rating': 0,
                'common_issues': [],
                'recommended_packages': {}
            }
            
            all_businesses = []
            
            # Sample businesses from each category in the niche
            for category in categories:
                businesses = self.finder.search_businesses_by_category(category)
                # Limit sample to prevent API quota issues
                sample_businesses = businesses[:min(sample_size // len(categories), 20)]
                all_businesses.extend(sample_businesses)
            
            scores = []
            issues = []
            packages = []
            ratings = []
            review_counts = []
            
            for business in all_businesses:
                place_id = business.get('place_id')
                if not place_id:
                    continue
                    
                details = self.finder.get_business_details(place_id)
                if not details:
                    continue
                
                scoring = self.finder.score_gmb_listing(details)
                score = scoring['total_score']
                scores.append(score)
                
                # Collect common issues
                fixes = self.finder._identify_priority_fixes(scoring)
                issues.extend(fixes)
                
                # Collect package recommendations
                package = self.finder._suggest_package(scoring)
                packages.append(package)
                
                # Collect rating and review data
                rating = details.get('rating', 0)
                review_count = details.get('user_ratings_total', 0)
                ratings.append(rating)
                review_counts.append(review_count)
                
                # Categorize opportunity level
                if score < 40:
                    niche_data['high_opportunity'] += 1
                elif score < 60:
                    niche_data['medium_opportunity'] += 1
                else:
                    niche_data['low_opportunity'] += 1
            
            if scores:
                niche_data['total_businesses'] = len(scores)
                niche_data['opportunities'] = len([s for s in scores if 30 <= s <= 70])
                niche_data['avg_score'] = round(sum(scores) / len(scores), 1)
                niche_data['avg_rating'] = round(sum(ratings) / len(ratings), 1) if ratings else 0
                niche_data['avg_review_count'] = round(sum(review_counts) / len(review_counts), 1) if review_counts else 0
                
                # Calculate revenue potential
                high_revenue = niche_data['high_opportunity'] * 700  # Premium packages
                medium_revenue = niche_data['medium_opportunity'] * 400  # Standard packages
                low_revenue = niche_data['low_opportunity'] * 200  # Basic packages
                niche_data['revenue_potential'] = high_revenue + medium_revenue + low_revenue
                
                # Find most common issues
                issue_counts = {}
                for issue in issues:
                    issue_counts[issue] = issue_counts.get(issue, 0) + 1
                niche_data['common_issues'] = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                
                # Package distribution
                package_counts = {}
                for package in packages:
                    package_counts[package] = package_counts.get(package, 0) + 1
                niche_data['recommended_packages'] = package_counts
            
            niche_analysis[niche_name] = niche_data
            
        return niche_analysis
    
    def rank_niches(self, analysis: Dict) -> List[Dict]:
        """Rank niches by opportunity potential"""
        
        ranked_niches = []
        
        for niche_name, data in analysis.items():
            if data['total_businesses'] == 0:
                continue
                
            # Calculate opportunity score (0-100)
            opportunity_percentage = (data['opportunities'] / data['total_businesses']) * 100
            high_opp_percentage = (data['high_opportunity'] / data['total_businesses']) * 100
            revenue_per_business = data['revenue_potential'] / data['total_businesses'] if data['total_businesses'] > 0 else 0
            
            # Combined score weights different factors
            opportunity_score = (
                opportunity_percentage * 0.4 +  # 40% weight on total opportunities
                high_opp_percentage * 0.3 +     # 30% weight on high-value opportunities  
                (revenue_per_business / 10) * 0.2 +  # 20% weight on revenue potential
                (100 - data['avg_score']) * 0.1     # 10% weight on how much improvement needed
            )
            
            ranked_niches.append({
                'niche': niche_name,
                'opportunity_score': round(opportunity_score, 1),
                'total_businesses': data['total_businesses'],
                'opportunities': data['opportunities'],
                'opportunity_percentage': round(opportunity_percentage, 1),
                'high_opportunity': data['high_opportunity'],
                'revenue_potential': data['revenue_potential'],
                'avg_score': data['avg_score'],
                'avg_rating': data['avg_rating'],
                'top_issues': [issue[0] for issue in data['common_issues'][:2]],
                'recommendation': self._get_niche_recommendation(data)
            })
        
        return sorted(ranked_niches, key=lambda x: x['opportunity_score'], reverse=True)
    
    def _get_niche_recommendation(self, data: Dict) -> str:
        """Generate recommendation for each niche"""
        
        if data['high_opportunity'] >= 5:
            return "🎯 HIGH PRIORITY - Many businesses need major help"
        elif data['opportunities'] >= 10:
            return "✅ GOOD TARGET - Solid opportunity volume"
        elif data['avg_score'] < 50:
            return "🔧 POTENTIAL - Low scores but fewer businesses"
        else:
            return "⚠️ SATURATED - Most businesses already optimized"
    
    def generate_niche_report(self, ranked_niches: List[Dict]) -> str:
        """Generate a detailed niche analysis report"""
        
        report = """
# Berlin GMB Optimization - Niche Analysis Report

## Executive Summary

Based on analysis of Berlin businesses across 5 major niches, here are the top opportunities:

"""
        
        for i, niche in enumerate(ranked_niches[:3], 1):
            report += f"""
### #{i}. {niche['niche'].title().replace('_', ' & ')} - Score: {niche['opportunity_score']}/100

**Key Metrics:**
- 📊 Businesses analyzed: {niche['total_businesses']}
- 🎯 Optimization opportunities: {niche['opportunities']} ({niche['opportunity_percentage']}%)
- 💰 Revenue potential: €{niche['revenue_potential']:,}
- 📈 Average GMB score: {niche['avg_score']}/100
- ⭐ Average rating: {niche['avg_rating']}/5

**Top Issues to Fix:**
{chr(10).join(f"- {issue}" for issue in niche['top_issues'])}

**Recommendation:** {niche['recommendation']}

---
"""
        
        report += """
## Detailed Niche Comparison

| Niche | Opp Score | Total Biz | Opportunities | Revenue Pot | Avg Score | Recommendation |
|-------|-----------|-----------|---------------|-------------|-----------|----------------|
"""
        
        for niche in ranked_niches:
            report += f"| {niche['niche'].replace('_', ' ')} | {niche['opportunity_score']} | {niche['total_businesses']} | {niche['opportunities']} | €{niche['revenue_potential']:,} | {niche['avg_score']} | {niche['recommendation']} |\n"
        
        report += """

## Action Plan Recommendations

### Start Here (Week 1):
Focus on **""" + ranked_niches[0]['niche'].replace('_', ' ').title() + f"""** - highest opportunity score of {ranked_niches[0]['opportunity_score']}/100

### Expand To (Week 2-3):
Add **""" + ranked_niches[1]['niche'].replace('_', ' ').title() + f"""** - solid secondary market with {ranked_niches[1]['opportunities']} opportunities

### Scale With (Month 2):
Include **""" + ranked_niches[2]['niche'].replace('_', ' ').title() + f"""** - additional {ranked_niches[2]['revenue_potential']} euro revenue potential

## Next Steps

1. **Run targeted search** on top niche using: `finder.find_gmb_opportunities(niche='{ranked_niches[0]['niche']}')`
2. **Create niche-specific scripts** addressing top issues identified
3. **Start manual outreach** with data-backed audit reports
4. **Track conversion rates** by niche to validate analysis

*Analysis based on Google Places API data for Berlin businesses.*
"""
        
        return report

def main():
    """Run complete niche analysis"""
    
    api_key = os.getenv('GOOGLE_PLACES_API_KEY', 'YOUR_API_KEY_HERE')
    
    if api_key == 'YOUR_API_KEY_HERE':
        print("Please set your Google Places API key in GOOGLE_PLACES_API_KEY environment variable")
        return
    
    analyzer = NicheAnalyzer(api_key)
    
    print("🔍 Analyzing Berlin business niches for GMB opportunities...")
    print("This may take 5-10 minutes due to API rate limits...")
    
    # Analyze all niches
    analysis = analyzer.analyze_all_niches(sample_size=30)
    
    # Rank by opportunity
    ranked_niches = analyzer.rank_niches(analysis)
    
    # Generate report
    report = analyzer.generate_niche_report(ranked_niches)
    
    # Save results
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save detailed analysis as JSON
    with open(f"niche_analysis_{timestamp}.json", 'w') as f:
        json.dump({
            'analysis': analysis,
            'ranked_niches': ranked_niches,
            'timestamp': timestamp
        }, f, indent=2)
    
    # Save human-readable report
    with open(f"niche_report_{timestamp}.md", 'w') as f:
        f.write(report)
    
    print(f"\n✅ Analysis complete!")
    print(f"📊 Detailed data: niche_analysis_{timestamp}.json")
    print(f"📋 Report: niche_report_{timestamp}.md")
    
    # Show quick summary
    print(f"\n🏆 TOP 3 NICHES FOR GMB OPTIMIZATION:")
    for i, niche in enumerate(ranked_niches[:3], 1):
        print(f"{i}. {niche['niche'].replace('_', ' ').title()}: {niche['opportunity_score']}/100 ({niche['opportunities']} opportunities)")
    
    print(f"\n💡 Start with {ranked_niches[0]['niche'].replace('_', ' ')} - highest potential!")

if __name__ == "__main__":
    main()