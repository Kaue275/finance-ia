from typing import List, Optional
from sqlalchemy import ForeignKey, Column, Integer, String, Float, func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import Uuid
from src.database import Base

class Users(Base):
    __tablename__ = "users"

    id = Mapped[Uuid] = mapped_column(as_uuid=True, primary_key=True)
    username = mapped_column(String(50), nullable=False)
    email = mapped_column(String(100), unique=True, nullable=False)
    password = mapped_column(String(100), nullable=False)
