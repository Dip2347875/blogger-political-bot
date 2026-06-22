import os
import smtplib
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Secrets (আপনার গিটহাব সেটিংস থেকে আসবে)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
BLOGGER_EMAIL = "dipg74666.01924@blogger.com" # আপনার ইমেইল টু ব্লগার আইডি

CATEGORIES = ["Politics", "News", "Opinion", "Analysis", "Interviews"]
INDEX_FILE = "loop_state.txt"

def generate_blog_content(category):
    # এসইও এবং মনিটাইজেশন ফ্রেন্ডলি কন্টেন্ট জেনারেশন
    prompt = f"""
    Write a 800-word SEO-optimized viral political article in English for the category: [{category}].
    Requirements:
    1. SUBJECT: [Category] Catchy and viral headline.
    2. Add an image from Unsplash with this HTML: <img src="https://source.unsplash.com/800x400/?{category.lower()},politics" alt="Political News">
    3. Use professional H2 and H3 tags for subheadings.
    4. Include bold keywords, bullet points for readability.
    5. Add a 3-item FAQ section.
    6. Include this disclaimer at the end: <p><b>Disclaimer:</b> This article is generated for informational purposes based on current trending data.</p>
    If the article is incomplete or error-prone, output 'INCOMPLETE'.
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        content = response.json()['candidates'][0]['content']['parts'][0]['text']
        
        if len(content) < 600 or "INCOMPLETE" in content.upper():
            return None, None
        
        subject = content.split("SUBJECT:")[1].split("\n")[0].strip() if "SUBJECT:" in content else f"Update: {category}"
        return subject, content
    except:
        return None, None

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = BLOGGER_EMAIL
    msg.attach(MIMEText(body, 'html'))
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, BLOGGER_EMAIL, msg.as_string())

if __name__ == "__main__":
    # লুপ ম্যানেজমেন্ট
    idx = 0
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r") as f: idx = int(f.read().strip())
    
    category = CATEGORIES[idx]
    subject, content = generate_blog_content(category)
    
    if content:
        send_email(subject, content)
        # লুপ আপডেট
        with open(INDEX_FILE, "w") as f: f.write(str((idx + 1) % len(CATEGORIES)))
        print(f"Success: {category} posted.")
    else:
        print("Skipped: Quality check failed.")
    
