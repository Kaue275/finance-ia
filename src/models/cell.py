from typing import List, Optional
from sqlalchemy import ForeignKey, Column, Integer, String, Float, func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import Uuid
from src.database import Base

class Cell(Base):
    __tablename__ = "cell"

    id = Mapped[Uuid] = mapped_column(as_uuid=True, primary_key=True)
    value = Mapped[float] = mapped_column(Float, nullable=False)
    created_at = mapped_column(server_default=func.now(), nullable=False)
    updated_at = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    sheet_id: Mapped[Uuid] = mapped_column(ForeignKey("sheet.id"))