import os
import ast
import re
import uuid
import requests
import subprocess
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
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Failed: {response.status_code} - {response.text}")

def clean_code(text: str) -> str:
    code_block = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    return code_block.group(1).strip() if code_block else text.strip()

def fix_code(code: str) -> str:
    try:
        ast.parse(code)
        print("\n*****no code error*****\n")
        return code
    except SyntaxError as e:
        line = e.lineno
        lines = code.splitlines()
        if 0 < line <= len(lines):
            bad_line = lines[line - 1]
        else:
            raise Exception("Unable to isolate faulty line.")
        fix_prompt = f"You are a Python expert. The following line has a syntax error:\nLine {line}: {bad_line}\nFix ONLY this line and return the corrected version without explanations."
        fixed = call_llm(fix_prompt).strip()
        lines[line - 1] = fixed
        return "\n".join(lines)

def extract_class_name(code: str) -> str:
    for line in code.splitlines():
        if line.strip().startswith("class") and "(Scene)" in line:
            return line.split("class")[1].split("(")[0].strip()
    raise ValueError("No Scene class found.")

def render_manim(code: str) -> str:
    class_name = extract_class_name(code)
    filename = f"temp_scene_{uuid.uuid4().hex}.py"

    with open(filename, "w") as f:
        f.write(code)

    try:
        subprocess.run(["manim", "-ql", filename, class_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        video_path = f"media/videos/{filename.replace('.py', '')}/480p15/{class_name}.mp4"
        if os.path.exists(video_path):
            return video_path
        else:
            raise FileNotFoundError("Video not found.")
    finally:
        os.remove(filename)

if __name__ == "__main__":
    user_prompt = input("Describe the Manim animation you want: ")

    try:
        raw_code = call_llm(user_prompt)
        cleaned_code = clean_code(raw_code)
        fixed_code = fix_code(cleaned_code)

        print("\nGenerated Code:\n")
        print(fixed_code)

        video_path = render_manim(fixed_code)
        print(f"\nVideo saved at: {video_path}")

    except Exception as e:
        print("Error:", e)
