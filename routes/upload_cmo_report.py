from flask import Blueprint, request, render_template, redirect, flash, send_from_directory
import os
from datetime import datetime

from config import Config
from database import SessionLocal
from models.upload_cmo_report import UploadCmoReport


upload_cmo_report_bp = Blueprint(
    "upload_cmo_report",
    __name__
)


# =========================================================
# LIST DATA LAPORAN CMO
# =========================================================

@upload_cmo_report_bp.route("/upload-cmo-report")
def index():

    db = SessionLocal()

    reports = (
        db.query(UploadCmoReport)
        .order_by(UploadCmoReport.id.desc())
        .all()
    )

    db.close()

    return render_template(
        "upload_cmo_report/index.html",
        reports=reports
    )


# =========================================================
# UPLOAD LAPORAN CMO
# =========================================================

@upload_cmo_report_bp.route(
    "/upload-cmo-report/upload",
    methods=["POST"]
)
def upload():

    file = request.files.get("file")

    if not file or file.filename == "":
        flash(
            "File Excel wajib dipilih.",
            "danger"
        )

        return redirect("/upload-cmo-report")


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

        return redirect("/upload-cmo-report")


    # =====================================================
    # FOLDER UPLOAD
    # =====================================================

    upload_folder = os.path.join(
        Config.UPLOAD_FOLDER,
        "cmo_reports"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )


    # =====================================================
    # BUAT NAMA FILE UNIK
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

    nama_cmo = request.form.get("nama_cmo")

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

    report = UploadCmoReport(

        kode_agent=kode_agent,

        nama_cmo=nama_cmo,

        periode=periode_date,

        file_name=filename,

        file_path=filepath
    )

    db.add(report)

    db.commit()

    db.close()


    flash(
        "Laporan CMO berhasil diupload.",
        "success"
    )

    return redirect("/upload-cmo-report")


# =========================================================
# DOWNLOAD FILE
# =========================================================

@upload_cmo_report_bp.route(
    "/upload-cmo-report/download/<int:id>"
)
def download(id):

    db = SessionLocal()

    report = (
        db.query(UploadCmoReport)
        .filter_by(id=id)
        .first()
    )

    db.close()


    if not report:

        flash(
            "Data laporan tidak ditemukan.",
            "danger"
        )

        return redirect("/upload-cmo-report")


    if not os.path.exists(report.file_path):

        flash(
            "File tidak ditemukan.",
            "danger"
        )

        return redirect("/upload-cmo-report")


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
# DELETE LAPORAN
# =========================================================

@upload_cmo_report_bp.route(
    "/upload-cmo-report/delete/<int:id>",
    methods=["POST"]
)
def delete(id):

    db = SessionLocal()

    report = (
        db.query(UploadCmoReport)
        .filter_by(id=id)
        .first()
    )


    if not report:

        db.close()

        flash(
            "Data laporan tidak ditemukan.",
            "danger"
        )

        return redirect("/upload-cmo-report")


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
        "Laporan CMO berhasil dihapus.",
        "success"
    )

    return redirect("/upload-cmo-report")