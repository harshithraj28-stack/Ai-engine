"""Pre-loaded multimodal crisis scenarios for 1-click evaluation and demo testing.
Enables instant judging of messy real-world unstructured data streams.
"""

from typing import Dict, Any, List


SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "scenario-flood",
        "title": "Scenario 1: Flash Flood & Multi-Vehicle Pileup (Trapped Cardiac/Hemophilic Patient)",
        "badge": "Water Rescue / Trauma",
        "badge_color": "#3B82F6",
        "data": {
            "voice_transcript": (
                "911, please hurry! We're on Lincoln Bridge right at the lower riverfront ramp! "
                "A huge wall of water came over the embankment and smashed 4 cars together! "
                "My father is pinned in the driver seat, the water is already up to our chests inside the cab! "
                "He's bleeding heavily from his forehead and leg and he has hemophilia! He cannot stop bleeding! "
                "The engine is dead and the doors won't open! We need rescue boats right now!"
            ),
            "medical_history": (
                "Patient: Harold Jenkins, 62yo male. "
                "Diagnoses: Severe Hemophilia A (Factor VIII deficiency, baseline activity <1%), "
                "Coronary Artery Disease s/p drug-eluting stent (LAD 2022). "
                "Active Meds: Eliquis (apixaban) 5mg BID, Metoprolol succinate 50mg daily. "
                "Allergies: Anaphylaxis to PENICILLIN (throat swelling), severe hives to ASPIRIN and NSAIDs. "
                "Blood Type: O-Negative."
            ),
            "traffic_feed": (
                "CITY DOT TRAFFIC SENSOR #418: Lincoln Bridge lower deck completely submerged under 4.2 feet of fast-moving water. "
                "Multi-vehicle collision blocking all 3 Eastbound lanes. Westbound lanes at complete standstill. "
                "Detour: Emergency vehicles must avoid Lincoln Bridge Lower Deck. Use Upper 7th Ave Viaduct only."
            ),
            "weather_data": (
                "NATIONAL WEATHER SERVICE FLASH FLOOD EMERGENCY: Flash flood warning in effect. "
                "Torrential rainfall exceeding 4.1 inches per hour. River gauge at Lincoln Basin is at 18.4 ft (3.4 ft above major flood stage). "
                "Strong current velocity 14 knots. Debris hazard high."
            ),
            "news_social_sos": (
                "BREAKING @CityNewsScanner: Multiple motorists trapped in submerged vehicles at Lincoln Riverfront Overpass! "
                "911 dispatch overwhelmed. Tweets from @sarah_j: 'Water rising super fast at Lincoln Bridge, please send help, people trapped in car!' #LincolnFlood #911"
            ),
            "photo_description": (
                "Visual analysis: Dark sedan and SUV submerged to window level in churning murky brown floodwater, "
                "wedged against deformed guardrail. Visible damage to driver cabin door, driver visible with head slumped, water swirling rapidly."
            )
        }
    },
    {
        "id": "scenario-chemical",
        "title": "Scenario 2: Industrial Chemical Tank Explosion & Toxic Vapor Plume",
        "badge": "HAZMAT / Respiratory",
        "badge_color": "#F59E0B",
        "data": {
            "voice_transcript": (
                "Mayday! Mayday! Security desk at Apex Chemical Processing on Pier 48! "
                "Anhydrous ammonia tank #3 ruptured following a boiler explosion! "
                "There is a dense greenish-yellow vapor cloud billowing towards the eastern residential streets! "
                "Three workers are collapsed on the loading dock, coughing violently, unable to breathe! "
                "Do NOT enter from the South, wind is blowing the plume East-Northeast!"
            ),
            "medical_history": (
                "Casualty 1: Marcus Vance, 44yo. "
                "History of brittle adult-onset asthma with 3 previous intubations. "
                "Severe hypersensitivity to SULFA drugs and Morphine. "
                "Current medications: Advair Diskus, Albuterol rescue inhaler. "
                "Notes: Immediate risk of acute laryngospasm and chemical pneumonitis upon chlorine/ammonia exposure."
            ),
            "traffic_feed": (
                "PORT AUTHORITY TRANSIT ADVISORY: Cross-Town Expressway closed from Exit 12 to 18 due to hazardous material spill. "
                "Harbor Tunnel evacuated and sealed. Massive bottleneck on Southbound I-95 with 6-mile tailback."
            ),
            "weather_data": (
                "NOAA ATMOSPHERIC HAZARD MODEL: Surface winds 280 deg at 19 mph, gusting to 32 mph. "
                "Atmospheric inversion keeping toxic chemical plume hugging ground level across 1.8 mile radius. "
                "Relative humidity 82% causing ammonia gas to convert to caustic aerosol."
            ),
            "news_social_sos": (
                "URGENT POLICE DISPATCH: Mandatory evacuation order issued for East River district within 2 miles of Pier 48. "
                "Citizens experiencing eye burn and shortness of breath. Local emergency shelter at St. Mary's School reaching capacity."
            ),
            "photo_description": (
                "Aerial drone imagery: Massive greenish vapor cloud emanating from breached cylindrical pressurized container. "
                "Structural roof collapse over Loading Bay 4, two unmoving figures visible on concrete apron."
            )
        }
    },
    {
        "id": "scenario-earthquake",
        "title": "Scenario 3: Urban Structural Collapse & Broken Gas Mains",
        "badge": "Urban SAR / Mass Casualty",
        "badge_color": "#EF4444",
        "data": {
            "voice_transcript": (
                "This is Engine 4 arriving at 240 Market Street! We have a catastrophic pancake collapse of a 4-story commercial building! "
                "We hear tapping and cries for help from the void space under the 2nd floor ceiling slab! "
                "At least 4 persons confirmed trapped! We have a severe smell of mercaptan—natural gas line is severed and hissing! "
                "Need Urban Search and Rescue, K9 units, and gas utility emergency shutoff immediately!"
            ),
            "medical_history": (
                "Victim in Void A (identified by coworker): Elena Rostova, 58yo female. "
                "Type 1 Diabetes Mellitus (Insulin dependent), hypertensive. "
                "Severe compound fracture of right lower extremity with heavy active blood loss. "
                "Allergies: Anaphylactic to LATEX and IV Iodinated Contrast Dye."
            ),
            "traffic_feed": (
                "METRO TRANSIT ALERT: Market Street completely closed between 1st and 5th Avenue. "
                "Underground subway tunnels evacuated due to structural tremors and gas accumulation. All surface traffic halted."
            ),
            "weather_data": (
                "LOCAL WEATHER MONITOR: Ambient temperature dropping rapidly to 38°F with steady freezing drizzle. "
                "Hypothermia hazard severe for immobilized victims trapped in rubble voids."
            ),
            "news_social_sos": (
                "@BreakingNews: 6.2 magnitude shock strikes Downtown core! Building collapse reported on Market St. "
                "Fire crews on scene requesting silence for acoustic listening devices to detect trapped survivors."
            ),
            "photo_description": (
                "Scene photo: Four stories compressed down to two, twisted steel rebar protruding through concrete slabs. "
                "First responders deploying acoustic search microphones and pneumatic lifting airbags."
            )
        }
    }
]


def get_all_scenarios() -> List[Dict[str, Any]]:
    """Return all available crisis scenarios."""
    return SCENARIOS


def get_scenario_by_id(scenario_id: str) -> Dict[str, Any]:
    """Retrieve a specific crisis scenario by ID."""
    for s in SCENARIOS:
        if s["id"] == scenario_id:
            return s
    return SCENARIOS[0]
