from pydantic import BaseModel
from typing import List, Dict, Optional

class ImageSelection(BaseModel):
    filename: str
    type: str

class Rating(BaseModel):
    character_id: str
    selected_images: Optional[List[ImageSelection]] = []
    user_id: str
    is_skipped: bool = False 