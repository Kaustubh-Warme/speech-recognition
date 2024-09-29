import os
import speech_recognition as sr
from moviepy.editor import VideoFileClip
from detoxify import Detoxify
import streamlit as st
import wave
import pyaudio

# Function to convert video to audio and then to text
def video_to_text(video_path):
    video = VideoFileClip(video_path)
    audio_path = "temp_audio.wav"
    video.audio.write_audiofile(audio_path, codec='pcm_s16le')
    text = audio_to_text(audio_path)
    os.remove(audio_path)
    return text

# Function to convert audio to text
def audio_to_text(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "Could not request results from Google Speech Recognition service"

# Function to classify text using Detoxify
def classify_text(text):
    detoxify_model = Detoxify('original')
    classification = detoxify_model.predict(text)
    return classification

# Streamlit UI
st.title("Audio/Video to Text Converter and Classifier")

if "recording" not in st.session_state:
    st.session_state.recording = False

if "stream" not in st.session_state:
    st.session_state.stream = None

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WAVE_OUTPUT_FILENAME = "temp_audio.wav"

def start_recording():
    audio = pyaudio.PyAudio()
    st.session_state.stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    st.session_state.frames = []
    st.session_state.recording = True
    st.write("Recording... Press 'Stop Recording' to stop.")

def stop_recording():
    stream = st.session_state.stream
    stream.stop_stream()
    stream.close()
    audio = pyaudio.PyAudio()
    frames = st.session_state.frames
    audio.terminate()

    st.write("Recording complete.")
    with wave.open("temp_audio.wav", 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    text = audio_to_text(WAVE_OUTPUT_FILENAME)

    if text:
        st.write("Extracted Text:")
        st.write(text)
        classification = classify_text(text)
        st.write("Classification Results:")
        st.json(classification)

if st.button("Start Recording"):
    start_recording()

if st.button("Stop Recording") and st.session_state.recording:
    stop_recording()

uploaded_file = st.file_uploader("Choose an audio or video file", type=['mp4', 'avi', 'mov', 'wav', 'mp3', 'm4a'])

if uploaded_file is not None:
    with open("temp_uploaded_file", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    file_extension = uploaded_file.name.split('.')[-1].lower()

    if file_extension in ['mp4', 'avi', 'mov']:
        st.write("Processing video file...")
        text = video_to_text("temp_uploaded_file")
    elif file_extension in ['wav', 'mp3', 'm4a']:
        st.write("Processing audio file...")
        text = audio_to_text("temp_uploaded_file")
    elif file_extension == 'txt':
        st.write("Processing text file...")
        with open("temp_uploaded_file", 'r') as file:
            text = file.read()
    else:
        st.error("Unsupported file format. Please upload a video, audio, or text file.")
        text = None
    
    if text:
        st.write("Extracted Text:")
        st.write(text)
        classification = classify_text(text)
        st.write("Classification Results:")
        st.json(classification)

# Clean up temporary file
if os.path.exists("temp_uploaded_file"):
    os.remove("temp_uploaded_file")
