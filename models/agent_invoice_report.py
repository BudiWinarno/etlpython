from sqlalchemy import Column,Integer,String,Numeric,Date,DateTime
from sqlalchemy.sql import func

from database import Base


class AgentInvoiceReport(Base):

    __tablename__ = "agent_invoice_reports_baru"

    id = Column(Integer, primary_key=True)

    agent_id = Column(Integer)

    bulan = Column(Integer)

    tahun = Column(Integer)

    nama_agen = Column(String)

    kode_customer = Column(String)

    nama_customer = Column(String)

    alamat_customer = Column(String)

    nomor_telepon_customer = Column(String)

    invoice_nomor_agen = Column(String)

    tanggal_invoice = Column(Date)

    tipe_customer = Column(String)

    sales = Column(String)

    kode_sku_agent = Column(String)

    nama_sku = Column(String)

    qty_terjual_karton = Column(Numeric)

    qty_terjual_pcs = Column(Numeric)

    diskon_1_reguler = Column(Numeric)

    diskon_2_cash = Column(Numeric)

    diskon_3_dc_fee = Column(Numeric)

    diskon_4_promo_1 = Column(Numeric)

    diskon_5_promo_2 = Column(Numeric)

    diskon_6_rp = Column(Numeric)

    quantity_bonus = Column(Numeric)

    rafraksi = Column(Numeric)

    total_invoice_value = Column(Numeric)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )