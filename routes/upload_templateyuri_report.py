from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    flash,
    send_from_directory
)

import os
from datetime import datetime

from config import Config
from database import SessionLocal
from models.upload_yuri_report import UploadTemplateYuriReport


upload_template_yuri_bp = Blueprint(
    "upload_template_yuri",
    __name__
)


# =========================================================
# LIST DATA TEMPLATE YURI
# =========================================================

# @upload_template_yuri_bp.route("/upload-template-yuri")
# def index():

#     db = SessionLocal()

#     reports = (
#         db.query(UploadTemplateYuriReport)
#         .order_by(UploadTemplateYuriReport.id.desc())
#         .all()
#     )

#     db.close()

#     return render_template(
#         "upload_template_yuri/index.html",
#         reports=reports
#     )
@upload_template_yuri_bp.route("/upload-template-yuri")
def index():

    db = SessionLocal()

    # ==============================
    # PAGINATION
    # ==============================

    page = request.args.get(
        "page",
        1,
        type=int
    )

    per_page = 10

    query = (
        db.query(UploadTemplateYuriReport)
        .order_by(
            UploadTemplateYuriReport.id.desc()
        )
    )

    total = query.count()

    reports = (
        query
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    total_pages = (
        (total + per_page - 1)
        // per_page
    )

    db.close()

    return render_template(
        "upload_template_yuri/index.html",
        reports=reports,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages
    )


# =========================================================
# UPLOAD TEMPLATE YURI
# =========================================================

@upload_template_yuri_bp.route(
    "/upload-template-yuri/upload",
    methods=["POST"]
)
def upload():

    file = request.files.get("file")

    if not file or file.filename == "":
        flash(
            "File Excel wajib dipilih.",
            "danger"
        )

        return redirect("/upload-template-yuri")


    # =====================================================
    # VALIDASI FILE
    # =====================================================

    filename = file.filename

    allowed_extensions = [".xls", ".xlsx"]

    extension = os.path.splitext(filename)[1].lower()

    if extension not in allowed_extensions:

        flash(
            "File harus berformat XLS atau XLSX.",
            "danger"
        )

        return redirect("/upload-template-yuri")


    # =====================================================
    # FOLDER UPLOAD
    # =====================================================

    upload_folder = os.path.join(
        Config.UPLOAD_FOLDER,
        "template_yuri"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )


    # =====================================================
    # NAMA FILE
    # =====================================================

    name, ext = os.path.splitext(filename)

    filename = f"{name}{ext}"

    filepath = os.path.join(
        upload_folder,
        filename
    )


    # =====================================================
    # SIMPAN FILE
    # =====================================================

    file.save(filepath)


    # =====================================================
    # AMBIL FORM
    # =====================================================

    kode_agent = request.form.get("kode_agent")

    nama = request.form.get("nama")

    periode = request.form.get("periode")


    # =====================================================
    # KONVERSI PERIODE
    # =====================================================

    periode_date = None

    if periode:

        try:

            periode_date = datetime.strptime(
                periode,
                "%Y-%m"
            ).date()

        except ValueError:

            periode_date = None


    # =====================================================
    # SIMPAN DATABASE
    # =====================================================

    db = SessionLocal()

    report = UploadTemplateYuriReport(

        kode_agent=kode_agent,

        nama=nama,

        periode=periode_date,

        file_name=filename,

        file_path=filepath
    )

    db.add(report)

    db.commit()

    db.close()


    flash(
        "Template Yuri berhasil diupload.",
        "success"
    )

    return redirect("/upload-template-yuri")


# =========================================================
# DOWNLOAD FILE
# =========================================================

@upload_template_yuri_bp.route(
    "/upload-template-yuri/download/<int:id>"
)
def download(id):

    db = SessionLocal()

    report = (
        db.query(UploadTemplateYuriReport)
        .filter_by(id=id)
        .first()
    )

    db.close()


    if not report:

        flash(
            "Template tidak ditemukan.",
            "danger"
        )

        return redirect("/upload-template-yuri")


    if not os.path.exists(report.file_path):

        flash(
            "File tidak ditemukan.",
            "danger"
        )

        return redirect("/upload-template-yuri")


    directory = os.path.dirname(
        report.file_path
    )

    filename = os.path.basename(
        report.file_path
    )


    return send_from_directory(
        directory,
        filename,
        as_attachment=True
    )


# =========================================================
# DELETE TEMPLATE
# =========================================================

@upload_template_yuri_bp.route(
    "/upload-template-yuri/delete/<int:id>",
    methods=["POST"]
)
def delete(id):

    db = SessionLocal()

    report = (
        db.query(UploadTemplateYuriReport)
        .filter_by(id=id)
        .first()
    )


    if not report:

        db.close()

        flash(
            "Template tidak ditemukan.",
            "danger"
        )

        return redirect("/upload-template-yuri")


    # =====================================================
    # HAPUS FILE FISIK
    # =====================================================

    if report.file_path:

        if os.path.exists(report.file_path):

            os.remove(report.file_path)


    # =====================================================
    # HAPUS DATABASE
    # =====================================================

    db.delete(report)

    db.commit()

    db.close()


    flash(
        "Template Yuri berhasil dihapus.",
        "success"
    )

    return redirect("/upload-template-yuri")