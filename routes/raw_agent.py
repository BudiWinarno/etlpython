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
from models.uploads_raw_agent import UploadsRawAgent


raw_agent_bp = Blueprint(
    "raw_agent",
    __name__
)


# =========================================================
# LIST DATA RAW AGENT
# =========================================================

@raw_agent_bp.route("/upload-raw-agent")
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
        db.query(UploadsRawAgent)
        .order_by(
            UploadsRawAgent.id.desc()
        )
    )

    total = query.count()

    total_pages = (
        (total + per_page - 1)
        // per_page
    )

    # Pastikan page tidak melebihi total halaman
    if total_pages > 0 and page > total_pages:
        page = total_pages

    if page < 1:
        page = 1

    uploads = (
        query
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    db.close()

    return render_template(
        "raw_agent/index.html",
        uploads=uploads,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages
    )


# =========================================================
# UPLOAD RAW AGENT
# =========================================================

@raw_agent_bp.route(
    "/upload-raw-agent/upload",
    methods=["POST"]
)
def upload():

    # =====================================================
    # AMBIL FILE
    # =====================================================

    file = request.files.get("file")

    if not file or file.filename == "":

        flash(
            "File Excel wajib dipilih.",
            "danger"
        )

        return redirect("/upload-raw-agent")


    # =====================================================
    # VALIDASI FILE
    # =====================================================

    filename = file.filename

    allowed_extensions = [
        ".xls",
        ".xlsx"
    ]

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension not in allowed_extensions:

        flash(
            "File harus berformat XLS atau XLSX.",
            "danger"
        )

        return redirect("/upload-raw-agent")


    # =====================================================
    # AMBIL FORM
    # =====================================================

    kode_agent = request.form.get(
        "kode_agent"
    )

    nama = request.form.get(
        "nama"
    )

    periode = request.form.get(
        "periode"
    )

    jenis_data = request.form.get(
        "jenis_data"
    )


    # =====================================================
    # VALIDASI JENIS DATA
    # =====================================================

    allowed_jenis_data = [
        "SELL_OUT",
        "STOCK"
    ]

    if jenis_data not in allowed_jenis_data:

        flash(
            "Jenis data harus SELL OUT atau STOCK.",
            "danger"
        )

        return redirect("/upload-raw-agent")


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

            flash(
                "Format periode tidak valid.",
                "danger"
            )

            return redirect("/upload-raw-agent")


    # =====================================================
    # FOLDER UPLOAD
    # =====================================================

    upload_folder = os.path.join(
        Config.UPLOAD_FOLDER,
        "raw_agent"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )


    # =====================================================
    # NAMA FILE
    # =====================================================

    name, ext = os.path.splitext(
        filename
    )

    filename = f"{name}{ext}"


    filepath = os.path.join(
        upload_folder,
        filename
    )


    # =====================================================
    # SIMPAN FILE
    # =====================================================

    try:

        file.save(filepath)

    except Exception as e:

        flash(
            f"Gagal menyimpan file: {str(e)}",
            "danger"
        )

        return redirect("/upload-raw-agent")


    # =====================================================
    # SIMPAN DATABASE
    # =====================================================

    db = SessionLocal()

    try:

        report = UploadsRawAgent(

            kode_agent=kode_agent,

            nama=nama,

            periode=periode_date,

            jenis_data=jenis_data,

            file_name=filename,

            file_path=filepath,

            status="uploaded",

            error_message=None
        )

        db.add(report)

        db.commit()

    except Exception as e:

        db.rollback()

        # Hapus file jika database gagal
        if os.path.exists(filepath):

            os.remove(filepath)

        flash(
            f"Gagal menyimpan data: {str(e)}",
            "danger"
        )

        db.close()

        return redirect("/upload-raw-agent")

    finally:

        db.close()


    # =====================================================
    # SUCCESS
    # =====================================================

    flash(
        "Laporan Raw Agent berhasil diupload.",
        "success"
    )

    return redirect("/upload-raw-agent")


# =========================================================
# DOWNLOAD FILE
# =========================================================

@raw_agent_bp.route(
    "/upload-raw-agent/download/<int:id>"
)
def download(id):

    db = SessionLocal()

    report = (
        db.query(UploadsRawAgent)
        .filter_by(id=id)
        .first()
    )

    db.close()


    # =====================================================
    # DATA TIDAK DITEMUKAN
    # =====================================================

    if not report:

        flash(
            "Laporan Raw Agent tidak ditemukan.",
            "danger"
        )

        return redirect("/upload-raw-agent")


    # =====================================================
    # FILE TIDAK DITEMUKAN
    # =====================================================

    if not report.file_path:

        flash(
            "Path file tidak tersedia.",
            "danger"
        )

        return redirect("/upload-raw-agent")


    if not os.path.exists(
        report.file_path
    ):

        flash(
            "File tidak ditemukan di server.",
            "danger"
        )

        return redirect("/upload-raw-agent")


    # =====================================================
    # DOWNLOAD
    # =====================================================

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
# DELETE RAW AGENT
# =========================================================

@raw_agent_bp.route(
    "/upload-raw-agent/delete/<int:id>",
    methods=["POST"]
)
def delete(id):

    db = SessionLocal()

    report = (
        db.query(UploadsRawAgent)
        .filter_by(id=id)
        .first()
    )


    # =====================================================
    # DATA TIDAK DITEMUKAN
    # =====================================================

    if not report:

        db.close()

        flash(
            "Laporan Raw Agent tidak ditemukan.",
            "danger"
        )

        return redirect("/upload-raw-agent")


    # =====================================================
    # HAPUS FILE FISIK
    # =====================================================

    if report.file_path:

        if os.path.exists(
            report.file_path
        ):

            try:

                os.remove(
                    report.file_path
                )

            except Exception as e:

                db.close()

                flash(
                    f"Gagal menghapus file: {str(e)}",
                    "danger"
                )

                return redirect(
                    "/upload-raw-agent"
                )


    # =====================================================
    # HAPUS DATABASE
    # =====================================================

    try:

        db.delete(report)

        db.commit()

    except Exception as e:

        db.rollback()

        db.close()

        flash(
            f"Gagal menghapus data: {str(e)}",
            "danger"
        )

        return redirect(
            "/upload-raw-agent"
        )


    db.close()


    # =====================================================
    # SUCCESS
    # =====================================================

    flash(
        "Laporan Raw Agent berhasil dihapus.",
        "success"
    )

    return redirect(
        "/upload-raw-agent"
    )
    
@raw_agent_bp.route("/upload-raw-agent/agent-search")
def agent_search():

    search = request.args.get(
        "q",
        "",
        type=str
    ).strip()

    if not search:
        return {
            "data": []
        }

    db = SessionLocal()

    try:

        search_pattern = f"%{search}%"

        results = (
            db.query(UploadsRawAgent.kode_agent, UploadsRawAgent.nama)
            .filter(
                (UploadsRawAgent.kode_agent.ilike(search_pattern)) |
                (UploadsRawAgent.nama.ilike(search_pattern))
            )
            .distinct()
            .order_by(
                UploadsRawAgent.nama.asc()
            )
            .limit(10)
            .all()
        )

        return {
            "data": [
                {
                    "kode_agent": row.kode_agent,
                    "nama": row.nama
                }
                for row in results
            ]
        }

    finally:

        db.close()