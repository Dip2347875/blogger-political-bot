import os
import smtplib
import json
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# কনফিগারেশন
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_viral_content(category):
    # মডেলটিকে একটু সরল করে দেওয়া হয়েছে যাতে এরর কম হয়
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Act as a professional journalist and SEO expert. Write a premium blog post for the category: "{category}".
    Output MUST be in pure JSON format with two keys: "title" and "body".
    
    In "title": A catchy, viral title.
    In "body": HTML content containing:
    1. A short meta description and keywords at the top.
    2. An <img> tag at the top with src="https://images.unsplash.com/photo-1503694978374-8a2fa686963a?auto=format&fit=crop&w=800&q=80".
    3. H2 and H3 tags for headings.
    4. Short, punchy paragraphs (max 3 sentences per <p> tag).
    5. Bold key insights using <strong> tags.
    6. A strong conclusion and call-to-action.
    
    Respond with raw JSON only. Do not add any extra text.
    """
    
    response = model.generate_content(prompt)
    # JSON ক্লিন করা
    text = response.text.replace('```json', '').replace('```', '').strip()
    data = json.loads(text)
    return data.get("title"), data.get("body")

def main():
    cat = ["Politics", "News", "Opinion", "Analysis", "Interviews"]
    state_file = "loop_state.txt"
    idx = int(open(state_file, "r").read()) if os.path.exists(state_file) else 0
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
        
        with open(state_file, "w") as f: f.write(str(idx + 1))
        print(f"Success: {cat[idx]}")

if __name__ == "__main__":
    main()
    
