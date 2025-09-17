#!/usr/bin/env python3
"""
GMB Client Success Dashboard - MVP Framework
A complete system to transform one-time GMB clients into recurring revenue
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import requests
from typing import Dict, List, Optional
import os

# Configuration
DATABASE_PATH = "gmb_dashboard.db"
API_KEYS = {
    'gmb_api_key': os.getenv('GMB_API_KEY', 'your_gmb_api_key'),
    'analytics_api_key': os.getenv('ANALYTICS_API_KEY', 'your_analytics_key')
}

class DatabaseManager:
    """Handle all database operations"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                subscription_tier TEXT DEFAULT 'basic',
                gmb_location_id TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # GMB Performance Data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gmb_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                date DATE NOT NULL,
                profile_views INTEGER DEFAULT 0,
                search_views INTEGER DEFAULT 0,
                maps_views INTEGER DEFAULT 0,
                phone_calls INTEGER DEFAULT 0,
                direction_requests INTEGER DEFAULT 0,
                website_clicks INTEGER DEFAULT 0,
                photo_views INTEGER DEFAULT 0,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        # Competitor Data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                competitor_name TEXT NOT NULL,
                competitor_gmb_id TEXT,
                date DATE NOT NULL,
                rating REAL,
                review_count INTEGER,
                photo_count INTEGER,
                posts_last_30_days INTEGER,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        # Client Goals and Settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS client_settings (
                client_id INTEGER PRIMARY KEY,
                monthly_revenue_target REAL,
                lead_value REAL DEFAULT 100,
                conversion_rate REAL DEFAULT 0.1,
                notification_email TEXT,
                alert_thresholds TEXT, -- JSON string
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_client(self, business_name: str, email: str, password: str, 
                   subscription_tier: str = 'basic') -> int:
        """Add new client to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO clients (business_name, email, password_hash, subscription_tier)
            VALUES (?, ?, ?, ?)
        ''', (business_name, email, password_hash, subscription_tier))
        
        client_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return client_id
    
    def authenticate_client(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate client login"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            SELECT id, business_name, subscription_tier, is_active
            FROM clients 
            WHERE email = ? AND password_hash = ? AND is_active = 1
        ''', (email, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'business_name': result[1],
                'subscription_tier': result[2],
                'is_active': result[3]
            }
        return None
    
    def add_performance_data(self, client_id: int, date: str, metrics: Dict):
        """Add GMB performance data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO gmb_performance 
            (client_id, date, profile_views, search_views, maps_views, 
             phone_calls, direction_requests, website_clicks, photo_views)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            client_id, date, 
            metrics.get('profile_views', 0),
            metrics.get('search_views', 0),
            metrics.get('maps_views', 0),
            metrics.get('phone_calls', 0),
            metrics.get('direction_requests', 0),
            metrics.get('website_clicks', 0),
            metrics.get('photo_views', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def get_performance_data(self, client_id: int, days: int = 30) -> pd.DataFrame:
        """Get performance data for client"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT date, profile_views, search_views, maps_views,
                   phone_calls, direction_requests, website_clicks, photo_views
            FROM gmb_performance 
            WHERE client_id = ? AND date >= date('now', '-{} days')
            ORDER BY date DESC
        '''.format(days)
        
        df = pd.read_sql_query(query, conn, params=(client_id,))
        conn.close()
        
        return df

class GMBDataCollector:
    """Collect data from Google My Business API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def fetch_insights_data(self, location_id: str, start_date: str, end_date: str) -> Dict:
        """
        Fetch GMB insights data
        Note: This is a simplified version. Real implementation requires OAuth2 setup
        """
        # Placeholder for actual GMB API call
        # In real implementation, you'd use Google's client library
        
        # Sample data structure for development
        sample_data = {
            'profile_views': 150 + (hash(location_id) % 100),
            'search_views': 100 + (hash(location_id) % 50),
            'maps_views': 50 + (hash(location_id) % 30),
            'phone_calls': 25 + (hash(location_id) % 15),
            'direction_requests': 35 + (hash(location_id) % 20),
            'website_clicks': 45 + (hash(location_id) % 25),
            'photo_views': 200 + (hash(location_id) % 150)
        }
        
        return sample_data
    
    def get_competitor_data(self, competitor_name: str) -> Dict:
        """Get basic competitor information"""
        # Placeholder for competitor data collection
        # In real implementation, you'd scrape public GMB data carefully
        
        sample_competitor_data = {
            'rating': 4.2 + (hash(competitor_name) % 8) / 10,
            'review_count': 50 + (hash(competitor_name) % 200),
            'photo_count': 15 + (hash(competitor_name) % 30),
            'posts_last_30_days': hash(competitor_name) % 10
        }
        
        return sample_competitor_data

class ROICalculator:
    """Calculate ROI and business impact metrics"""
    
    @staticmethod
    def calculate_lead_value(phone_calls: int, direction_requests: int, 
                           website_clicks: int, conversion_rate: float = 0.1,
                           avg_lead_value: float = 100) -> Dict:
        """Calculate estimated lead value from GMB metrics"""
        
        total_actions = phone_calls + direction_requests + website_clicks
        estimated_leads = total_actions * conversion_rate
        estimated_revenue = estimated_leads * avg_lead_value
        
        return {
            'total_actions': total_actions,
            'estimated_leads': round(estimated_leads, 1),
            'estimated_revenue': round(estimated_revenue, 2),
            'cost_per_lead': round(avg_lead_value / conversion_rate, 2) if conversion_rate > 0 else 0
        }
    
    @staticmethod
    def calculate_monthly_roi(current_revenue: float, baseline_revenue: float,
                            monthly_service_cost: float) -> Dict:
        """Calculate ROI of GMB optimization service"""
        
        revenue_increase = current_revenue - baseline_revenue
        roi_percentage = ((revenue_increase - monthly_service_cost) / monthly_service_cost * 100) if monthly_service_cost > 0 else 0
        
        return {
            'revenue_increase': round(revenue_increase, 2),
            'roi_percentage': round(roi_percentage, 1),
            'payback_period_days': round((monthly_service_cost / (revenue_increase / 30)), 1) if revenue_increase > 0 else 0
        }

class DashboardUI:
    """Main dashboard interface using Streamlit"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.gmb_collector = GMBDataCollector(API_KEYS['gmb_api_key'])
        
        # Configure Streamlit page
        st.set_page_config(
            page_title="GMB Success Dashboard",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def login_page(self):
        """Client login interface"""
        st.title("🚀 GMB Success Dashboard")
        st.subheader("Login to view your Google My Business performance")
        
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                client = self.db.authenticate_client(email, password)
                if client:
                    st.session_state.client = client
                    st.success(f"Welcome back, {client['business_name']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
    
    def main_dashboard(self, client: Dict):
        """Main dashboard interface"""
        st.title(f"📊 {client['business_name']} - GMB Performance Dashboard")
        
        # Sidebar controls
        with st.sidebar:
            st.header("Dashboard Controls")
            
            date_range = st.selectbox(
                "Time Period",
                ["Last 7 days", "Last 30 days", "Last 90 days"],
                index=1
            )
            
            days_map = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90}
            days = days_map[date_range]
            
            if st.button("Refresh Data"):
                self.update_client_data(client['id'])
                st.success("Data updated!")
        
        # Get performance data
        df = self.db.get_performance_data(client['id'], days)
        
        if df.empty:
            st.warning("No data available. Please contact support to set up data collection.")
            return
        
        # Key Metrics Row
        self.display_key_metrics(df)
        
        # Charts Row
        col1, col2 = st.columns(2)
        
        with col1:
            self.display_performance_chart(df)
        
        with col2:
            self.display_actions_chart(df)
        
        # ROI Analysis
        if client['subscription_tier'] in ['professional', 'enterprise']:
            self.display_roi_analysis(df, client)
        
        # Competitor Analysis
        if client['subscription_tier'] == 'enterprise':
            self.display_competitor_analysis(client['id'])
    
    def display_key_metrics(self, df: pd.DataFrame):
        """Display key performance metrics"""
        if len(df) < 2:
            return
        
        current = df.iloc[0]
        previous = df.iloc[1] if len(df) > 1 else df.iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            delta = current['profile_views'] - previous['profile_views']
            st.metric(
                "Profile Views",
                f"{current['profile_views']:,}",
                delta=f"{delta:+,}"
            )
        
        with col2:
            delta = current['phone_calls'] - previous['phone_calls']
            st.metric(
                "Phone Calls",
                f"{current['phone_calls']:,}",
                delta=f"{delta:+,}"
            )
        
        with col3:
            delta = current['direction_requests'] - previous['direction_requests']
            st.metric(
                "Direction Requests",
                f"{current['direction_requests']:,}",
                delta=f"{delta:+,}"
            )
        
        with col4:
            delta = current['website_clicks'] - previous['website_clicks']
            st.metric(
                "Website Clicks",
                f"{current['website_clicks']:,}",
                delta=f"{delta:+,}"
            )
    
    def display_performance_chart(self, df: pd.DataFrame):
        """Display performance trend chart"""
        st.subheader("📈 Performance Trends")
        
        fig = px.line(
            df, 
            x='date', 
            y=['profile_views', 'search_views', 'maps_views'],
            title="Views Over Time",
            labels={'value': 'Views', 'date': 'Date'}
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Views",
            legend_title="Metric Type"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_actions_chart(self, df: pd.DataFrame):
        """Display customer actions chart"""
        st.subheader("🎯 Customer Actions")
        
        # Create stacked bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['phone_calls'],
            name='Phone Calls',
            marker_color='#FF6B6B'
        ))
        
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['direction_requests'],
            name='Directions',
            marker_color='#4ECDC4'
        ))
        
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['website_clicks'],
            name='Website Clicks',
            marker_color='#45B7D1'
        ))
        
        fig.update_layout(
            title="Customer Actions Over Time",
            xaxis_title="Date",
            yaxis_title="Actions",
            barmode='stack'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_roi_analysis(self, df: pd.DataFrame, client: Dict):
        """Display ROI analysis for professional/enterprise clients"""
        st.subheader("💰 ROI Analysis")
        
        # Get latest data
        latest = df.iloc[0]
        
        # Calculate ROI metrics
        roi_data = ROICalculator.calculate_lead_value(
            latest['phone_calls'],
            latest['direction_requests'],
            latest['website_clicks']
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Estimated Monthly Leads",
                f"{roi_data['estimated_leads']}"
            )
        
        with col2:
            st.metric(
                "Estimated Monthly Revenue",
                f"€{roi_data['estimated_revenue']:,.2f}"
            )
        
        with col3:
            service_cost = 300  # Default professional tier cost
            roi = ((roi_data['estimated_revenue'] - service_cost) / service_cost) * 100
            st.metric(
                "ROI %",
                f"{roi:.1f}%"
            )
        
        # ROI explanation
        st.info(f"""
        **ROI Calculation**: Based on {roi_data['total_actions']} total customer actions 
        this month, with an estimated 10% conversion rate and €100 average lead value.
        
        Your GMB optimization is generating an estimated **€{roi_data['estimated_revenue']:,.2f}** 
        in monthly revenue, compared to a service cost of €{service_cost}.
        """)
    
    def display_competitor_analysis(self, client_id: int):
        """Display competitor analysis for enterprise clients"""
        st.subheader("🏆 Competitive Intelligence")
        
        # Sample competitor data
        competitors = [
            {"name": "Competitor A", "rating": 4.2, "reviews": 156, "photos": 23},
            {"name": "Competitor B", "rating": 4.0, "reviews": 89, "photos": 15},
            {"name": "Your Business", "rating": 4.5, "reviews": 203, "photos": 35}
        ]
        
        df_comp = pd.DataFrame(competitors)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                df_comp, 
                x='name', 
                y='rating',
                title="Average Rating Comparison",
                color='rating',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                df_comp, 
                x='name', 
                y='reviews',
                title="Review Count Comparison",
                color='reviews',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def update_client_data(self, client_id: int):
        """Update client data from GMB API"""
        # In real implementation, this would fetch from actual GMB API
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Generate sample data for demonstration
        sample_metrics = self.gmb_collector.fetch_insights_data(
            f"location_{client_id}", today, today
        )
        
        self.db.add_performance_data(client_id, today, sample_metrics)
    
    def run(self):
        """Main application runner"""
        # Initialize session state
        if 'client' not in st.session_state:
            st.session_state.client = None
        
        # Show login or dashboard
        if st.session_state.client is None:
            self.login_page()
        else:
            # Logout button
            if st.sidebar.button("Logout"):
                st.session_state.client = None
                st.rerun()
            
            self.main_dashboard(st.session_state.client)

class ReportGenerator:
    """Generate automated reports for clients"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def generate_monthly_report(self, client_id: int) -> str:
        """Generate monthly performance report"""
        df = self.db.get_performance_data(client_id, 30)
        
        if df.empty:
            return "No data available for report generation."
        
        # Calculate summary metrics
        total_views = df['profile_views'].sum()
        total_calls = df['phone_calls'].sum()
        total_directions = df['direction_requests'].sum()
        total_clicks = df['website_clicks'].sum()
        
        # Generate report
        report = f"""
        MONTHLY GMB PERFORMANCE REPORT
        ==============================
        
        SUMMARY METRICS (Last 30 Days):
        • Profile Views: {total_views:,}
        • Phone Calls: {total_calls:,}
        • Direction Requests: {total_directions:,}
        • Website Clicks: {total_clicks:,}
        
        KEY INSIGHTS:
        • Your GMB listing generated {total_calls + total_directions + total_clicks:,} customer actions
        • Average daily profile views: {total_views/30:.1f}
        • Estimated monthly leads: {(total_calls + total_directions + total_clicks) * 0.1:.1f}
        • Estimated revenue impact: €{(total_calls + total_directions + total_clicks) * 0.1 * 100:,.2f}
        
        RECOMMENDATIONS:
        • Continue posting regular updates to maintain visibility
        • Respond to all customer reviews promptly
        • Add more photos to increase engagement
        
        Questions? Contact your GMB specialist for a strategy review.
        """
        
        return report
    
    def send_email_report(self, client_email: str, report_content: str):
        """Send email report to client"""
        # Email configuration (use environment variables in production)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "your-business@gmail.com"
        sender_password = "your-app-password"
        
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = client_email
            msg['Subject'] = "Your Monthly GMB Performance Report"
            
            msg.attach(MIMEText(report_content, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

def setup_sample_data():
    """Set up sample data for testing"""
    db = DatabaseManager()
    
    # Add sample client
    client_id = db.add_client(
        "Sample Restaurant Berlin",
        "owner@samplerestaurant.de",
        "password123",
        "professional"
    )
    
    # Add sample performance data for last 30 days
    gmb_collector = GMBDataCollector(API_KEYS['gmb_api_key'])
    
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        metrics = gmb_collector.fetch_insights_data(f"location_{client_id}", date, date)
        
        # Add some variation to make data more realistic
        for key in metrics:
            metrics[key] = max(0, metrics[key] + (i % 7 - 3) * 5)
        
        db.add_performance_data(client_id, date, metrics)
    
    print(f"Sample data created for client ID: {client_id}")
    print("Login credentials: owner@samplerestaurant.de / password123")

if __name__ == "__main__":
    # Uncomment to set up sample data
    # setup_sample_data()
    
    # Run the dashboard
    dashboard = DashboardUI()
    dashboard.run()