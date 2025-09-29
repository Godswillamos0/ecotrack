from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import re
from dotenv import load_dotenv
import os

load_dotenv()


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

bcrypt_context = CryptContext(
    schemes=["bcrypt", "argon2"],  # fallback to argon2 for longer passwords
    deprecated="auto",
)
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]


token_blacklist = set()

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    if token in token_blacklist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please log in again."
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user"
            )
        return {"username": username, "id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user"
        )
        
        
class CreateUserRequest(BaseModel):
    username:str = Field(min_length=3, max_length=15)
    email: str 
    password:str
    

class Token(BaseModel):
    access_token:str
    token_type:str
    
    
@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    create_user_model = Users(
        email = create_user_request.email,
        username =  create_user_request.username,
        hashed_password = bcrypt_context.hash(create_user_request.password)
    )
    
    db.add(create_user_model)
    db.commit()
    return {"message": "User created successfully", "user_id": create_user_model.id}


@router.post('/token',response_model=Token, status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
        
    access_token = create_access_token(
        username=user.username, 
        user_id=user.id, 
        expires_delta =timedelta(minutes=45)
    )
    
    ##access_token = jwt.encode({'sub': user.username, 'id': user.id}, SECRET_KEY, algorithm=ALGORITHM)
    return {'access_token': access_token, 'token_type': 'bearer'}



def create_access_token(username:str, 
                        user_id: int, 
                        expires_delta: timedelta):
    encode = {
        'sub': username,
        'id': user_id
    }
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
        

def authenticate_user(username_or_email: str, password: str, db: Session):
    # Check if the input is an email
    is_email = re.match(r"[^@]+@[^@]+\.[^@]+", username_or_email)

    if is_email:
        user = db.query(Users).filter(Users.email == username_or_email).first()
    else:
        user = db.query(Users).filter(Users.username == username_or_email).first()

    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return False

    return user


@router.post('/logout', status_code=status.HTTP_200_OK)
async def delete_access_token_to_logout(user: Annotated[dict, Depends(get_current_user)]):
    user.get
    return {'message': 'Successfully logged out'}
