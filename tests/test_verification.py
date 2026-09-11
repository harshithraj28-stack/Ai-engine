"""Unit tests for Verification and Anti-Hallucination Engine."""

import pytest
from core.models import CrisisRawInput, ExtractedSignals
from core.verification_engine import VerificationEngine


@pytest.fixture
def flood_sample_data():
    raw = CrisisRawInput(
        voice_transcript="Mayday! We are trapped on Lincoln Bridge lower deck with water rising fast!",
        medical_history="Patient Harold Jenkins, Hemophilia A, severe allergy to Penicillin and Aspirin.",
        traffic_feed="DOT Sensor: Lincoln Bridge lower ramp submerged under 4ft of water. Eastbound blocked.",
        weather_data="NWS Flash Flood Warning: 4.1 in/hr rainfall, Lincoln River gauge above flood stage.",
        news_social_sos="Breaking: Motorists submerged at Lincoln Bridge overpass. Rescue boats needed.",
        photo_description="Vehicle submerged to windows in brown floodwater against guardrail."
    )
    signals = ExtractedSignals(
        incident_name="Lincoln Riverfront Flash Flood Evacuation",
        incident_type="Flash Flood & Multi-Vehicle Entrapment",
        location_name="Lincoln Bridge",
        latitude=37.7833,
        longitude=-122.4167,
        estimated_casualties=2,
        primary_severity="RED",
        critical_risks=["Active hemorrhage in hemophilic patient"],
        environmental_hazards=["Rapidly rising floodwaters", "Submerged debris"],
        road_closures=["Lincoln Bridge Lower Span"]
    )
    return raw, signals


def test_verification_corroborates_geography(flood_sample_data):
    """Test that geographic references across voice, traffic, weather, and news are corroborated."""
    raw, signals = flood_sample_data
    report = VerificationEngine.verify(raw, signals)

    assert report.is_verified is True
    assert report.overall_confidence >= 80.0
    
    geo_signals = [s for s in report.verification_signals if "Lincoln Bridge" in s.claim]
    assert len(geo_signals) > 0
    assert geo_signals[0].status == "VERIFIED"
    assert len(geo_signals[0].corroborating_sources) >= 1


def test_verification_detects_pharmacological_allergies(flood_sample_data):
    """Test that medical allergies are extracted and flagged as life-saving contraindications."""
    raw, signals = flood_sample_data
    report = VerificationEngine.verify(raw, signals)

    # Check safety check warnings for penicillin
    penicillin_alert = any("Penicillin" in check for check in report.safety_checks_passed)
    assert penicillin_alert is True, "Penicillin allergy must be flagged in safety checks"


def test_verification_handles_sparse_single_source_input():
    """Test that single-source input reduces confidence and notes unconfirmed status."""
    sparse_raw = CrisisRawInput(
        voice_transcript="Car crash on Unknown Lone Street, someone help"
    )
    sparse_signals = ExtractedSignals(
        incident_name="Traffic Incident",
        incident_type="Vehicle Collision",
        location_name="Unknown Lone Street",
        latitude=37.7749,
        longitude=-122.4194,
        estimated_casualties=1,
        primary_severity="YELLOW",
        critical_risks=["Potential trauma"],
        environmental_hazards=[],
        road_closures=[]
    )
    report = VerificationEngine.verify(sparse_raw, sparse_signals)
    assert len(report.conflicts_detected) > 0 or not report.is_verified or report.overall_confidence <= 75.0
