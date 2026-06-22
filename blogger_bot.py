import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Secrets (গিটহাব সিক্রেট থেকে আসবে)
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
    
    # সকল বাটন ও হোম লিংকসহ নেভিগেশন বার
    navigation_html = f"""
    <div style="text-align: center; margin: 50px 0; padding: 30px; border-top: 2px solid #eee; border-bottom: 2px solid #eee; background-color: #f9f9f9;">
        <h4 style="margin-bottom: 20px;">Explore More Categories:</h4>
        <div style="margin-bottom: 20px;">
            <a href="/search/label/Politics">Politics</a> | <a href="/search/label/News">News</a> | 
            <a href="/search/label/Opinion">Opinion</a> | <a href="/search/label/Analysis">Analysis</a> | 
            <a href="/search/label/Interviews">Interviews</a>
        </div>
        <a href="/" style="padding: 12px 30px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">Back to Home</a>
    </div>
    """

    # শক্তিশালী প্রম্পট: ট্রেন্ডিং টপিক ও এসইও অপ্টিমাইজড
    prompt = f"""
    You are an expert SEO Content Writer for a viral blog. Your category is: {category}.
    
    MANDATORY TASKS:
    1. TRENDING TOPIC: Research and write about a currently trending, viral topic specifically related to {category}. Do not write generic articles.
    2. TITLE: Start with 'TITLE: [A Viral, Click-Worthy Title]'.
    3. META: Start with 'META: [Write a 150-character SEO meta-description]'.
    4. IMAGE: Add <img src="https://picsum.photos/800/400?random={os.urandom(1).hex()}" alt="{category}" style="width:100%; border-radius:10px;"> at the top.
    5. STRUCTURE: Short paragraphs (2-3 sentences max) for AdSense. Use H1, H2, H3 tags.
    6. SEO: Bold keywords. 
    7. FAQ: 3 unique questions and answers at the end.
    
    Write a 900+ word professional post.
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        full_response = response.json()['candidates'][0]['content']['parts'][0]['text']
        
        if "TITLE:" in full_response and "META:" in full_response:
            meta = full_response.split("META:", 1)[1].split("\n", 1)[0].strip()
            title = full_response.split("TITLE:", 1)[1].split("\n", 1)[0].strip()
            
            if title in previous_titles:
                return None, None
            
            content = full_response.split(title, 1)[1].replace("META:", "").replace(meta, "").replace("TITLE:", "").strip()
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
    
