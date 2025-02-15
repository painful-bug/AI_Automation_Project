# import whisper
# import os


# def transcriber(file_path):
#     """
#     Given a path to an audio file, this function:
#     1. Detects the language of the audio.
#     2. Transcribes the audio in that detected language.
#     3. Saves the transcription to 'transcription.txt'.
#     """

#     if not os.path.exists(file_path):
#         print("File not found")
#         return None

#     try:
#         # Load the Whisper model (automatically detects language and transcribes accordingly)
#         model = whisper.load_model("base")

#         # Transcribe the audio file
#         result = model.transcribe(file_path)
#         transcription = result.get("text", "")
#         detected_language = result.get("language", "unknown")
#         print(f"Detected language: {detected_language}")

#         # Save the transcription in a file
#         with open("transcription.txt", "w", encoding="utf-8") as f:
#             f.write(transcription)

#         return transcription
#     except Exception as e:
#         print(f"An error occurred during transcription: {e}")
#         return None


import speech_recognition as sr
from pydub import AudioSegment
import os
import subprocess
import sys

def check_dependencies():
    # Check if ffmpeg is installed
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("Error: ffmpeg is not installed. Install it using:")
        print("sudo apt-get update && sudo apt-get install ffmpeg")
        sys.exit(1)

def transcriber(audio_path):
    check_dependencies()
    # Check if input file exists
    if not os.path.exists(audio_path):
        print(f"Error: File '{audio_path}' not found")
        return
    
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    # Convert mp3 to wav using pydub
    print("Converting mp3 to wav...")
    try:
        audio = AudioSegment.from_mp3(audio_path)
        wav_path = "/tmp/temp_audio.wav"  # Using /tmp directory for temporary files
        audio.export(wav_path, format="wav")
    except Exception as e:
        print(f"Error converting audio: {e}")
        return
    
    # Transcribe the audio
    print("Transcribing audio...")
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            
            # Save transcription to file
            output_path = os.path.join(os.getcwd(), "transcription.txt")
            with open(output_path, "w") as f:
                f.write(text)
            print(f"Transcription saved to: {output_path}")
            
        except sr.UnknownValueError:
            print("Speech recognition could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results from speech recognition service; {e}")
        finally:
            # Clean up temporary wav file
            if os.path.exists(wav_path):
                os.remove(wav_path)

# if __name__ == "__main__":
#     # Check for ffmpeg first
#     check_dependencies()
    
#     # Get audio file path from command line or use default
#     if len(sys.argv) > 1:
#         audio_file = sys.argv[1]
#     else:
#         audio_file = "hello.mp3"
#         print("No audio file specified. Usage: python script.py <audio_file.mp3>")
#         sys.exit(1)
    
#     transcribe_audio(audio_file)
