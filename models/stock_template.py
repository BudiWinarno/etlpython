from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class StockTemplate(Base):

    __tablename__ = "stock_templates"

    id = Column(Integer, primary_key=True)

    agent_id = Column(Integer)

    template_name = Column(String(255))

    is_active = Column(Boolean)