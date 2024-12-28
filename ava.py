from commands.time import get_detailed_time
from commands.amazon_search import handle_amazon_voice_command, normalize_input
from commands.play import handle_yt_voice_command
from ava_tts import  speak_with_pyttsx3
from vosk import Model, KaldiRecognizer
from rapidfuzz import process
import sounddevice as sd
import queue
import json
import re


WAKE_WORDS = [
    "ava",
    "hey ava",
    "hello ava",
    "hi ava",
    "hi there ava",
    "hey there ava",
    "hello there ava",
    "ava please",
    "ava are you there",
    "ava can you hear me",
    "hello",
    "hi",
    "hey",
    "hi there",
    "hot",
    "heather"
]

MODEL_PATH = r"C:\Users\jeffr\Downloads\vosk-model-small-en-us-0.15"
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)

audio_queue = queue.Queue()

command_map = {
    "time": get_detailed_time,
    "amazon": lambda command: handle_amazon_voice_command(command, listen_for_freeform),
    "play music": lambda command: handle_yt_voice_command(command),  
}


def audio_callback(indata, data, frames, status):
    audio_queue.put(bytes(indata))

def listen_for_wake_word():
    print("\n")
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                           channels=1, callback=audio_callback):
        while True:
            audio_data = audio_queue.get()
            if recognizer.AcceptWaveform(audio_data):
                result = json.loads(recognizer.Result())
                if "text" in result:
                    text = result["text"].lower()
                    if any(word in text for word in WAKE_WORDS):
                        return text

def listen_for_command():
    """
    Listens for a command after the wake word is detected using VOSK.
    """
    print("Listening for command...")
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                           channels=1, callback=audio_callback):
        while True:
            audio_data = audio_queue.get()
            if recognizer.AcceptWaveform(audio_data):
                result = json.loads(recognizer.Result())
                if "text" in result:
                    command = result["text"].lower()
                    print(f"Detected command: {command}")
                    return command

def listen_for_freeform():
    """
    Listens for free-form user input using VOSK.
    Returns the transcribed text or None if no input is detected.
    """
    print("Listening for input...")
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                           channels=1, callback=audio_callback):
        while True:
            audio_data = audio_queue.get()
            if recognizer.AcceptWaveform(audio_data):
                result = json.loads(recognizer.Result())
                if "text" in result and result["text"].strip():
                    text = result["text"].strip().lower()
                    print(f"Detected input: {text}")
                    return text
                else:
                    return None



def execute_command(command):
    """
    Routes the recognized command to the appropriate handler.
    """
    best_match, score, *_ = process.extractOne(command, command_map.keys())
    confidence_threshold = 70
    if score >= confidence_threshold:
        command_map[best_match](command)
    else:
        clarification_prompt = {
            "time": "What time is it?",
            "amazon": "Search for items on Amazon?",
            "play music": "Play some music?",
            "stop music": "Stop playing music?"
        }
        if best_match in clarification_prompt:
            prompt = clarification_prompt[best_match]
            speak_with_pyttsx3(f"Did you mean to say {prompt}?")
            follow_up = listen_for_freeform()
            if "y" in follow_up:
                command_map[best_match](command)
            else:
                execute_command(follow_up)
        else:
           speak_with_pyttsx3("I'm sorry, I didn't catch that. Let's try again.")
           listen_for_command()



def main():
    print('\nSay "Hi", "Hey", "Hi Ava", or "Hey Ava" to activate')
    wake_word = listen_for_wake_word()
    if wake_word:
        print("Hi! I'm Ava, How can I help you today?")
        speak_with_pyttsx3("Hi Jeffrey! This is Ava, How can I help you today?")
    while True:
        try:
            while True:
                command = listen_for_command()
                if command:
                    execute_command(command)                    
                    while True: 
                            speak_with_pyttsx3("Is there anything else I can help you with?")                            
                            response = listen_for_command()
                            if response:
                                normalized_response = normalize_input(response)
                                if re.search(r'\b(no(\w+)?|not really|nothing|i\'m good|all set)\b', normalized_response, re.IGNORECASE):
                                    speak_with_pyttsx3("Okay, have a great day! Goodbye!")
                                    return
                                execute_command(normalized_response)
                            else:
                                speak_with_pyttsx3("I didn't catch that. Can you please repeat that?")
        
        except KeyboardInterrupt:
            print("Stopping AVA...")
            break


if __name__ == "__main__":
    main()
