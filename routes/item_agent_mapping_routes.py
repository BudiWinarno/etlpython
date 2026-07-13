from flask import Blueprint, render_template

from database import SessionLocal
from models.item_agent_mapping import ItemAgentMapping

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)

from database import SessionLocal
from models.item_agent_mapping import ItemAgentMapping
from models.agent import Agent

item_agent_mapping_bp = Blueprint(
    "item_agent_mapping",
    __name__
)


@item_agent_mapping_bp.route("/item-agent-mapping")
def index():

    db = SessionLocal()

    mappings = (
        db.query(ItemAgentMapping)
        .filter(ItemAgentMapping.is_active == True)
        .all()
    )

    db.close()

    return render_template(
        "item_agent_mapping/index.html",
        mappings=mappings
    )

@item_agent_mapping_bp.route("/item-agent-mapping/create")
def create():

    db = SessionLocal()

    agents = (
        db.query(Agent)
        .order_by(Agent.kode_agent)
        .all()
    )

    db.close()

    return render_template(
        "item_agent_mapping/create.html",
        agents=agents
    )

@item_agent_mapping_bp.route(
    "/item-agent-mapping/store",
    methods=["POST"]
)
def store():

    db = SessionLocal()

    item = ItemAgentMapping(

        agent_id=request.form["agent_id"],

        kode_sku_agent=request.form["kode_sku_agent"],

        kode_sku_jim=request.form["kode_sku_jim"],

        nama_sku_jim=request.form["nama_sku_jim"],

        item_box=request.form["item_box"],

        item_group=request.form["item_group"],

        is_active=True

    )

    db.add(item)

    db.commit()

    db.close()

    return redirect(
        url_for("item_agent_mapping.index")
    )

@item_agent_mapping_bp.route("/item-agent-mapping/edit/<int:id>")
def edit(id):

    db = SessionLocal()

    mapping = (
        db.query(ItemAgentMapping)
        .filter(ItemAgentMapping.id == id)
        .first()
    )

    agents = (
        db.query(Agent)
        .order_by(Agent.kode_agent)
        .all()
    )

    db.close()

    return render_template(
        "item_agent_mapping/edit.html",
        mapping=mapping,
        agents=agents
    )

@item_agent_mapping_bp.route(
    "/item-agent-mapping/update/<int:id>",
    methods=["POST"]
)
def update(id):

    db = SessionLocal()

    mapping = (
        db.query(ItemAgentMapping)
        .filter(ItemAgentMapping.id == id)
        .first()
    )

    mapping.agent_id = request.form["agent_id"]
    mapping.kode_sku_agent = request.form["kode_sku_agent"]
    mapping.kode_sku_jim = request.form["kode_sku_jim"]
    mapping.nama_sku_jim = request.form["nama_sku_jim"]
    mapping.item_box = request.form["item_box"]
    mapping.item_group = request.form["item_group"]

    db.commit()

    db.close()

    return redirect(
        url_for("item_agent_mapping.index")
    )

@item_agent_mapping_bp.route("/item-agent-mapping/delete/<int:id>")
def delete(id):

    db = SessionLocal()

    mapping = (
        db.query(ItemAgentMapping)
        .filter(ItemAgentMapping.id == id)
        .first()
    )

    mapping.is_active = False

    db.commit()

    db.close()

    return redirect(
        url_for("item_agent_mapping.index")
    )