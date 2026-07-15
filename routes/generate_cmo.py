from flask import Blueprint
from flask import render_template
from flask import request

from database import SessionLocal
from models.agent import Agent
from models.agent_stock_report import AgentStockReport
import os
import pandas as pd
from flask import send_file
from config import Config


generate_cmo_bp = Blueprint(
    "generate_cmo",
    __name__
)


# ==========================
# Halaman Generate CMO
# ==========================

@generate_cmo_bp.route("/generate-cmo")
def index():

    db = SessionLocal()

    agents = (
        db.query(Agent)
        .order_by(Agent.kode_agent)
        .all()
    )

    db.close()

    return render_template(
        "generate_cmo/index.html",
        agents=agents
    )


# ==========================
# Generate CMO
# ==========================

@generate_cmo_bp.route(
    "/generate-cmo",
    methods=["POST"]
)
def generate():

    db = SessionLocal()

    agent_id = int(request.form["agent_id"])
    bulan = int(request.form["bulan"])
    tahun = int(request.form["tahun"])

    # Ambil data agent
    agent = (
        db.query(Agent)
        .filter(Agent.id == agent_id)
        .first()
    )

    # Bulan stock = bulan sebelumnya
    if bulan == 1:
        stock_bulan = 12
        stock_tahun = tahun - 1
    else:
        stock_bulan = bulan - 1
        stock_tahun = tahun

    stock = (
        db.query(AgentStockReport)
        .filter(
            AgentStockReport.agent_id == agent_id,
            AgentStockReport.bulan == stock_bulan,
            AgentStockReport.tahun == stock_tahun
        )
        .order_by(AgentStockReport.id)
        .all()
    )
    
    sheet_stock = pd.DataFrame([
    {
        "Kode SKU JIM": item.kode_sku_jim,
        "Nama SKU JIM": item.nama_sku_jim,
        "Qty Karton": item.qty_karton
    }
    for item in stock
])

    # Nama file
    output = os.path.join(
        Config.OUTPUT_FOLDER,
        f"CMO_{agent.kode_agent}_{tahun}{bulan:02d}.xlsx"
    )

    # Export Excel
    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        sheet_stock.to_excel(
            writer,
            sheet_name="CMO",
            index=False
        )

    db.close()

    return send_file(
        output,
        as_attachment=True
    )