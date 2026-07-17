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
from models.cmo_template import CMOTemplate


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
    # CMO TEMPLATE
    # ==========================

    templates = (
        db.query(CMOTemplate)
        .filter(
            CMOTemplate.agent_id == agent_id,
            CMOTemplate.is_active == True
        )
        .all()
    )
    
    sheet_template = pd.DataFrame([
        {
            "Kode SKU JIM": item.item_code,
            "Nama SKU JIM": item.item_name,
            "Item Group": item.item_group_name,
            "Customer Name": item.customer_name,
            "Berat (kg)": item.berat,
            "Volume (m3)": item.volume,
            "Item Box": item.item_box,
            "Buffer (Hari)": item.buffer_hari,
            "NKA 1": item.nka_1,
            "NKA 2": item.nka_2,
            "NKA 3": item.nka_3,
            "NKA 4": item.nka_4,
            "Min Stock": item.min_stock,
            "Min Stock NKA 1": item.min_stock_nka_1,
            "Min Stock NKA 2": item.min_stock_nka_2,
            "Order Tambahan": item.order_tambahan
        }
        for item in templates
    ])
    
    # ==========================
    # MERGE STOCK
    # ==========================

    sheet_cmo = sheet_template.merge(
        sheet_stock[
            [
                "Kode SKU JIM",
                "Qty Karton"
            ]
        ],
        on="Kode SKU JIM",
        how="left"
    )
    
    sheet_cmo["Qty Karton"] = (
        sheet_cmo["Qty Karton"]
        .fillna(0)
    )
    
    # ==========================
    # MERGE OUTSELL
    # ==========================

    sheet_cmo = sheet_cmo.merge(
        sheet_outsell[
            [
                "Kode SKU JIM",
                "Qty Karton"
            ]
        ].rename(
            columns={
                "Qty Karton": "Outsell Karton"
            }
        ),
        on="Kode SKU JIM",
        how="left"
    )

    sheet_cmo["Outsell Karton"] = (
        sheet_cmo["Outsell Karton"]
        .fillna(0)
    )
    
    # ==========================
    # MERGE AVG OUTSELL
    # ==========================

    sheet_cmo = sheet_cmo.merge(
        sheet_avg_outsell[
            [
                "Kode SKU JIM",
                "Avg Qty Outsell Karton"
            ]
        ],
        on="Kode SKU JIM",
        how="left"
    )

    sheet_cmo["Avg Qty Outsell Karton"] = (
        sheet_cmo["Avg Qty Outsell Karton"]
        .fillna(0)
    )
    
    # sheet_template = pd.DataFrame([
    #     {
    #         "Kode SKU JIM": t.item_code,
    #         "Nama SKU JIM": t.item_name,
    #         "Buffer": t.buffer_hari,
    #         "Berat": t.berat,
    #         "Volume": t.volume,
    #         "Item Box": t.item_box,
    #         "Order Tambahan": t.order_tambahan
    #     }
    #     for t in templates
    # ])

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
        
        sheet_template.to_excel(
            writer,
            sheet_name="CMO Template",
            index=False
        )
        
        sheet_cmo.to_excel(
            writer,
            sheet_name="CMO + Stock",
            index=False
        )

    db.close()

    return send_file(
        output,
        as_attachment=True
    )