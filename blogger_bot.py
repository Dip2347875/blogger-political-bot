import os
import smtplib
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# জেমিনি এপিআই কি এবং এপিআই ইউআরএল
API_KEY = os.environ.get("GEMINI_API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

def generate_viral_content(category):
    prompt = f"""
    Write a premium, viral, and extensive blog post for the category: "{category}".
    Output MUST be in pure JSON format with two keys: "title" and "body".
    Rules:
    1. "title": Catchy, viral title.
    2. "body": Full HTML content with meta description, featured image, H2/H3 tags, short paragraphs, and strong conclusion.
    3. Respond ONLY with valid JSON. Do not use markdown code blocks.
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        text = data['candidates'][0]['content']['parts'][0]['text'].strip()
        # JSON ক্লিন করা
        text = text.replace('```json', '').replace('```', '')
        return json.loads(text)
    else:
        print(f"API Error: {response.text}")
        return None

def send_email(title, body, category):
    try:
        msg = MIMEMultipart()
        msg['From'] = os.environ.get("SENDER_EMAIL")
        msg['To'] = os.environ.get("BLOGGER_EMAIL")
        msg['Subject'] = f"{title} [{category}]"
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(os.environ.get("SENDER_EMAIL"), os.environ.get("SENDER_PASSWORD"))
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False

def main():
    categories = ["Politics", "News", "Opinion", "Analysis", "Interviews"]
    state_file = "loop_state.txt"
    idx = int(open(state_file, "r").read()) if os.path.exists(state_file) else 0
    idx = idx % len(categories)
    
    content = generate_viral_content(categories[idx])
    if content and send_email(content['title'], content['body'], categories[idx]):
        with open(state_file, "w") as f: f.write(str(idx + 1))
        print("Success!")

if __name__ == "__main__":
    main()
    
