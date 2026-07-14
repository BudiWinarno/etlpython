from sqlalchemy import Column, Integer, String
from database import Base

class StockTemplateMapping(Base):

    __tablename__ = "stock_template_mappings"

    id = Column(Integer, primary_key=True)

    template_id = Column(Integer)

    standard_header = Column(String(255))

    excel_header = Column(String(255))