from pydantic import BaseModel

class AnimationRequest(BaseModel):
    prompt: str

class AnimationResponse(BaseModel):
    success: bool 
    video_path : str = None
    error : str = None