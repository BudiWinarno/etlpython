from flask import Blueprint, request, render_template, redirect, flash, send_from_directory, jsonify
import os
from datetime import datetime

from config import Config
from database import SessionLocal
from models.upload_cmo_report import UploadCmoReport
from sqlalchemy import extract


upload_cmo_report_bp = Blueprint(
    "upload_cmo_report",
    __name__
)


# =========================================================
# LIST DATA LAPORAN CMO
# =========================================================

# @upload_cmo_report_bp.route("/upload-cmo-report")
# def index():

#     db = SessionLocal()

#     reports = (
#         db.query(UploadCmoReport)
#         .order_by(UploadCmoReport.id.desc())
#         .all()
#     )

#     db.close()

#     return render_template(
#         "upload_cmo_report/index.html",
#         reports=reports
#     )

# @upload_cmo_report_bp.route("/upload-cmo-report")
# def index():

#     db = SessionLocal()

#     # ==========================================
#     # PAGINATION
#     # ==========================================

#     page = request.args.get("page", 1, type=int)

#     per_page = 1

#     query = (
#         db.query(UploadCmoReport)
#         .order_by(UploadCmoReport.id.desc())
#     )

#     total = query.count()

#     total_pages = (total + per_page - 1) // per_page

#     reports = (
#         query
#         .offset((page - 1) * per_page)
#         .limit(per_page)
#         .all()
#     )

#     db.close()

#     return render_template(
#         "upload_cmo_report/index.html",
#         reports=reports,
#         page=page,
#         total_pages=total_pages
#     )

@upload_cmo_report_bp.route("/upload-cmo-report")
def index():

    db = SessionLocal()

    page = request.args.get("page", 1, type=int)
    per_page = 10

    search_nama = request.args.get("nama", "").strip()
    search_periode = request.args.get("periode", "").strip()

    query = (
        db.query(UploadCmoReport)
        .order_by(UploadCmoReport.id.desc())
    )

    # ==========================
    # FILTER NAMA
    # ==========================

    if search_nama:
        query = query.filter(
            UploadCmoReport.nama_cmo.ilike(
                f"%{search_nama}%"
            )
        )

    # ==========================
    # FILTER PERIODE
    # ==========================

    if search_periode:
        tahun, bulan = search_periode.split("-")

        query = query.filter(
            extract(
                "year",
                UploadCmoReport.periode
            ) == int(tahun)
        ).filter(
            extract(
                "month",
                UploadCmoReport.periode
            ) == int(bulan)
        )

    # ==========================
    # TOTAL DATA
    # ==========================

    total = query.count()

    total_pages = max(
        1,
        (total + per_page - 1) // per_page
    )

    # ==========================
    # PAGINATION
    # ==========================

    reports = (
        query
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    db.close()

    return render_template(
        "upload_cmo_report/index.html",
        reports=reports,
        page=page,
        total_pages=total_pages,
        search_nama=search_nama,
        search_periode=search_periode
    )
    
@upload_cmo_report_bp.route("/upload-cmo-report/agents")
def get_agents():

    db = SessionLocal()

    agents = (
        db.query(UploadCmoReport.nama_cmo)
        .filter(
            UploadCmoReport.nama_cmo.isnot(None),
            UploadCmoReport.nama_cmo != ""
        )
        .distinct()
        .order_by(UploadCmoReport.nama_cmo.asc())
        .all()
    )

    db.close()

    return jsonify([
        row[0]
        for row in agents
    ])


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