from fastapi import FastAPI
from video_generator.controller import router as video_generator_router

def register_routes(app: FastAPI):
    app.include_router(video_generator_router)