import re
import urllib.parse, webbrowser
from ava_tts import speak_with_pyttsx3

conversation_state = {"current_context": None, "search_type": None, "details": None}

def normalize_input(input_text: str) -> str:
    """
    Normalize user input to account for common typos and variations.
    """
    input_text = input_text.lower()
    input_text = re.sub(r'\bzon\b', 'amazon', input_text)
    input_text = re.sub(r'\bbucks?\b', 'books', input_text)
    input_text = re.sub(r'\bbook?\b', 'books', input_text)
    input_text = re.sub(r'\bfour\b', 'for', input_text)
    input_text = re.sub(r'\bor\b', 'for', input_text)
    input_text = re.sub(r'\bsear\b', 'search', input_text)
    input_text = re.sub(r'\bfor (\w+)\b', r'search for \1', input_text)

    

    return input_text

def handle_amazon_voice_command(command: str, listen_for_freeform):
    global conversation_state
    cmd_lower = normalize_input(command)

    if "amazon" in cmd_lower:
        search_type = re.sub(r'\b(search|for|an?\s*amazon|on?\s*amazon|in?\s*amazon)\b', '', cmd_lower, flags=re.IGNORECASE).strip()


        search_type = search_type if search_type else "items"

        conversation_state["current_context"] = "search"
        conversation_state["search_type"] = search_type

        speak_with_pyttsx3(f"Okay, you want {search_type}. Any specific details?")

        
        follow_up_command = listen_for_freeform()
        if follow_up_command:
            follow_up_cmd_lower = normalize_input(follow_up_command)
            if "no" in follow_up_cmd_lower:
                search_term = search_type
                speak_with_pyttsx3(f"Got it! Searching for {search_term} on Amazon...")
                open_amazon_search(search_term)
                return 
            else:
                search_term = follow_up_cmd_lower if search_type in follow_up_cmd_lower else f"{follow_up_cmd_lower} {search_type}"
                conversation_state["details"] = follow_up_cmd_lower

                speak_with_pyttsx3(f"Got it! Searching for {search_term} on Amazon...")
                open_amazon_search(search_term)
        else:
            speak_with_pyttsx3("I didn't hear anything. Please try again.")
        reset_conversation_state()
    else:
        speak_with_pyttsx3("Command not recognized.")




def reset_conversation_state():
    """
    Resets the global conversation state to idle.
    """
    global conversation_state
    conversation_state = {"current_context": None, "search_type": None, "details": None}

def open_amazon_search(phrase: str):
    """
    Opens the Amazon search page with the given search phrase.
    """

    base_url = "https://www.amazon.com/s"
    params = {"k": phrase}
    full_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    webbrowser.open(full_url)
