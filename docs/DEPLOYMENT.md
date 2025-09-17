# Deployment Guide

## 🚀 Deployment Options

### 1. Vercel (Recommended)

#### Quick Deploy
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from project root
vercel --prod
```

#### Configuration
File: `vercel.json`
```json
{
  "name": "berlin-business-growth-assessment",
  "version": 2,
  "builds": [
    {
      "src": "index.html",
      "use": "@vercel/static"
    }
  ]
}
```

#### Environment Setup
```bash
# Set environment variables
vercel env add GOOGLE_PLACES_API_KEY
vercel env add EMAIL_SERVICE_KEY
```

### 2. Netlify

#### Deploy via Git
1. Connect GitHub repository
2. Set build command: (none needed)
3. Set publish directory: `/`
4. Deploy

#### Configuration
File: `netlify.toml`
```toml
[build]
  publish = "."
  
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
```

### 3. GitHub Pages

#### Setup
```bash
# Create gh-pages branch
git checkout -b gh-pages
git push origin gh-pages

# Enable GitHub Pages in repository settings
# Source: gh-pages branch
```

### 4. Custom Server

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/berlin-assessment;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

## 🔧 Development Workflow

### Local Development
```bash
# Clone repository
git clone https://github.com/Sam-707/berlin-business-assessment.git
cd berlin-business-assessment

# Start local server
python -m http.server 8000
# OR
npx serve .
# OR
php -S localhost:8000

# Open browser
open http://localhost:8000
```

### Development Tools
```bash
# Live reload with browser-sync
npx browser-sync start --server --files "*.html, *.css, *.js"

# Simple HTTP server with live reload
npx live-server .
```

## 🌍 Custom Domain Setup

### Vercel Custom Domain
```bash
# Add domain to Vercel project
vercel domains add yourdomain.com

# Configure DNS
# Add CNAME record: www -> cname.vercel-dns.com
# Add A record: @ -> 76.76.19.61
```

### Domain Configuration Example
```bash
# DNS Records for custom domain
Type    Name    Value
A       @       76.76.19.61
CNAME   www     cname.vercel-dns.com
```

## 📊 Analytics Setup

### Google Analytics 4
Add to `<head>` section:
```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### Event Tracking
```javascript
// Track question progression
gtag('event', 'question_answered', {
    question_number: this.currentQuestion,
    answer_value: selectedValue
});

// Track form submission
gtag('event', 'form_submit', {
    form_type: 'contact_form'
});
```

## 🔒 Security Configuration

### Content Security Policy
```html
<meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com;
    font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com;
    script-src 'self' https://www.googletagmanager.com;
    img-src 'self' data: https:;
    connect-src 'self' https://www.google-analytics.com;
">
```

### Environment Variables
```bash
# Production environment variables
GOOGLE_PLACES_API_KEY=your_api_key_here
EMAIL_SERVICE_KEY=your_email_key_here
ANALYTICS_ID=your_analytics_id_here
```

## 🚀 CI/CD Pipeline

### GitHub Actions Example
File: `.github/workflows/deploy.yml`
```yaml
name: Deploy to Vercel
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Install Vercel CLI
      run: npm install -g vercel@latest
      
    - name: Pull Vercel Environment Information
      run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
      
    - name: Build Project Artifacts
      run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
      
    - name: Deploy Project Artifacts to Vercel
      run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
```

## 📱 Mobile App Deployment (Future)

### Progressive Web App (PWA)
```json
// manifest.json
{
  "name": "Berlin Business Assessment",
  "short_name": "BBA",
  "description": "Professional business growth assessment tool",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0f0f23",
  "theme_color": "#6366f1",
  "icons": [
    {
      "src": "icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}
```

## 🔍 SEO Optimization

### Meta Tags
```html
<!-- Essential meta tags -->
<meta name="description" content="Professional business growth assessment for Berlin companies. Get personalized strategy recommendations in 5 minutes.">
<meta name="keywords" content="business consulting, Berlin, growth strategy, business assessment">

<!-- Open Graph -->
<meta property="og:title" content="Berlin Business Growth Assessment">
<meta property="og:description" content="Professional business growth assessment for Berlin companies">
<meta property="og:image" content="https://yourdomain.com/og-image.jpg">
<meta property="og:url" content="https://yourdomain.com">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Berlin Business Growth Assessment">
<meta name="twitter:description" content="Professional business growth assessment for Berlin companies">
<meta name="twitter:image" content="https://yourdomain.com/twitter-image.jpg">
```

### Structured Data
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "Berlin Business Growth Assessment",
  "description": "Professional business growth assessment tool",
  "url": "https://yourdomain.com",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Any"
}
</script>
```

## 📊 Performance Monitoring

### Web Vitals Tracking
```javascript
// Track Core Web Vitals
import {getCLS, getFID, getFCP, getLCP, getTTFB} from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getFCP(console.log);
getLCP(console.log);
getTTFB(console.log);
```

### Lighthouse CI
```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI
on: [push]
jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm install -g @lhci/cli@0.8.x
      - run: lhci autorun
```

## 🔄 Rollback Strategy

### Vercel Rollback
```bash
# List deployments
vercel ls

# Rollback to previous deployment
vercel rollback [deployment-url]
```

### Git-based Rollback
```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Or reset to specific commit
git reset --hard [commit-hash]
git push --force-with-lease origin main
```

## 📋 Pre-deployment Checklist

### Code Quality
- [ ] No console.log statements in production
- [ ] All TODO comments addressed
- [ ] Code properly formatted and linted
- [ ] All features tested manually

### Performance
- [ ] Images optimized
- [ ] CSS minified for production
- [ ] JavaScript bundled and minified
- [ ] Fonts preloaded

### SEO & Accessibility
- [ ] Meta descriptions added
- [ ] Alt text for all images
- [ ] Proper heading hierarchy
- [ ] Keyboard navigation tested

### Security
- [ ] No sensitive data in client-side code
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Environment variables secured

### Functionality
- [ ] All forms working
- [ ] Email automation tested
- [ ] Analytics tracking verified
- [ ] Mobile responsiveness confirmed

## 🚨 Troubleshooting

### Common Issues

#### Deployment Fails
```bash
# Clear Vercel cache
vercel --prod --force

# Check build logs
vercel logs [deployment-url]
```

#### CSS/JS Not Loading
```bash
# Check file paths are relative
# Ensure proper MIME types
# Verify CDN resources are accessible
```

#### Analytics Not Working
```bash
# Verify tracking ID
# Check console for errors
# Test in private/incognito mode
```

---

**Remember**: Always test in a staging environment before deploying to production!