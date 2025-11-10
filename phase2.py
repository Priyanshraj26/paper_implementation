import os
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage

# --- 1. Configuration: UPDATE THESE VALUES ---

# Your Google Cloud Project ID
PROJECT_ID = "spark-f5c5c"  # UPDATE THIS

# The GCS bucket you created
BUCKET_NAME = "speech-to-text-prg"  # UPDATE THIS

# --- NEW ---
# The exact name of the one file you uploaded to the 'audio' folder
SPECIFIC_AUDIO_FILE = "interview_cleaned.wav"  # UPDATE THIS

# The full path to your service account JSON key file
KEY_FILE_PATH = "D:\\Study\\paper_implementation\\spark-f5c5c-28e0f0bee33c.json"

# --- (These paths are now built from the filename) ---
GCS_INPUT_URI = f"gs://{BUCKET_NAME}/audio/{SPECIFIC_AUDIO_FILE}"
OUTPUT_FILE_NAME = f"{SPECIFIC_AUDIO_FILE}.json"
GCS_OUTPUT_URI = f"gs://{BUCKET_NAME}/transcripts/{OUTPUT_FILE_NAME}"


# --- 2. Speech Adaptation (To Catch Filler Words) ---
filler_phrases = ["um", "uh", "hmm", "like", "so", "yeah", "okay"]

phrase_set = speech.PhraseSet(
    phrases=[speech.PhraseSet.Phrase(value=phrase, boost=10.0) for phrase in filler_phrases]
)

speech_adaptation = speech.SpeechAdaptation(
    phrase_sets=[phrase_set]
)

# --- 3. Main Recognition Configuration ---
config = speech.RecognitionConfig(
    # TODO: Update these based on your file details
    language_code="en-US",  # UNCOMMENT AND UPDATE IF NEEDED
    sample_rate_hertz=16000,  # UNCOMMENT IF YOU KNOW THE SAMPLE RATE
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # UNCOMMENT IF NEEDED

    model="video", 
    enable_automatic_punctuation=True,
    adaptation=speech_adaptation
)

# --- 4. Define and Run the Single Job ---
def transcribe_single_file():
    """
    Submits a single transcription job and waits for it to complete.
    """
    
    speech_client = speech.SpeechClient.from_service_account_file(KEY_FILE_PATH)
    
    print(f"Submitting job for: {GCS_INPUT_URI}")

    audio = speech.RecognitionAudio(uri=GCS_INPUT_URI)
    
    # --- FIXED: Use gcs_uri directly ---
    output_config = speech.TranscriptOutputConfig(
        gcs_uri=GCS_OUTPUT_URI
    )

    request = speech.LongRunningRecognizeRequest(
        config=config,
        audio=audio,
        output_config=output_config
    )

    try:
        operation = speech_client.long_running_recognize(request=request)
        
        print("  ...Job submitted. Waiting for operation to complete...")
        
        response = operation.result(timeout=600) 
        
        print(f"\n--- Done ---")
        print(f"Transcription complete.")
        print(f"Check the output file at: {GCS_OUTPUT_URI}")

    except Exception as e:
        print(f"Error processing file {GCS_INPUT_URI}: {e}")

# --- 5. Main Execution ---
if __name__ == "__main__":
    # FIXED: Check for placeholder values
    if SPECIFIC_AUDIO_FILE == "your_file_name_here.wav":
        print("Error: Please update the SPECIFIC_AUDIO_FILE variable in the script.")
    elif PROJECT_ID == "your-project-id":
        print("Error: Please update the PROJECT_ID variable in the script.")
    elif BUCKET_NAME == "your-unique-bucket-name":
        print("Error: Please update the BUCKET_NAME variable in the script.")
    else:
        transcribe_single_file()