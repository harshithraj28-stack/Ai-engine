"""Unit tests for Pydantic data schemas in core.models."""

import pytest
from pydantic import ValidationError
from core.models import (
    CrisisRawInput,
    ExtractedSignals,
    VerificationSignal,
    VerificationReport,
    PatientProfile,
    DispatchedUnit,
    HospitalSBAR,
    LifeSavingActionPlan,
    CommonAlertingProtocol
)


def test_crisis_raw_input_defaults():
    """Verify default initialization with empty strings."""
    raw = CrisisRawInput()
    assert raw.voice_transcript == ""
    assert raw.medical_history == ""
    assert raw.traffic_feed == ""
    assert raw.weather_data == ""
    assert raw.news_social_sos == ""
    assert raw.photo_description == ""
    assert raw.coordinates_hint is None


def test_crisis_raw_input_with_data():
    """Verify CrisisRawInput parses rich input fields."""
    raw = CrisisRawInput(
        voice_transcript="Mayday call from Lincoln Bridge",
        medical_history="Allergy: Penicillin",
        traffic_feed="Lane 1 blocked",
        weather_data="Heavy rain 4 in/hr",
        news_social_sos="#LincolnBridge flood",
        photo_description="Submerged car"
    )
    assert "Lincoln Bridge" in raw.voice_transcript
    assert "Penicillin" in raw.medical_history
    assert "blocked" in raw.traffic_feed


def test_extracted_signals_validation():
    """Verify ExtractedSignals requires compulsory fields."""
    signals = ExtractedSignals(
        incident_name="Bridge Collapse Emergency",
        incident_type="Structural Trauma",
        location_name="Lincoln Bridge",
        latitude=37.7833,
        longitude=-122.4167,
        estimated_casualties=2,
        primary_severity="RED",
        critical_risks=["Entrapment in vehicle"],
        environmental_hazards=["Rising water"],
        road_closures=["Lower Deck Ramp"]
    )
    assert signals.incident_name == "Bridge Collapse Emergency"
    assert signals.latitude == 37.7833
    assert signals.primary_severity == "RED"
    assert len(signals.critical_risks) == 1


def test_patient_profile_triage_tags():
    """Verify PatientProfile tags and interventions."""
    patient = PatientProfile(
        patient_id="PT-01",
        age_gender_indicator="62yo Male",
        triage_tag="RED",
        identified_conditions=["Hemophilia A"],
        known_allergies=["Penicillin"],
        active_medications=["Eliquis"],
        critical_vitals={"SpO2": "88%", "BP": "80/50"},
        immediate_field_intervention="Tourniquet + Factor VIII Infusion"
    )
    assert patient.triage_tag == "RED"
    assert "Penicillin" in patient.known_allergies
    assert patient.critical_vitals["SpO2"] == "88%"


def test_cap_alert_structure():
    """Verify Common Alerting Protocol generation."""
    cap = CommonAlertingProtocol(
        identifier="RESQ-TEST123",
        event="FLASH FLOOD EMERGENCY",
        headline="Immediate Evacuation Required",
        instruction="Move to higher ground immediately.",
        area_description="Lincoln Bridge 3km radius"
    )
    assert cap.status == "Actual"
    assert cap.urgency == "Immediate"
    assert cap.severity == "Extreme"
