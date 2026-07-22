from flask import Blueprint, render_template, request,flash, redirect, url_for

from database import SessionLocal
from models.insell_report import InsellReport
from models.agent import Agent
import pandas as pd
from sqlalchemy.orm import joinedload

insell_report_bp = Blueprint(
    "insell_report",
    __name__,
    url_prefix="/insell-reports"
)


@insell_report_bp.route("/")
def index():

    db = SessionLocal()

    page = request.args.get("page", 1, type=int)
    per_page = 10

    query = (
        db.query(InsellReport)
        .options(joinedload(InsellReport.agent))
        .join(Agent)
        .order_by(
            InsellReport.id.desc()
        )
    )

    total = query.count()

    reports = (
        query.offset((page - 1) * per_page)
             .limit(per_page)
             .all()
    )

    db.close()

    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "insell_report/index.html",
        reports=reports,
        page=page,
        total_pages=total_pages
    )

@insell_report_bp.route("/import")
def import_page():

    db = SessionLocal()

    agents = (
        db.query(Agent)
        .order_by(Agent.kode_agent)
        .all()
    )

    db.close()

    return render_template(
        "insell_report/import.html",
        agents=agents
    )


@insell_report_bp.route("/import", methods=["POST"])
def import_store():

    agent_id = int(request.form.get("agent_id"))
    file = request.files.get("file")

    if not file or file.filename == "":
        flash("Silakan pilih file Excel.", "danger")
        return redirect(url_for("insell_report.import_page"))

    df = pd.read_excel(file)

    db = SessionLocal()

    try:

        for _, row in df.iterrows():

            report = InsellReport(
                agent_id=agent_id,
                customer_code=row["Customer Code"],
                customer_name=row["Customer Name"],
                item_code=row["Item Code"],
                item_name=row["Item Name"],
                bulan=int(row["MONTH"]),
                tahun=int(row["YEAR"]),
                so_qty_pcs=float(row["SO Quantity PCS"]),
                so_qty_karton=float(row["SO Quantity Karton"])
            )

            db.add(report)

        db.commit()

        flash(f"Import berhasil. {len(df)} data berhasil disimpan.", "success")

    except Exception as e:

        db.rollback()
        flash(str(e), "danger")

    finally:

        db.close()

    return redirect(url_for("insell_report.index"))