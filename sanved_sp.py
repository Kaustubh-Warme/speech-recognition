import os
import speech_recognition as sr
from moviepy.editor import VideoFileClip
from detoxify import Detoxify
 
# Function to convert video to audio and then to text
def video_to_text(video_path):
    # Load video file
    video = VideoFileClip(video_path)
    audio_path = "temp_audio.mp4"
   
    # Extract audio and save it as a temporary wav file
    video.audio.write_audiofile(audio_path, codec='pcm_s16le')
   
    # Convert audio to text
    text = audio_to_text(audio_path)
   
    # Clean up temporary audio file
    os.remove(audio_path)
   
    return text
 
# Function to convert audio to text
def audio_to_text(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)  # Read the entire audio file
 
    try:
        text = recognizer.recognize_google(audio)  # Using Google Web Speech API
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
 
# Main function
def main(input_path):
    if input_path.endswith(('.mp4', '.avi', '.mov')):
        # If input is a video file
        text = video_to_text(input_path)
    elif input_path.endswith(('.wav', '.mp3', '.m4a')):
        # If input is an audio file
        text = audio_to_text(input_path)
    elif input_path.endswith('.txt'):
        # If input is a text file
        with open(input_path, 'r') as file:
            text = file.read()
    else:
        raise ValueError("Unsupported file format. Please provide a video, audio, or text file.")
   
    print("Extracted Text:")
    print(text)
 
    # Classify the extracted text
    classification = classify_text(text)
    print("\nClassification Results:")
    print(classification)
 
if __name__ == "__main__":
    input_file_path = input("Enter the path to the audio/video/text file: ")
    main(input_file_path)