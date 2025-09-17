# Berlin Business GMB Opportunity Finder - Setup Guide

## Quick Setup (5 minutes)

### 1. Get Google Places API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing one
3. Enable "Places API"
4. Create credentials → API Key
5. **Important**: Restrict the key to Places API only for security

### 2. Install Requirements
```bash
cd /Users/samhizam/Documents/B2B
pip install -r requirements.txt
```

### 3. Set Your API Key
```bash
export GOOGLE_PLACES_API_KEY="your_actual_api_key_here"
```

### 4. Run the Automation
```bash
python berlin_business_finder.py
```

## What This Does

**Automatically finds Berlin businesses with GMB optimization opportunities:**

1. **Searches multiple niches**: restaurants, health/wellness, professional services, retail, services
2. **Scores each business 0-100** based on:
   - Basic info completeness (25 pts)
   - Photo count (20 pts) 
   - Reviews & rating (25 pts)
   - Business description (15 pts)
   - Recent activity (15 pts)

3. **Identifies opportunities** (scores 30-70 = good prospects)
4. **Suggests packages** based on needs
5. **Prioritizes fixes** for each business
6. **Exports to CSV** for follow-up

## Example Output

```
Found 47 opportunities!

=== TOP 5 OPPORTUNITIES ===

Café Berlin Mitte
  Score: 32/100
  Package: Premium Package (€700)
  Priority Fixes: Add business hours, Add more photos, Improve review strategy
  Address: Friedrichstraße 123, 10117 Berlin

Restaurant Zur Linde
  Score: 38/100  
  Package: Premium Package (€700)
  Priority Fixes: Add website, Add more photos
  Address: Prenzlauer Allee 45, 10405 Berlin
```

## Cost Analysis

**Google Places API Pricing:**
- Text Search: €17 per 1,000 requests
- Place Details: €17 per 1,000 requests
- **Total cost to find 100 opportunities: ~€3-5**

**ROI:**
- If you close 2 clients at €400 each = €800 revenue
- API costs = €5
- **ROI: 16,000%**

## Niche-Specific Search

**To focus on specific niches, modify the script:**

```python
# Restaurants only
opportunities = finder.find_gmb_opportunities(niche='restaurants')

# Health & wellness only  
opportunities = finder.find_gmb_opportunities(niche='health_wellness')

# Professional services only
opportunities = finder.find_gmb_opportunities(niche='professional')
```

## Advanced Features

### 1. Competitor Analysis
Add this function to track what other GMB services are doing:

```python
def analyze_competitors(self):
    competitors = [
        "gmb optimization berlin",
        "google my business service berlin", 
        "local seo berlin"
    ]
    # Search and analyze competitor offerings
```

### 2. Contact Information Extraction
Enhance to get email addresses and social media:

```python
def extract_contact_info(self, business_details):
    # Parse website for contact forms
    # Find social media profiles
    # Extract decision maker names
```

### 3. Automated Outreach Preparation
Generate personalized audit reports:

```python
def generate_audit_report(self, business_data):
    # Create PDF audit report
    # Include specific improvement recommendations
    # Add competitor comparison
```

## Next Steps After Running

1. **Review the CSV output** - sort by lowest scores first
2. **Verify contact information** - check websites for email addresses
3. **Create personalized audit reports** for top 10 prospects
4. **Start outreach** with specific, data-backed improvement suggestions

## Scaling Options

**Week 1**: Run script for one niche (restaurants)
**Week 2**: Expand to health/wellness  
**Week 3**: Add professional services
**Week 4**: Full automation across all niches

**Monthly**: Re-run to find new businesses and track improvements

## Legal & Ethical Notes

- ✅ Uses public Google Places data
- ✅ Respects API rate limits
- ✅ No scraping of private data
- ✅ Provides value to businesses contacted

This automation gives you data-driven confidence and specific talking points for every prospect - no more guessing or cold calling!