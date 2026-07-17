from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from database import Base


class CMOTemplate(Base):
    __tablename__ = "cmo_templates"

    id = Column(Integer, primary_key=True, index=True)

    agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
        nullable=False
    )

    item_code = Column(String(100), nullable=False)
    item_name = Column(String(255), nullable=False)
    item_group_name = Column(String(255))
    customer_name = Column(String(255))

    berat = Column(Numeric(10, 2))
    volume = Column(Numeric(10, 4))
    item_box = Column(Numeric(10, 2))

    buffer_hari = Column(Integer, default=45)

    nka_1 = Column(Numeric(10, 2))
    nka_2 = Column(Numeric(10, 2))
    nka_3 = Column(Numeric(10, 2))
    nka_4 = Column(Numeric(10, 2))

    min_stock = Column(Numeric(10, 2))
    min_stock_nka_1 = Column(Numeric(10, 2))
    min_stock_nka_2 = Column(Numeric(10, 2))

    order_tambahan = Column(Numeric(10, 2))

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship(
        "Agent",
        back_populates="cmo_templates"
    )