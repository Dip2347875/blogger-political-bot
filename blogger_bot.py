import os
import smtplib
import json
import time
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration from Environment Variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOGGER_EMAIL = "dipg74666.01924@blogger.com"
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD") # Gmail App Password

# File to track published topics to avoid duplication
TRACKING_FILE = "published_topics.json"

CATEGORIES = ["Politics", "News", "Opinion", "Analysis", "Interviews"]

def get_current_loop_index():
    try:
        with open("loop_state.txt", "r") as f:
            return int(f.read().strip())
    except:
        return 0

def save_next_loop_index(current_index):
    next_index = (current_index + 1) % len(CATEGORIES)
    with open("loop_state.txt", "w") as f:
        f.write(str(next_index))

def get_published_topics():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, "r") as f:
            return json.load(f)
    return []

def save_published_topic(topic):
    topics = get_published_topics()
    topics.append(topic)
    if len(topics) > 50:
        topics.pop(0)
    with open(TRACKING_FILE, "w") as f:
        json.dump(topics, f)

def generate_blog_content(category):
    already_published = get_published_topics()
    exclude_prompt = f" Do NOT write about these exact recent topics: {', '.join(already_published)}" if already_published else ""

    url = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=](https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=){GEMINI_API_KEY}"
    
    prompt = f"""
    Act as an autonomous AI Political Journalist. Scan the current internet environment for a real-time viral/trending political news story today (Year 2026). 
    Generate a highly engaging, YouTube-style viral political content in English for the category: [{category}].{exclude_prompt}
    
    CRITICAL ANTI-BOREDOM RULE: Ensure the chosen topic is completely unique, fresh, and not similar to typical mainstream repetitive structures.
    
    You MUST apply the following 30-point blueprint strictly using HTML styling since it will be sent via email:
    1. Professional, 100% factual, neutral, and verified information.
    2. Detailed breakdown covering background layers.
    3. The response must output the Subject line at the very top formatted exactly as: SUBJECT: [{category}] Catchy & Dramatic Headline.
    4. Hook intro within 3 seconds.
    5. Open Loop Technique setup.
    6. Cinematic Political Storytelling style.
    7. Pattern Interrupt with statistical data, shocking turning points, or emojis.
    8. Direct Address ("You" Element).
    9. Emotional Trigger points.
    10. Focus SEO Keyword naturally placed 4-5 times in the text.
    11. Sub-Heading Optimization (H2/H3) based on Google search behavior.
    12. Force Sub-headings to look bold and large using <h2 style="font-size:24px;"> or <h3 style="font-size:20px;">.
    13. Force body text to <p style="font-size:14px; font-family:Arial;">. Keep paragraphs 2-3 sentences max.
    14. Apply the HTML underline tag <u>...</u> to highly critical breaking statements or core turning points so they catch eyes on scroll.
    15. Bold key names, parties, or dates using <b>...</b>.
    16. Address ongoing public confusion/media spin.
    17. Provide objective, unbiased, intellectual analysis.
    18. Explicitly list Pros and Cons of the political move, underlining key takeaways.
    19. Include Cliffhangers/Suspense lines at paragraph transitions.
    20. Use plain, easy-to-understand high-retention English.
    21. Textually describe a perfect thumbnail/visual idea inside a box wrapper, named with a keyword-rich filename like 'election-clash.jpg' for SEO Alt text reference.
    22. Present timelines using clean <ul>/<li> bullet points.
    23. Use an easy Analogy/Metaphor (e.g., comparing it to chess).
    24. Textually cite top-tier news agencies (e.g., "According to official reports...") without inserting URLs.
    25. Provide your final logical independent summary.
    26. Offer a data-backed predictive future outcome for upcoming elections/landscape.
    27. Ensure the first 150 words serve as a compelling Search Meta Description.
    28. Conclude with a 3-4 item FAQ section (Commonly searched questions and brief answers) for SEO FAQ schema tracking.
    29. End with a Public Opinion Poll Context asking readers to type "Yes" or "No" in the comments.
    30. Ensure maximum user dwell time optimization with dense pacing.
    
    Do not output any introductory or conclusion conversational filler text outside the post. Start directly with the SUBJECT line and then the HTML body content.
    """
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    generated_text = result['candidates'][0]['content']['parts'][0]['text']
    return generated_text

def send_email_to_blogger(subject, html_body):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = BLOGGER_EMAIL
    
    part = MIMEText(html_body, 'html')
    msg.attach(part)
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, BLOGGER_EMAIL, msg.as_string())
    print(f"Successfully published post: {subject}")

def main():
    current_index = get_current_loop_index()
    category = CATEGORIES[current_index]
    
    print(f"Processing infinite loop slot for category: {category}")
    raw_content = generate_blog_content(category)
    
    if "SUBJECT:" in raw_content:
        parts = raw_content.split("SUBJECT:", 1)[1].split("\n", 1)
        subject = parts[0].strip()
        html_body = parts[1].strip()
    else:
        subject = f"[{category}] Automated Political Update - {int(time.time())}"
        html_body = raw_content

    # ফিক্সড: স্ট্রিং রিপ্লেস করার সময় ব্যাকটিক্স কোড ব্লক সঠিকভাবে রিমুভ করার ব্যবস্থা করা হয়েছে
    if html_body.startswith("```html"):
        html_body = html_body.replace("```html", "", 1).rstrip("```").strip()
    elif html_body.startswith("```"):
        html_body = html_body.replace("
```", "", 1).rstrip("```").strip()

    send_email_to_blogger(subject, html_body)
    
    save_published_topic(subject)
    save_next_loop_index(current_index)

if __name__ == "__main__":
    main()
