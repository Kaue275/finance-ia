from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from routes.models import model_user

router = APIRouter()

class ResponseUser(BaseModel):
    message: str
    status: int

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

@router.post("/users", response_model=ResponseUser)
def register_user(data: UserCreate, db: Session = Depends(get_db)) -> ResponseUser:
    model_user.create_user(
        db=db, 
        username = data.username, 
        email = data.email, 
        password = data.password
    )

    return ResponseUser(message = "Usuário criado com sucesso", status = 200)