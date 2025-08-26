import os
import requests
from dotenv import load_dotenv

load_dotenv()

MOCK_MODE = False
API_KEY = os.getenv("GEMMA_API_KEY")
API_URL = os.getenv("GEMMA_API_URL", "")
API_TYPE = os.getenv("API_TYPE", "google")  # "google" or "huggingface"

def generate_text(prompt):
    if MOCK_MODE:
        return {"success": True, "text": f"[MOCK MODE] You entered: '{prompt}'"}

    if not API_KEY:
        return {"success": False, "error": "API key not found."}

    headers = {"Content-Type": "application/json"}
    if API_TYPE == "google":
        headers["X-goog-api-key"] = API_KEY
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
    else:  # Hugging Face
        headers["Authorization"] = f"Bearer {API_KEY}"
        data = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 512, "temperature": 0.7}
        }

    try:
        response = requests.post(API_URL, json=data, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if API_TYPE == "google":
                candidates = result.get("candidates")
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return {"success": True, "text": parts[0].get("text", "")}
            else:
                return {"success": True, "text": result.get("generated_text", "")}

            return {"success": False, "error": "No generated text found."}

        return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}

    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Connection error: {e}"}
