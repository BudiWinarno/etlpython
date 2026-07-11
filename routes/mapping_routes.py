from flask import Blueprint, request, render_template, redirect
import os

from config import Config
from database import SessionLocal
from models.template_mapping import TemplateMapping
from models.agent import Agent
from models.template import Template
from services.normalize.factory import NormalizeFactory

mapping_bp = Blueprint("mapping", __name__)

STANDARD_HEADERS = [
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

@mapping_bp.route("/mapping")
def index():

    db = SessionLocal()

    templates = (
        db.query(Template, Agent)
        .join(Agent, Template.agent_id == Agent.id)
        .all()
    )

    db.close()

    return render_template(
        "mapping/list.html",
        templates=templates
    )

@mapping_bp.route("/mapping/create")
def create():

    return render_template("mapping/upload.html")

# @mapping_bp.route("/mapping")
# def index():

#     return render_template("mapping/upload.html")

@mapping_bp.route("/mapping/upload", methods=["POST"])
def upload():

    file = request.files["file"]

    filename = file.filename

    filepath = os.path.join(
        Config.UPLOAD_FOLDER,
        filename
    )

    file.save(filepath)

    kode_agent = request.form["kode_agent"]

    normalizer = NormalizeFactory.get(kode_agent)

    df = normalizer.normalize(filepath)

    headers = list(df.columns)

    db = SessionLocal()

    agents = db.query(Agent).all()

    db.close()

    return render_template(
    "mapping/index.html",
    headers=headers,
    standard_headers=STANDARD_HEADERS,
    agents=agents
)

@mapping_bp.route("/mapping/save", methods=["POST"])
def save():

    db = SessionLocal()

    # Ambil agent yang dipilih
    agent_id = request.form.get("agent_id")

    # Buat template baru
    template_name = request.form.get("template_name")

    template = Template(
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

        mapping = TemplateMapping(
            template_id=template.id,
            standard_header=standard_header,
            excel_header=excel_header
        )

        db.add(mapping)

    db.commit()
    db.close()

    return redirect("/mapping")

@mapping_bp.route("/mapping/delete/<int:id>", methods=["POST"])
def delete(id):

    db = SessionLocal()

    # Hapus semua mapping
    db.query(TemplateMapping)\
      .filter_by(template_id=id)\
      .delete()

    # Hapus template
    db.query(Template)\
      .filter_by(id=id)\
      .delete()

    db.commit()

    db.close()

    return redirect("/mapping")

@mapping_bp.route("/mapping/edit/<int:id>")
def edit(id):

    db = SessionLocal()

    template = db.query(Template).filter_by(id=id).first()

    agents = db.query(Agent).all()

    mappings = (
        db.query(TemplateMapping)
        .filter_by(template_id=id)
        .all()
    )

    db.close()

    return render_template(
        "mapping/edit_upload.html",
        template=template,
        agents=agents,
        mappings=mappings,
        standard_headers=STANDARD_HEADERS
    )

@mapping_bp.route("/mapping/edit/<int:id>/upload", methods=["POST"])
def edit_upload(id):

    file = request.files["file"]

    filename = file.filename

    filepath = os.path.join(
        Config.UPLOAD_FOLDER,
        filename
    )

    file.save(filepath)

    df = normalize_lk000019(filepath)

    headers = list(df.columns)

    db = SessionLocal()

    template = db.query(Template).filter_by(id=id).first()

    agents = db.query(Agent).all()

    mappings = db.query(TemplateMapping)\
                 .filter_by(template_id=id)\
                 .all()
    
    mapping_dict = {}

    for m in mappings:

        mapping_dict[m.standard_header] = m.excel_header

    db.close()

    return render_template(
        "mapping/edit.html",
        template=template,
        agents=agents,
        headers=headers,
        standard_headers=STANDARD_HEADERS,
        mapping_dict=mapping_dict
    )

@mapping_bp.route("/mapping/update/<int:id>", methods=["POST"])
def update(id):

    db = SessionLocal()

    # ==========================
    # Update Template
    # ==========================

    template = db.query(Template).filter_by(id=id).first()

    template.template_name = request.form.get("template_name")

    template.agent_id = request.form.get("agent_id")

    db.commit()

    # ==========================
    # Hapus Mapping Lama
    # ==========================

    db.query(TemplateMapping)\
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

        mapping = TemplateMapping(

            template_id=id,

            standard_header=standard_header,

            excel_header=excel_header

        )

        db.add(mapping)

    db.commit()

    db.close()

    return redirect("/mapping")