import os
import ast
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")  
API_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = "You are an expert in Python animation using the Manim library. Generate clean, runnable Manim code only. No extra explanations. Do not change the context of the code, only fix any syntax errors."

def call_llm(prompt: str) -> str:
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

def get_manim_code_from_llm(prompt: str) -> str:
    return call_llm(prompt)

def fix_code(code: str) -> str:
    try:
        ast.parse(code)
        return code
    except SyntaxError as e:
        error_line = e.lineno
        lines = code.splitlines()
        if 0 < error_line <= len(lines):
            faulty = lines[error_line - 1]
        else:
            raise Exception("Unable to isolate faulty line.")

        fix_prompt = (
            f"You are a Python expert. The following line has a syntax error:\n"
            f"Line {error_line}: {faulty}\n"
            f"Fix ONLY this line and return the corrected version without explanations."
        )

        fixed_line = call_llm(fix_prompt).strip()
        lines[error_line - 1] = fixed_line
        return "\n".join(lines)

if __name__ == "__main__":
    user_prompt = input("Describe the Manim animation you want: ")
    try:
        manim_code = get_manim_code_from_llm(user_prompt)
        print("\nGenerated Manim Code:\n")
        print(manim_code)

        fixed_code = fix_code(manim_code)
        print("\nFixed Manim Code:\n")
        print(fixed_code)

    except Exception as e:
        print("Error:", e)
