import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from bs4 import BeautifulSoup

# Fetches credentials securely from GitHub Secrets
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
APP_PASSWORD = os.environ.get("APP_PASSWORD")
RECEIVER_EMAIL = SENDER_EMAIL  # Automatically sends the alert to your own inbox

PORTALS = {
    "NCDMB NOGIC JQS Portal": "https://nogicjqs.gov.ng",
    "PTDF Scholarship Portal": "https://ptdf.gov.ng",
    "NLNG Careers Page": "https://nigerialng.com",
    "Air Peace Careers Page": "https://flyairpeace.com",
    "Nigeria College of Aviation Technology": "https://ncat.gov.ng"
}

KEYWORDS = ["training", "scholarship", "cadet", "pilot", "recruitment", "advertisement", "openings"]

def send_email_alert(portal_name, portal_url, found_keywords):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"🚨 AVIATION ALERT: Opportunity Detected on {portal_name}"

    body = f"Hello,\n\nAn active cycle keyword was found!\n\n📌 Portal: {portal_name}\n🔗 Link: {portal_url}\n🔍 Keywords: {', '.join(found_keywords)}\n\nPlease check immediately."
    msg.attach(MIMEText(body, 'plain'))

    try:
        # FIXED: Changed from '://gmail.com' to 'smtp.gmail.com'
        server = smtplib.SMTP('smtp.gmail.com', 587) 
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print(f"📧 Notification sent for {portal_name}!")
    except Exception as e:
        print(f"❌ Email failed: {e}")

def scan_portals():
    print("--- Starting Portal Scan ---")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    for name, url in PORTALS.items():
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text().lower()
                found_keywords = [word for word in KEYWORDS if word in page_text]
                
                if found_keywords:
                    print(f"⚠️ Match found on {name}!")
                    send_email_alert(name, url, found_keywords)
                else:
                    print(f"✅ {name}: Clear.")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Connection failed.")

if __name__ == "__main__":
    scan_portals()
