import io
import os
import pyaudio
import wave
from google.cloud import speech_v1p1beta1 as speech
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import google.generativeai as genai
from google.generativeai.types import BlockedPromptException

genai.configure(api_key="AIzaSyBLAeeTpROgizwkl-5gFXoppuNjdLDjJIk")

# Set up the model
generation_config = {
  "temperature": 0,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
]

class Faltu_Exception(Exception):
    pass


model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

convo = model.start_chat(history=[
  {
    "role": "user",
    "parts": ["Does the following text contain any harm or violence, return in only True or False:"]
  },
  {
    "role": "model",
    "parts": ["False"]
  },
])


def record_audio(output_file, duration=5):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000  # Sample rate
    RECORD_SECONDS = duration

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    frames = []

    print("Recording...")

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(output_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_audio(audio_file_path, credentials_file):
    string = ''
    # Authenticate using service account credentials
    client = speech.SpeechClient.from_service_account_json(credentials_file)

    # Read the audio file
    with io.open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Perform the transcription
    response = client.recognize(config=config, audio=audio)

    # Print the transcription
    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))
        text = str('' + format(result.alternatives[0].transcript))
    return text

if __name__ == "__main__":
    # Record audio from the microphone
    output_file = "recorded_audio.wav"
    duration = 5  # Duration of recording in seconds
    record_audio(output_file, duration)

    # Provide the path to your service account credentials JSON file
    credentials_file = "pup-aireo-d23a741e313e.json"

    # Transcribe the recorded audio
    text = transcribe_audio(output_file, credentials_file)

    # Clean up - delete the recorded audio file
    os.remove(output_file)

    try:
        convo.send_message(f"Does the following text contain any harmful intent, return in only True or False: '{text}'")
        print(convo.last.text)
        signal = False
    except BlockedPromptException:
        print("True")
        signal = True

    # Get current date and time
    current_datetime = datetime.datetime.now()

    # Format date as mm-dd-yyyy
    date_formatted = current_datetime.strftime("%m-%d-%Y")

    # Format time as 09:30
    time_formatted = current_datetime.strftime("%H:%M")

    # Initialize Firebase
    cred = credentials.Certificate("ser.json")
    firebase_admin.initialize_app(cred)

    # Access Firestore database
    db = firestore.client()

    # Add the message, signal, date, and time to the "alerts" collection
    doc_ref = db.collection(u'alerts').document()

    doc_ref.set({
        u'message': text,
        u'signal': signal,
        u'date': date_formatted,
        u'time': time_formatted
    })