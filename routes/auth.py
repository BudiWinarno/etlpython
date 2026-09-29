from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import check_password_hash

from database import SessionLocal
from models.user import User


auth_bp = Blueprint(
    "auth",
    __name__
)


# =========================================================
# LOGIN
# =========================================================

@auth_bp.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        print("EMAIL LOGIN:", email)


        db = SessionLocal()

        try:

            # Cari user berdasarkan email
            user = (
                db.query(User)
                .filter(
                    User.email == email
                )
                .first()
            )


            # =============================================
            # USER TIDAK DITEMUKAN
            # =============================================

            if not user:

                print("USER TIDAK DITEMUKAN")

                flash(
                    "Email atau password salah.",
                    "error"
                )

                return render_template(
                    "login.html"
                )


            # =============================================
            # CEK PASSWORD
            # =============================================

            if not check_password_hash(
                user.password,
                password
            ):

                print("PASSWORD SALAH")

                flash(
                    "Email atau password salah.",
                    "error"
                )

                return render_template(
                    "login.html"
                )


            # =============================================
            # LOGIN BERHASIL
            # =============================================

            print(
                "LOGIN BERHASIL:",
                user.email
            )


            session["logged_in"] = True

            session["user_id"] = user.id

            session["user_email"] = user.email

            session["user_name"] = user.name

            session["user_role"] = user.role


            return redirect(
                "/dashboard"
            )


        finally:

            db.close()


    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("auth.login")
    )

# from flask import Blueprint, render_template, request, redirect, url_for, flash, session

# auth_bp = Blueprint("auth", __name__)


# @auth_bp.route("/", methods=["GET", "POST"])
# def login():

#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("password")

#         # print("EMAIL:", email)
#         # print("PASSWORD:", password)

#         if email == "developeryuri2@gmail.com" and password == "qwertyuiop1":
#             print("LOGIN BERHASIL")

#             session["logged_in"] = True
#             session["user_email"] = email

#             return redirect("/dashboard")
        
#         elif email == "admin@gmail.com" and password == "admin1234#":
#             print("LOGIN BERHASIL")

#             session["logged_in"] = True
#             session["user_email"] = email

#             return redirect("/dashboard")

#         print("LOGIN GAGAL")
#         flash("Email atau password salah.", "error")

#     return render_template("login.html")

# @auth_bp.route("/logout")
# def logout():
#     session.clear()
#     return redirect(url_for("auth.login"))