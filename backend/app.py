# app.py
import os
from flask import Flask

from config import CORS_ALLOW_ORIGIN
from routes.health_routes import health_bp
from routes.stores_routes import stores_bp
from routes.forecast_routes import forecast_bp


def create_app() -> Flask:
    app = Flask(__name__)

    # Simple CORS for /api/* without needing flask_cors
    @app.after_request
    def add_cors_headers(response):
        origin = CORS_ALLOW_ORIGIN or "*"
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    # All APIs under /api, split by blueprint
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(stores_bp, url_prefix="/api")
    app.register_blueprint(forecast_bp, url_prefix="/api")

    return app
