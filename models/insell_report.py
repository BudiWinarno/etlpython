from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class InsellReport(Base):
    __tablename__ = "insell_reports"

    id = Column(Integer, primary_key=True, index=True)

    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)

    customer_code = Column(String(30), nullable=False)
    customer_name = Column(String(255), nullable=False)

    item_code = Column(String(50), nullable=False)
    item_name = Column(String, nullable=False)

    bulan = Column(Integer, nullable=False)
    tahun = Column(Integer, nullable=False)

    so_qty_pcs = Column(Numeric(18, 2), default=0)
    so_qty_karton = Column(Numeric(18, 2), default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    agent = relationship("Agent")