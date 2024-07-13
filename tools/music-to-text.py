import os
import subprocess
import sys
import wave

# Function to install a package using pip
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Function to install a package using apt-get
def install_apt(package):
    subprocess.check_call(["apt-get", "install", "-y", package])

# Install necessary libraries
try:
    import mutagen
except ImportError:
    install("mutagen")

try:
    import vosk
except ImportError:
    install("vosk")

try:
    import pydub
except ImportError:
    install("pydub")

try:
    subprocess.check_call(["ffmpeg", "-version"])
except subprocess.CalledProcessError:
    install_apt("ffmpeg")

import json
from mutagen.id3 import ID3, USLT, ID3NoHeaderError
from vosk import Model, KaldiRecognizer

def convert_mp3_to_wav(mp3_path, wav_path):
    # Ensure temp.wav is deleted if it exists
    if os.path.exists(wav_path):
        os.remove(wav_path)
    # Convert to WAV with mono PCM format and 16kHz sample rate
    result = subprocess.run(['ffmpeg', '-y', '-i', mp3_path, '-ac', '1', '-ar', '16000', wav_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error converting {mp3_path} to {wav_path}")
        print(result.stderr.decode('utf-8'))
    else:
        print(f"Successfully converted {mp3_path} to {wav_path}")

def extract_lyrics_metadata(mp3_path):
    try:
        audio = ID3(mp3_path)
        for tag in audio.values():
            if isinstance(tag, USLT):
                return tag.text
    except ID3NoHeaderError:
        return None

def recognize_speech_from_wav(wav_path, model_path):
    wf = wave.open(wav_path, "rb")
    print(f"Channels: {wf.getnchannels()}, Sample Width: {wf.getsampwidth()}, Frame Rate: {wf.getframerate()}")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        raise ValueError("Audio file must be WAV format mono PCM with 16kHz sample rate.")
    
    if not os.path.isdir(model_path):
        raise Exception(f"Model path {model_path} does not exist or is not a directory")
    
    try:
        model = Model(model_path)
    except Exception as e:
        raise Exception(f"Failed to create a model: {str(e)}")
    
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    
    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(json.loads(rec.Result()))
    
    results.append(json.loads(rec.FinalResult()))
    # Join results into a single string
    text = " ".join([res['text'] for res in results if 'text' in res])
    return text

def format_lyrics(text):
    # Split text into lines based on punctuation and add new lines at regular intervals
    lines = []
    sentence = ""
    word_count = 0
    max_words_per_line = 10  # Adjust this value as needed

    for word in text.split():
        sentence += word + " "
        word_count += 1
        if word.endswith((".", "!", "?")) or word_count >= max_words_per_line:
            lines.append(sentence.strip())
            sentence = ""
            word_count = 0

    if sentence:
        lines.append(sentence.strip())

    return "\n".join(lines)

def process_directory(mp3_directory, model_path):
    for filename in os.listdir(mp3_directory):
        if filename.endswith(".mp3"):
            mp3_file_path = os.path.join(mp3_directory, filename)
            wav_file_path = "temp.wav"
            txt_file_path = os.path.splitext(mp3_file_path)[0] + ".txt"

            lyrics = extract_lyrics_metadata(mp3_file_path)
            if not lyrics:
                convert_mp3_to_wav(mp3_file_path, wav_file_path)
                # Check the converted file format
                wf = wave.open(wav_file_path, "rb")
                print(f"Converted - Channels: {wf.getnchannels()}, Sample Width: {wf.getsampwidth()}, Frame Rate: {wf.getframerate()}")
                lyrics = recognize_speech_from_wav(wav_file_path, model_path)
            
            formatted_lyrics = format_lyrics(lyrics)
            
            with open(txt_file_path, "w") as txt_file:
                txt_file.write(formatted_lyrics)
            print(f"Extracted lyrics for {filename} and saved to {txt_file_path}")

# Directory containing MP3 files
mp3_directory = "/content"  # Update this path if necessary
# Path to Vosk model
model_path = "/content/vosk-model-small-en-us-0.15"  # Update this path if necessary

# Ensure the model is correctly downloaded and unzipped
if not os.path.isdir(model_path):
    raise Exception(f"Model path {model_path} does not exist. Please download and unzip the model correctly.")

# Process the directory
process_directory(mp3_directory, model_path)
