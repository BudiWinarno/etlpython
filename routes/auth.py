from flask import Blueprint, render_template, request, redirect, url_for, flash, session

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        print("EMAIL:", email)
        print("PASSWORD:", password)

        if email == "developeryuri2@gmail.com" and password == "qwertyuiop1":
            print("LOGIN BERHASIL")

            session["logged_in"] = True
            session["user_email"] = email

            return redirect("/dashboard")

        print("LOGIN GAGAL")
        flash("Email atau password salah.", "error")

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))