import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your Gemini API key from the .env file
API_KEY = os.getenv("GEMINI_API_KEY")

# Google Gemini API URL
API_URL = "https://gemini.googleapis.com/v1beta2:generateText"

# System prompt for better consistency
SYSTEM_PROMPT = "You are an expert in Python animation using the Manim library. Generate clean, runnable Manim code only. No extra explanations."

def get_manim_code_from_gemini(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gemini-v1.0",  # Ensure this is the correct model name for Gemini
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        completion = response.json()
        return completion["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    user_prompt = input("Describe the Manim animation you want: ")
    try:
        manim_code = get_manim_code_from_gemini(user_prompt)
        print("\nGenerated Manim Code:\n")
        print(manim_code)
    except Exception as e:
        print("Error:", e)


# import os
# import requests
# from dotenv import load_dotenv

# load_dotenv()

# # Set your OpenRouter API key
# API_KEY = os.getenv("OPENROUTER_API_KEY")  # Or replace with a string: "your_api_key_here"

# # LLaMA 3 70B endpoint
# API_URL = "https://openrouter.ai/api/v1/chat/completions"

# # System prompt for better consistency
# SYSTEM_PROMPT = "You are an expert in Python animation using the Manim library. Generate clean, runnable Manim code only. No extra explanations."

# def get_manim_code_from_llama(prompt: str) -> str:
#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "Content-Type": "application/json"
#     }

#     data = {
#         "model": "meta-llama/llama-3-70b-instruct",
#         "messages": [
#             {"role": "system", "content": SYSTEM_PROMPT},
#             {"role": "user", "content": prompt}
#         ],
#         "temperature": 0.5
#     }

#     response = requests.post(API_URL, headers=headers, json=data)

#     if response.status_code == 200:
#         completion = response.json()
#         return completion["choices"][0]["message"]["content"]
#     else:
#         raise Exception(f"Failed: {response.status_code} - {response.text}")

# if __name__ == "__main__":
#     user_prompt = input("Describe the Manim animation you want: ")
#     try:
#         manim_code = get_manim_code_from_llama(user_prompt)
#         print("\nGenerated Manim Code:\n")
#         print(manim_code)
#     except Exception as e:
#         print("Error:", e)
