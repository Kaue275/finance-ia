from typing import List, Optional
from sqlalchemy import ForeignKey, Column, Integer, String, Float, func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
import uuid
from database import Base

class Sheet(Base):
    __tablename__ = "sheet"

    id: Mapped[uuid.UUID] = mapped_column(as_uuid=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at = mapped_column(server_default=func.now(), nullable=False)

    group_id: Mapped[uuid.uuid7] = mapped_column(ForeignKey("groups.id"))