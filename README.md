# Nutrition Food Alert Agent

This agent uses the Groq AI model through the Agno framework to generate daily nutrition plans and send them to your email. The agent will provide a complete daily menu with breakfast, lunch, dinner, and snacks, focusing on healthy diet foods.

## Features

- Generates personalized daily diet food menus
- Sends the menu to your Gmail account
- Includes nutritional information and preparation tips
- Runs automatically at a scheduled time each day
- Creates balanced meals suitable for weight management
- Allows customization of dietary preferences

## Files Overview

- `nutrition_agent.py` - The main agent script
- `config.py` - Configuration settings for the agent
- `setup_windows_task.py` - Helper to set up automatic runs on Windows
- `README.md` - This documentation file

## Setup Instructions

### 1. Install Required Packages

```bash
pip install agno groq schedule
```

### 2. Set Up Gmail App Password

To send emails through Gmail, you need to create an App Password:

1. Go to your Google Account settings (https://myaccount.google.com/)
2. Navigate to Security > 2-Step Verification > App passwords
3. Select "Mail" as the app and "Other" as the device (name it "Nutrition Agent")
4. Copy the 16-character password that is generated

### 3. Configure Email Settings

Edit the `config.py` file and update the following variables:

```python
# Email configuration
EMAIL_SENDER = "your_email@gmail.com"  # Your Gmail address
EMAIL_PASSWORD = "your_app_password"  # App password from step 2
EMAIL_RECEIVER = "your_email@gmail.com"  # Where to send the diet plans
```

### 4. Customize Diet Preferences (Optional)

In the `config.py` file, you can customize your dietary preferences:

```python
# Diet preferences
DIETARY_PREFERENCES = {
    "diet_type": "balanced",  # Options: balanced, keto, vegan, vegetarian, paleo, mediterranean
    "calories_per_day": 2000,  # Target daily calories
    "allergies": [],  # List of allergies, e.g., ["nuts", "dairy", "shellfish"]
    "excluded_foods": [],  # Foods to avoid, e.g., ["mushrooms", "olives"]
    "meal_complexity": "medium",  # Options: simple, medium, complex (affects preparation time)
    "protein_focus": "balanced"  # Options: high, balanced, low
}
```

## Running the Agent

### Manual Execution

To start the agent manually, simply run:

```bash
python nutrition_agent.py
```

The agent will:
1. Generate a diet plan immediately for testing purposes (if `RUN_TEST_ON_START` is True in config.py)
2. Schedule itself to run daily at the time specified in config.py
3. Continue running in the background, sending diet plans at the scheduled time

### Automatic Execution (Windows)

To set up the agent to run automatically on Windows startup:

```bash
python setup_windows_task.py
```

This will create a scheduled task that runs the nutrition agent daily. You may need to run this as administrator.

### Automatic Execution (Linux/Mac)

For Linux/Mac users, you can set up a cron job:

1. Open the terminal and type: `crontab -e`
2. Add the following line (adjust the path as needed):
   ```
   0 6 * * * /path/to/python /path/to/nutrition_agent.py
   ```
3. Save and exit

## Troubleshooting

If you encounter email sending issues:
- Verify your Gmail app password is correct
- Check that "Less secure app access" is enabled in your Google account
- Ensure you have a stable internet connection

If the Windows Task Scheduler setup fails:
- Run the setup_windows_task.py script as administrator
- Check Windows Event Viewer for any error messages

## Customization

- Change the sending time in `config.py` by updating `DAILY_SEND_TIME`
- Modify email appearance by adjusting color codes in `config.py`
- Customize the prompt in `generate_diet_plan()` in nutrition_agent.py for more specific diet requirements 