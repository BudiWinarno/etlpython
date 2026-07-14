from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Numeric
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from database import Base


class AgentStockReport(Base):

    __tablename__ = "agent_stock_reports_baru"

    id = Column(Integer, primary_key=True, index=True)

    agent_id = Column(Integer, nullable=False)

    bulan = Column(Integer, nullable=False)

    tahun = Column(Integer, nullable=False)

    kode = Column(String(100))

    kode_sku_agent = Column(String(100))

    kode_sku_jim = Column(String(100))

    nama_sku_jim = Column(Text)

    qty_pcs = Column(Numeric(18, 2))

    item_box = Column(Numeric(18, 2))

    qty_karton = Column(Numeric(18, 2))

    created_at = Column(
        DateTime,
        server_default=func.now()
    )