"""Integration tests for Flask REST APIs and security endpoints."""

import pytest
import json
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check_endpoint(client):
    """Verify healthcheck endpoint for Cloud Run container monitoring."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "resq-verse"
    assert "port" in data


def test_security_headers_present(client):
    """Verify OWASP-recommended security headers are returned."""
    res = client.get("/api/health")
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"


def test_list_scenarios_endpoint(client):
    """Verify retrieval of preloaded crisis scenarios."""
    res = client.get("/api/scenarios")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["data"]) >= 3


def test_process_crisis_endpoint(client):
    """Verify full end-to-end multimodal crisis conversion."""
    payload = {
        "voice_transcript": "911 caller trapped on flooded bridge ramp with cardiac patient",
        "medical_history": "History of coronary stent, severe penicillin allergy",
        "traffic_feed": "Highway ramp closed due to 4ft standing water",
        "weather_data": "Flash flood warning 3.5 in/hr rainfall",
        "news_social_sos": "Citizen distress call on Twitter #LincolnBridge",
        "photo_description": "Submerged sedan against road barrier"
    }
    res = client.post("/api/process", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    
    plan = json_data["data"]
    assert "incident_id" in plan
    assert plan["signals"]["primary_severity"] in ("RED", "YELLOW", "GREEN")
    assert len(plan["patients"]) > 0
    assert len(plan["dispatched_fleet"]) > 0
    assert plan["verification"]["overall_confidence"] > 0.0


def test_cap_xml_export_endpoint(client):
    """Verify CAP XML export adheres to application/xml content-type."""
    res = client.get("/api/export/cap/RESQ-DEMO999")
    assert res.status_code == 200
    assert "application/xml" in res.content_type
    assert b"<alert" in res.data
    assert b"urn:oasis:names:tc:emergency:cap:1.2" in res.data
