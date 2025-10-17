#!/usr/bin/env python3
"""
VTU Internship Watcher

This script monitors the VTU Internyet website for new internship postings
and sends email notifications when new opportunities are found.
"""

import os
import json
import time
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Set
from pathlib import Path
from string import Template

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('internship_watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InternshipWatcher:
    def __init__(self):
        self.api_base_url = "https://vtuapi.internyet.in/api/v1/internships"
        self.website_base_url = "https://vtu.internyet.in/internships"
        self.data_file = "seen_internships.json"
        self.seen_internships: Set[str] = self.load_seen_internships()
        
        # Email configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')  # Gmail App Password
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            raise ValueError("Missing email configuration. Please set SENDER_EMAIL, SENDER_PASSWORD, and RECIPIENT_EMAIL environment variables.")
    
    def load_seen_internships(self) -> Set[str]:
        """Load previously seen internship IDs from file."""
        try:
            if Path(self.data_file).exists():
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('seen_internships', []))
        except Exception as e:
            logger.error(f"Error loading seen internships: {e}")
        return set()
    
    def save_seen_internships(self):
        """Save seen internship IDs to file."""
        try:
            data = {
                'seen_internships': list(self.seen_internships),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving seen internships: {e}")
    
    def fetch_internships_from_api(self, page: int = 1) -> Dict:
        """Fetch internships from the VTU API."""
        try:
            url = f"{self.api_base_url}?page={page}"
            logger.info(f"Fetching internships from API: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('success'):
                logger.error(f"API returned error: {data.get('message', 'Unknown error')}")
                return {}
            
            return data.get('data', {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from API: {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing API response: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error fetching internships: {e}")
            return {}
    
    def get_all_internships(self) -> List[Dict]:
        """Fetch all internships from all pages."""
        all_internships = []
        page = 1
        
        while True:
            try:
                api_data = self.fetch_internships_from_api(page)
                
                if not api_data or 'data' not in api_data:
                    logger.info(f"No more data found at page {page}")
                    break
                
                internships = api_data['data']
                if not internships:
                    logger.info(f"No internships found on page {page}")
                    break
                
                # Process each internship
                for internship_data in internships:
                    processed_internship = self.process_internship_data(internship_data)
                    if processed_internship:
                        all_internships.append(processed_internship)
                
                logger.info(f"Fetched {len(internships)} internships from page {page}")
                
                # Check if there are more pages
                if page >= api_data.get('last_page', 1):
                    logger.info(f"Reached last page: {page}")
                    break
                
                page += 1
                
                # Add a small delay to be respectful to the API
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing page {page}: {e}")
                break
        
        logger.info(f"Total internships fetched: {len(all_internships)}")
        return all_internships
    
    def process_internship_data(self, data: Dict) -> Dict:
        """Process raw API internship data into our format."""
        try:
            # Extract data from API response
            internship_id = str(data.get('id', ''))
            title = (data.get('title') or '').strip()
            company_dict = data.get('company') or {}
            company_name = (company_dict.get('name') or '').strip()
            city_dict = data.get('city') or {}
            city_name = (city_dict.get('name') or '').strip()
            description = (data.get('description') or '').strip()
            work_mode = (data.get('workMode') or '').strip()
            duration = (data.get('duration') or '').strip()
            deadline = (data.get('deadline') or '').strip()
            internship_type = (data.get('type') or '').strip()
            stipend = data.get('stipend') or data.get('internship_fee')
            job_offer = data.get('is_job_offer', 0)
            job_package = (data.get('job_offer_package') or '').strip()
            
            # Create internship link
            slug = (data.get('slug') or '')
            link = f"{self.website_base_url}/{slug}" if slug else self.website_base_url
            
            # Format stipend/fee information
            stipend_info = ""
            if stipend:
                stipend_info = f"₹{stipend}"
            if internship_type == "Paid" and not stipend_info:
                stipend_info = "Paid"
            elif internship_type == "Free":
                stipend_info = "Free"
            
            # Create processed internship object
            processed = {
                'id': internship_id,
                'title': title,
                'company': company_name,
                'location': city_name,
                'description': description[:500] if description else '',  # Limit description
                'work_mode': work_mode,
                'duration': f"{duration} months" if duration else '',
                'deadline': deadline,
                'type': internship_type,
                'stipend': stipend_info,
                'job_offer': bool(job_offer),
                'job_package': job_package,
                'link': link,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Only return if we have essential data
            if title and company_name:
                return processed
                
        except Exception as e:
            logger.error(f"Error processing internship data: {e}")
        
        return None
    
    def send_email_notification(self, new_internships: List[Dict], to_email: str = None, subject: str = None):
        """Send email notification for new internships.
        If to_email is provided, sends to that address; otherwise uses self.recipient_email.
        """
        try:
            msg = MIMEMultipart()
            target_email = to_email or self.recipient_email
            msg['From'] = self.sender_email
            msg['To'] = target_email
            default_subject = f"🚨 {len(new_internships)} New VTU Internship(s) Found!" if new_internships else "ℹ️ No New VTU Internships Today"
            msg['Subject'] = subject or default_subject
            
            # Create email body
            body = self.create_email_body(new_internships)
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent for {len(new_internships)} new internships")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")

    def get_subscribers(self) -> List[str]:
        """Fetch subscriber emails from a published CSV URL in SUBSCRIBERS_CSV_URL.
        CSV must contain a header with a column named 'email'.
        Returns empty list if URL is not set or on error.
        """
        subscribers = []
        csv_url = os.getenv('SUBSCRIBERS_CSV_URL')
        if not csv_url:
            return subscribers
        try:
            logger.info(f"Fetching subscribers from CSV: {csv_url}")
            resp = requests.get(csv_url, timeout=20)
            resp.raise_for_status()
            lines = resp.text.splitlines()
            if not lines:
                return subscribers
            headers = [h.strip().lower() for h in lines[0].split(',')]
            if 'email' not in headers:
                logger.warning("CSV missing 'email' header")
                return subscribers
            email_idx = headers.index('email')
            for line in lines[1:]:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) <= email_idx:
                    continue
                email = parts[email_idx]
                if email and '@' in email:
                    subscribers.append(email)
        except Exception as e:
            logger.error(f"Error fetching subscribers: {e}")
        return subscribers
    
    def create_email_body(self, internships: List[Dict]) -> str:
        """Create HTML email body for internship notifications."""
        tpl = Template(
            """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }
                .internship { border: 1px solid #ddd; margin: 20px 0; padding: 15px; border-radius: 8px; background-color: #fafafa; }
                .title { color: #2196F3; font-size: 18px; font-weight: bold; margin-bottom: 10px; }
                .company { color: #FF9800; font-weight: bold; font-size: 16px; }
                .location { color: #9E9E9E; }
                .description { margin: 10px 0; }
                .details { display: flex; flex-wrap: wrap; gap: 15px; margin: 10px 0; }
                .detail-item { background-color: #e8f5e8; padding: 5px 10px; border-radius: 4px; font-size: 12px; }
                .link { background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 10px; }
                .footer { margin-top: 30px; padding: 20px; background-color: #f5f5f5; text-align: center; }
                .paid { background-color: #fff3cd; border-left: 4px solid #ffc107; }
                .free { background-color: #d1ecf1; border-left: 4px solid #17a2b8; }
                .job-offer { background-color: #d4edda; border-left: 4px solid #28a745; }
            </style>
        </head>
        <body>
            <div class="header">
                $header_html
            </div>
        """
        )
        if internships:
            header_html = f"<h1>🎉 New VTU Internships Available!</h1><p>Found {len(internships)} new internship(s) that match your criteria</p>"
        else:
            header_html = "<h1>ℹ️ No New VTU Internships Today</h1><p>We didn't find new listings since yesterday. You’ll be notified when new ones appear.</p>"
        html = tpl.substitute(header_html=header_html)
        
        for internship in internships:
            # Determine CSS class based on internship type
            css_class = "internship"
            if internship.get('type') == 'Paid':
                css_class += " paid"
            elif internship.get('type') == 'Free':
                css_class += " free"
            if internship.get('job_offer'):
                css_class += " job-offer"
            
            html += f"""
            <div class="{css_class}">
                <div class="title">{internship.get('title', 'No Title')}</div>
                <div class="company">🏢 {internship.get('company', 'No Company')}</div>
                {f'<div class="location">📍 {internship["location"]}</div>' if internship.get('location') else ''}
                
                <div class="details">
                    {f'<span class="detail-item">💰 {internship["stipend"]}</span>' if internship.get('stipend') else ''}
                    {f'<span class="detail-item">⏱️ {internship["duration"]}</span>' if internship.get('duration') else ''}
                    {f'<span class="detail-item">🏠 {internship["work_mode"]}</span>' if internship.get('work_mode') else ''}
                    {f'<span class="detail-item">📅 Deadline: {internship["deadline"]}</span>' if internship.get('deadline') else ''}
                    {f'<span class="detail-item">💼 Job Offer: {internship["job_package"]}</span>' if internship.get('job_offer') and internship.get('job_package') else ''}
                </div>
                
                {f'<div class="description">{internship["description"]}</div>' if internship.get('description') else ''}
                {f'<a href="{internship["link"]}" class="link" target="_blank">Apply Now 🚀</a>' if internship.get('link') else ''}
                
                <div style="margin-top: 15px; font-size: 11px; color: #666; border-top: 1px solid #ddd; padding-top: 10px;">
                    ID: {internship.get('id', 'Unknown')} | Found at: {internship.get('scraped_at', 'Unknown')}
                </div>
            </div>
            """
        
        html += """
            <div class="footer">
                <p>🤖 This is an automated notification from VTU Internship Watcher</p>
                <p>Visit <a href="https://vtu.internyet.in/internships">VTU Internyet</a> for more details</p>
                <p style="font-size: 12px; color: #666;">
                    💡 Tip: Apply early! Popular internships fill up quickly.
                </p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def check_for_new_internships(self):
        """Main method to check for new internships and send notifications."""
        logger.info("Starting internship check using VTU API...")
        
        try:
            # Fetch current internships from API
            current_internships = self.get_all_internships()
            
            if not current_internships:
                logger.warning("No internships found from API")
                return
            
            logger.info(f"Fetched {len(current_internships)} total internships from API")
            
            # Find new internships
            new_internships = []
            for internship in current_internships:
                if internship['id'] not in self.seen_internships:
                    new_internships.append(internship)
                    self.seen_internships.add(internship['id'])
            
            # Determine recipients (multi-subscriber or fallback)
            subscribers = self.get_subscribers()
            if new_internships:
                logger.info(f"Found {len(new_internships)} new internships")
                if subscribers:
                    sent = 0
                    for email in subscribers:
                        try:
                            self.send_email_notification(new_internships, to_email=email)
                            sent += 1
                        except Exception as e:
                            logger.error(f"Failed to notify {email}: {e}")
                    logger.info(f"Notifications sent to {sent}/{len(subscribers)} subscribers")
                else:
                    self.send_email_notification(new_internships)
                self.save_seen_internships()
            else:
                logger.info("No new internships found — sending daily summary notice")
                if subscribers:
                    sent = 0
                    for email in subscribers:
                        try:
                            self.send_email_notification([], to_email=email, subject="ℹ️ No New VTU Internships Today")
                            sent += 1
                        except Exception as e:
                            logger.error(f"Failed to notify {email}: {e}")
                    logger.info(f"No-new notifications sent to {sent}/{len(subscribers)} subscribers")
                else:
                    self.send_email_notification([], subject="ℹ️ No New VTU Internships Today")
            
        except Exception as e:
            logger.error(f"Error during internship check: {e}")

def main():
    """Main function to run the internship watcher."""
    try:
        watcher = InternshipWatcher()
        watcher.check_for_new_internships()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
