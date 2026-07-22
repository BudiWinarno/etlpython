from flask import Blueprint, render_template, flash, jsonify

from database import SessionLocal
from models.item_agent_mapping import ItemAgentMapping
import pandas as pd
from sqlalchemy.orm import joinedload

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

    agents = (
        db.query(Agent)
        .order_by(Agent.kode_agent)
        .all()
    )

    # agent_id = request.args.get("agent_id")

    # query = (
    #     db.query(ItemAgentMapping)
    #     .filter(ItemAgentMapping.is_active == True)
    # )

    # if agent_id:

    #     query = query.filter(
    #         ItemAgentMapping.agent_id == int(agent_id)
    #     )

    # mappings = query.order_by(
    #     ItemAgentMapping.id
    # ).all()
    
    agent_id = request.args.get("agent_id")
    kode_sku_agent = request.args.get("kode_sku_agent")
    page = request.args.get("page", 1, type=int)

    query = (
        db.query(ItemAgentMapping)
        .options(joinedload(ItemAgentMapping.agent))
    )

    if agent_id:
        query = query.filter(
            ItemAgentMapping.agent_id == int(agent_id)
        )

    if kode_sku_agent:
        query = query.filter(
            ItemAgentMapping.kode_sku_agent.ilike(f"%{kode_sku_agent}%")
        )

    per_page = 10

    total = query.count()

    mappings = (
        query.order_by(ItemAgentMapping.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    db.close()

    return render_template(
        "item_agent_mapping/index.html",
        mappings=mappings,
        agents=agents,
        selected_agent=agent_id,
        selected_kode_sku_agent=kode_sku_agent,
        page=page,
        per_page=per_page,
        total=total
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
    
    flash(
        "Master Item Agent berhasil ditambahkan.",
        "success"
    )

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
    
    flash(
        "Master Item Agent berhasil diperbarui.",
        "success"
    )

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
    
    flash(
        "Master Item Agent berhasil dihapus.",
        "success"
    )

    db.close()

    return redirect(
        url_for("item_agent_mapping.index")
    )
    
@item_agent_mapping_bp.route("/item-agent-mapping/import")
def import_form():

    db = SessionLocal()

    agents = (
        db.query(Agent)
        .order_by(Agent.kode_agent)
        .all()
    )

    db.close()

    return render_template(
        "item_agent_mapping/import.html",
        agents=agents
    )
    
@item_agent_mapping_bp.route(
    "/item-agent-mapping/import",
    methods=["POST"]
)
def import_excel():

    db = SessionLocal()

    try:

        file = request.files["file"]

        agent_id = int(request.form["agent_id"])

        df = pd.read_excel(file)
        
        # Hilangkan spasi di kode SKU
        df["kode_sku_agent"] = (
            df["kode_sku_agent"]
            .astype(str)
            .str.strip()
        )

        # Cek duplicate di file Excel
        duplicate = df[df.duplicated(
            subset=["kode_sku_agent"],
            keep=False
        )]

        if not duplicate.empty:

            kode_list = duplicate["kode_sku_agent"].unique().tolist()

            flash(
                "Import gagal! Ditemukan Kode SKU Agent duplicate pada file Excel:<br><br>"
                + "<br>".join(kode_list[:20]),
                "danger"
            )

            return redirect(
                url_for("item_agent_mapping.import_form")
            )

        for _, row in df.iterrows():

            kode_sku_agent = str(
                row["kode_sku_agent"]
            ).strip()

            mapping = (
                db.query(ItemAgentMapping)
                .filter(
                    ItemAgentMapping.agent_id == agent_id,
                    ItemAgentMapping.kode_sku_agent == kode_sku_agent
                )
                .first()
            )

            if mapping:

                # UPDATE
                mapping.kode_sku_jim = str(
                    row["kode_sku_jim"]
                ).strip()

                mapping.nama_sku_jim = str(
                    row["nama_sku_jim"]
                ).strip()

                mapping.item_box = int(
                    row["item_box"]
                )

                mapping.item_group = str(
                    row["item_group"]
                ).strip()

                mapping.is_active = True

            else:

                # INSERT
                mapping = ItemAgentMapping(

                    agent_id=agent_id,

                    kode_sku_agent=kode_sku_agent,

                    kode_sku_jim=str(
                        row["kode_sku_jim"]
                    ).strip(),

                    nama_sku_jim=str(
                        row["nama_sku_jim"]
                    ).strip(),

                    item_box=int(
                        row["item_box"]
                    ),

                    item_group=str(
                        row["item_group"]
                    ).strip(),

                    is_active=True

                )

                db.add(mapping)

        db.commit()
        
        flash(
            "Import Master Item Agent berhasil.",
            "success"
        )

        return redirect(
            url_for("item_agent_mapping.index")
        )

    except Exception as e:

        db.rollback()

        flash(
            f"Import gagal! {str(e)}",
            "danger"
        )

        return redirect(
            url_for("item_agent_mapping.import_form")
        )

    finally:

        db.close()
        
@item_agent_mapping_bp.route("/item-agent-mapping/all-ids")
def all_ids():

    db = SessionLocal()

    query = db.query(ItemAgentMapping)

    agent_id = request.args.get("agent_id")
    kode_sku_agent = request.args.get("kode_sku_agent")

    if agent_id:
        query = query.filter(
            ItemAgentMapping.agent_id == int(agent_id)
        )

    if kode_sku_agent:
        query = query.filter(
            ItemAgentMapping.kode_sku_agent.ilike(f"%{kode_sku_agent}%")
        )

    ids = [
        str(item.id)
        for item in query.all()
    ]

    db.close()

    return jsonify(ids)

@item_agent_mapping_bp.route(
    "/item-agent-mapping/delete-selected",
    methods=["POST"]
)
def delete_selected():

    db = SessionLocal()

    try:

        ids = [int(x) for x in request.json.get("ids", [])]

        (
            db.query(ItemAgentMapping)
            .filter(ItemAgentMapping.id.in_(ids))
            .delete(synchronize_session=False)
        )

        db.commit()

        return jsonify({
            "success": True
        })

    except Exception as e:

        db.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        db.close()