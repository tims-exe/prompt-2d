import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")  

API_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = "You are an expert in Python animation using the Manim library. Generate clean, runnable Manim code only. No extra explanations. Do not change the context of the code, only fix any syntax errors."

def get_manim_code_from_llama(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/llama-3-70b-instruct", 
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

def verify_and_fix_code(manim_code: str) -> str:
    verification_prompt = (
        f"The following code is a Manim animation. Please check for any syntax errors, "
        f"and fix only the syntax errors without changing the context of the code.\n\n"
        f"Code:\n{manim_code}\n"
        f"Fix any syntax errors and return the corrected code."
    )

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/llama-3-70b-instruct", 
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": verification_prompt}
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
        manim_code = get_manim_code_from_llama(user_prompt)
        print("\nGenerated Manim Code:\n")
        print(manim_code)

        fixed_manim_code = verify_and_fix_code(manim_code)
        print("\nFixed Manim Code (with syntax corrections only):\n")
        print(fixed_manim_code)

    except Exception as e:
        print("Error:", e)
