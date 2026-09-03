from sqlalchemy import Column, BigInteger, String, Date, DateTime
from datetime import datetime

from database import Base


class UploadCmoReport(Base):

    __tablename__ = "uploads_cmo_reports"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    kode_agent = Column(
        String(100),
        nullable=True
    )

    nama_cmo = Column(
        String(255),
        nullable=True
    )

    periode = Column(
        Date,
        nullable=True
    )

    file_name = Column(
        String(255),
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=False
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