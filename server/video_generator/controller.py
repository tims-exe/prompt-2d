from fastapi import APIRouter, HTTPException
from .model import AnimationRequest, AnimationResponse
from .services import ManimService

router = APIRouter()
manim_service = ManimService()

@router.post("/generate-animation", response_model = AnimationResponse)
async def generate_animation(request : AnimationRequest):
    try:
        video_path = manim_service.generate_animation(request.prompt)
        return AnimationResponse(success=True, video_path=video_path)
    except Exception as e:
        return AnimationResponse(success=False, error=str(e))

@router.get("/health")
async def health_check():
    return {"status" : "healthy"}