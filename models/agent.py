from sqlalchemy import Column, Integer, String
from database import Base


class Agent(Base):

    __tablename__ = "agents"

    id = Column(Integer, primary_key=True)

    kode_agent = Column(String(50), unique=True)

    nama_agent = Column(String(200))