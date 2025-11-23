# app.py
from flask import Flask
from flask_cors import CORS

from config import CORS_ALLOW_ORIGIN
from routes.health_routes import health_bp
from routes.stores_routes import stores_bp
from routes.forecast_routes import forecast_bp


def create_app() -> Flask:
    app = Flask(__name__)

    CORS(
        app,
        resources={r"/api/*": {"origins": CORS_ALLOW_ORIGIN}},
    )

    # All APIs under /api, just split by blueprint
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(stores_bp, url_prefix="/api")
    app.register_blueprint(forecast_bp, url_prefix="/api")

    return app
