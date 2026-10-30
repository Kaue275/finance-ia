from sqlalchemy import select
from sqlalchemy.orm import Session
from models .users import Users

def search_user_from_email(db: Session, email: str):
    user = select(Users.id).where(Users.email == email)
    return db.scalars(user)
