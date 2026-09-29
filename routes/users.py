from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from werkzeug.security import generate_password_hash

from database import SessionLocal
from models.user import User


user_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/dashboard/users"
)


# =========================================================
# DAFTAR USER
# URL: /dashboard/users/
# =========================================================

@user_bp.route("/")
def index():

    db = SessionLocal()

    try:

        users = (
            db.query(User)
            .order_by(User.id.desc())
            .all()
        )

        return render_template(
            "users/index.html",
            users=users
        )

    finally:

        db.close()


# =========================================================
# TAMBAH USER
# URL: /dashboard/users/create
# =========================================================

@user_bp.route("/create", methods=["GET", "POST"])
def create():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        role = request.form.get(
            "role",
            "user"
        ).strip()


        # ---------------------------------------------
        # VALIDASI
        # ---------------------------------------------

        if not name:

            flash(
                "Nama wajib diisi.",
                "danger"
            )

            return redirect(
                url_for("users.create")
            )


        if not email:

            flash(
                "Email wajib diisi.",
                "danger"
            )

            return redirect(
                url_for("users.create")
            )


        if not password:

            flash(
                "Password wajib diisi.",
                "danger"
            )

            return redirect(
                url_for("users.create")
            )


        # Pastikan role valid

        if role not in ["admin", "user"]:

            role = "user"


        db = SessionLocal()

        try:

            # -----------------------------------------
            # CEK EMAIL
            # -----------------------------------------

            existing_user = (
                db.query(User)
                .filter(
                    User.email == email
                )
                .first()
            )


            if existing_user:

                flash(
                    "Email sudah digunakan.",
                    "danger"
                )

                return redirect(
                    url_for("users.create")
                )


            # -----------------------------------------
            # BUAT USER
            # -----------------------------------------

            user = User(

                name=name,

                email=email,

                password=generate_password_hash(
                    password
                ),

                role=role

            )


            db.add(user)

            db.commit()


            flash(
                "User berhasil ditambahkan.",
                "success"
            )

            return redirect(
                url_for("users.index")
            )

        except Exception as e:

            db.rollback()

            flash(
                f"Gagal menambahkan user: {e}",
                "danger"
            )

            return redirect(
                url_for("users.create")
            )

        finally:

            db.close()


    return render_template(
        "users/create.html"
    )


# =========================================================
# EDIT USER
# URL: /dashboard/users/edit/<id>
# =========================================================

@user_bp.route(
    "/edit/<int:id>",
    methods=["GET", "POST"]
)
def edit(id):

    db = SessionLocal()

    try:

        # ---------------------------------------------
        # CARI USER
        # ---------------------------------------------

        user = (
            db.query(User)
            .filter(
                User.id == id
            )
            .first()
        )


        if not user:

            flash(
                "User tidak ditemukan.",
                "danger"
            )

            return redirect(
                url_for("users.index")
            )


        # ---------------------------------------------
        # PROSES UPDATE
        # ---------------------------------------------

        if request.method == "POST":

            name = request.form.get(
                "name",
                ""
            ).strip()

            email = request.form.get(
                "email",
                ""
            ).strip()

            password = request.form.get(
                "password",
                ""
            )

            role = request.form.get(
                "role",
                "user"
            ).strip()


            # -----------------------------------------
            # VALIDASI
            # -----------------------------------------

            if not name:

                flash(
                    "Nama wajib diisi.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "users.edit",
                        id=id
                    )
                )


            if not email:

                flash(
                    "Email wajib diisi.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "users.edit",
                        id=id
                    )
                )


            if role not in ["admin", "user"]:

                role = "user"


            # -----------------------------------------
            # CEK EMAIL DUPLIKAT
            # -----------------------------------------

            existing_user = (
                db.query(User)
                .filter(
                    User.email == email,
                    User.id != id
                )
                .first()
            )


            if existing_user:

                flash(
                    "Email sudah digunakan user lain.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "users.edit",
                        id=id
                    )
                )


            # -----------------------------------------
            # UPDATE DATA
            # -----------------------------------------

            user.name = name

            user.email = email

            user.role = role


            # Password hanya diubah
            # kalau field diisi

            if password:

                user.password = (
                    generate_password_hash(
                        password
                    )
                )


            db.commit()


            flash(
                "User berhasil diperbarui.",
                "success"
            )

            return redirect(
                url_for("users.index")
            )


        # GET
        # tampilkan form edit

        return render_template(
            "users/edit.html",
            user=user
        )


    except Exception as e:

        db.rollback()

        flash(
            f"Gagal memperbarui user: {e}",
            "danger"
        )

        return redirect(
            url_for("users.index")
        )


    finally:

        db.close()


# =========================================================
# DELETE USER
# URL: /dashboard/users/delete/<id>
# =========================================================

@user_bp.route(
    "/delete/<int:id>",
    methods=["POST"]
)
def delete(id):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.id == id
            )
            .first()
        )


        if not user:

            flash(
                "User tidak ditemukan.",
                "danger"
            )

            return redirect(
                url_for("users.index")
            )


        # ---------------------------------------------
        # HAPUS USER
        # ---------------------------------------------

        db.delete(user)

        db.commit()


        flash(
            "User berhasil dihapus.",
            "success"
        )


        return redirect(
            url_for("users.index")
        )


    except Exception as e:

        db.rollback()

        flash(
            f"Gagal menghapus user: {e}",
            "danger"
        )

        return redirect(
            url_for("users.index")
        )


    finally:

        db.close()