import whisper
import os


def transcriber(file_path):
    """
    Given a path to an audio file, this function:
    1. Detects the language of the audio.
    2. Transcribes the audio in that detected language.
    3. Saves the transcription to 'transcription.txt'.
    """

    if not os.path.exists(file_path):
        print("File not found")
        return None

    try:
        # Load the Whisper model (automatically detects language and transcribes accordingly)
        model = whisper.load_model("base")

        # Transcribe the audio file
        result = model.transcribe(file_path)
        transcription = result.get("text", "")
        detected_language = result.get("language", "unknown")
        print(f"Detected language: {detected_language}")

        # Save the transcription in a file
        with open("transcription.txt", "w", encoding="utf-8") as f:
            f.write(transcription)

        return transcription
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return None
