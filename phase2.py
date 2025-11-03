import os
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage

# --- 1. Configuration: UPDATE THESE VALUES ---

# Your Google Cloud Project ID
PROJECT_ID = "spark-f5c5c" 

# The GCS bucket you created
BUCKET_NAME = "speech-to-text-prg" 

# --- NEW ---
# The exact name of the one file you uploaded to the 'audio' folder
SPECIFIC_AUDIO_FILE = "P1.wav" 

# --- (These paths are now built from the filename) ---
GCS_INPUT_URI = f"gs://{BUCKET_NAME}/audio/{SPECIFIC_AUDIO_FILE}"
OUTPUT_FILE_NAME = f"{SPECIFIC_AUDIO_FILE}.json"
GCS_OUTPUT_URI = f"gs://{BUCKET_NAME}/transcripts/{OUTPUT_FILE_NAME}"


# --- 2. Speech Adaptation (To Catch Filler Words) ---
# This tells the API to be "more sensitive" to these specific words.
filler_phrases = ["um", "uh", "hmm", "like", "so", "yeah", "okay"]

phrase_set = speech.PhraseSet(
    phrases=[speech.PhraseSet.Phrase(value=phrase, boost=10.0) for phrase in filler_phrases]
)

speech_adaptation = speech.SpeechAdaptation(
    phrase_sets=[phrase_set]
)

# --- 3. Main Recognition Configuration ---
# This config will be used for your file.
# You MUST provide your file's details here for high accuracy.

config = speech.RecognitionConfig(
    # TODO: Update these based on your file details (see below)
    # language_code="en-US", 
    # sample_rate_hertz=16000,
    # encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,

    # High-quality model. Use "telephony" if it's phone calls.
    model="video", 
    
    # Enables features for better readability
    enable_automatic_punctuation=True,
    
    # This is the key part for capturing filler words
    adaptation=speech_adaptation
)

# --- 4. Define and Run the Single Job ---
def transcribe_single_file():
    """
    Submits a single transcription job and waits for it to complete.
    """
    speech_client = speech.SpeechClient()
    
    print(f"Submitting job for: {GCS_INPUT_URI}")

    # Set the GCS path for the audio file
    audio = speech.RecognitionAudio(uri=GCS_INPUT_URI)
    
    # Set the GCS path for the output JSON transcript
    output_config = speech.RecognitionOutputConfig(
        gcs_output_config=speech.GcsOutputConfig(uri=GCS_OUTPUT_URI)
    )

    # Create the asynchronous request
    request = speech.LongRunningRecognizeRequest(
        config=config,
        audio=audio,
        output_config=output_config
    )

    # Submit the transcription job
    try:
        operation = speech_client.long_running_recognize(request=request)
        
        print("  ...Job submitted. Waiting for operation to complete (this can take a moment)...")
        
        # --- NEW: Wait for the result ---
        # For a single file, we can wait for it to finish.
        # Set a 10-minute timeout (600 seconds)
        response = operation.result(timeout=600) 
        
        print(f"\n--- Done ---")
        print(f"Transcription complete.")
        print(f"Check the output file at: {GCS_OUTPUT_URI}")

    except Exception as e:
        print(f"Error processing file {GCS_INPUT_URI}: {e}")

# --- 5. Main Execution ---
if __name__ == "__main__":
    # Ensure the environment variable is set
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        print("Error: GOOGLE_APPLICATION_CREDENTIALS environment variable not set.")
        print("Please follow Phase 2 of the guide to set it.")
    else:
        # Check that the user updated the file name
        if SPECIFIC_AUDIO_FILE == "your_file_name_here.wav":
            print("Error: Please update the SPECIFIC_AUDIO_FILE variable in the script.")
        else:
            transcribe_single_file()