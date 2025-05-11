import os
import subprocess
import sys
from datetime import datetime, timedelta

def create_windows_task():
    """Create a scheduled task on Windows to run the nutrition agent daily."""
    try:
        # Get the absolute path to the current directory and python executable
        current_dir = os.path.abspath(os.path.dirname(__file__))
        python_path = sys.executable
        script_path = os.path.join(current_dir, "nutrition_agent.py")
        
        # Create task name and task XML file path
        task_name = "NutritionFoodAlertAgent"
        
        # Calculate start time (5 minutes from now)
        start_time = (datetime.now() + timedelta(minutes=5)).strftime("%H:%M")
        
        # Build the schtasks command
        cmd = [
            "schtasks", "/create", "/tn", task_name, "/tr", 
            f'"{python_path} "{script_path}""', 
            "/sc", "daily", 
            "/st", start_time,
            "/ru", "SYSTEM",
            "/f"  # Force creation if task already exists
        ]
        
        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Task created successfully! The nutrition agent will run daily at {start_time}.")
            print("✓ The first run will happen automatically 5 minutes from now.")
            print("\nTo modify or delete this task:")
            print("1. Open Task Scheduler (search for 'Task Scheduler' in Windows)")
            print(f"2. Find the task named '{task_name}'")
            print("3. Right-click and select 'Properties' to modify or 'Delete' to remove")
        else:
            print("Failed to create task. Error details:")
            print(result.stderr)
            print("\nYou might need to run this script as an administrator.")
    
    except Exception as e:
        print(f"Error creating scheduled task: {e}")
        print("You may need to run this script as an administrator.")

if __name__ == "__main__":
    print("Setting up Windows Task Scheduler task for Nutrition Food Alert Agent...")
    create_windows_task()
    print("\nPress Enter to exit...")
    input() 