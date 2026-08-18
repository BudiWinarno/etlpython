from flask import Blueprint, request, send_file, render_template
import os

from config import Config
from services.normalize.stock.factory import StockNormalizeFactory
from database import SessionLocal
from models.agent import Agent

stock_bp = Blueprint("stock", __name__)


@stock_bp.route("/upload")
def upload_form():

    return render_template("stock/index.html")


@stock_bp.route("/upload", methods=["POST"])
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
    
    # LK-000010 membutuhkan agent_id
    if kode_agent == "LK-000010":

        db = SessionLocal()

        try:
            agent = (
                db.query(Agent)
                .filter(
                    Agent.kode_agent == kode_agent
                )
                .first()
            )

            if not agent:
                raise Exception(
                    f"Agent {kode_agent} tidak ditemukan."
                )

            agent_id = agent.id

        finally:
            db.close()

        df = normalizer.normalize(
            filepath,
            agent_id
        )

    else:

        df = normalizer.normalize(filepath)

    output = os.path.join(
        Config.OUTPUT_FOLDER,
        "Hasil_Normalisasi_Stock_" + filename
    )

    df.to_excel(output, index=False)

    return send_file(
        output,
        as_attachment=True
    )