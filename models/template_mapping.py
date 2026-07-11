from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class TemplateMapping(Base):

    __tablename__ = "template_mappings"

    id = Column(Integer, primary_key=True)

    template_id = Column(Integer, ForeignKey("templates.id"))

    standard_header = Column(String(100))

    excel_header = Column(String(150))