# GMB Dashboard Setup Guide

*Complete step-by-step guide to deploy your client success dashboard*

---

## Quick Start (Get Running in 30 Minutes)

### **Prerequisites**
- Python 3.8+ installed
- Basic command line knowledge
- Gmail account for email reports
- €10/month for hosting (optional, can run locally first)

### **Step 1: Environment Setup**
```bash
# Create project directory
mkdir gmb-dashboard
cd gmb-dashboard

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install required packages
pip install streamlit pandas plotly sqlite3 requests python-dotenv
```

### **Step 2: Download and Setup Files**
```bash
# Copy the framework file to your directory
# (You already have GMB_Dashboard_Code_Framework.py)

# Create environment file for API keys
touch .env
```

Add to `.env` file:
```
GMB_API_KEY=your_google_my_business_api_key
ANALYTICS_API_KEY=your_google_analytics_api_key
EMAIL_PASSWORD=your_gmail_app_password
```

### **Step 3: Initialize Sample Data**
```bash
# Run the setup script to create sample data
python GMB_Dashboard_Code_Framework.py
```

In the Python file, uncomment this line at the bottom:
```python
setup_sample_data()  # Uncomment this line
```

### **Step 4: Launch Dashboard**
```bash
# Start the Streamlit dashboard
streamlit run GMB_Dashboard_Code_Framework.py
```

**Test Login Credentials:**
- Email: `owner@samplerestaurant.de`
- Password: `password123`

---

## Production Deployment

### **Option 1: Heroku Deployment (Recommended)**

**Step 1: Prepare for Heroku**
```bash
# Install Heroku CLI
# macOS: brew install heroku/brew/heroku
# Windows: Download from heroku.com

# Create requirements.txt
pip freeze > requirements.txt

# Create Procfile
echo "web: streamlit run GMB_Dashboard_Code_Framework.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# Create runtime.txt
echo "python-3.9.16" > runtime.txt
```

**Step 2: Deploy to Heroku**
```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-gmb-dashboard

# Set environment variables
heroku config:set GMB_API_KEY=your_api_key
heroku config:set ANALYTICS_API_KEY=your_analytics_key
heroku config:set EMAIL_PASSWORD=your_email_password

# Deploy
git init
git add .
git commit -m "Initial deployment"
git push heroku main
```

**Cost: €7/month for basic dyno**

### **Option 2: DigitalOcean Droplet**

**Step 1: Create Droplet**
- Create €10/month droplet (1GB RAM, Ubuntu 20.04)
- SSH into your server

**Step 2: Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv nginx -y

# Create app directory
sudo mkdir /var/www/gmb-dashboard
sudo chown $USER:$USER /var/www/gmb-dashboard
cd /var/www/gmb-dashboard

# Upload your files (use scp or git)
git clone your-repository .

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Step 3: Configure Nginx and Systemd**
```bash
# Create systemd service
sudo nano /etc/systemd/system/gmb-dashboard.service
```

Add to service file:
```ini
[Unit]
Description=GMB Dashboard
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/gmb-dashboard
Environment=PATH=/var/www/gmb-dashboard/venv/bin
ExecStart=/var/www/gmb-dashboard/venv/bin/streamlit run GMB_Dashboard_Code_Framework.py --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl daemon-reload
sudo systemctl enable gmb-dashboard
sudo systemctl start gmb-dashboard

# Configure Nginx
sudo nano /etc/nginx/sites-available/gmb-dashboard
```

Add Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/gmb-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Google API Setup

### **Google My Business API**

**Step 1: Create Google Cloud Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "GMB Dashboard"
3. Enable Google My Business API
4. Create service account credentials

**Step 2: Set Up Authentication**
```python
# Add to your code
from google.oauth2 import service_account
from googleapiclient.discovery import build

def setup_gmb_api():
    credentials = service_account.Credentials.from_service_account_file(
        'path/to/service-account-key.json',
        scopes=['https://www.googleapis.com/auth/business.manage']
    )
    
    service = build('mybusinessbusinessinformation', 'v1', credentials=credentials)
    return service
```

**Step 3: Get Location Data**
```python
def get_gmb_insights(service, location_name, start_date, end_date):
    request = service.locations().reportInsights(
        name=location_name,
        body={
            'locationNames': [location_name],
            'basicRequest': {
                'timeRange': {
                    'startTime': start_date,
                    'endTime': end_date
                },
                'metricRequests': [
                    {'metric': 'QUERIES_DIRECT'},
                    {'metric': 'QUERIES_INDIRECT'},
                    {'metric': 'VIEWS_MAPS'},
                    {'metric': 'VIEWS_SEARCH'},
                    {'metric': 'ACTIONS_WEBSITE'},
                    {'metric': 'ACTIONS_PHONE'},
                    {'metric': 'ACTIONS_DRIVING_DIRECTIONS'}
                ]
            }
        }
    )
    
    return request.execute()
```

### **Google Analytics API**

**Step 1: Enable Analytics API**
1. In same Google Cloud project
2. Enable Google Analytics Reporting API
3. Use same service account

**Step 2: Get Website Traffic Data**
```python
from googleapiclient.discovery import build

def setup_analytics_api():
    credentials = service_account.Credentials.from_service_account_file(
        'path/to/service-account-key.json',
        scopes=['https://www.googleapis.com/auth/analytics.readonly']
    )
    
    analytics = build('analyticsreporting', 'v4', credentials=credentials)
    return analytics

def get_analytics_data(analytics, view_id, start_date, end_date):
    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                    'metrics': [
                        {'expression': 'ga:sessions'},
                        {'expression': 'ga:users'},
                        {'expression': 'ga:pageviews'}
                    ],
                    'dimensions': [{'name': 'ga:date'}]
                }
            ]
        }
    ).execute()
```

---

## Client Onboarding Process

### **Step 1: Create Client Account**
```python
# Add new client through admin interface
def add_new_client():
    st.title("Add New Client")
    
    with st.form("new_client"):
        business_name = st.text_input("Business Name")
        email = st.text_input("Email")
        password = st.text_input("Temporary Password")
        tier = st.selectbox("Subscription Tier", ["basic", "professional", "enterprise"])
        
        if st.form_submit_button("Create Client"):
            db = DatabaseManager()
            client_id = db.add_client(business_name, email, password, tier)
            st.success(f"Client created with ID: {client_id}")
```

### **Step 2: Connect GMB Account**
```python
def connect_gmb_account(client_id):
    st.subheader("Connect Google My Business Account")
    
    # OAuth2 flow for client to authorize access
    # This requires implementing Google OAuth2
    
    gmb_location_id = st.text_input("GMB Location ID")
    
    if st.button("Test Connection"):
        # Test API connection
        try:
            data = fetch_gmb_data(gmb_location_id)
            st.success("Connection successful!")
        except Exception as e:
            st.error(f"Connection failed: {e}")
```

### **Step 3: Set Up Competitor Tracking**
```python
def setup_competitor_tracking(client_id):
    st.subheader("Competitor Tracking Setup")
    
    competitors = st.text_area(
        "Enter competitor business names (one per line)",
        placeholder="Competitor Restaurant 1\nCompetitor Restaurant 2"
    )
    
    if st.button("Add Competitors"):
        competitor_list = competitors.strip().split('\n')
        for competitor in competitor_list:
            if competitor.strip():
                # Add competitor to database
                add_competitor(client_id, competitor.strip())
        
        st.success(f"Added {len(competitor_list)} competitors for tracking")
```

---

## Pricing and Billing Integration

### **Stripe Integration**
```python
import stripe

stripe.api_key = "your_stripe_secret_key"

def create_subscription(client_email, price_id):
    try:
        # Create customer
        customer = stripe.Customer.create(
            email=client_email,
            description=f"GMB Dashboard Client"
        )
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'price': price_id}],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )
        
        return subscription
    except Exception as e:
        return None

def handle_webhook(request):
    payload = request.body
    sig_header = request.headers.get('stripe-signature')
    endpoint_secret = 'your_webhook_secret'
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400
    
    # Handle subscription events
    if event['type'] == 'invoice.payment_succeeded':
        # Update client subscription status
        pass
    elif event['type'] == 'invoice.payment_failed':
        # Handle failed payment
        pass
    
    return "Success", 200
```

### **Subscription Management**
```python
def subscription_management_page():
    st.title("Subscription Management")
    
    client = st.session_state.client
    
    # Display current plan
    st.subheader(f"Current Plan: {client['subscription_tier'].title()}")
    
    # Plan comparison
    plans = {
        'basic': {'price': 150, 'features': ['Basic metrics', 'Monthly reports']},
        'professional': {'price': 300, 'features': ['All basic features', 'ROI tracking', 'Competitor analysis']},
        'enterprise': {'price': 500, 'features': ['All professional features', 'Multi-location', 'API access']}
    }
    
    for plan_name, plan_info in plans.items():
        with st.expander(f"{plan_name.title()} Plan - €{plan_info['price']}/month"):
            for feature in plan_info['features']:
                st.write(f"✅ {feature}")
            
            if plan_name != client['subscription_tier']:
                if st.button(f"Upgrade to {plan_name.title()}", key=plan_name):
                    # Handle plan upgrade
                    upgrade_subscription(client['id'], plan_name)
```

---

## Automated Reporting System

### **Email Report Automation**
```python
import schedule
import time
from datetime import datetime

def send_monthly_reports():
    """Send monthly reports to all active clients"""
    db = DatabaseManager()
    report_gen = ReportGenerator(db)
    
    # Get all active clients
    clients = db.get_active_clients()
    
    for client in clients:
        try:
            # Generate report
            report = report_gen.generate_monthly_report(client['id'])
            
            # Send email
            success = report_gen.send_email_report(client['email'], report)
            
            if success:
                print(f"Report sent to {client['business_name']}")
            else:
                print(f"Failed to send report to {client['business_name']}")
                
        except Exception as e:
            print(f"Error processing {client['business_name']}: {e}")

# Schedule monthly reports
schedule.every().month.do(send_monthly_reports)

# Run scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour
```

### **Performance Alerts**
```python
def check_performance_alerts():
    """Check for significant performance changes and alert clients"""
    db = DatabaseManager()
    clients = db.get_active_clients()
    
    for client in clients:
        # Get recent performance data
        df = db.get_performance_data(client['id'], 7)
        
        if len(df) >= 7:
            # Calculate week-over-week changes
            current_week = df.head(7)['profile_views'].sum()
            previous_week = df.tail(7)['profile_views'].sum()
            
            change_percent = ((current_week - previous_week) / previous_week) * 100
            
            # Alert for significant changes (>20% up or down)
            if abs(change_percent) > 20:
                send_alert_email(
                    client['email'],
                    f"GMB Performance Alert: {change_percent:+.1f}% change in profile views",
                    f"Your profile views changed by {change_percent:+.1f}% this week. "
                    f"Current week: {current_week:,} views, Previous week: {previous_week:,} views."
                )

# Schedule daily alert checks
schedule.every().day.at("09:00").do(check_performance_alerts)
```

---

## Security and Data Protection

### **Data Encryption**
```python
from cryptography.fernet import Fernet
import os

def generate_key():
    """Generate encryption key"""
    key = Fernet.generate_key()
    with open('secret.key', 'wb') as key_file:
        key_file.write(key)

def load_key():
    """Load encryption key"""
    return open('secret.key', 'rb').read()

def encrypt_sensitive_data(data):
    """Encrypt sensitive client data"""
    key = load_key()
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

def decrypt_sensitive_data(encrypted_data):
    """Decrypt sensitive client data"""
    key = load_key()
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data)
    return decrypted_data.decode()
```

### **GDPR Compliance**
```python
def handle_data_deletion_request(client_id):
    """Handle GDPR data deletion requests"""
    db = DatabaseManager()
    
    try:
        # Delete all client data
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Delete from all tables
        cursor.execute("DELETE FROM gmb_performance WHERE client_id = ?", (client_id,))
        cursor.execute("DELETE FROM competitor_data WHERE client_id = ?", (client_id,))
        cursor.execute("DELETE FROM client_settings WHERE client_id = ?", (client_id,))
        cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error deleting client data: {e}")
        return False

def export_client_data(client_id):
    """Export all client data for GDPR compliance"""
    db = DatabaseManager()
    
    # Get all client data
    client_data = {
        'client_info': db.get_client_info(client_id),
        'performance_data': db.get_performance_data(client_id, 365).to_dict(),
        'competitor_data': db.get_competitor_data(client_id),
        'settings': db.get_client_settings(client_id)
    }
    
    return client_data
```

---

## Monitoring and Maintenance

### **System Health Monitoring**
```python
import psutil
import logging

def system_health_check():
    """Monitor system health and performance"""
    
    # Check CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # Check memory usage
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    # Check disk usage
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    
    # Log warnings for high usage
    if cpu_percent > 80:
        logging.warning(f"High CPU usage: {cpu_percent}%")
    
    if memory_percent > 80:
        logging.warning(f"High memory usage: {memory_percent}%")
    
    if disk_percent > 80:
        logging.warning(f"High disk usage: {disk_percent}%")
    
    return {
        'cpu': cpu_percent,
        'memory': memory_percent,
        'disk': disk_percent,
        'status': 'healthy' if all(x < 80 for x in [cpu_percent, memory_percent, disk_percent]) else 'warning'
    }

# Schedule health checks
schedule.every(15).minutes.do(system_health_check)
```

### **Database Backup**
```python
import shutil
from datetime import datetime

def backup_database():
    """Create database backup"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"gmb_dashboard_backup_{timestamp}.db"
    
    try:
        shutil.copy2(DATABASE_PATH, f"backups/{backup_filename}")
        print(f"Database backed up to {backup_filename}")
        
        # Keep only last 30 backups
        cleanup_old_backups()
        
    except Exception as e:
        print(f"Backup failed: {e}")

def cleanup_old_backups():
    """Remove backups older than 30 days"""
    import glob
    import os
    from datetime import datetime, timedelta
    
    backup_files = glob.glob("backups/gmb_dashboard_backup_*.db")
    cutoff_date = datetime.now() - timedelta(days=30)
    
    for backup_file in backup_files:
        file_time = datetime.fromtimestamp(os.path.getctime(backup_file))
        if file_time < cutoff_date:
            os.remove(backup_file)
            print(f"Removed old backup: {backup_file}")

# Schedule daily backups
schedule.every().day.at("02:00").do(backup_database)
```

---

## Launch Checklist

### **Pre-Launch (Week 1)**
- [ ] Set up development environment
- [ ] Test dashboard with sample data
- [ ] Configure Google APIs
- [ ] Set up email system
- [ ] Create basic client onboarding process

### **Beta Launch (Week 2)**
- [ ] Deploy to staging environment
- [ ] Test with 2-3 existing clients
- [ ] Gather feedback and iterate
- [ ] Fix any bugs or issues
- [ ] Create user documentation

### **Production Launch (Week 3)**
- [ ] Deploy to production environment
- [ ] Set up monitoring and alerts
- [ ] Configure automated backups
- [ ] Launch with all existing clients
- [ ] Create marketing materials

### **Post-Launch (Week 4)**
- [ ] Monitor system performance
- [ ] Collect client feedback
- [ ] Plan feature improvements
- [ ] Set up billing and subscriptions
- [ ] Scale infrastructure as needed

---

## Success Metrics

### **Technical Metrics**
- System uptime: >99.5%
- Page load time: <3 seconds
- API response time: <1 second
- Error rate: <1%

### **Business Metrics**
- Client retention rate: >90%
- Monthly recurring revenue growth: >20%
- Client satisfaction score: >4.5/5
- Support ticket volume: <5% of active users

### **Client Success Metrics**
- Dashboard usage: >80% monthly active users
- Report engagement: >60% open rate
- Feature adoption: >50% use advanced features
- Referral rate: >20% of clients refer others

---

*Remember: Start simple, launch fast, iterate based on real client feedback. Your first version doesn't need to be perfect - it just needs to solve the core problem and generate recurring revenue.*