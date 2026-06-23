import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
# লেটেস্ট গুগল জেমিনি লাইব্রেরি
from google import genai
from google.genai import types

# গিটহাব সিক্রেটস থেকে ডেটা লোড করা হচ্ছে
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
BLOGGER_EMAIL = os.environ.get("BLOGGER_EMAIL") 
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# জেমিনি ক্লায়েন্ট ইনিশিয়ালাইজেশন
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_viral_content(category):
    try:
        # জেমিনিকে পিওর JSON আউটপুট দেওয়ার নির্দেশনা
        prompt = f"""
        Act as an elite global journalist, web designer, and premium SEO specialist. 
        Find a highly trending, viral, and high-CPC global news or political topic appropriate for the category: "{category}".
        
        Write an extensive, premium, and 100% complete blog post in English. 
        You must structure the output strictly in JSON format with exactly two keys: "title" and "body".
        
        In the "title" key: Provide a catchy, viral, and professional English title (without any HTML tags).
        
        In the "body" key: Provide the full article using beautiful HTML styling based on these layout rules:
        1. **SEO Meta Data**: Include meta description and keywords tags at the very beginning of the body.
        2. **Featured Image**: Insert this premium, copyright-free Unsplash image tag at the top:
           <img src="https://images.unsplash.com/photo-1503694978374-8a2fa686963a?auto=format&fit=crop&w=800&q=80" alt="{category} global trending news" style="width:100%; max-width:800px; height:auto; margin-bottom:25px; display:block; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        3. **Visual Hierarchy (Typography)**: 
           - Break down the core coverage into 5 to 6 distinct sections using bold and larger <h2> and <h3> tags for subheadings.
           - Keep the core body text in standard size, but split into short, highly readable paragraphs (maximum 2-3 sentences per <p> tag).
        4. **Styling Elements**: 
           - Bold critical insights and powerful phrases using the <strong> tag.
           - Use beautifully formatted unordered lists (<ul> and <li>).
        5. **Conclusion**: End with a strong professional conclusion and an interactive call-to-action question.
        
        Respond ONLY with a valid JSON object containing "title" and "body". Do not wrap it in markdown code blocks.
        """
        
        # লেটেস্ট জেমিনি ২.৫ ফ্ল্যাশ মডেল ব্যবহার করা হচ্ছে
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )
        
        text_response = response.text.strip()
        data = json.loads(text_response)
        return data.get("title"), data.get("body")
    except Exception as e:
        print(f"Error generating content with Gemini: {e}")
        return None, None

def send_email(subject_title, body_content, category):
    if not SENDER_EMAIL or not SENDER_PASSWORD or not BLOGGER_EMAIL:
        print("Error: Missing email configuration in GitHub Secrets!")
        return False

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = BLOGGER_EMAIL 
    msg['Subject'] = f"{subject_title} [{category}]"
    msg.attach(MIMEText(body_content, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587) 
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, BLOGGER_EMAIL, msg.as_string()) 
        server.quit()
        print(f"Successfully published designed post to Home and [{category}]: {subject_title}")
        return True
    except Exception as e:
        print(f"Failed to send email via Gmail: {e}")
        return False

def main():
    categories = ["Politics", "News", "Opinion", "Analysis", "Interviews"]
    state_file = "loop_state.txt"

    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            try:
                current_index = int(f.read().strip())
            except:
                current_index = 0
    else:
        current_index = 0

    if current_index >= len(categories):
        current_index = 0

    selected_category = categories[current_index]
    print(f"Targeting Category: {selected_category}")

    title, body = generate_viral_content(selected_category)
    
    if title and body:
        if send_email(title, body, selected_category):
            current_index += 1
            with open(state_file, "w") as f:
                f.write(str(current_index))
            print("Action Completed Successfully.")
    else:
        raise RuntimeError("Skipping execution as content generation failed. Check Gemini API or Response format.")

if __name__ == "__main__":
    main()
    
