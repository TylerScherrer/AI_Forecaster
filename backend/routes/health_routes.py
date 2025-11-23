# routes/health_routes.py
from flask import Blueprint

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return {"ok": True}
