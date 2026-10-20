from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

class Base(DeclarativeBase):
    pass

engine = create_engine(os.getenv("DATABASE_URL"), echo=True)

Base.metadata.create_all(engine)