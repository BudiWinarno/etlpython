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
from models.agent_invoice_report import AgentInvoiceReport
import math


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


@generate_cmo_bp.route(
    "/generate-cmo",
    methods=["POST"]
)
def generate():

    db = SessionLocal()

    agent_id = int(request.form["agent_id"])
    bulan = int(request.form["bulan"])
    tahun = int(request.form["tahun"])

    # ==========================
    # Ambil Data Agent
    # ==========================

    agent = (
        db.query(Agent)
        .filter(Agent.id == agent_id)
        .first()
    )

    # ==========================
    # Bulan Sebelumnya
    # ==========================

    if bulan == 1:
        stock_bulan = 12
        stock_tahun = tahun - 1
    else:
        stock_bulan = bulan - 1
        stock_tahun = tahun

   # ==========================
    # STOCK
    # ==========================

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

    # ==========================
    # OUTSELL (1 BULAN)
    # ==========================

    outsell = (
        db.query(AgentInvoiceReport)
        .filter(
            AgentInvoiceReport.agent_id == agent_id,
            AgentInvoiceReport.bulan == stock_bulan,
            AgentInvoiceReport.tahun == stock_tahun
        )
        .all()
    )

    sheet_outsell = pd.DataFrame([
        {
            "Kode SKU JIM": item.kode_sku_jim,
            "Nama SKU JIM": item.nama_sku_jim,
            "Qty PCS": item.qty_terjual_pcs,
            "Item Box": item.item_box
        }
        for item in outsell
    ])

    if not sheet_outsell.empty:

        sheet_outsell = (
            sheet_outsell
            .groupby(
                [
                    "Kode SKU JIM",
                    "Nama SKU JIM"
                ],
                as_index=False
            )
            .agg({
                "Qty PCS": "sum",
                "Item Box": "first"
            })
        )

        sheet_outsell["Qty Karton"] = (
            sheet_outsell["Qty PCS"].astype(float) /
            sheet_outsell["Item Box"].astype(float)
        ).apply(lambda x: math.floor(x + 0.5))

        sheet_outsell = sheet_outsell[
            [
                "Kode SKU JIM",
                "Nama SKU JIM",
                "Qty Karton"
            ]
        ]

    else:

        sheet_outsell = pd.DataFrame(
            columns=[
                "Kode SKU JIM",
                "Nama SKU JIM",
                "Qty Karton"
            ]
        )

    # ==========================
    # AVG OUTSELL (3 BULAN)
    # ==========================

    avg_rows = []

    for i in range(1, 4):

        avg_bulan = bulan - i
        avg_tahun = tahun

        if avg_bulan <= 0:
            avg_bulan += 12
            avg_tahun -= 1

        data = (
            db.query(AgentInvoiceReport)
            .filter(
                AgentInvoiceReport.agent_id == agent_id,
                AgentInvoiceReport.bulan == avg_bulan,
                AgentInvoiceReport.tahun == avg_tahun
            )
            .all()
        )

        avg_rows.extend(data)

    sheet_avg_outsell = pd.DataFrame([
        {
            "Kode SKU JIM": item.kode_sku_jim,
            "Nama SKU JIM": item.nama_sku_jim,
            "Qty Karton": item.qty_karton
        }
        for item in avg_rows
    ])

    if not sheet_avg_outsell.empty:

        sheet_avg_outsell = (
            sheet_avg_outsell
            .groupby(
                [
                    "Kode SKU JIM",
                    "Nama SKU JIM"
                ],
                as_index=False
            )
            .agg({
                "Qty Karton": "sum"
            })
        )

        sheet_avg_outsell["Avg Qty Outsell Karton"] = (
            sheet_avg_outsell["Qty Karton"]
                .apply(lambda x: math.floor(float(x) / 3 + 0.5))
        )

        sheet_avg_outsell = sheet_avg_outsell[
            [
                "Kode SKU JIM",
                "Nama SKU JIM",
                "Avg Qty Outsell Karton"
            ]
        ]

    else:

        sheet_avg_outsell = pd.DataFrame(
            columns=[
                "Kode SKU JIM",
                "Nama SKU JIM",
                "Avg Qty Outsell Karton"
            ]
        )

    # ==========================
    # EXPORT EXCEL
    # ==========================

    output = os.path.join(
        Config.OUTPUT_FOLDER,
        f"CMO_{agent.kode_agent}_{tahun}{bulan:02d}.xlsx"
    )

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        sheet_stock.to_excel(
            writer,
            sheet_name="Stock",
            index=False
        )

        sheet_outsell.to_excel(
            writer,
            sheet_name="Outsell",
            index=False
        )

        sheet_avg_outsell.to_excel(
            writer,
            sheet_name="Avg Outsell",
            index=False
        )

    db.close()

    return send_file(
        output,
        as_attachment=True
    )