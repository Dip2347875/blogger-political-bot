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

def generate_blog_content(category):
    navigation_html = f"""
    <div style="text-align: center; margin: 40px 0; padding: 20px; border-top: 2px solid #eee;">
        <h4 style="margin-bottom: 15px;">Explore Categories:</h4>
        <a href="/search/label/Politics" style="margin: 5px; padding: 8px 15px; background: #f1f1f1; text-decoration: none;">Politics</a>
        <a href="/search/label/News" style="margin: 5px; padding: 8px 15px; background: #f1f1f1; text-decoration: none;">News</a>
        <a href="/search/label/Opinion" style="margin: 5px; padding: 8px 15px; background: #f1f1f1; text-decoration: none;">Opinion</a>
        <a href="/search/label/Analysis" style="margin: 5px; padding: 8px 15px; background: #f1f1f1; text-decoration: none;">Analysis</a>
        <a href="/search/label/Interviews" style="margin: 5px; padding: 8px 15px; background: #f1f1f1; text-decoration: none;">Interviews</a>
        <br><br>
        <a href="/" style="padding: 10px 20px; background: #333; color: white; text-decoration: none;">Back to Home</a>
    </div>
    """

    prompt = f"""
    Write a 800-word professional SEO-optimized blog post for the category: {category}.
    Requirements:
    1. TRENDING: Write about a current trending topic in {category}.
    2. TITLE: Start with 'TITLE: [Viral Title]'. 
    3. CONTENT: Start the article body AFTER the Title. Do not include 'TITLE:' in the body.
    4. IMAGE: Add <img src="https://picsum.photos/800/400?random=1" alt="{category}" style="width:100%;"> at the very top.
    5. STRUCTURE: Use H1, H2, H3 tags. Bold keywords and use bullet points.
    6. FAQ: Include a 3-question FAQ section.
    7. NAVIGATION: Include this at the end: {navigation_html}
    8. LENGTH: Ensure it is at least 700 words. If not, stop.
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        full_response = response.json()['candidates'][0]['content']['parts'][0]['text']
        
        # টাইটেল আলাদা করা
        if "TITLE:" in full_response:
            title = full_response.split("TITLE:")[1].split("\n")[0].strip()
            content = full_response.split(title)[1].replace("TITLE:", "").strip()
        else:
            title = f"Latest Update on {category}"
            content = full_response

        if len(content.split()) < 400: # শব্দ সংখ্যা চেক
            return None, None
            
        return title, content
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
            
        with open(INDEX_FILE, "w") as f: f.write(str((idx + 1) % len(CATEGORIES)))
        print(f"Success: Posted '{title}'")
    
