from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Numeric,
    ForeignKey
)

from sqlalchemy.orm import relationship

from database import Base


class ItemAgentMapping(Base):

    __tablename__ = "item_agent_mappings"

    id = Column(Integer, primary_key=True)

    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)

    kode_sku_agent = Column(String(100))

    kode_sku_jim = Column(String(100))

    nama_sku_jim = Column(String(255))

    item_box = Column(Numeric(10, 2))

    item_group = Column(String(100))

    is_active = Column(Boolean)

    # Relationship ke Agent
    agent = relationship("Agent", back_populates="item_mappings")