# import requests
# import os

# ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
# VOICE_ID = "MaLeGj8yeAGK8yQXRAzr"  # Replace with your voice ID

# TTS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

# headers = {
#     "xi-api-key": ELEVEN_API_KEY,
#     "Content-Type": "application/json"
# }

# data = {
#     "text": "Hello! This is a test of your ElevenLabs TTS voice.",
#     "model_id": "eleven_multilingual_v2",  # Match model you use with LiveKit
#     "voice_settings": {
#         "stability": 0.5,
#         "similarity_boost": 0.5
#     }
# }

# response = requests.post(TTS_URL, json=data, headers=headers)

# if response.status_code == 200:
#     with open("output.wav", "wb") as f:
#         f.write(response.content)
#     print("Audio saved as output.wav. Play this file to hear the voice.")
# else:
#     print(f"Error: {response.status_code}\n{response.text}")
