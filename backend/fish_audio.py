from fastapi import APIRouter, HTTPException, Response
from fish_audio_sdk import Session
import requests
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import dotenv
import os
from datetime import datetime
dotenv.load_dotenv()

router = APIRouter(prefix="/api/fish-audio")

# 初始化 Fish Audio SDK
token = os.getenv("FISH_AUDIO_API_KEY")
session = Session(os.getenv("FISH_AUDIO_API_KEY"))


class Sample(BaseModel):
    title: str
    text: str
    task_id: str
    audio: str

class Author(BaseModel):
    _id: str
    nickname: str
    avatar: str

class Model(BaseModel):
    _id: str
    type: str
    title: str
    description: str
    cover_image: str
    train_mode: str
    state: str
    tags: List[str]
    samples: List[Sample]
    created_at: datetime
    updated_at: datetime
    languages: List[str]
    visibility: str
    lock_visibility: bool
    like_count: int
    mark_count: int
    shared_count: int
    task_count: int
    unliked: bool
    liked: bool
    marked: bool
    author: Author

# 定義查詢model列表所返回的結構
class ModelResponse(BaseModel):
    total: int
    items: List[Model]



@router.get("/models", response_model=ModelResponse)
async def list_models(
    page_size: int = 5,
    page_number: int = 1,
    sort_by: Optional[str] = "score",
    title: Optional[str] = None
):
    url = "https://api.fish.audio/model"


    querystring = {"title":title,"page_size":page_size,"page_number":page_number,"sort_by":sort_by}

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()






@router.post("/preview")
async def preview_speech(text: str, model_id: str):
    try:
        # 限制預覽文字長度
        preview_text = text[:100]
        
        # 生成音訊
        audio_chunks = []
        async for chunk in session.tts.awaitable({
            "text": preview_text,
            "model_id": model_id
        }):
            audio_chunks.append(chunk)
            
        # 組合音訊數據
        audio_data = b''.join(audio_chunks)
        
        return Response(
            content=audio_data,
            media_type="audio/mp3",
            headers={
                "Content-Disposition": "attachment; filename=preview.mp3"
            }
        )
    except Exception as e:
        print(f"Error in preview_speech: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate preview: {str(e)}"
        )


# @router.post("/synthesize")
# async def synthesize_speech(text: str, model_id: str):
#     try:
#         # 生成音訊
#         audio_chunks = []
#         async for chunk in session.tts.awaitable({
#             "text": text,
#             "model_id": model_id
#         }):
#             audio_chunks.append(chunk)
            
#         # 組合音訊數據
#         audio_data = b''.join(audio_chunks)
        
#         return Response(
#             content=audio_data,
#             media_type="audio/mp3",
#             headers={
#                 "Content-Disposition": "attachment; filename=speech.mp3"
#             }
#         )
#     except Exception as e:
#         print(f"Error in synthesize_speech: {str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to synthesize speech: {str(e)}"
#         ) 
