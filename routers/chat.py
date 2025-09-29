from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from chat import chat
from .auth import get_current_user
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]



router = APIRouter(
    prefix='/chat',
    tags=['chat']
)

class Message(BaseModel):
    message: str = Field(..., example="Hello, how are you?")


@router.post("/chat", status_code=status.HTTP_200_OK, response_model=dict)
async def chat_with_ai(message: Message, 
                       user: user_dependency):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user',
            headers={'WWW-Authenticate': 'Bearer'}
        )
        
    return {
        "reply" : chat(user['username'], message.message)
        }