from flask import Flask
from config import Config

from routes.agent_routes import agent_bp
from routes.upload_routes import upload_bp
from routes.mapping_routes import mapping_bp
from models.template import Template
from models.template_mapping import TemplateMapping
from routes.generate_routes import generate_bp
from routes.home_routes import home_bp

app = Flask(__name__)

app.config.from_object(Config)

app.register_blueprint(agent_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(mapping_bp)
app.register_blueprint(generate_bp)
app.register_blueprint(home_bp)

if __name__ == "__main__":
    app.run(debug=True)