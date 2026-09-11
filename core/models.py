"""Data models and schemas for ResQ-Verse Crisis Action Engine.
Built with Pydantic v2 for robust validation, type safety, and serialization.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone


class CrisisRawInput(BaseModel):
    """Raw, unstructured multi-modal inputs submitted from the field."""
    voice_transcript: Optional[str] = Field(default="", description="911 voice call transcript or caller speech")
    medical_history: Optional[str] = Field(default="", description="Messy patient EHR, handwritten notes, medications, allergies")
    traffic_feed: Optional[str] = Field(default="", description="Live traffic sensor report, camera alerts, road closures")
    weather_data: Optional[str] = Field(default="", description="Severe weather warnings, rainfall rate, wind, flood stage")
    news_social_sos: Optional[str] = Field(default="", description="Breaking news tickers, Twitter/X SOS calls, bystander posts")
    photo_description: Optional[str] = Field(default="", description="Description or vision tags from scene damage photos")
    image_base64: Optional[str] = Field(default=None, description="Base64 encoded image if uploaded")
    coordinates_hint: Optional[Dict[str, float]] = Field(
        default=None, 
        description="Optional coordinates hint {'lat': float, 'lng': float}"
    )


class ExtractedSignals(BaseModel):
    """Normalized signals extracted across all chaotic input streams."""
    incident_name: str = Field(..., description="Short descriptive title of the emergency event")
    incident_type: str = Field(..., description="Classification e.g., Flash Flood Trauma, Chemical Fire, Structure Collapse")
    location_name: str = Field(..., description="Identified physical address or landmark")
    latitude: float = Field(default=37.7749, description="Target geocoded latitude")
    longitude: float = Field(default=-122.4194, description="Target geocoded longitude")
    estimated_casualties: int = Field(default=1, ge=0)
    primary_severity: str = Field(default="RED", description="Overall highest severity (RED, YELLOW, GREEN, BLACK)")
    critical_risks: List[str] = Field(default_factory=list, description="Immediate life threats")
    environmental_hazards: List[str] = Field(default_factory=list, description="Surrounding physical hazards")
    road_closures: List[str] = Field(default_factory=list, description="Impassable arteries or bottlenecks")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class VerificationSignal(BaseModel):
    """Individual signal verification and cross-source corroboration trace."""
    claim: str
    source_origin: str
    corroborating_sources: List[str] = Field(default_factory=list)
    confidence_level: str = Field(default="HIGH", description="HIGH, MEDIUM, LOW")
    status: str = Field(default="VERIFIED", description="VERIFIED, UNCONFIRMED, CONFLICT")


class VerificationReport(BaseModel):
    """Comprehensive anti-hallucination verification matrix."""
    overall_confidence: float = Field(..., ge=0.0, le=100.0, description="Corroboration score 0-100%")
    is_verified: bool = Field(default=True)
    verification_signals: List[VerificationSignal] = Field(default_factory=list)
    conflicts_detected: List[str] = Field(default_factory=list)
    safety_checks_passed: List[str] = Field(default_factory=list)
    anti_hallucination_guard: str = Field(default="Active: Grounded on multi-source sensor and transcript overlap")


class PatientProfile(BaseModel):
    """START (Simple Triage and Rapid Treatment) triage patient record."""
    patient_id: str
    age_gender_indicator: Optional[str] = "Unknown"
    triage_tag: str = Field(..., description="RED (Immediate), YELLOW (Delayed), GREEN (Minor), BLACK (Expectant)")
    identified_conditions: List[str] = Field(default_factory=list)
    known_allergies: List[str] = Field(default_factory=list)
    active_medications: List[str] = Field(default_factory=list)
    critical_vitals: Dict[str, str] = Field(default_factory=dict)
    immediate_field_intervention: str = Field(..., description="Actionable first aid / triage intervention")


class DispatchedUnit(BaseModel):
    """Emergency responder unit tasking and routing."""
    unit_id: str
    unit_type: str = Field(..., description="ALS Ambulance, Heavy Rescue, HAZMAT, Boat SAR, Fire Engine, Trauma Helicopter")
    station_origin: str
    eta_minutes: int = Field(..., ge=1)
    assigned_route: str
    route_status: str = Field(default="Clear of flood & debris zones")
    specialized_equipment: List[str] = Field(default_factory=list)


class HospitalSBAR(BaseModel):
    """Standardized SBAR communication packet for receiving Emergency Trauma Center."""
    receiving_hospital: str
    trauma_level_required: str
    situation: str
    background: str
    assessment: str
    recommendation: str
    eta_to_er_minutes: int


class EvacuationCorridor(BaseModel):
    """Route navigation avoiding detected traffic jams and environmental hazards."""
    corridor_name: str
    direction: str
    safe_waypoints: List[str]
    avoid_zones: List[str]
    clearance_status: str


class CommonAlertingProtocol(BaseModel):
    """CAP-compliant emergency alert message for civilian broadcast."""
    identifier: str
    sender: str = "ResQ-Verse Crisis Coordination Engine"
    sent: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "Actual"
    msg_type: str = "Alert"
    scope: str = "Public"
    urgency: str = "Immediate"
    severity: str = "Extreme"
    certainty: str = "Observed"
    event: str
    headline: str
    instruction: str
    area_description: str


class LifeSavingActionPlan(BaseModel):
    """The master, structured, verified life-saving action plan produced from chaotic inputs."""
    incident_id: str
    signals: ExtractedSignals
    verification: VerificationReport
    patients: List[PatientProfile]
    dispatched_fleet: List[DispatchedUnit]
    hospital_sbar: HospitalSBAR
    evacuation_corridors: List[EvacuationCorridor]
    first_responder_directives: List[str]
    cap_alert: CommonAlertingProtocol
    processing_time_ms: float
    engine_mode: str = Field(default="Google Gemini AI + Corroboration Engine")
