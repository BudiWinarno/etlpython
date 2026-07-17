from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base

class Agent(Base):

    __tablename__ = "agents"

    id = Column(Integer, primary_key=True)

    kode_agent = Column(String(100))

    nama_agent = Column(String(255))

    item_mappings = relationship(
        "ItemAgentMapping",
        back_populates="agent"
    )
    
    cmo_templates = relationship(
        "CMOTemplate",
        back_populates="agent"
    )