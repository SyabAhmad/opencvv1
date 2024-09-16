import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import speech_recognition as sr
from moviepy.editor import VideoFileClip
import tempfile
import math
import threading
import time

class SubtitleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Subtitle Generator")
        self.processing = False

        # Create and place widgets
        self.create_widgets()
        
    def create_widgets(self):
        # File selection
        self.file_label = tk.Label(self.root, text="Video File:")
        self.file_label.pack(pady=5)
        
        self.file_entry = tk.Entry(self.root, width=50)
        self.file_entry.pack(pady=5)
        
        self.browse_button = tk.Button(self.root, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=5)
        
        # Generate subtitles button
        self.generate_button = tk.Button(self.root, text="Generate Subtitles", command=self.start_processing)
        self.generate_button.pack(pady=20)
        
        # Status and log
        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack(pady=5)
        
        self.log_text = scrolledtext.ScrolledText(self.root, height=15, width=80, wrap=tk.WORD)
        self.log_text.pack(pady=5)
        self.log_text.insert(tk.END, "Log:\n")
        self.log_text.config(state=tk.DISABLED)  # Make the text widget read-only

    def browse_file(self):
        """Open a file dialog to select a video file."""
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def format_time(self, seconds):
        """Convert seconds to SRT timestamp format."""
        milliseconds = int((seconds - int(seconds)) * 1000)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f'{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}'
    
    def extract_audio_and_transcribe(self, video_filepath, chunk_duration=10):
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
                self.log("Audio extraction successful.")
            except Exception as e:
                self.log(f"Error extracting audio: {str(e)}")
                return None
    
            # Perform speech recognition using Google Speech-to-Text
            recognizer = sr.Recognizer()
            audio_duration = audio_clip.duration
            num_chunks = math.ceil(audio_duration / chunk_duration)
    
            self.log(f"Processing {num_chunks} chunks of audio.")
    
            for i in range(num_chunks):
                start_time = i * chunk_duration
                end_time = min((i + 1) * chunk_duration, audio_duration)
                temp_chunk_file = os.path.join(temp_dir, f"chunk_{i}.wav")
    
                # Extract audio chunk
                try:
                    audio_clip.subclip(start_time, end_time).write_audiofile(temp_chunk_file)
                except Exception as e:
                    self.log(f"Error extracting audio chunk: {str(e)}")
                    continue
    
                # Transcribe audio chunk
                with sr.AudioFile(temp_chunk_file) as source:
                    try:
                        audio_data = recognizer.record(source)
                        transcription = recognizer.recognize_google(audio_data)
                        subtitles.append((start_time, end_time, transcription))
                        self.log(f"Transcription successful for chunk {i}.")
                    except sr.UnknownValueError:
                        self.log("Google Speech Recognition could not understand audio")
                    except sr.RequestError as e:
                        self.log(f"Could not request results from Google Speech Recognition service; {e}")
                    except Exception as e:
                        self.log(f"Unexpected error during speech recognition: {str(e)}")
    
        return subtitles
    
    def generate_srt(self, subtitles, filename='output.srt'):
        """
        Generates an SRT file from a list of subtitles.
    
        Args:
            subtitles (list): List of subtitles with start and end times.
            filename (str): Path to the output SRT file.
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for index, (start_time, end_time, text) in enumerate(subtitles, 1):
                    f.write(f"{index}\n")
                    f.write(f"{self.format_time(start_time)} --> {self.format_time(end_time)}\n")
                    f.write(f"{text}\n\n")
            self.log("SRT file created successfully.")
        except Exception as e:
            self.log(f"Error writing SRT file: {str(e)}")
    
    def generate_subtitles(self):
        """Handle the button click event to generate subtitles."""
        video_path = self.file_entry.get()
        if not os.path.isfile(video_path):
            messagebox.showerror("Error", "Invalid file path. Please select a valid video file.")
            return
        
        self.processing = True
        self.status_label.config(text="Generating subtitles...")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)  # Clear previous logs
        self.log_text.insert(tk.END, "Log:\n")
        self.log_text.config(state=tk.DISABLED)
        
        subtitles = self.extract_audio_and_transcribe(video_path)
        if subtitles:
            self.generate_srt(subtitles)
            self.status_label.config(text="SRT file created successfully.")
            messagebox.showinfo("Success", "SRT file created successfully.")
        else:
            self.status_label.config(text="Failed to create SRT file.")
            messagebox.showerror("Error", "Failed to create SRT file.")
        
        self.processing = False

    def start_processing(self):
        """Start the subtitle generation process in a separate thread."""
        if self.processing:
            messagebox.showinfo("Info", "Processing is already in progress.")
            return
        
        threading.Thread(target=self.generate_subtitles, daemon=True).start()
        self.update_log()

    def update_log(self):
        """Update the log area every second."""
        if self.processing:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.yview(tk.END)  # Auto-scroll to the bottom
            self.log_text.config(state=tk.DISABLED)
            self.root.after(1000, self.update_log)  # Schedule to run update_log again after 1000ms (1s)

    def log(self, message):
        """Log messages to the text widget."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.yview(tk.END)  # Auto-scroll to the bottom

# Create the main window
root = tk.Tk()
app = SubtitleApp(root)
root.mainloop()
