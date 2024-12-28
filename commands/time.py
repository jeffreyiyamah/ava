from datetime import datetime
from ava_tts import speak_with_pyttsx3
import time

def get_detailed_time(command: str):
    """Returns the current time, date, and timezone."""
    current_time = datetime.now().strftime("%I:%M %p")
    timezone = time.tzname[0]  
    am_pm = current_time.split(" ")[1]
    speak_with_pyttsx3(f"The time right now is {current_time}  {timezone}.")