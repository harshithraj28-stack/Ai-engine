"""Main Application Server for ResQ-Verse Crisis Action Engine.
Serves the accessible Web Command Center UI and high-performance REST APIs.
Fully container-ready for Google Cloud Run (port 8080 binding, healthchecks, security headers).
"""

import os
import time
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
from pydantic import ValidationError

import config
from core.models import CrisisRawInput, LifeSavingActionPlan
from core.gemini_service import GeminiService
from core.verification_engine import VerificationEngine
from core.triage_planner import TriagePlanner
from core.mock_scenarios import get_all_scenarios, get_scenario_by_id

current_dir = Path(__file__).resolve().parent
template_candidates = [
    current_dir / "templates",
    current_dir.parent / "templates",
    Path("/var/task/templates"),
    Path("templates")
]
template_dir = next((str(p) for p in template_candidates if p.exists()), str(current_dir / "templates"))

static_candidates = [
    current_dir / "static",
    current_dir.parent / "static",
    Path("/var/task/static"),
    Path("static")
]
static_dir = next((str(p) for p in static_candidates if p.exists()), str(current_dir / "static"))

app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir
)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

class VercelPathMiddleware:
    """Normalizes serverless rewrite paths so Flask receives the clean original path."""
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        from urllib.parse import parse_qs
        qs = parse_qs(environ.get("QUERY_STRING", ""))
        vercel_path = qs.get("__vercel_path", [None])[0]
        matched_path = environ.get("HTTP_X_MATCHED_PATH")

        real_path = None
        if vercel_path is not None:
            real_path = "/" + vercel_path.lstrip("/")
        elif matched_path and not matched_path.startswith("/api/index"):
            real_path = matched_path

        if real_path:
            environ["PATH_INFO"] = real_path
        elif environ.get("PATH_INFO") in ("/api/index.py", "/api/index", "/api/"):
            environ["PATH_INFO"] = "/"

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)

# Enable CORS for open inter-agency integrations
CORS(app, resources={r"/api/*": {"origins": config.CORS_ORIGINS}})

# In-memory incident cache for quick retrieval and CAP export
INCIDENT_STORE = {}


@app.after_request
def set_security_headers(response: Response) -> Response:
    """Apply strict security and accessibility headers on all HTTP responses."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "microphone=(self), camera=()"
    return response


@app.route("/")
@app.route("/api/index.py")
@app.route("/api/index")
@app.route("/api")
def index():
    """Render the accessible real-time command dashboard."""
    scenarios = get_all_scenarios()
    has_api_key = bool(config.GEMINI_API_KEY)
    try:
        return render_template(
            "index.html",
            app_name=config.APP_NAME,
            app_version=config.APP_VERSION,
            scenarios=scenarios,
            has_api_key=has_api_key
        )
    except Exception:
        # Fallback in case template loader was isolated by serverless bundler
        for p in template_candidates:
            html_file = p / "index.html"
            if html_file.exists():
                from jinja2 import Template
                with open(html_file, "r", encoding="utf-8") as f:
                    return Template(f.read()).render(
                        app_name=config.APP_NAME,
                        app_version=config.APP_VERSION,
                        scenarios=scenarios,
                        has_api_key=has_api_key
                    )
        raise


@app.route("/api/health", methods=["GET"])
def health():
    """Readiness and liveness probe for Google Cloud Run and container orchestrators."""
    return jsonify({
        "status": "healthy",
        "service": "resq-verse",
        "version": config.APP_VERSION,
        "environment": "production" if not config.DEBUG else "development",
        "gemini_api_configured": bool(config.GEMINI_API_KEY),
        "port": config.PORT,
        "timestamp": time.time()
    }), 200


@app.route("/api/scenarios", methods=["GET"])
def list_scenarios():
    """Retrieve preloaded multi-modal crisis scenarios."""
    return jsonify({"status": "success", "data": get_all_scenarios()}), 200


@app.route("/api/scenarios/<scenario_id>", methods=["GET"])
def get_scenario(scenario_id: str):
    """Retrieve a specific scenario by ID."""
    scenario = get_scenario_by_id(scenario_id)
    return jsonify({"status": "success", "data": scenario}), 200


@app.route("/api/process", methods=["POST"])
def process_crisis():
    """Core pipeline: Ingests unstructured inputs and produces verified life-saving action plan."""
    start_time = time.perf_counter()

    try:
        data = request.get_json(force=True, silent=False)
        if not data:
            return jsonify({"status": "error", "message": "Missing JSON request body"}), 400

        # Validate input schema
        raw_input = CrisisRawInput(**data)
    except ValidationError as ve:
        return jsonify({"status": "error", "message": "Validation Error", "details": ve.errors()}), 422
    except Exception as e:
        return jsonify({"status": "error", "message": f"Malformed request: {str(e)}"}), 400

    # 1. Multimodal AI Extraction (Gemini 1.5 Flash + Heuristic Fallback)
    user_key = request.headers.get("X-Gemini-Key") or None
    signals, engine_mode = GeminiService.extract_signals(raw_input, api_key=user_key)

    # 2. Multi-Signal Verification & Anti-Hallucination Corroboration
    verification = VerificationEngine.verify(raw_input, signals)

    # 3. Life-Saving Action Planning (START Triage, Fleet Dispatch, SBAR, CAP)
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 1)
    plan = TriagePlanner.generate_plan(
        raw=raw_input,
        signals=signals,
        verification=verification,
        processing_time_ms=elapsed_ms,
        engine_mode=engine_mode
    )

    # Store plan in memory
    INCIDENT_STORE[plan.incident_id] = plan

    return jsonify({
        "status": "success",
        "data": plan.model_dump()
    }), 200


@app.route("/api/verify", methods=["POST"])
def verify_signals():
    """Standalone verification check for quick validation tests."""
    try:
        data = request.get_json(force=True)
        raw_input = CrisisRawInput(**data)
        signals, _ = GeminiService.extract_signals(raw_input)
        verification = VerificationEngine.verify(raw_input, signals)
        return jsonify({"status": "success", "data": verification.model_dump()}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/export/cap/<incident_id>", methods=["GET"])
def export_cap_xml(incident_id: str):
    """Export Common Alerting Protocol (CAP v1.2) XML for broadcast alert systems."""
    plan = INCIDENT_STORE.get(incident_id)
    if not plan:
        # Fallback to demo scenario if not found in cache
        scenarios = get_all_scenarios()
        raw_input = CrisisRawInput(**scenarios[0]["data"])
        signals, mode = GeminiService.extract_signals(raw_input)
        ver = VerificationEngine.verify(raw_input, signals)
        plan = TriagePlanner.generate_plan(raw_input, signals, ver)

    cap = plan.cap_alert
    root = ET.Element("alert", xmlns="urn:oasis:names:tc:emergency:cap:1.2")
    ET.SubElement(root, "identifier").text = cap.identifier
    ET.SubElement(root, "sender").text = cap.sender
    ET.SubElement(root, "sent").text = cap.sent
    ET.SubElement(root, "status").text = cap.status
    ET.SubElement(root, "msgType").text = cap.msg_type
    ET.SubElement(root, "scope").text = cap.scope

    info = ET.SubElement(root, "info")
    ET.SubElement(info, "category").text = "Safety"
    ET.SubElement(info, "event").text = cap.event
    ET.SubElement(info, "urgency").text = cap.urgency
    ET.SubElement(info, "severity").text = cap.severity
    ET.SubElement(info, "certainty").text = cap.certainty
    ET.SubElement(info, "headline").text = cap.headline
    ET.SubElement(info, "description").text = cap.instruction

    area = ET.SubElement(info, "area")
    ET.SubElement(area, "areaDesc").text = cap.area_description
    ET.SubElement(area, "circle").text = f"{plan.signals.latitude},{plan.signals.longitude},3.0"

    xml_str = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return Response(xml_str, mimetype="application/xml")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", config.PORT))
    print(f"Starting {config.APP_NAME} on http://0.0.0.0:{port}")
    app.run(host=config.HOST, port=port, debug=config.DEBUG)
