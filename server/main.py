from fastapi import FastAPI
from api import register_routes

app = FastAPI(title="Manim Animation Server", version="1.0.0")

register_routes(app)