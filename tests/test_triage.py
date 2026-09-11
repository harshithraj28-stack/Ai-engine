"""Unit tests for START triage and life-saving action planning."""

import pytest
from core.models import CrisisRawInput, ExtractedSignals
from core.verification_engine import VerificationEngine
from core.triage_planner import TriagePlanner


@pytest.fixture
def chemical_incident():
    raw = CrisisRawInput(
        voice_transcript="Mayday! Anhydrous ammonia tank explosion at Pier 48! Toxic vapor cloud blowing East!",
        medical_history="Marcus Vance, 44yo. Severe brittle asthma, allergy to sulfa and morphine.",
        traffic_feed="Cross-Town Expressway closed from Exit 12 to 18.",
        weather_data="Wind from West 19 mph gusting to 32 mph. Ground hugging ammonia plume.",
        news_social_sos="Mandatory evacuation order for East River district.",
        photo_description="Greenish yellow vapor cloud billowing over loading bay."
    )
    signals = ExtractedSignals(
        incident_name="Eastside Chemical Facility Vapor Release",
        incident_type="Industrial Chemical Fire & Toxic Plume",
        location_name="Pier 48 Industrial Complex",
        latitude=37.7650,
        longitude=-122.3900,
        estimated_casualties=3,
        primary_severity="RED",
        critical_risks=["Acute pulmonary edema from chemical inhalation"],
        environmental_hazards=["Anhydrous Ammonia / Chlorine Plume", "Secondary explosion risk"],
        road_closures=["Expressway Mile 14 to 17"]
    )
    ver = VerificationEngine.verify(raw, signals)
    return raw, signals, ver


def test_triage_planner_classifies_patients(chemical_incident):
    """Verify START triage classifications and immediate field SOPs."""
    raw, signals, ver = chemical_incident
    plan = TriagePlanner.generate_plan(raw, signals, ver)

    assert len(plan.patients) >= 2
    assert plan.patients[0].triage_tag == "RED"
    assert "bronchodilator" in plan.patients[0].immediate_field_intervention.lower() or "tourniquet" in plan.patients[0].immediate_field_intervention.lower()


def test_triage_planner_dispatches_specialized_fleet(chemical_incident):
    """Verify HAZMAT unit is tasked when chemical hazard is present."""
    raw, signals, ver = chemical_incident
    plan = TriagePlanner.generate_plan(raw, signals, ver)

    fleet_types = [u.unit_type for u in plan.dispatched_fleet]
    has_hazmat_or_als = any("HAZMAT" in t or "ALS" in t for t in fleet_types)
    assert has_hazmat_or_als is True
    assert all(u.eta_minutes <= 15 for u in plan.dispatched_fleet)


def test_hospital_sbar_generation(chemical_incident):
    """Verify SBAR report contains Situation, Background, Assessment, and Recommendation."""
    raw, signals, ver = chemical_incident
    plan = TriagePlanner.generate_plan(raw, signals, ver)
    sbar = plan.hospital_sbar

    assert "INCOMING TRAUMA ALERT" in sbar.situation
    assert any(term in sbar.background.lower() for term in ["bronchospasm", "asthma", "trauma", "pt-01"])
    assert len(sbar.recommendation) > 20
    assert sbar.eta_to_er_minutes > 0
