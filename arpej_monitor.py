import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import json
import time
import os

# Configuration
ARPEJ_URL = "https://www.arpej.fr/fr/nos-residences/"
# Your filters based on the URL
FILTERS = {
    "related_city": "54157,52682,52740,52722,52782,52768,54167",  # La Garenne-Colombes, Gennevilliers, Courbevoie, Colombes, Nanterre, Neuilly-sur-Seine, Suresnes
    "iam": "etudiants"  # Students filter
}

# Email Configuration
SENDER_EMAIL = "your-email@gmail.com"  # Your Gmail address
SENDER_PASSWORD = "your-app-password"  # Gmail app password (NOT your regular password)
RECIPIENT_EMAIL = "your-email@gmail.com"  # Where to send notifications
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# File to store previously found residences (to avoid duplicate notifications)
STATE_FILE = "arpej_state.json"

def load_state():
    """Load previously found residences"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"found_residences": []}
    return {"found_residences": []}

def save_state(state):
    """Save found residences"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def fetch_residences():
    """Fetch available residences from Arpej"""
    try:
        # Build the URL with parameters
        params = "&".join([f"{k}={v}" for k, v in FILTERS.items()])
        url = f"{ARPEJ_URL}?{params}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract residences - look for residence cards/listings
        # This selector may need adjustment based on the actual HTML structure
        residences = []
        
        # Look for residence items (you may need to inspect the website to find the correct selector)
        residence_items = soup.find_all('div', class_=lambda x: x and 'residence' in x.lower())
        
        if not residence_items:
            # Alternative: look for links with specific patterns
            residence_items = soup.find_all('a', class_=lambda x: x and ('card' in x.lower() or 'item' in x.lower()))
        
        for item in residence_items:
            name = item.get_text(strip=True)
            link = item.get('href', '')
            
            if name and link:
                residences.append({
                    'name': name,
                    'url': link if link.startswith('http') else f"https://www.arpej.fr{link}"
                })
        
        return residences
    
    except Exception as e:
        print(f"Error fetching residences: {e}")
        return []

def send_email(subject, body, residences):
    """Send email notification"""
    try:
        message = MIMEText(body)
        message['Subject'] = subject
        message['From'] = SENDER_EMAIL
        message['To'] = RECIPIENT_EMAIL
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message.as_string())
        
        print("✓ Email sent successfully!")
        return True
    
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        return False

def check_for_new_residences():
    """Check if new residences are available"""
    state = load_state()
    current_residences = fetch_residences()
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking Arpej...")
    print(f"Found {len(current_residences)} total residence(s)")
    
    # Find new residences
    new_residences = []
    for residence in current_residences:
        if residence['url'] not in state['found_residences']:
            new_residences.append(residence)
            state['found_residences'].append(residence['url'])
    
    if new_residences:
        print(f"🎉 Found {len(new_residences)} NEW residence(s)!")
        
        # Prepare email
        email_body = f"Great news! {len(new_residences)} new residence(s) available on Arpej!\n\n"
        email_body += "Details:\n" + "-" * 50 + "\n"
        
        for i, res in enumerate(new_residences, 1):
            email_body += f"\n{i}. {res['name']}\n   Link: {res['url']}\n"
        
        email_body += "\n" + "-" * 50 + "\n"
        email_body += f"Check the website immediately: {ARPEJ_URL}?{FILTERS['related_city']}&iam={FILTERS['iam']}\n"
        email_body += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        send_email(
            f"🎉 Arpej Alert: {len(new_residences)} New Residence(s) Available!",
            email_body,
            new_residences
        )
    else:
        print("No new residences at this time.")
    
    # Save updated state
    save_state(state)

if __name__ == "__main__":
    print("=" * 60)
    print("ARPEJ RESIDENCE AVAILABILITY MONITOR")
    print("=" * 60)
    
    try:
        # Test the fetching
        print("\n[*] Testing website connection...")
        residences = fetch_residences()
        print(f"[✓] Successfully connected. Found {len(residences)} residence(s)")
        
        # Do initial check
        print("\n[*] Performing check for new residences...")
        check_for_new_residences()
        print("[✓] Check completed successfully!")
        
    except Exception as e:
        print(f"[✗] Error occurred: {e}")
        import traceback
        traceback.print_exc()
