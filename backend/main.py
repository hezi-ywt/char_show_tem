from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from backend.database import Database
from backend.models import Rating
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录，确保路径正确
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# 添加根路由返回index.html
@app.get("/")
async def read_root():
    return FileResponse("frontend/index.html")

db = Database()

@app.get("/api/character")
async def get_character(user_id: str):
    character = await db.get_unrated_character(user_id)
    if not character:
        raise HTTPException(status_code=404, detail="No more characters to rate")
    return character

@app.post("/api/rate")
async def rate_character(rating: Rating):
    try:
        rating_dict = rating.dict()
        result = await db.save_rating(rating_dict)
        return {"status": "success", "id": str(result["inserted_id"])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/character/details")
async def get_character_details(character_id: str):
    character = await db.get_character_details(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character 

@app.get("/api/ratings/{user_id}")
async def get_user_ratings(user_id: str):
    try:
        ratings = await db.get_user_ratings(user_id)
        return ratings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/ratings/{rating_id}")
async def update_rating(rating_id: str, rating: Rating):
    try:
        result = await db.update_rating(rating_id, rating.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

@app.get("/api/character/edit/{user_id}/{character_id}")
async def get_character_for_edit(user_id: str, character_id: str):
    try:
        character = await db.get_character_for_edit(user_id, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character rating not found")
        return character
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

@app.get("/api/ratings/{rating_id}")
async def get_rating(rating_id: str):
    try:
        rating = await db.get_rating(rating_id)
        if not rating:
            raise HTTPException(status_code=404, detail="Rating not found")
        return rating
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 