import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import google.generativeai as genai

# গিটহাব সিক্রেটস (GitHub Secrets) থেকে ডেটা লোড করা হচ্ছে
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
BLOGGER_EMAIL = os.environ.get("BLOGGER_EMAIL") 
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# জেমিনি এপিআই কনফিগারেশন
genai.configure(api_key=GEMINI_API_KEY)

def generate_viral_content(category):
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # জেমিনিকে ডিজাইন, সম্পূর্ণ লেখা, এসইও এবং অ্যাডসেন্স অপ্টিমাইজেশনের কড়া নির্দেশনা
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
           - Keep the core body text in standard size, but split into short, highly readable paragraphs (maximum 2-3 sentences per <p> tag). This multi-paragraph layout looks clean and allows Google Auto Ads to embed high-paying ads smoothly.
        4. **Styling Elements**: 
           - Bold critical insights and powerful phrases using the <strong> tag to make them pop out.
           - Use beautifully formatted unordered lists (<ul> and <li>) for presenting points, statistics, or facts to maximize user dwell time.
        5. **Conclusion**: End with a strong professional conclusion and an interactive call-to-action question to increase reader interaction and comments.
        
        The whole article must be in professional English, deeply researched, complete, beautifully structured, and fully finalized. Do not leave any section incomplete, and do not use placeholders. Respond ONLY with the valid JSON.
        """
        
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        
        # জেমিনির JSON রেসপন্স ক্লিন করার লজিক
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        elif text_response.startswith("```"):
            text_response = text_response[3:]
            
        if text_response.endswith("```"):
            text_response = text_response[:-3]
            
        data = json.loads(text_response.strip())
        return data.get("title"), data.get("body")
    except Exception as e:
        print(f"Error generating content with Gemini: {e}")
        return None, None

def send_email(subject_title, body_content, category):
    # সিক্রেটস চেক করা
    if not SENDER_EMAIL or not SENDER_PASSWORD or not BLOGGER_EMAIL:
        print("Error: Missing email configuration in GitHub Secrets!")
        return False

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = BLOGGER_EMAIL 
    
    # সাবজেক্ট ফরম্যাট: টাইটেল এবং শেষে [Category] 
    # এটি ব্লগারকে নির্দেশ দেয় পোস্টটি হোম পেজ এবং নির্দিষ্ট ক্যাটাগরি বাটনে রাখতে।
    msg['Subject'] = f"{subject_title} [{category}]"

    # HTML বডি সেট করা হচ্ছে যাতে ডিজাইন, ইমেজ ও এসইও কাজ করে
    msg.attach(MIMEText(body_content, 'html'))

    try:
        # জিমেইলের মাধ্যমে মেইল পাঠানোর কনফিগারেশন
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
    # আপনার রিকোয়েস্ট করা ৫টি ক্যাটাগরি
    categories = ["Politics", "News", "Opinion", "Analysis", "Interviews"]
    state_file = "loop_state.txt"

    # লুপ স্টেট রিড করা (পরের বার রান হলে যেন নতুন ক্যাটাগরি পায়)
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

    # কনটেন্ট জেনারেট করা হচ্ছে
    title, body = generate_viral_content(selected_category)
    
    if title and body:
        # জিমেইলের মাধ্যমে ব্লগারে পোস্ট পাঠানো
        if send_email(title, body, selected_category):
            # সফল হলে পরের রান-এর জন্য ইনডেক্স আপডেট করা
            current_index += 1
            with open(state_file, "w") as f:
                f.write(str(current_index))
            print("Action Completed Successfully.")
    else:
        print("Skipping execution as content generation failed.")

if __name__ == "__main__":
    main()
        
