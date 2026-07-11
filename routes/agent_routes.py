from flask import Blueprint, request, redirect
from sqlalchemy import select

from database import SessionLocal
from models.agent import Agent

agent_bp = Blueprint("agent", __name__)


@agent_bp.route("/agents")
def index():

    db = SessionLocal()

    agents = db.execute(select(Agent)).scalars().all()

    html = """
    <h2>Data Agent</h2>

    <a href="/agents/create">Tambah Agent</a>

    <br><br>

    <table border="1" cellpadding="5">

    <tr>

        <th>ID</th>
        <th>Kode Agent</th>
        <th>Nama Agent</th>
        <th>Aksi</th>

    </tr>
    """

    for a in agents:

        html += f"""
        <tr>

            <td>{a.id}</td>

            <td>{a.kode_agent}</td>

            <td>{a.nama_agent}</td>

            <td>

                <a href="/agents/edit/{a.id}">Edit</a>

                |

                <a href="/agents/delete/{a.id}">Delete</a>

            </td>

        </tr>
        """

    html += "</table>"

    db.close()

    return html


@agent_bp.route("/agents/create")
def create():

    return """
    <h2>Tambah Agent</h2>

    <form method="POST">

        <p>Kode Agent</p>
        <input name="kode_agent">

        <p>Nama Agent</p>
        <input name="nama_agent">

        <br><br>

        <button type="submit">Simpan</button>

    </form>

    <br>

    <a href="/agents">Kembali</a>
    """


@agent_bp.route("/agents/create", methods=["POST"])
def store():

    db = SessionLocal()

    agent = Agent(
        kode_agent=request.form["kode_agent"], nama_agent=request.form["nama_agent"]
    )

    db.add(agent)
    db.commit()

    db.close()

    return redirect("/agents")


@agent_bp.route("/agents/edit/<int:id>")
def edit(id):

    db = SessionLocal()

    agent = db.get(Agent, id)

    db.close()

    return f"""
    <h2>Edit Agent</h2>

    <form method="POST">

        <p>Kode Agent</p>
        <input
            name="kode_agent"
            value="{agent.kode_agent}"
        >

        <p>Nama Agent</p>
        <input
            name="nama_agent"
            value="{agent.nama_agent}"
        >

        <br><br>

        <button type="submit">Update</button>

    </form>

    <br>

    <a href="/agents">Kembali</a>
    """


@agent_bp.route("/agents/edit/<int:id>", methods=["POST"])
def update(id):

    db = SessionLocal()

    agent = db.get(Agent, id)

    agent.kode_agent = request.form["kode_agent"]
    agent.nama_agent = request.form["nama_agent"]

    db.commit()
    db.close()

    return redirect("/agents")


@agent_bp.route("/agents/delete/<int:id>")
def delete(id):

    db = SessionLocal()

    agent = db.get(Agent, id)

    db.delete(agent)

    db.commit()
    db.close()

    return redirect("/agents")
