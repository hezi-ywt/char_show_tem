from pydantic import BaseModel
from typing import List, Dict

class ImageSelection(BaseModel):
    filename: str
    type: str

class Rating(BaseModel):
    character_id: str
    selected_images: List[ImageSelection]
    user_id: str 