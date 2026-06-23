import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import google.generativeai as genai

# গিটহাব সিক্রেটস থেকে ডেটা নেওয়া
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
BLOGGER_EMAIL = os.environ.get("BLOGGER_EMAIL") 
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

def generate_viral_content(category):
    try:
        # বর্তমানে কার্যকর এবং স্থিতিশীল মডেল ব্যবহার করা হচ্ছে
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Act as an elite global journalist and SEO specialist. 
        Write a premium, extensive, and trending blog post for the category: "{category}".
        Structure the output strictly in JSON format with two keys: "title" and "body".
        
        Rules:
        1. "title": Catchy, viral, professional title.
        2. "body": Full HTML content with meta description, featured image (using <img> tag), H2/H3 tags, short paragraphs, and <strong> tags.
        3. Respond ONLY with valid JSON. Do not use any markdown code blocks (```json ... ```).
        """
        
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        
        # ক্লিনিং লজিক
        if text_response.startswith("```"):
            text_response = text_response.split("```")[1]
            if text_response.startswith("json"):
                text_response = text_response[4:]
        
        data = json.loads(text_response.strip())
        return data.get("title"), data.get("body")
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None, None

def send_email(title, body, category):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = BLOGGER_EMAIL 
    msg['Subject'] = f"{title} [{category}]"
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587) 
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, BLOGGER_EMAIL, msg.as_string()) 
        server.quit()
        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False

def main():
    categories = ["Politics", "News", "Opinion", "Analysis", "Interviews"]
    state_file = "loop_state.txt"
    
    current_index = 0
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            try: current_index = int(f.read().strip())
            except: current_index = 0
            
    if current_index >= len(categories): current_index = 0
    
    category = categories[current_index]
    title, body = generate_viral_content(category)
    
    if title and body:
        if send_email(title, body, category):
            with open(state_file, "w") as f:
                f.write(str(current_index + 1))
            print("Successfully Posted!")
    else:
        raise Exception("Content generation failed.")

if __name__ == "__main__":
    main()
        
