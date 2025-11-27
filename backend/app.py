# app.py
import os
from flask import Flask, request

from config import CORS_ALLOWED_ORIGINS
from routes.health_routes import health_bp
from routes.stores_routes import stores_bp
from routes.forecast_routes import forecast_bp
from routes.ai_routes import ai_bp  # ✅ make sure this import exists


def create_app() -> Flask:
    app = Flask(__name__)

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        if origin in CORS_ALLOWED_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"

        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(stores_bp, url_prefix="/api")
    app.register_blueprint(forecast_bp, url_prefix="/api")
    app.register_blueprint(ai_bp, url_prefix="/api")  # ✅ add this

    return app
