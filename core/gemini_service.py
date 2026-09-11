"""Google Gemini Multimodal AI Service for ResQ-Verse.
Connects with Google Generative AI (Gemini 1.5/2.0 Flash) to parse unstructured
multimodal inputs (voice, photos, EHR notes, traffic text, weather bulletins)
with an intelligent built-in heuristic fallback engine when API keys are absent.
"""

import os
import json
import logging
import re
from typing import Dict, Any, Optional, Tuple
import config
from core.models import CrisisRawInput, ExtractedSignals

logger = logging.getLogger(__name__)

# Try importing google.generativeai if available
try:
    import google.generativeai as genai
    HAS_GENAI_LIB = True
except ImportError:
    genai = None
    HAS_GENAI_LIB = False


class GeminiService:
    """Google Gemini Multimodal Engine for Crisis Signal Extraction."""

    @classmethod
    def extract_signals(cls, raw: CrisisRawInput, api_key: Optional[str] = None) -> Tuple[ExtractedSignals, str]:
        """Extract structured crisis signals using Gemini AI with deterministic fallback."""
        active_key = api_key or config.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")

        if HAS_GENAI_LIB and active_key:
            try:
                genai.configure(api_key=active_key)
                model = genai.GenerativeModel("gemini-1.5-flash")

                prompt = cls._build_extraction_prompt(raw)
                response = model.generate_content(prompt)
                extracted_json = cls._parse_json_from_response(response.text)

                if extracted_json:
                    return ExtractedSignals(
                        incident_name=extracted_json.get("incident_name", "Emergency Response Action"),
                        incident_type=extracted_json.get("incident_type", "Multi-Threat Crisis"),
                        location_name=extracted_json.get("location_name", "Metro Intersection"),
                        latitude=float(extracted_json.get("latitude", 37.7749)),
                        longitude=float(extracted_json.get("longitude", -122.4194)),
                        estimated_casualties=int(extracted_json.get("estimated_casualties", 2)),
                        primary_severity=extracted_json.get("primary_severity", "RED"),
                        critical_risks=extracted_json.get("critical_risks", ["Trauma and environmental hazards"]),
                        environmental_hazards=extracted_json.get("environmental_hazards", ["Severe weather"]),
                        road_closures=extracted_json.get("road_closures", ["Main arterial closure"]),
                    ), "Google Gemini 1.5 Flash (Cloud API)"
            except Exception as e:
                logger.warning(f"Gemini API call failed, falling back to heuristic engine: {e}")

        # Intelligent Heuristic Fallback Engine
        return cls._heuristic_extraction(raw), "ResQ-Verse Heuristic Neural Engine (Grounded Offline Mode)"

    @classmethod
    def _build_extraction_prompt(cls, raw: CrisisRawInput) -> str:
        """Construct prompt for Gemini to structure chaotic real-world inputs."""
        return f"""
You are the core intelligence parser for an emergency crisis dispatch system.
Analyze the following unstructured, messy real-world inputs:

--- 911 VOICE / CALL TRANSCRIPT ---
{raw.voice_transcript or "None"}

--- MESSY MEDICAL HISTORY / EHR NOTES ---
{raw.medical_history or "None"}

--- LIVE TRAFFIC SENSOR DATA ---
{raw.traffic_feed or "None"}

--- SEVERE WEATHER BULLETINS ---
{raw.weather_data or "None"}

--- BREAKING NEWS & SOCIAL SOS FEEDS ---
{raw.news_social_sos or "None"}

--- SCENE PHOTO OBSERVATIONS ---
{raw.photo_description or "None"}

Convert these messy inputs into a strict JSON object with these EXACT keys:
{{
  "incident_name": "Short title",
  "incident_type": "Primary crisis classification e.g. Flash Flood & Multi-Vehicle Trauma, Chemical Plant Fire",
  "location_name": "Specific physical location, bridge, cross-streets, or landmark",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "estimated_casualties": 3,
  "primary_severity": "RED",
  "critical_risks": ["Risk 1", "Risk 2"],
  "environmental_hazards": ["Hazard 1", "Hazard 2"],
  "road_closures": ["Closure 1", "Closure 2"]
}}
Output ONLY the raw JSON object, without markdown formatting or code blocks.
"""

    @staticmethod
    def _parse_json_from_response(text: str) -> Optional[Dict[str, Any]]:
        """Extract and clean JSON from Gemini output."""
        try:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```[a-zA-Z]*\n", "", cleaned)
                cleaned = re.sub(r"\n```$", "", cleaned)
            return json.loads(cleaned)
        except Exception:
            return None

    @classmethod
    def _heuristic_extraction(cls, raw: CrisisRawInput) -> ExtractedSignals:
        """Heuristic rule-based parsing of unstructured text."""
        combined = f"{raw.voice_transcript} {raw.traffic_feed} {raw.weather_data} {raw.news_social_sos} {raw.medical_history} {raw.photo_description}".lower()

        # Determine Incident Type
        if "flood" in combined or "water" in combined or "submerged" in combined or "river" in combined:
            incident_type = "Flash Flood & Multi-Vehicle Entrapment"
            incident_name = "Lincoln Riverfront Flash Flood Evacuation"
            lat, lng = 37.7833, -122.4167
            hazards = ["Rapidly rising floodwaters (4-6 ft depth)", "Submerged electrical conduits", "Zero-visibility underwater debris"]
            closures = ["Lincoln Bridge Lower Span", "River Parkway between 4th & 8th St"]
        elif "fire" in combined or "chemical" in combined or "plume" in combined or "explosion" in combined:
            incident_type = "Industrial Chemical Fire & Toxic Plume"
            incident_name = "Eastside Chemical Facility Vapor Release"
            lat, lng = 37.7650, -122.3900
            hazards = ["Anhydrous Ammonia / Chlorine Plume", "Secondary pressure tank explosion risk", "Airborne caustic particulates"]
            closures = ["Expressway Mile 14 to 17", "Pier 48 Cargo Road"]
        elif "earthquake" in combined or "collapse" in combined or "rubble" in combined or "structural" in combined:
            incident_type = "Structural Collapse & Urban Mass Casualty"
            incident_name = "Downtown Transit Center Structure Failure"
            lat, lng = 37.7890, -122.4010
            hazards = ["Unstable concrete slabs", "High-pressure natural gas main fracture", "Aftershock vulnerability"]
            closures = ["Market St Transit Corridor", "Mission St between 1st and 3rd"]
        else:
            incident_type = "Multi-Vehicle Major Collision & Trauma"
            incident_name = "Metropolitan Arterial Incident"
            lat, lng = 37.7749, -122.4194
            hazards = ["Flammable fuel spill", "High-speed traffic proximity"]
            closures = ["Northbound Highway Ramp 101"]

        # Parse Location Name
        loc_match = re.search(r"(at|on|near|along)\s+([A-Z0-9][a-zA-Z0-9\s&,.'-]{3,35})", f"{raw.voice_transcript} {raw.traffic_feed}")
        location_name = loc_match.group(2).strip() if loc_match else "Lincoln Bridge & River Parkway"

        # Determine Casualties
        casualties = 2
        cas_match = re.search(r"(\d+)\s+(people|victims|casualties|passengers|injured|trapped)", combined)
        if cas_match:
            try:
                casualties = int(cas_match.group(1))
            except ValueError:
                casualties = 3
        elif "three" in combined:
            casualties = 3
        elif "four" in combined:
            casualties = 4
        elif "two" in combined:
            casualties = 2

        # Severity
        severity = "RED" if ("trapped" in combined or "unconscious" in combined or "bleeding" in combined or "critical" in combined or "drowning" in combined) else "YELLOW"

        # Critical Risks
        risks = []
        if "hemophilia" in combined or "bleeding" in combined:
            risks.append("Uncontrolled hemorrhage in hemophilic patient")
        if "trapped" in combined or "submerged" in combined:
            risks.append("Immediate risk of asphyxiation and drowning in cabin")
        if "chemical" in combined or "chlorine" in combined or "ammonia" in combined:
            risks.append("Acute pulmonary edema from chemical inhalation")
        if not risks:
            risks.append("Severe blunt trauma with potential c-spine injury")

        return ExtractedSignals(
            incident_name=incident_name,
            incident_type=incident_type,
            location_name=location_name,
            latitude=lat,
            longitude=lng,
            estimated_casualties=casualties,
            primary_severity=severity,
            critical_risks=risks,
            environmental_hazards=hazards,
            road_closures=closures
        )
