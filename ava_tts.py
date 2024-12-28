import pyttsx3

def speak_with_pyttsx3(text):
    """
    Convert text to speech using pyttsx3 with voice index 1.
    """
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error: {e}")
