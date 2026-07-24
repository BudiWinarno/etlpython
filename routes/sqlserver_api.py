from flask import Blueprint, render_template, jsonify, request
import pandas as pd
from sqlalchemy import text
from database_sqlserver import engine_sqlserver
from flask import send_file
from io import BytesIO
from openpyxl import load_workbook

sqlserver_bp = Blueprint("sqlserver", __name__)


@sqlserver_bp.route("/ods-ec-detail")
def ods_ec_detail():
    return render_template("sqlserver/ods_ec_detail.html")


@sqlserver_bp.route("/api/ods-ec-detail")
def api_ods_ec_detail():

    customer_code = request.args.get("customer_code", "").strip()
    month = request.args.get("month", "").strip()
    year = request.args.get("year", "").strip()

    sql = """
    SELECT TOP 100
        [Customer Code],
        [Customer Name],
        [Item Code],
        [Item Name],
        [BULAN_INV],
        [TAHUN_INV],
        [SO Quantity PCS],
        [SO Quantity Karton]
    FROM ODS_EC_DETAIL
    WHERE 1=1
    """

    params = {}

    if customer_code:
        sql += " AND [Customer Code] LIKE :customer_code"
        params["customer_code"] = f"%{customer_code}%"

    if month:
        sql += " AND [BULAN_INV] = :month"
        params["month"] = int(month)

    if year:
        sql += " AND [TAHUN_INV] = :year"
        params["year"] = int(year)

    sql += """
    ORDER BY
        [TAHUN_INV] DESC,
        [BULAN_INV] DESC,
        [Customer Code]
    """

    print(sql)
    print(params)

    df = pd.read_sql(
        text(sql),
        engine_sqlserver,
        params=params
    )

    return jsonify(df.to_dict(orient="records"))

@sqlserver_bp.route("/export-ods-ec-detail")
def export_ods_ec_detail():

    customer_code = request.args.get("customer_code", "").strip()
    month = request.args.get("month", "").strip()
    year = request.args.get("year", "").strip()

    sql = """
    SELECT
        [Customer Code],
        [Customer Name],
        [Item Code],
        [Item Name],
        [BULAN_INV],
        [TAHUN_INV],
        [SO Quantity PCS],
        [SO Quantity Karton]
    FROM ODS_EC_DETAIL
    WHERE 1=1
    """

    params = {}

    if customer_code:
        sql += " AND [Customer Code] LIKE :customer_code"
        params["customer_code"] = f"%{customer_code}%"

    if month:
        sql += " AND [BULAN_INV] = :month"
        params["month"] = int(month)

    if year:
        sql += " AND [TAHUN_INV] = :year"
        params["year"] = int(year)

    sql += """
    ORDER BY
        [TAHUN_INV] DESC,
        [BULAN_INV] DESC,
        [Customer Code],
        [Item Code]
    """

    df = pd.read_sql(
        text(sql),
        engine_sqlserver,
        params=params
    )
    
    df = (
        df.groupby("Item Code", as_index=False)
        .agg({
            "Customer Code": "first",
            "Customer Name": "first",
            "Item Name": "first",
            "BULAN_INV": "first",
            "TAHUN_INV": "first",
            "SO Quantity PCS": "sum",
            "SO Quantity Karton": "sum"
        })
    )

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="ODS EC Detail"
        )

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="ODS EC Detail"
        )

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="ODS_EC_DETAIL.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )