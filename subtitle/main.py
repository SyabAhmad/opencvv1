import cv2
import numpy as np
import os
import speech_recognition as sr
from moviepy.editor import VideoFileClip
import tempfile
import math

# Path to video
videoPath = r'I:\Code\opencv\subtitle\video\smalltext.mp4'

def format_time(seconds):
    """Convert seconds to SRT timestamp format."""
    milliseconds = int((seconds - int(seconds)) * 1000)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f'{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}'

def extract_audio_and_transcribe(video_filepath, chunk_duration=10):
    """
    Extracts audio from a video file, transcribes it using Google Speech-to-Text,
    and returns a list of subtitles with their timestamps.

    Args:
        video_filepath (str): Path to the video file.
        chunk_duration (int): Duration of each audio chunk in seconds.

    Returns:
        list: List of subtitles with their start and end times.
    """
    subtitles = []
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_audio_file = os.path.join(temp_dir, "extracted_audio.wav")

        # Extract audio using moviepy
        try:
            video_clip = VideoFileClip(video_filepath)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(temp_audio_file)
        except Exception as e:
            print(f"Error extracting audio: {str(e)}")
            return None

        # Perform speech recognition using Google Speech-to-Text
        recognizer = sr.Recognizer()
        audio_duration = audio_clip.duration
        num_chunks = math.ceil(audio_duration / chunk_duration)

        for i in range(num_chunks):
            start_time = i * chunk_duration
            end_time = min((i + 1) * chunk_duration, audio_duration)
            temp_chunk_file = os.path.join(temp_dir, f"chunk_{i}.wav")

            # Extract audio chunk
            try:
                # audio_clip.subclip(start_time, end_time).write_audiofile(temp_chunk_file)
                audio_clip.subclip(start_time, end_time).write_audiofile(temp_chunk_file)
            except Exception as e:
                print(f"Error extracting audio chunk: {str(e)}")
                continue

            # Transcribe audio chunk
            with sr.AudioFile(temp_chunk_file) as source:
                try:
                    audio_data = recognizer.record(source)
                    transcription = recognizer.recognize_google(audio_data)
                    subtitles.append((start_time, end_time, transcription))
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
                except Exception as e:
                    print(f"Unexpected error during speech recognition: {str(e)}")

    return subtitles

def generate_srt(subtitles, filename='output.srt'):
    """
    Generates an SRT file from a list of subtitles.

    Args:
        subtitles (list): List of subtitles with start and end times.
        filename (str): Path to the output SRT file.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for index, (start_time, end_time, text) in enumerate(subtitles, 1):
            f.write(f"{index}\n")
            f.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
            f.write(f"{text}\n\n")

# Extract audio and transcribe
subtitles = extract_audio_and_transcribe(videoPath)
if subtitles:
    generate_srt(subtitles)
    print("SRT file created successfully.")
else:
    print("Failed to create SRT file.")
