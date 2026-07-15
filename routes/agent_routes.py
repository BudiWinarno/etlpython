from flask import Blueprint, request, redirect, render_template
from sqlalchemy import select

from database import SessionLocal
from models.agent import Agent

agent_bp = Blueprint("agent", __name__)


# ==========================
# List Agent
# ==========================
@agent_bp.route("/agents")
def index():

    db = SessionLocal()

    agents = db.execute(
        select(Agent)
    ).scalars().all()

    db.close()

    return render_template(
        "agents/index.html",
        agents=agents
    )


# ==========================
# Form Tambah
# ==========================
@agent_bp.route("/agents/create")
def create():

    return render_template("agents/create.html")


# ==========================
# Simpan Agent
# ==========================
@agent_bp.route("/agents/create", methods=["POST"])
def store():

    db = SessionLocal()

    agent = Agent(
        kode_agent=request.form["kode_agent"],
        nama_agent=request.form["nama_agent"]
    )

    db.add(agent)
    db.commit()

    db.close()

    return redirect("/agents")


# ==========================
# Form Edit
# ==========================
@agent_bp.route("/agents/edit/<int:id>")
def edit(id):

    db = SessionLocal()

    agent = db.get(Agent, id)

    db.close()

    return render_template(
        "agents/edit.html",
        agent=agent
    )


# ==========================
# Update Agent
# ==========================
@agent_bp.route("/agents/edit/<int:id>", methods=["POST"])
def update(id):

    db = SessionLocal()

    agent = db.get(Agent, id)

    agent.kode_agent = request.form["kode_agent"]
    agent.nama_agent = request.form["nama_agent"]

    db.commit()

    db.close()

    return redirect("/agents")


# ==========================
# Delete Agent
# ==========================
@agent_bp.route("/agents/delete/<int:id>")
def delete(id):

    db = SessionLocal()

    agent = db.get(Agent, id)

    db.delete(agent)

    db.commit()

    db.close()

    return redirect("/agents")