from flask import Blueprint, request, send_file, render_template
import os

from config import Config
from services.normalize.factory import NormalizeFactory

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload")
def upload_form():

    return render_template("normalize/index.html")


@upload_bp.route("/upload", methods=["POST"])
def upload():

    file = request.files["file"]

    filename = file.filename

    filepath = os.path.join(
        Config.UPLOAD_FOLDER,
        filename
    )

    file.save(filepath)

    # sementara hanya support LK-000019
    kode_agent = request.form["kode_agent"]

    normalizer = NormalizeFactory.get(kode_agent)

    df = normalizer.normalize(filepath)

    output = os.path.join(
        Config.OUTPUT_FOLDER,
        "hasil_" + filename
    )

    df.to_excel(output, index=False)

    return send_file(
        output,
        as_attachment=True
    )