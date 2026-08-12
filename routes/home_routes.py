from flask import Blueprint, render_template, redirect, url_for, session

home_bp = Blueprint("home", __name__)

# DASHBOARD BARU
@home_bp.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    return render_template("home_baru.html")


# DASHBOARD LAMA
@home_bp.route("/dashboard_lama")
def dashboard_lama():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    return render_template("home.html")