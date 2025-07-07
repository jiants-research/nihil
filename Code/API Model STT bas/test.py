import requests

file_path = "C:\Users\GENIUS ELECTRONICS\STT-Bassa\Bassa\clips_wav\common_voice_bas_24602547.wav"
with open(file_path, "rb") as f:
    response = requests.post("http://localhost:8000/transcribe/", files={"file": f})

print(response.json())
