# Nutrition Agent Configuration

# Groq API credentials
GROQ_API_KEY = ""
GROQ_MODEL = "llama-3.3-70b-versatile"

# Email configuration
EMAIL_SENDER = ""
EMAIL_PASSWORD = ""
EMAIL_RECEIVER = ""

# Scheduling configuration
DAILY_SEND_TIME = "06:00"
RUN_TEST_ON_START = True

# Diet preferences
DIETARY_PREFERENCES = {
    "diet_type": "balanced",
    "calories_per_day": 2000,
    "allergies": [],
    "excluded_foods": [],
    "meal_complexity": "medium",
    "protein_focus": "balanced"
}

# Email template customization
EMAIL_SUBJECT_TEMPLATE = "Your Daily Nutrition Plan - {date}"
EMAIL_COLOR_PRIMARY = "#1e8a3e"
EMAIL_COLOR_SECONDARY = "#4285f4" 
