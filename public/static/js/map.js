/**
 * Leaflet Tactical Incident Map Visualizer for ResQ-Verse.
 * Renders emergency epicenter, hazard exclusion zones, road closures, and ER routing.
 */

let mapInstance = null;
let markersLayer = null;

function initTacticalMap(lat = 37.7833, lng = -122.4167, locationName = "Incident Epicenter") {
    const mapElement = document.getElementById("tactical-map");
    if (!mapElement) return;

    // Reset if previously initialized
    if (mapInstance) {
        mapInstance.remove();
        mapInstance = null;
    }

    // Initialize Map with dark-matter open tiles
    mapInstance = L.map("tactical-map", {
        center: [lat, lng],
        zoom: 14,
        zoomControl: true,
        attributionControl: false
    });

    // Dark-themed tactical tiles (CartoDB DarkMatter)
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        maxZoom: 19,
        subdomains: "abcd"
    }).addTo(mapInstance);

    markersLayer = L.layerGroup().addTo(mapInstance);

    updateTacticalMap(lat, lng, locationName, []);
}

function updateTacticalMap(lat, lng, locationName, hazards = []) {
    if (!mapInstance || !markersLayer) {
        initTacticalMap(lat, lng, locationName);
        return;
    }

    markersLayer.clearLayers();

    // 1. Incident Epicenter Marker (Red pulsing icon)
    const redIcon = L.divIcon({
        className: 'custom-pin-incident',
        html: `<div style="background-color: #ef4444; width: 22px; height: 22px; border-radius: 50%; border: 3px solid #fff; box-shadow: 0 0 15px #ef4444; display: flex; align-items: center; justify-content: center; font-size: 11px;">⚠️</div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    });

    const incidentMarker = L.marker([lat, lng], { icon: redIcon })
        .bindPopup(`<b>🚨 Incident Epicenter</b><br>${locationName}<br><b>Lat:</b> ${lat.toFixed(4)}, <b>Lng:</b> ${lng.toFixed(4)}`)
        .openPopup();
    markersLayer.addLayer(incidentMarker);

    // 2. Hazard Perimeter Exclusion Zone (Red Circle)
    const hazardRadius = 750; // 750 meters
    const hazardCircle = L.circle([lat, lng], {
        color: '#ef4444',
        fillColor: '#ef4444',
        fillOpacity: 0.2,
        radius: hazardRadius,
        weight: 2,
        dashArray: '6, 6'
    }).bindPopup("<b>⚠️ Hot Zone Exclusion Perimeter (750m)</b><br>Respiratory / Flash Hazard Active");
    markersLayer.addLayer(hazardCircle);

    // 3. St. Jude Trauma Hospital Marker (Blue / Green)
    const hospLat = lat + 0.015;
    const hospLng = lng - 0.012;
    const hospIcon = L.divIcon({
        className: 'custom-pin-hosp',
        html: `<div style="background-color: #3b82f6; width: 20px; height: 20px; border-radius: 50%; border: 2px solid #fff; box-shadow: 0 0 10px #3b82f6; display: flex; align-items: center; justify-content: center; font-size: 11px;">🏥</div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10]
    });

    const hospMarker = L.marker([hospLat, hospLng], { icon: hospIcon })
        .bindPopup("<b>🏥 St. Jude Level 1 Trauma Center</b><br>Receiving ER & Surgical Suites");
    markersLayer.addLayer(hospMarker);

    // 4. Safe Ingress / Egress Route Polyline (Green glowing path)
    const safeRoutePoints = [
        [lat, lng],
        [lat + 0.005, lng - 0.004],
        [lat + 0.010, lng - 0.008],
        [hospLat, hospLng]
    ];

    const safePolyline = L.polyline(safeRoutePoints, {
        color: '#10b981',
        weight: 4,
        opacity: 0.85,
        dashArray: '8, 8'
    }).bindPopup("<b>🟢 Verified Clear Corridor</b><br>Lincoln Arterial Bypass (ETA: 4 mins)");
    markersLayer.addLayer(safePolyline);

    // Pan map to epicenter
    mapInstance.setView([lat, lng], 14);

    // Ensure Leaflet tiles render correctly if container resized
    setTimeout(() => {
        if (mapInstance) mapInstance.invalidateSize();
    }, 200);
}

window.initTacticalMap = initTacticalMap;
window.updateTacticalMap = updateTacticalMap;
