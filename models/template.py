from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Template(Base):

    __tablename__ = "templates"

    id = Column(Integer, primary_key=True)

    agent_id = Column(Integer)

    template_name = Column(String(100))

    is_active = Column(Boolean)