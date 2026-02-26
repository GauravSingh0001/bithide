"""
BitHide Backend - Application Entry Point
Creates the Flask app, registers blueprints, error handlers, CORS, and rate limiting.
"""

import os
import sys

from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config, config_map
from utils.logger import get_logger

logger = get_logger("bithide.app")


def create_app(env: str = "default") -> Flask:
    """Application factory pattern."""
    cfg = config_map.get(env, config_map["default"])
    cfg.ensure_directories()

    app = Flask(__name__)
    app.config.from_object(cfg)

    # ─── Extensions ──────────────────────────────────────────────────────────

    # CORS — allow requests from the Vite frontend (localhost:5173) and any deployed domain
    CORS(
        app,
        resources={r"/*": {"origins": os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")}},
    )

    # Rate limiter (in-memory; swap to Redis in production)
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=[cfg.RATE_LIMIT_DEFAULT],
        storage_uri=os.getenv("RATE_LIMIT_STORAGE", "memory://"),
    )

    # ─── Blueprints ──────────────────────────────────────────────────────────
    # FIX #1: Import blueprint AFTER limiter is created, then register.
    # Apply per-route limits post-registration so view_functions dict is populated.
    from api.routes import stego_bp  # noqa: E402
    app.register_blueprint(stego_bp)

    # Apply per-route rate limits now that the view functions are registered
    limiter.limit(cfg.RATE_LIMIT_ENCODE)(app.view_functions["stego.encode"])
    limiter.limit(cfg.RATE_LIMIT_DECODE)(app.view_functions["stego.decode"])

    # ─── Centralised Error Handlers ──────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": True, "message": "Endpoint not found.", "status": 404}), 404

    @app.errorhandler(405)
    def method_not_allowed(_e):
        return jsonify({"error": True, "message": "Method not allowed.", "status": 405}), 405

    @app.errorhandler(413)
    def request_entity_too_large(_e):
        max_mb = app.config.get("MAX_CONTENT_LENGTH", 50 * 1024 * 1024) // (1024 * 1024)
        return jsonify({"error": True, "message": f"File too large. Max {max_mb} MB.", "status": 413}), 413

    @app.errorhandler(429)
    def rate_limit_exceeded(_e):
        return jsonify({"error": True, "message": "Too many requests. Please slow down.", "status": 429}), 429

    @app.errorhandler(500)
    def internal_error(_e):
        return jsonify({"error": True, "message": "Internal server error.", "status": 500}), 500

    logger.info(f"BitHide app created [env={env}]")
    return app


# ─── Dev Entry Point ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Ensure imports resolve when running `python app.py` directly
    sys.path.insert(0, os.path.dirname(__file__))
    env = os.getenv("FLASK_ENV", "development")
    app = create_app(env)
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=app.config["DEBUG"],
    )
