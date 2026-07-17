from flask import Blueprint, request, render_template, redirect, flash
import os

from config import Config
from database import SessionLocal
from models.agent import Agent
from services.normalize.stock.factory import StockNormalizeFactory
from models.stock_template import StockTemplate
from models.stock_template_mapping import StockTemplateMapping

stock_mapping_bp = Blueprint("stock_mapping", __name__)

STANDARD_HEADERS = [
    "Kode SKU Agen",
    "QTY (Pcs)"
]

@stock_mapping_bp.route("/stock-mapping")
def index():

    db = SessionLocal()

    templates = (
        db.query(StockTemplate, Agent)
        .join(Agent, StockTemplate.agent_id == Agent.id)
        .all()
    )

    db.close()

    return render_template(
        "stock_mapping/list.html",
        templates=templates
    )

@stock_mapping_bp.route("/stock-mapping/create")
def create():

    return render_template("stock_mapping/upload.html")

# @stock_mapping_bp.route("/mapping")
# def index():

#     return render_template("mapping/upload.html")

@stock_mapping_bp.route("/stock-mapping/upload", methods=["POST"])
def upload():

    file = request.files["file"]

    filename = file.filename

    filepath = os.path.join(
        Config.UPLOAD_FOLDER,
        filename
    )

    file.save(filepath)

    kode_agent = request.form["kode_agent"]

    normalizer = StockNormalizeFactory.get(kode_agent)

    df = normalizer.normalize(filepath)

    headers = list(df.columns)

    db = SessionLocal()

    agents = db.query(Agent).all()

    db.close()

    return render_template(
    "stock_mapping/index.html",
    headers=headers,
    standard_headers=STANDARD_HEADERS,
    agents=agents
)

@stock_mapping_bp.route("/stock-mapping/save", methods=["POST"])
def save():

    db = SessionLocal()

    # Ambil agent yang dipilih
    agent_id = request.form.get("agent_id")

    # Buat template baru
    template_name = request.form.get("template_name")

    template = StockTemplate(
        agent_id=agent_id,
        template_name=template_name,
        is_active=True
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    # Simpan mapping
    for standard_header, excel_header in request.form.items():

        # Jangan simpan agent_id ke template_mappings
        if standard_header in ["agent_id", "template_name"]:
            continue

        # Lewati jika tidak dipilih
        if excel_header == "":
            continue

        mapping = StockTemplateMapping(
            template_id=template.id,
            standard_header=standard_header,
            excel_header=excel_header
        )

        db.add(mapping)

    db.commit()
    db.close()

    return redirect("/stock-mapping")

@stock_mapping_bp.route("/stock-mapping/delete/<int:id>", methods=["POST"])
def delete(id):

    db = SessionLocal()

    # Hapus semua mapping
    db.query(StockTemplateMapping)\
      .filter_by(template_id=id)\
      .delete()

    # Hapus template
    db.query(StockTemplate)\
      .filter_by(id=id)\
      .delete()

    db.commit()

    db.close()

    return redirect("/stock-mapping")

@stock_mapping_bp.route("/stock-mapping/edit/<int:id>")
def edit(id):

    db = SessionLocal()

    template = db.query(StockTemplate).filter_by(id=id).first()

    agents = db.query(Agent).all()

    mappings = (
        db.query(StockTemplateMapping)
        .filter_by(template_id=id)
        .all()
    )

    db.close()

    return render_template(
        "stock_mapping/edit_upload.html",
        template=template,
        agents=agents,
        mappings=mappings,
        standard_headers=STANDARD_HEADERS
    )

@stock_mapping_bp.route("/stock-mapping/edit/<int:id>/upload", methods=["POST"])
def edit_upload(id):

    file = request.files["file"]

    filename = file.filename

    filepath = os.path.join(
        Config.UPLOAD_FOLDER,
        filename
    )

    file.save(filepath)

    db = SessionLocal()

    template = db.query(StockTemplate).filter_by(id=id).first()

    agent = db.query(Agent).filter_by(id=template.agent_id).first()

    kode_agent = agent.kode_agent

    normalizer = StockNormalizeFactory.get(kode_agent)

    df = normalizer.normalize(filepath)

    headers = list(df.columns)

    db = SessionLocal()

    template = db.query(StockTemplate).filter_by(id=id).first()

    agents = db.query(Agent).all()

    mappings = db.query(StockTemplateMapping)\
                 .filter_by(template_id=id)\
                 .all()
    
    mapping_dict = {}

    for m in mappings:

        mapping_dict[m.standard_header] = m.excel_header

    db.close()

    return render_template(
        "stock_mapping/edit.html",
        template=template,
        agents=agents,
        headers=headers,
        standard_headers=STANDARD_HEADERS,
        mapping_dict=mapping_dict
    )

@stock_mapping_bp.route("/stock-mapping/update/<int:id>", methods=["POST"])
def update(id):

    db = SessionLocal()

    # ==========================
    # Update Template
    # ==========================

    template = db.query(StockTemplate).filter_by(id=id).first()

    template.template_name = request.form.get("template_name")

    template.agent_id = request.form.get("agent_id")

    db.commit()

    # ==========================
    # Hapus Mapping Lama
    # ==========================

    db.query(StockTemplateMapping)\
      .filter_by(template_id=id)\
      .delete()

    db.commit()

    # ==========================
    # Simpan Mapping Baru
    # ==========================

    for standard_header, excel_header in request.form.items():

        # Skip field yang bukan mapping
        if standard_header in ["template_name", "agent_id"]:
            continue

        # Skip jika kosong
        if excel_header == "":
            continue

        mapping = StockTemplateMapping(

            template_id=id,

            standard_header=standard_header,

            excel_header=excel_header

        )

        db.add(mapping)

    db.commit()
    
    flash("Mapping berhasil diperbarui.", "success")

    db.close()

    return redirect("/stock-mapping")