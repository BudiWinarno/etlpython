from flask import Flask
from config import Config

from routes.agent_routes import agent_bp
from routes.upload_routes import upload_bp
from routes.mapping_routes import mapping_bp
from models.template import Template
from models.template_mapping import TemplateMapping
from routes.generate_routes import generate_bp
from routes.home_routes import home_bp
from routes.stock_routes import stock_bp
from routes.item_agent_mapping_routes import item_agent_mapping_bp
from routes.stock_mapping_routes import stock_mapping_bp
from routes.generate_stock_routes import generate_stock_bp
from routes.generate_yuri_routes import generate_yuri_bp
from routes.generate_cmo import generate_cmo_bp
from routes.cmo_template import cmo_template_bp
from routes.sqlserver_api import sqlserver_bp
from routes.insell_report import insell_report_bp

app = Flask(__name__)
app.secret_key = "secret123"

app.config.from_object(Config)

app.register_blueprint(agent_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(mapping_bp)
app.register_blueprint(generate_bp)
app.register_blueprint(home_bp)
app.register_blueprint(stock_bp, url_prefix="/stock")
app.register_blueprint(item_agent_mapping_bp)
app.register_blueprint(stock_mapping_bp)
app.register_blueprint(generate_stock_bp)
app.register_blueprint(generate_yuri_bp)
app.register_blueprint(generate_cmo_bp)
app.register_blueprint(cmo_template_bp)
app.register_blueprint(sqlserver_bp)
app.register_blueprint(insell_report_bp)

if __name__ == "__main__":
    app.run(debug=True)