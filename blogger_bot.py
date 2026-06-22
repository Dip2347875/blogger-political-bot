import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Secrets
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
BLOGGER_EMAIL = "dipg74666.01924@blogger.com"

CATEGORIES = ["Politics", "News", "Opinion", "Analysis", "Interviews"]
INDEX_FILE = "loop_state.txt"
TITLE_HISTORY_FILE = "titles.txt"

def get_previous_titles():
    if os.path.exists(TITLE_HISTORY_FILE):
        with open(TITLE_HISTORY_FILE, "r") as f:
            return f.read().splitlines()
    return []

def save_title(title):
    with open(TITLE_HISTORY_FILE, "a") as f:
        f.write(title + "\n")

def generate_blog_content(category):
    previous_titles = get_previous_titles()
    
    navigation_html = f"""
    <div style="text-align: center; margin: 50px 0; padding: 30px; border-top: 2px solid #eee; border-bottom: 2px solid #eee;">
        <h4 style="margin-bottom: 20px;">আরও পড়ুন:</h4>
        <div style="margin-bottom: 20px;">
            <a href="/search/label/Politics">Politics</a> | <a href="/search/label/News">News</a> | 
            <a href="/search/label/Opinion">Opinion</a> | <a href="/search/label/Analysis">Analysis</a> | 
            <a href="/search/label/Interviews">Interviews</a>
        </div>
        <a href="/" style="padding: 12px 30px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">Home</a>
    </div>
    """

    prompt = f"""
    Write a 900+ word professional, SEO-optimized blog post for category: {category}.
    Requirements:
    1. AVOID DUPLICATES: Do not write about the same topic that has been written before. Use a fresh, unique angle.
    2. META DESCRIPTION: Provide a 150-character SEO meta-description at the very beginning starting with 'META: '.
    3. TITLE: Start with 'TITLE: [Unique Viral Title]'.
    4. STRUCTURE: Use short paragraphs (3-4 sentences) for high AdSense readability.
    5. IMAGE: Add <img src="https://picsum.photos/800/400?random={os.urandom(1).hex()}" alt="{category}" style="width:100%; border-radius:10px;">.
    6. SEO: Use H1, H2, H3 tags. Bold main keywords.
    7. FAQ: 3 unique questions and answers at the end.
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        full_response = response.json()['candidates'][0]['content']['parts'][0]['text']
        
        # ডাটা প্রসেসিং
        if "TITLE:" in full_response and "META:" in full_response:
            meta = full_response.split("META:", 1)[1].split("\n", 1)[0].strip()
            title = full_response.split("TITLE:", 1)[1].split("\n", 1)[0].strip()
            
            if title in previous_titles:
                return None, None
            
            content = full_response.split(title, 1)[1].replace("META:", "").replace(meta, "").replace("TITLE:", "").strip()
            
            # মেটা ডেসক্রিপশন ব্লগের শুরুর জন্য HTML এ যোগ করা (SEO Meta)
            full_html = f'<p style="display:none;">{meta}</p>' + content + navigation_html
            return title, full_html
        return None, None
    except:
        return None, None

if __name__ == "__main__":
    idx = 0
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r") as f: 
            val = f.read().strip()
            if val.isdigit(): idx = int(val)
    
    category = CATEGORIES[idx]
    title, content = generate_blog_content(category)
    
    if content:
        msg = MIMEMultipart()
        msg['Subject'] = title
        msg['From'] = SENDER_EMAIL
        msg['To'] = BLOGGER_EMAIL
        msg.attach(MIMEText(content, 'html'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, BLOGGER_EMAIL, msg.as_string())
            
        save_title(title)
        with open(INDEX_FILE, "w") as f: f.write(str((idx + 1) % len(CATEGORIES)))
        print(f"Success: Posted '{title}'")
    
