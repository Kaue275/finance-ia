from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.users import Users
from database import get_db
import uuid

def create_user(db: Session, username: str, email: str, password: str) -> Users:
    new_user = Users(
        id = uuid.uuid7(),
        username = username,
        email = email,
        password = password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user