import os
import smtplib
import json
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# জেমিনি কনফিগারেশন
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_viral_content(category):
    try:
        # gemini-pro মডেল ব্যবহার করা হচ্ছে যা সবসময় কাজ করে
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"Write a viral blog post for category '{category}'. Output ONLY in JSON format with 'title' and 'body' keys. Include HTML tags in body."
        
        response = model.generate_content(prompt)
        text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text)
        return data.get("title"), data.get("body")
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def main():
    # ক্যাটাগরি এবং লুপ স্টেট
    cat = ["Politics", "News", "Opinion", "Analysis", "Interviews"]
    if os.path.exists("loop_state.txt"):
        with open("loop_state.txt", "r") as f: idx = int(f.read().strip())
    else: idx = 0
    idx = idx % len(cat)
    
    title, body = generate_viral_content(cat[idx])
    
    if title and body:
        msg = MIMEMultipart()
        msg['Subject'] = f"{title} [{cat[idx]}]"
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(os.environ.get("SENDER_EMAIL"), os.environ.get("SENDER_PASSWORD"))
        server.sendmail(os.environ.get("SENDER_EMAIL"), os.environ.get("BLOGGER_EMAIL"), msg.as_string())
        server.quit()
        
        with open("loop_state.txt", "w") as f: f.write(str(idx + 1))
        print("Success")
    else:
        raise Exception("Generation failed")

if __name__ == "__main__":
    main()
    
