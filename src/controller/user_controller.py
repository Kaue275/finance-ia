from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from models.users import Users
from exceptions.user_exception import UserError
from database import get_db
from utils.password_hash import PasswordSecurity, InvalidPasswordError
import re
import uuid

class EmailAlreadyExistError(UserError):
    status_code = 409

class EmailReExceptionError(UserError):
    status_code = 422

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)*$"
)

def create_user(db: Session, username: str, email: str, password: str):
    security = PasswordSecurity    

    if not re.match(EMAIL_REGEX, email):
        raise EmailReExceptionError
    
    security.valid_password(password)
    hashed = security.hash_password(password)

    new_user = Users(
        id = uuid.uuid7(),
        username = username,
        email = email,
        password = hashed
    )

    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EmailAlreadyExistError(email)
    db.refresh(new_user)
    return new_user