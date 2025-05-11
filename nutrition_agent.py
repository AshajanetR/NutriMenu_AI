import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import schedule
import time
import json
import re

from agno.agent import Agent
from agno.models.groq import Groq

# Import configuration
import config

# Initialize the Groq agent with API key
agent = Agent(model=Groq(id=config.GROQ_MODEL, api_key=config.GROQ_API_KEY), markdown=True)

def generate_diet_plan():
    """Generate a daily diet plan using the Groq model"""
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    # Convert dietary preferences to a string format for the prompt
    preferences = config.DIETARY_PREFERENCES
    allergies_str = ", ".join(preferences["allergies"]) if preferences["allergies"] else "None"
    excluded_foods_str = ", ".join(preferences["excluded_foods"]) if preferences["excluded_foods"] else "None"
    
    prompt = f"""
    Act as a certified nutritionist and diet expert. Create a healthy diet menu for today, {current_date}.
    
    Dietary preferences:
    - Diet type: {preferences['diet_type']}
    - Target daily calories: {preferences['calories_per_day']}
    - Allergies to avoid: {allergies_str}
    - Foods to exclude: {excluded_foods_str}
    - Meal complexity: {preferences['meal_complexity']}
    - Protein focus: {preferences['protein_focus']}
    
    The menu should:
    1. Include tamilnadu stylebreakfast, lunch, dinner, and 2 healthy snacks
    2. Be nutritionally balanced with appropriate macros
    3. Focus on whole foods and be suitable for weight management
    4. Include approximate calorie counts for each meal
    5. Include preparation tips for each meal
    6. Suggest hydration throughout the day
    7. For each meal, provide macro information: protein, carbs, and fiber content in grams
   
    output format:
        1.and it shouldnt contain any comments or markdown language make it more readable and userfriendly and presentable.
        2.make sure no special characters included
        3.no introduction and conclusion needed.
        4. Format the response in a clean, organized way with clear section headers.
        5. For macros, use format like "Protein: 25g | Carbs: 30g | Fiber: 5g" after each meal description.
    """
    
    response = agent.run(prompt)
    return response.content

def process_diet_content(diet_text):
    # Identify meal sections
    sections = {}
    current_section = "General"
    lines = []
    
    # Parse the content into sections
    for line in diet_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Detect main headers (BREAKFAST, LUNCH, etc.)
        header_match = re.match(r'^(BREAKFAST|LUNCH|DINNER|SNACK|MORNING SNACK|EVENING SNACK|HYDRATION|WATER).*$', line.upper())
        if header_match:
            current_section = line
            sections[current_section] = []
        else:
            if current_section in sections:
                sections[current_section].append(line)
            else:
                lines.append(line)
    
    # If no sections were found, return the original text with basic formatting
    if not sections:
        return f"<p>{diet_text.replace(chr(10), '<br>')}</p>"
    
    # Build HTML with sections
    html = ""
    
    # Process each section
    for section, content in sections.items():
        icon = "🍳"  # Default icon
        
        # Choose appropriate icon for section
        if "BREAKFAST" in section.upper():
            icon = "🍳"
        elif "LUNCH" in section.upper():
            icon = "🍛"
        elif "DINNER" in section.upper():
            icon = "🍽️"
        elif "SNACK" in section.upper():
            icon = "🥜"
        elif "HYDRATION" in section.upper() or "WATER" in section.upper():
            icon = "💧"
        
        # Add section header
        html += f"""
        <div class="meal-section">
            <h2><span class="meal-icon">{icon}</span> {section}</h2>
            <div class="meal-content">
        """
        
        # Process content
        for line in content:
            # Try to detect calorie information
            calorie_match = re.search(r'(\d+)\s*(?:kcal|calories|cal)', line, re.IGNORECASE)
            
            # Try to detect macro information (protein, carbs, fiber)
            macro_match = re.search(r'(?:protein|proteins|carbs|carbohydrates|fiber|fibre)[^\d]*(\d+).*g', line, re.IGNORECASE)
            macro_full_match = re.search(r'protein:?\s*(\d+)\s*g.*carbs?:?\s*(\d+)\s*g.*fiber:?\s*(\d+)\s*g', line, re.IGNORECASE)
            
            if macro_full_match:
                protein = macro_full_match.group(1)
                carbs = macro_full_match.group(2)
                fiber = macro_full_match.group(3)
                html += f"""
                <div class="macro-box">
                    <div class="macro-item">
                        <span class="macro-icon">🥩</span>
                        <span class="macro-label">Protein</span>
                        <span class="macro-value">{protein}g</span>
                    </div>
                    <div class="macro-item">
                        <span class="macro-icon">🍚</span>
                        <span class="macro-label">Carbs</span>
                        <span class="macro-value">{carbs}g</span>
                    </div>
                    <div class="macro-item">
                        <span class="macro-icon">🌱</span>
                        <span class="macro-label">Fiber</span>
                        <span class="macro-value">{fiber}g</span>
                    </div>
                </div>
                """
            elif calorie_match:
                calorie_count = calorie_match.group(1)
                html += f'<div class="calorie-info">{calorie_count} calories</div>'
            # Check if line is a preparation tip
            elif "tip" in line.lower() or "prepare" in line.lower() or "cook" in line.lower():
                html += f'<div class="prep-tip"><span class="tip-icon">💡</span> {line}</div>'
            else:
                html += f'<p>{line}</p>'
        
        html += """
            </div>
        </div>
        """
    
    return html

def get_html_template(current_date, diet_plan):
    """Create the HTML email template without f-strings to avoid syntax issues"""
    # Get the nicely formatted content
    diet_content = process_diet_content(diet_plan)
    
    primary_color = config.EMAIL_COLOR_PRIMARY
    secondary_color = config.EMAIL_COLOR_SECONDARY
    diet_type = config.DIETARY_PREFERENCES['diet_type'].title()
    calories = config.DIETARY_PREFERENCES['calories_per_day']
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f9f9f9;
        }}
        .wrapper {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .date {{
            font-size: 16px;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .meal-section {{
            margin-bottom: 30px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 1px 5px rgba(0,0,0,0.05);
            padding: 15px;
            border-left: 4px solid {primary_color};
            transition: transform 0.2s ease;
        }}
        .meal-section:hover {{
            transform: translateY(-3px);
        }}
        h2 {{
            color: {primary_color};
            margin: 0 0 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
            display: flex;
            align-items: center;
        }}
        h3 {{
            color: {secondary_color};
            margin: 15px 0 10px;
        }}
        p {{
            margin-bottom: 12px;
        }}
        .meal-icon {{
            display: inline-block;
            width: 30px;
            text-align: center;
            margin-right: 10px;
            font-size: 20px;
        }}
        .meal-content {{
            padding-left: 10px;
        }}
        .calorie-info {{
            display: inline-block;
            background-color: #f5f5f5;
            padding: 3px 10px;
            border-radius: 20px;
            font-weight: bold;
            color: {secondary_color};
            margin: 8px 0;
        }}
        .prep-tip {{
            background-color: #fffbea;
            padding: 10px 15px;
            border-radius: 6px;
            margin: 10px 0;
            border-left: 3px solid #ffd34e;
        }}
        .tip-icon {{
            margin-right: 5px;
        }}
        .macro-box {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            background-color: #f9f9f9;
            padding: 12px;
            border-radius: 8px;
            margin: 15px 0;
        }}
        .macro-item {{
            flex: 1;
            min-width: 80px;
            padding: 8px;
            background: white;
            border-radius: 6px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .macro-icon {{
            font-size: 18px;
            margin-bottom: 5px;
        }}
        .macro-label {{
            font-size: 12px;
            color: #777;
            margin-bottom: 3px;
        }}
        .macro-value {{
            font-weight: bold;
            color: {primary_color};
        }}
        .footer {{
            background-color: #f5f5f5;
            padding: 20px 30px;
            font-size: 13px;
            color: #777;
            border-top: 1px solid #eee;
        }}
        .diet-specs {{
            display: inline-block;
            background-color: {primary_color}22;
            padding: 4px 12px;
            border-radius: 30px;
            color: {primary_color};
            font-weight: 500;
            margin-right: 10px;
            margin-top: 5px;
        }}
        .quote {{
            font-style: italic;
            text-align: center;
            margin: 20px 0;
            color: #888;
            padding: 15px;
            border-top: 1px solid #eee;
            border-bottom: 1px solid #eee;
        }}
        .daily-summary {{
            background: linear-gradient(135deg, {primary_color}11 0%, {secondary_color}11 100%);
            border-radius: 8px;
            padding: 15px;
            margin: 25px 0;
            border: 1px solid {primary_color}22;
        }}
        .daily-summary h3 {{
            margin-top: 0;
            font-size: 16px;
            color: {primary_color};
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }}
        .summary-item {{
            background: white;
            padding: 10px;
            border-radius: 6px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .summary-value {{
            font-size: 18px;
            font-weight: bold;
            color: {secondary_color};
        }}
        .summary-label {{
            font-size: 12px;
            color: #777;
        }}
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="container">
            <div class="header">
                <h1>Your Daily Nutrition Plan</h1>
                <div class="date">{current_date}</div>
            </div>
            <div class="content">
                <div class="daily-summary">
                    <h3>Daily Nutritional Goals</h3>
                    <div class="summary-grid">
                        <div class="summary-item">
                            <div class="summary-value">{calories}</div>
                            <div class="summary-label">Calories</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-value">{int(calories * 0.25 / 4)}g</div>
                            <div class="summary-label">Protein Target</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-value">{int(calories * 0.5 / 4)}g</div>
                            <div class="summary-label">Carbs Target</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-value">25-30g</div>
                            <div class="summary-label">Fiber Target</div>
                        </div>
                    </div>
                </div>
                
                <div class="diet-content">
                    {diet_content}
                </div>
                <div class="quote">
                    "Let food be thy medicine, and medicine be thy food." — Hippocrates
                </div>
            </div>
            <div class="footer">
                <p>Personalized for your wellness journey</p>
                <span class="diet-specs">{diet_type}</span>
                <span class="diet-specs">{calories} calories</span>
                <p style="margin-top: 15px;">Generated by AI Nutritionist Assistant. Please consult with a healthcare professional for personalized advice.</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html

def send_email(diet_plan):
    """Send the diet plan via email"""
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    # Create email message
    message = MIMEMultipart("alternative")
    message["Subject"] = config.EMAIL_SUBJECT_TEMPLATE.format(date=current_date)
    message["From"] = config.EMAIL_SENDER
    message["To"] = config.EMAIL_RECEIVER
    
    # Create HTML version of message
    html = get_html_template(current_date, diet_plan)
    
    # Attach parts to email
    part = MIMEText(html, "html")
    message.attach(part)
    
    # Create secure connection and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        try:
            server.login(config.EMAIL_SENDER, config.EMAIL_PASSWORD)
            server.sendmail(config.EMAIL_SENDER, config.EMAIL_RECEIVER, message.as_string())
            print(f"✓ Email sent successfully on {current_date}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

def nutrition_job():
    """Generate and send daily nutrition plan"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Generating daily nutrition plan...")
    diet_plan = generate_diet_plan()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sending nutrition plan via email...")
    success = send_email(diet_plan)
    
    if success:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Daily nutrition plan delivered successfully!")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed to deliver nutrition plan.")

def setup_scheduler():
    """Set up the scheduler to run at specified times"""
    # Schedule to run at the configured time
    schedule.every().day.at(config.DAILY_SEND_TIME).do(nutrition_job)
    print(f"Nutrition agent scheduled to run daily at {config.DAILY_SEND_TIME}")
    
    # For testing/demonstration purposes, run immediately if configured
    if config.RUN_TEST_ON_START:
        print("Running initial nutrition plan now for testing...")
        nutrition_job()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    import sys
    
    # Check for test-only flag
    if len(sys.argv) > 1 and sys.argv[1] == "--test-only":
        print("=" * 60)
        print("TESTING NUTRITION FOOD ALERT AGENT (WITHOUT SCHEDULING)")
        print(f"Diet Type: {config.DIETARY_PREFERENCES['diet_type']}")
        print(f"Target Calories: {config.DIETARY_PREFERENCES['calories_per_day']}")
        print("=" * 60)
        nutrition_job()
    else:
        print("=" * 60)
        print("Starting Nutrition Food Alert Agent...")
        print(f"Diet Type: {config.DIETARY_PREFERENCES['diet_type']}")
        print(f"Target Calories: {config.DIETARY_PREFERENCES['calories_per_day']}")
        print(f"Send Time: {config.DAILY_SEND_TIME}")
        print("=" * 60)
        setup_scheduler() 