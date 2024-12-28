import re
from ava_tts import speak_with_pyttsx3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

def play_music_on_youtube(song_name: str):
    """
    Uses Selenium to search for and play a song on YouTube.
    
    :param song_name: The name of the song to search for.
    """
    try:
        driver = webdriver.Chrome() 
        
        driver.get("https://www.youtube.com")
        time.sleep(2)
        
        search_box = driver.find_element(By.NAME, "search_query")
        search_box.send_keys(song_name)
        search_box.send_keys(Keys.RETURN) 
        time.sleep(3)
        
        first_video = driver.find_element(By.XPATH, '//*[@id="video-title"]')
        first_video.click()
        time.sleep(5) 
        speak_with_pyttsx3(f"Now playing {song_name} on YouTube.")
        time.sleep(180)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        speak_with_pyttsx3("Sorry, I couldn't play the song on YouTube.")

def normalize_input(input_text: str):
    input_text = input_text.lower()
    input_text = re.sub(r'\b\w*ay\b', r'play', input_text)
    return input_text
 
def handle_yt_voice_command(command: str):
    cmd_lower = command.lower().strip()
    normalize_input(cmd_lower)

    if cmd_lower.startswith("play"):
        song_name = re.sub(r'\bon?\s*y[ou]*\s*t[ube]*\b', '', re.sub(r'\b\w*ay\b', '', cmd_lower)).strip()
        if song_name:
            play_music_on_youtube(song_name)
        else:
            speak_with_pyttsx3("What would you like me to play?")
    else:
        speak_with_pyttsx3("Command not recognized.")
