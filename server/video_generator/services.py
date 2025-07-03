import os
import ast
import re
import uuid
import requests
import subprocess
from dotenv import load_dotenv

load_dotenv()

class ManimService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.system_prompt = "You are an expert in Python animation using the Manim library. Generate clean, runnable Manim code only. No extra explanations. Do not change the context of the code, only fix any syntax errors."

    def call_llm(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "meta-llama/llama-3-70b-instruct",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }

        response = requests.post(self.api_url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Failed: {response.status_code} - {response.text}")

    def clean_code(self, text: str) -> str:
        code_block = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
        return code_block.group(1).strip() if code_block else text.strip()

    def fix_code(self, code: str) -> str:
        try:
            ast.parse(code)
            return code
        except SyntaxError as e:
            line = e.lineno
            lines = code.splitlines()
            if 0 < line <= len(lines):
                bad_line = lines[line - 1]
            else:
                raise Exception("Unable to isolate faulty line.")
            
            fix_prompt = f"You are a Python expert. The following line has a syntax error:\nLine {line}: {bad_line}\nFix ONLY this line and return the corrected version without explanations."
            fixed = self.call_llm(fix_prompt).strip()
            lines[line - 1] = fixed
            return "\n".join(lines)

    def extract_class_name(self, code: str) -> str:
        for line in code.splitlines():
            if line.strip().startswith("class") and "(Scene)" in line:
                return line.split("class")[1].split("(")[0].strip()
        raise ValueError("No Scene class found.")

    def render_manim(self, code: str) -> str:
        class_name = self.extract_class_name(code)
        filename = f"temp_scene_{uuid.uuid4().hex}.py"

        with open(filename, "w") as f:
            f.write(code)

        try:
            result = subprocess.run(
                ["manim", "-ql", filename, class_name], 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            video_path = f"media/videos/{filename.replace('.py', '')}/480p15/{class_name}.mp4"
            if os.path.exists(video_path):
                return video_path
            else:
                raise FileNotFoundError("Video not found.")
        except subprocess.CalledProcessError as e:
            error_msg = f"Manim error: {e.stderr if e.stderr else e.stdout}"
            raise Exception(error_msg)
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    def validate_manim_code(self, code: str) -> bool:
        """Validate if the code contains required Manim imports and structure"""
        required_imports = ['from manim import', 'import manim']
        has_import = any(imp in code for imp in required_imports)
        has_scene_class = 'class' in code and '(Scene)' in code
        has_construct = 'def construct(self)' in code
        
        if not has_import:
            raise ValueError("Code must import manim library")
        if not has_scene_class:
            raise ValueError("Code must contain a Scene class")
        if not has_construct:
            raise ValueError("Scene class must have a construct method")
        
        return True

    def generate_animation(self, prompt: str) -> str:
        raw_code = self.call_llm(prompt)
        cleaned_code = self.clean_code(raw_code)
        fixed_code = self.fix_code(cleaned_code)
        
        # Validate the code structure
        self.validate_manim_code(fixed_code)
        
        video_path = self.render_manim(fixed_code)
        return video_path