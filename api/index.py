"""Vercel Serverless Function entrypoint for ResQ-Verse."""

import os
import sys
import traceback
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from app import app
except Exception as e:
    from flask import Flask, Response
    app = Flask(__name__)
    err_tb = traceback.format_exc()

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        return Response(
            f"<h1>ResQ-Verse Startup Error</h1><p>A serverless error occurred during startup:</p><pre style='background:#f8d7da;color:#721c24;padding:15px;border-radius:6px;'>{err_tb}</pre>",
            mimetype="text/html",
            status=500
        )
