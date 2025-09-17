#!/usr/bin/env python3
"""
Berlin Business Assessment - Email Automation System
Sends personalized results based on assessment responses
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import json
from datetime import datetime
import os

class AssessmentEmailer:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_user = os.getenv('GMAIL_USER')  # Your Gmail address
        self.email_password = os.getenv('GMAIL_APP_PASSWORD')  # Gmail App Password
        
    def classify_business_type(self, data):
        """Classify business based on assessment responses"""
        
        tech_comfort = data.get('tech_comfort', '')
        customer_acquisition = data.get('customer_acquisition', '')
        
        if tech_comfort == 'very_comfortable' and customer_acquisition == 'social_media':
            return {
                'type': 'Digital Native',
                'description': 'Sie nutzen bereits digitale Kanäle gut und können diese optimieren.',
                'icon': '📱'
            }
        elif tech_comfort == 'not_comfortable' and customer_acquisition == 'foot_traffic':
            return {
                'type': 'Traditional Business', 
                'description': 'Sie haben eine starke lokale Präsenz und können von digitaler Ergänzung profitieren.',
                'icon': '🏪'
            }
        else:
            return {
                'type': 'Hybrid Business',
                'description': 'Sie haben sowohl traditionelle als auch digitale Potentiale.',
                'icon': '🔄'
            }
    
    def generate_recommendations(self, data, business_type):
        """Generate personalized recommendations"""
        
        recommendations = []
        
        # Based on customer acquisition method
        if data.get('customer_acquisition') == 'foot_traffic':
            recommendations.extend([
                '🏪 Google My Business Profil vollständig optimieren für lokale Suchen',
                '📸 Instagram für visuelle Kundenbindung nutzen (Fotos von Produkten/Atmosphäre)',
                '⭐ Systematisches Review-Management implementieren'
            ])
        elif data.get('customer_acquisition') == 'word_of_mouth':
            recommendations.extend([
                '🎁 Empfehlungsprogramm für bestehende Kunden erstellen',
                '⭐ Zufriedene Kunden aktiv um Google-Bewertungen bitten',
                '📱 WhatsApp Business für einfache Kundenkommunikation nutzen'
            ])
        elif data.get('customer_acquisition') == 'social_media':
            recommendations.extend([
                '📊 Instagram/Facebook Analytics nutzen für bessere Zielgruppenansprache',
                '🎯 Bezahlte Social Media Werbung für lokale Zielgruppe testen',
                '📸 User-generated Content fördern (Kunden posten über Sie)'
            ])
        else:  # google_search or other
            recommendations.extend([
                '🔍 Google My Business Optimierung für bessere Sichtbarkeit',
                '📝 Lokale SEO-Strategie entwickeln',
                '💰 Google Ads für lokale Suchanfragen testen'
            ])
        
        # Based on tech comfort level
        if data.get('tech_comfort') == 'very_comfortable':
            recommendations.append('📊 Google Analytics einrichten für datenbasierte Entscheidungen')
        elif data.get('tech_comfort') == 'not_comfortable':
            recommendations.append('🤝 Mit einfachen, bewährten Tools starten (WhatsApp Business, Google My Business)')
        
        # Based on biggest challenge
        challenge = data.get('biggest_challenge', '')
        if challenge == 'not_enough_customers':
            recommendations.append('🎯 Lokale Online-Präsenz stärken (Google, Facebook, Instagram)')
        elif challenge == 'customers_not_spending':
            recommendations.append('💡 Upselling-Strategien entwickeln (Kombi-Angebote, Loyalty Programme)')
        elif challenge == 'competition':
            recommendations.append('💎 Einzigartiges Wertversprechen entwickeln und kommunizieren')
        
        return recommendations[:4]  # Return top 4 recommendations
    
    def generate_next_steps(self, data, business_type):
        """Generate actionable next steps"""
        
        steps = []
        
        if data.get('previous_attempts') == 'nothing_too_busy':
            steps.extend([
                'Google My Business Profil in 30 Minuten komplett ausfüllen',
                'Erste 10 Fotos von Ihrem Business hochladen',
                'System für Kundenbewertungen einrichten'
            ])
        else:
            steps.extend([
                'Performance der bisherigen Maßnahmen analysieren',
                'Profitabelste Kanäle identifizieren und verstärken',
                'Konkurrenzanalyse durchführen'
            ])
        
        # Always include these universal steps
        steps.extend([
            'Kundenfeedback-System implementieren',
            'Monatliche 15-Minuten Marketing-Reviews einplanen'
        ])
        
        return steps[:4]
    
    def calculate_priority_level(self, data):
        """Calculate how urgently they need help"""
        
        score = 0
        
        if data.get('biggest_challenge') == 'not_enough_customers':
            score += 3
        if data.get('previous_attempts') == 'nothing_too_busy':
            score += 2
        if data.get('customer_acquisition') == 'foot_traffic':
            score += 2
        if data.get('tech_comfort') in ['not_comfortable', 'what_is_digital']:
            score += 1
        
        if score >= 5:
            return {'level': 'HIGH', 'description': 'Hohe Priorität - Sofortiger Handlungsbedarf'}
        elif score >= 3:
            return {'level': 'MEDIUM', 'description': 'Mittlere Priorität - Handlungsbedarf in 2-4 Wochen'}
        else:
            return {'level': 'LOW', 'description': 'Niedrige Priorität - Optimierung möglich'}
    
    def create_email_content(self, data):
        """Create personalized email content"""
        
        business_type = self.classify_business_type(data)
        recommendations = self.generate_recommendations(data, business_type)
        next_steps = self.generate_next_steps(data, business_type)
        priority = self.calculate_priority_level(data)
        
        first_name = data.get('firstName', 'Liebe/r Geschäftsinhaber/in')
        business_name = data.get('businessName', 'Ihr Business')
        
        # Create HTML email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #3498db, #2980b9); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; background: #f9f9f9; }}
                .section {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #3498db; }}
                .recommendations {{ background: #e8f5e8; border-left-color: #27ae60; }}
                .steps {{ background: #fff3cd; border-left-color: #f39c12; }}
                .priority {{ background: #ffebee; border-left-color: #e74c3c; }}
                .cta {{ text-align: center; margin: 30px 0; }}
                .btn {{ background: #3498db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: bold; }}
                ul {{ padding-left: 0; list-style: none; }}
                li {{ padding: 8px 0; border-bottom: 1px solid #eee; }}
                li:before {{ content: "✓ "; color: #27ae60; font-weight: bold; }}
                ol li:before {{ content: counter(item) ". "; color: #3498db; font-weight: bold; }}
                ol {{ counter-reset: item; }}
                ol li {{ counter-increment: item; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 Ihre persönlichen Berlin Business Empfehlungen</h1>
                <p>Für {business_name}</p>
            </div>
            
            <div class="content">
                <p>Hallo {first_name},</p>
                
                <p>vielen Dank für Ihre Teilnahme an unserem Berlin Business Growth Assessment! Basierend auf Ihren Antworten haben wir eine personalisierte Wachstumsstrategie für {business_name} erstellt.</p>
                
                <div class="section">
                    <h3>{business_type['icon']} Ihr Business-Typ: {business_type['type']}</h3>
                    <p>{business_type['description']}</p>
                </div>
                
                <div class="section recommendations">
                    <h3>🎯 Ihre Top-Empfehlungen für mehr Kunden:</h3>
                    <ul>
                        {''.join([f'<li>{rec}</li>' for rec in recommendations])}
                    </ul>
                </div>
                
                <div class="section steps">
                    <h3>📋 Ihre nächsten konkreten Schritte:</h3>
                    <ol>
                        {''.join([f'<li>{step}</li>' for step in next_steps])}
                    </ol>
                </div>
                
                <div class="section priority">
                    <h3>⚡ Prioritätslevel: {priority['level']}</h3>
                    <p>{priority['description']}</p>
                    <p><strong>Empfehlung:</strong> {self.get_priority_recommendation(priority['level'])}</p>
                </div>
                
                <div class="cta">
                    <h3>🎁 Kostenlose 15-Minuten Strategieberatung</h3>
                    <p>Möchten Sie diese Empfehlungen gemeinsam durchgehen und einen konkreten Umsetzungsplan entwickeln?</p>
                    <p>Als Berlin Business unterstützen wir Sie gerne mit einer kostenlosen Strategieberatung.</p>
                    <a href="https://calendly.com/berlinbusiness/strategy" class="btn">Kostenlosen Termin buchen</a>
                    <p style="font-size: 0.9em; color: #666; margin-top: 15px;">
                        Oder antworten Sie einfach auf diese Email - wir melden uns innerhalb von 24 Stunden!
                    </p>
                </div>
                
                <div class="section">
                    <h3>📊 Benchmark: Wie Sie im Vergleich stehen</h3>
                    <p>Basierend auf unserer Analyse von über 200 Berlin Businesses in ähnlichen Branchen:</p>
                    <ul>
                        <li>85% der Businesses haben noch Optimierungspotential bei Google My Business</li>
                        <li>Durchschnittlich 40% mehr Kundenanfragen nach professioneller Optimierung</li>
                        <li>ROI von 300-500% bei richtig umgesetzten lokalen Marketing-Maßnahmen</li>
                    </ul>
                </div>
                
                <p>Falls Sie Fragen haben oder direkt loslegen möchten, antworten Sie einfach auf diese Email!</p>
                
                <p>Viel Erfolg für {business_name}!<br>
                Ihr Berlin Business Growth Team</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 0.8em; color: #666;">
                    Diese Analyse wurde erstellt am {datetime.now().strftime('%d.%m.%Y um %H:%M')} Uhr.<br>
                    Berlin Business Growth • Wir helfen lokalen Businesses beim digitalen Wachstum.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Also create plain text version
        text_content = f"""
        Hallo {first_name},
        
        vielen Dank für Ihre Teilnahme an unserem Berlin Business Growth Assessment!
        
        IHR BUSINESS-TYP: {business_type['type']}
        {business_type['description']}
        
        IHRE TOP-EMPFEHLUNGEN:
        {chr(10).join([f'• {rec}' for rec in recommendations])}
        
        NÄCHSTE SCHRITTE:
        {chr(10).join([f'{i+1}. {step}' for i, step in enumerate(next_steps)])}
        
        PRIORITÄTSLEVEL: {priority['level']}
        {priority['description']}
        
        Möchten Sie eine kostenlose 15-Minuten Strategieberatung?
        Antworten Sie einfach auf diese Email!
        
        Viel Erfolg für {business_name}!
        Ihr Berlin Business Growth Team
        """
        
        return {
            'html': html_content,
            'text': text_content,
            'subject': f"🚀 Ihre persönlichen Wachstumsempfehlungen für {business_name}",
            'priority': priority['level'],
            'business_type': business_type['type']
        }
    
    def get_priority_recommendation(self, priority_level):
        """Get recommendation based on priority level"""
        
        if priority_level == 'HIGH':
            return "Starten Sie in den nächsten 7 Tagen mit Schritt 1. Schnelles Handeln kann Ihren Umsatz deutlich steigern."
        elif priority_level == 'MEDIUM':
            return "Planen Sie die Umsetzung in den nächsten 2-4 Wochen. Solide Basis für nachhaltiges Wachstum."
        else:
            return "Implementieren Sie die Maßnahmen schrittweise über die nächsten 2 Monate für optimale Ergebnisse."
    
    def send_assessment_email(self, recipient_email, assessment_data):
        """Send personalized assessment results via email"""
        
        if not self.email_user or not self.email_password:
            print("Error: Gmail credentials not set. Please set GMAIL_USER and GMAIL_APP_PASSWORD environment variables.")
            return False
        
        try:
            # Generate email content
            email_content = self.create_email_content(assessment_data)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_user
            msg['To'] = recipient_email
            msg['Subject'] = email_content['subject']
            
            # Attach both text and HTML versions
            text_part = MIMEText(email_content['text'], 'plain', 'utf-8')
            html_part = MIMEText(email_content['html'], 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            print(f"Assessment results sent successfully to {recipient_email}")
            
            # Log the lead for follow-up
            self.log_lead(assessment_data, email_content)
            
            return True
            
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
    
    def log_lead(self, assessment_data, email_content):
        """Log lead information for follow-up"""
        
        lead_data = {
            'timestamp': datetime.now().isoformat(),
            'first_name': assessment_data.get('firstName'),
            'last_name': assessment_data.get('lastName'),
            'email': assessment_data.get('email'),
            'business_name': assessment_data.get('businessName'),
            'whatsapp': assessment_data.get('whatsapp'),
            'priority_level': email_content['priority'],
            'business_type': email_content['business_type'],
            'assessment_responses': assessment_data
        }
        
        # Save to JSON file (in production, this would go to a database)
        leads_file = 'assessment_leads.json'
        leads = []
        
        if os.path.exists(leads_file):
            with open(leads_file, 'r', encoding='utf-8') as f:
                leads = json.load(f)
        
        leads.append(lead_data)
        
        with open(leads_file, 'w', encoding='utf-8') as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
        
        print(f"Lead logged: {assessment_data.get('businessName')} - Priority: {email_content['priority']}")

# Example usage and test
if __name__ == "__main__":
    # Sample assessment data for testing
    sample_data = {
        'firstName': 'Maria',
        'lastName': 'Schmidt',
        'email': 'maria@cafe-beispiel.de',
        'businessName': 'Café Beispiel',
        'whatsapp': '+49 30 12345678',
        'customer_acquisition': 'foot_traffic',
        'previous_attempts': 'nothing_too_busy',
        'tech_comfort': 'not_comfortable',
        'decision_style': 'discuss_with_others',
        'biggest_challenge': 'not_enough_customers'
    }
    
    emailer = AssessmentEmailer()
    
    # Generate and display email content (for testing without actually sending)
    email_content = emailer.create_email_content(sample_data)
    print("Subject:", email_content['subject'])
    print("Priority:", email_content['priority'])
    print("Business Type:", email_content['business_type'])
    
    # To actually send emails, set these environment variables:
    # export GMAIL_USER="your-gmail@gmail.com"
    # export GMAIL_APP_PASSWORD="your-16-char-app-password"
    
    # Then uncomment this line:
    # emailer.send_assessment_email(sample_data['email'], sample_data)