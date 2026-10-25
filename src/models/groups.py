from typing import List, Optional
from sqlalchemy import ForeignKey, Column, Integer, String, Float, func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import Uuid
from database import Base
import uuid

class Groups(Base):
    __tablename__ = "groups"

    id: Mapped[uuid.UUID] = mapped_column(as_uuid=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    created_at = mapped_column(server_default=func.now(), nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))