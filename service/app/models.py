from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Float, Text

from .db import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    endpoint: Mapped[str] = mapped_column(String(64), default="/forward", nullable=False)
    mode: Mapped[str] = mapped_column(String(32), default="unknown", nullable=False)

    input_type: Mapped[str] = mapped_column(String(16), default="unknown", nullable=False)
    prompt_len: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    image_w: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    image_h: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, default=200, nullable=False)

    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
