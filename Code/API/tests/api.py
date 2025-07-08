#!/usr/bin/env python3
import requests
import json

def translate(text: str, target_language: str) -> dict:
    url = "https://d43c52d786be.ngrok-free.app/translate/"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "target_language": target_language,
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # will raise an HTTPError if the status is 4xx/5xx
    return response.json()

if __name__ == "__main__":
    # Example usage
    try:
        result = translate("string", "string")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except requests.HTTPError as e:
        print(f"Request failed: {e} — {e.response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")
