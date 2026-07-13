from flask import Blueprint, request, send_file, render_template
import os

from config import Config
from services.normalize.stock.factory import StockNormalizeFactory

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

    df = normalizer.normalize(filepath)

    output = os.path.join(
        Config.OUTPUT_FOLDER,
        "hasil_stock_" + filename
    )

    df.to_excel(output, index=False)

    return send_file(
        output,
        as_attachment=True
    )