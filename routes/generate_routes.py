from flask import Blueprint, render_template, request, send_file
import os

from config import Config
from database import SessionLocal

from models.template import Template
from models.agent import Agent

from services.generate_service import get_mapping
from services.normalize.factory import NormalizeFactory

from openpyxl import load_workbook
from openpyxl.styles import NamedStyle
from openpyxl.utils import get_column_letter
from models.agent_invoice_report import AgentInvoiceReport
import pandas as pd

generate_bp = Blueprint("generate", __name__)

STANDARD_HEADERS = [
    "Nama Agen",
    "Kode Customer",
    "Nama Customer",
    "Alamat Customer",
    "Nomor Telepon/HP Customer",
    "Invoice Nomor Agen",
    "Tanggal Invoice",
    "Tipe Customer",
    "Sales",
    "SKU Kode Agen",
    "Nama SKU",
    "Qty Terjual (Karton)",
    "Qty Terjual (Pcs)",
    "% Diskon 1 (Reguler)",
    "% Diskon 2 (Cash)",
    "% Diskon 3 (DC Fee)",
    "% Diskon 4 (Promo 1)",
    "% Diskon 5 (Promo 2)",
    "% Diskon 6 (Rp)",
    "Quantity Bonus",
    "Rafraksi",
    "Total Invoice Value"
]


@generate_bp.route("/generate")
def index():

    db = SessionLocal()

    templates = db.query(Template).all()

    db.close()

    return render_template(
        "generate/index.html",
        templates=templates
    )


@generate_bp.route("/generate", methods=["POST"])
def generate():

    db = SessionLocal()

    template_id = int(request.form["template_id"])
    
    bulan = int(request.form["bulan"])

    tahun = int(request.form["tahun"])

    file = request.files["file"]

    filepath = os.path.join(
        Config.UPLOAD_FOLDER,
        file.filename
    )

    file.save(filepath)

    # Baca excel
    # template = db.query(Template).filter_by(id=template_id).first()

    # agent = db.query(Agent).filter_by(id=template.agent_id).first()

    # normalizer = NormalizeFactory.get(agent.kode_agent)

    # df = normalizer.normalize(filepath)
    
    # Ambil template
    template = db.query(Template).filter_by(id=template_id).first()

    # Ambil agent
    agent = db.query(Agent).filter_by(id=template.agent_id).first()

    # File sudah dinormalisasi
    df = pd.read_excel(filepath)

    # Ambil mapping
    mapping = get_mapping(template_id)

    # Ambil hanya kolom yang dimapping
    df = df[list(mapping.keys())]

    # Rename sesuai standard header
    df = df.rename(columns=mapping)

    # Ambil template
    # template = db.query(Template).filter_by(id=template_id).first()

    # Ambil agent
    # agent = db.query(Agent).filter_by(id=template.agent_id).first()
    
    exists = (
    db.query(AgentInvoiceReport)
        .filter(
            AgentInvoiceReport.agent_id == agent.id,
            AgentInvoiceReport.bulan == bulan,
            AgentInvoiceReport.tahun == tahun
        )
        .first()
    )
    
    print(exists)
    
    if exists:

        db.close()

        return "Data bulan dan tahun tersebut sudah ada."

    # Isi Nama Agen
    df["Nama Agen"] = agent.nama_agent

    # Tambahkan kolom yang belum ada
    for col in STANDARD_HEADERS:

        if col not in df.columns:

            df[col] = None

    # Urutkan kolom
    df = df[STANDARD_HEADERS]
    
    # ==========================
    # Insert ke Database
    # ==========================

    for _, row in df.iterrows():

        report = AgentInvoiceReport(

            agent_id=agent.id,

            bulan=bulan,

            tahun=tahun,

            nama_agen=row["Nama Agen"],

            kode_customer=row["Kode Customer"],

            nama_customer=row["Nama Customer"],

            alamat_customer=row["Alamat Customer"],

            nomor_telepon_customer=row["Nomor Telepon/HP Customer"],

            invoice_nomor_agen=row["Invoice Nomor Agen"],

            tanggal_invoice=row["Tanggal Invoice"],

            tipe_customer=row["Tipe Customer"],

            sales=row["Sales"],

            kode_sku_agent=row["SKU Kode Agen"],

            nama_sku=row["Nama SKU"],

            qty_terjual_karton=row["Qty Terjual (Karton)"],

            qty_terjual_pcs=row["Qty Terjual (Pcs)"],

            diskon_1_reguler=row["% Diskon 1 (Reguler)"],

            diskon_2_cash=row["% Diskon 2 (Cash)"],

            diskon_3_dc_fee=row["% Diskon 3 (DC Fee)"],

            diskon_4_promo_1=row["% Diskon 4 (Promo 1)"],

            diskon_5_promo_2=row["% Diskon 5 (Promo 2)"],

            diskon_6_rp=row["% Diskon 6 (Rp)"],

            quantity_bonus=row["Quantity Bonus"],

            rafraksi=row["Rafraksi"],

            total_invoice_value=row["Total Invoice Value"]

        )

        db.add(report)

    db.commit()

    output = os.path.join(
        Config.OUTPUT_FOLDER,
        "Hasil_Generate_Invoice" + file.filename
    )

    df.to_excel(output, index=False)

    # Buka file Excel yang sudah dibuat
    wb = load_workbook(output)
    ws = wb.active

    # Format tanggal
    date_style = NamedStyle(name="date_style")
    date_style.number_format = "mm/dd/yyyy"

    for col in ws.iter_cols():

        for cell in col:

            # Jika nilainya berupa datetime
            if hasattr(cell.value, "year"):
                cell.style = date_style

    # Autofit semua kolom
    for column_cells in ws.columns:

        max_length = 0
        column = get_column_letter(column_cells[0].column)

        for cell in column_cells:

            try:
                if cell.value is not None:
                    max_length = max(max_length, len(str(cell.value)))
            except Exception:
                pass

        ws.column_dimensions[column].width = max_length + 3

    wb.save(output)

    db.close()

    return send_file(
        output,
        as_attachment=True
    )