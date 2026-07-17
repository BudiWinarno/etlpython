from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

import pandas as pd
from sqlalchemy.orm import joinedload

from database import SessionLocal
from models.agent import Agent
from models.cmo_template import CMOTemplate


cmo_template_bp = Blueprint(
    "cmo_template",
    __name__
)


@cmo_template_bp.route("/cmo-template")
def index():

    db = SessionLocal()

    agents = (
        db.query(Agent)
        .order_by(Agent.kode_agent)
        .all()
    )

    agent_id = request.args.get("agent_id", type=int)
    item_code = request.args.get("item_code", "")
    page = request.args.get("page", 1, type=int)

    query = (
        db.query(CMOTemplate)
        .options(joinedload(CMOTemplate.agent))
        .filter(CMOTemplate.is_active == True)
    )

    if agent_id is not None:
        query = query.filter(
            CMOTemplate.agent_id == agent_id
        )

    if item_code:
        query = query.filter(
            CMOTemplate.item_code.ilike(f"%{item_code}%")
        )

    per_page = 10

    total = query.count()

    templates = (
        query.order_by(CMOTemplate.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    db.close()

    return render_template(
        "cmo_template/index.html",
        templates=templates,
        agents=agents,
        selected_agent=agent_id,
        selected_item_code=item_code,
        page=page,
        per_page=per_page,
        total=total
    )


@cmo_template_bp.route("/cmo-template/create")
def create():

    db = SessionLocal()

    agents = (
        db.query(Agent)
        .order_by(Agent.kode_agent)
        .all()
    )

    db.close()

    return render_template(
        "cmo_template/create.html",
        agents=agents
    )


@cmo_template_bp.route(
    "/cmo-template/store",
    methods=["POST"]
)
def store():

    db = SessionLocal()

    template = CMOTemplate(

        agent_id=request.form["agent_id"],

        item_code=request.form["item_code"],
        item_name=request.form["item_name"],
        item_group_name=request.form["item_group_name"],
        customer_name=request.form["customer_name"],

        berat=request.form["berat"],
        volume=request.form["volume"],
        item_box=request.form["item_box"],

        buffer_hari=request.form["buffer_hari"],

        nka_1=request.form["nka_1"],
        nka_2=request.form["nka_2"],
        nka_3=request.form["nka_3"],
        nka_4=request.form["nka_4"],

        min_stock=request.form["min_stock"],
        min_stock_nka_1=request.form["min_stock_nka_1"],
        min_stock_nka_2=request.form["min_stock_nka_2"],

        order_tambahan=request.form["order_tambahan"],

        is_active=True
    )

    db.add(template)
    db.commit()

    flash(
        "CMO Template berhasil ditambahkan.",
        "success"
    )

    db.close()

    return redirect(
        url_for("cmo_template.index")
    )


@cmo_template_bp.route("/cmo-template/edit/<int:id>")
def edit(id):

    db = SessionLocal()

    template = (
        db.query(CMOTemplate)
        .filter(CMOTemplate.id == id)
        .first()
    )

    agents = (
        db.query(Agent)
        .order_by(Agent.kode_agent)
        .all()
    )

    db.close()

    return render_template(
        "cmo_template/edit.html",
        template=template,
        agents=agents
    )


@cmo_template_bp.route(
    "/cmo-template/update/<int:id>",
    methods=["POST"]
)
def update(id):

    db = SessionLocal()

    template = (
        db.query(CMOTemplate)
        .filter(CMOTemplate.id == id)
        .first()
    )

    template.agent_id = request.form["agent_id"]

    template.item_code = request.form["item_code"]
    template.item_name = request.form["item_name"]
    template.item_group_name = request.form["item_group_name"]
    template.customer_name = request.form["customer_name"]

    template.berat = request.form["berat"]
    template.volume = request.form["volume"]
    template.item_box = request.form["item_box"]

    template.buffer_hari = request.form["buffer_hari"]

    template.nka_1 = request.form["nka_1"]
    template.nka_2 = request.form["nka_2"]
    template.nka_3 = request.form["nka_3"]
    template.nka_4 = request.form["nka_4"]

    template.min_stock = request.form["min_stock"]
    template.min_stock_nka_1 = request.form["min_stock_nka_1"]
    template.min_stock_nka_2 = request.form["min_stock_nka_2"]

    template.order_tambahan = request.form["order_tambahan"]

    db.commit()

    flash(
        "CMO Template berhasil diperbarui.",
        "success"
    )

    db.close()

    return redirect(
        url_for("cmo_template.index")
    )


@cmo_template_bp.route("/cmo-template/delete/<int:id>")
def delete(id):

    db = SessionLocal()

    template = (
        db.query(CMOTemplate)
        .filter(CMOTemplate.id == id)
        .first()
    )

    template.is_active = False

    db.commit()

    flash(
        "CMO Template berhasil dihapus.",
        "success"
    )

    db.close()

    return redirect(
        url_for("cmo_template.index")
    )


@cmo_template_bp.route("/cmo-template/import")
def import_form():

    db = SessionLocal()

    agents = (
        db.query(Agent)
        .order_by(Agent.kode_agent)
        .all()
    )

    db.close()

    return render_template(
        "cmo_template/import.html",
        agents=agents
    )


@cmo_template_bp.route(
    "/cmo-template/import",
    methods=["POST"]
)
def import_excel():

    db = SessionLocal()

    try:

        file = request.files["file"]

        agent_id = int(request.form["agent_id"])

        df = pd.read_excel(file)

        for _, row in df.iterrows():

            item_code = str(row["item_code"]).strip()

            template = (
                db.query(CMOTemplate)
                .filter(
                    CMOTemplate.agent_id == agent_id,
                    CMOTemplate.item_code == item_code
                )
                .first()
            )

            if template:

                template.item_name = str(row["item_name"]).strip()
                template.item_group_name = str(row["item_group_name"]).strip()
                template.customer_name = str(row["customer_name"]).strip()

                template.berat = row["berat"]
                template.volume = row["volume"]
                template.item_box = row["item_box"]

                template.buffer_hari = row["buffer_hari"]

                template.nka_1 = row["nka_1"]
                template.nka_2 = row["nka_2"]
                template.nka_3 = row["nka_3"]
                template.nka_4 = row["nka_4"]

                template.min_stock = row["min_stock"]
                template.min_stock_nka_1 = row["min_stock_nka_1"]
                template.min_stock_nka_2 = row["min_stock_nka_2"]

                template.order_tambahan = row["order_tambahan"]

                template.is_active = True

            else:

                template = CMOTemplate(

                    agent_id=agent_id,

                    item_code=item_code,
                    item_name=str(row["item_name"]).strip(),
                    item_group_name=str(row["item_group_name"]).strip(),
                    customer_name=str(row["customer_name"]).strip(),

                    berat=row["berat"],
                    volume=row["volume"],
                    item_box=row["item_box"],

                    buffer_hari=row["buffer_hari"],

                    nka_1=row["nka_1"],
                    nka_2=row["nka_2"],
                    nka_3=row["nka_3"],
                    nka_4=row["nka_4"],

                    min_stock=row["min_stock"],
                    min_stock_nka_1=row["min_stock_nka_1"],
                    min_stock_nka_2=row["min_stock_nka_2"],

                    order_tambahan=row["order_tambahan"],

                    is_active=True
                )

                db.add(template)

        db.commit()

        flash(
            "Import CMO Template berhasil.",
            "success"
        )

        return redirect(
            url_for("cmo_template.index")
        )

    except Exception as e:

        db.rollback()

        return str(e)

    finally:

        db.close()