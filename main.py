import os
import time
import pygame
from gtts import gTTS
import streamlit as st
import speech_recognition as sr
from googletrans import LANGUAGES, Translator

isTranslateOn = False 

translator = Translator()  # Initialize the translator module.
pygame.mixer.init()  # Initialize the mixer module.

# Create a mapping between language names and language codes
language_mapping = {name: code for code, name in LANGUAGES.items()}

def get_language_code(language_name):
    return language_mapping.get(language_name, language_name)

def translator_function(spoken_text, from_language, to_language):
    try:
        return translator.translate(spoken_text, src=from_language, dest=to_language)
    except Exception as e:
        st.error(f"Translation error: {e}")
        return None

def text_to_voice(text_data, to_language):
    try:
        myobj = gTTS(text=text_data, lang=to_language, slow=False)
        myobj.save("cache_file.mp3")
        audio = pygame.mixer.Sound("cache_file.mp3")  # Load a sound.
        audio.play()
        os.remove("cache_file.mp3")
    except Exception as e:
        st.error(f"Text-to-speech error: {e}")

def main_process(output_placeholder, from_language, to_language):
    global isTranslateOn
    
    rec = sr.Recognizer()  # Initialize recognizer once

    while isTranslateOn:
        with sr.Microphone() as source:
            output_placeholder.text("Listening...")
            rec.pause_threshold = 1
            try:
                audio = rec.listen(source, phrase_time_limit=10)
            except Exception as e:
                output_placeholder.text(f"Microphone error: {e}")
                continue
        
        try:
            output_placeholder.text("Processing...")
            spoken_text = rec.recognize_google(audio, language=from_language)
            
            output_placeholder.text("Translating...")
            translated_text = translator_function(spoken_text, from_language, to_language)
            if translated_text:
                text_to_voice(translated_text.text, to_language)
    
        except sr.UnknownValueError:
            output_placeholder.text("Google Speech Recognition could not understand audio.")
        except sr.RequestError as e:
            output_placeholder.text(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            output_placeholder.text(f"An error occurred: {e}")

# UI layout
st.title("Language Translator")

# Dropdowns for selecting languages
from_language_name = st.selectbox("Select Source Language:", list(LANGUAGES.values()))
to_language_name = st.selectbox("Select Target Language:", list(LANGUAGES.values()))

# Convert language names to language codes
from_language = get_language_code(from_language_name)
to_language = get_language_code(to_language_name)

# Button to trigger translation
start_button = st.button("Start")
stop_button = st.button("Stop")

# Check if "Start" button is clicked
if start_button:
    if not isTranslateOn:
        isTranslateOn = True
        output_placeholder = st.empty()
        main_process(output_placeholder, from_language, to_language)

# Check if "Stop" button is clicked
if stop_button:
    isTranslateOn = False
