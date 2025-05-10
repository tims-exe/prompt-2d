from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from contextlib import asynccontextmanager
import subprocess
import shutil
import os
import re
import uuid
import ast
from dotenv import load_dotenv
from manim_generator import call_llm, clean_code, fix_code  # utility functions

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from media directory
app.mount("/media", StaticFiles(directory="media"), name="media")

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("temp", exist_ok=True)
    os.makedirs("media/videos/main/480p15", exist_ok=True)
    yield
    if os.path.exists("temp"):
        shutil.rmtree("temp")

app.lifespan = lifespan

class Prompt(BaseModel):
    prompt: str

def extract_scene_name(code: str) -> str | None:
    match = re.search(r"class\s+(\w+)\s*\(\s*Scene\s*\):", code)
    return match.group(1) if match else None

@app.post("/generate-video")
async def generate_video(prompt: Prompt):
    file_path = None
    video_path = None

    try:
        raw_code = call_llm(prompt.prompt)
        code = clean_code(raw_code)
        code = fix_code(code)

        try:
            ast.parse(code)
        except SyntaxError as e:
            return JSONResponse({"error": f"Syntax error: {e}"}, status_code=400)

        scene_name = extract_scene_name(code)
        if not scene_name:
            return JSONResponse({"error": "Could not extract scene name."}, status_code=400)

        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}.py")
        with open(file_path, "w") as f:
            f.write(code)

        result = subprocess.run(
            ["manim", "-ql", file_path, scene_name],
            capture_output=True, text=True, timeout=120
        )

        if result.returncode != 0:
            return JSONResponse({"error": result.stderr}, status_code=400)

        video_file = f"{scene_name}.mp4"
        video_path = os.path.join("media", "videos", "main", "480p15", video_file)
        if not os.path.exists(video_path):
            return JSONResponse({"error": f"Video not found at {video_path}"}, status_code=500)

        return {
            "videoUrl": f"/media/videos/main/480p15/{video_file}",
            "code": code
        }

    except subprocess.TimeoutExpired:
        return JSONResponse({"error": "Rendering timed out."}, status_code=408)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
