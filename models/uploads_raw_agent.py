from sqlalchemy import Column, BigInteger, String, Date, DateTime, Text
from datetime import datetime

from database import Base


class UploadsRawAgent(Base):

    __tablename__ = "uploads_raw_agent"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    kode_agent = Column(
        String(100),
        nullable=True
    )

    nama = Column(
        String(255),
        nullable=True
    )

    periode = Column(
        Date,
        nullable=True
    )

    jenis_data = Column(
        String(30),
        nullable=False
    )

    file_name = Column(
        String(255),
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=False
    )

    status = Column(
        String(30),
        default="uploaded"
    )

    error_message = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )