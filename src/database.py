from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()



class Base(DeclarativeBase):
    pass

engine = create_engine(os.getenv("DATABASE_URL"), echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 