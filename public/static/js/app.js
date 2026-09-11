/**
 * Main Client Controller for ResQ-Verse Crisis Action Engine.
 * Handles multimodal data submission, Web Speech recording, API orchestration, and UI rendering.
 */

document.addEventListener("DOMContentLoaded", () => {
    // Elements
    const scenarioDropdown = document.getElementById("scenario-dropdown");
    const btnLoadScenario = document.getElementById("btn-load-scenario");
    const btnProcessCrisis = document.getElementById("btn-process-crisis");
    const btnClearInputs = document.getElementById("btn-clear-inputs");
    const btnRecordAudio = document.getElementById("btn-record-audio");
    const recordText = document.getElementById("record-text");
    const toggleContrast = document.getElementById("toggle-contrast");

    // Input fields
    const inputVoice = document.getElementById("input-voice");
    const inputMedical = document.getElementById("input-medical");
    const inputTraffic = document.getElementById("input-traffic");
    const inputWeather = document.getElementById("input-weather");
    const inputNews = document.getElementById("input-news");
    const inputPhoto = document.getElementById("input-photo");

    // Output views
    const emptyState = document.getElementById("empty-state");
    const loadingState = document.getElementById("loading-state");
    const outputDashboard = document.getElementById("output-dashboard");

    // Output fields
    const bannerSeverity = document.getElementById("banner-severity");
    const bannerIncidentName = document.getElementById("banner-incident-name");
    const bannerConfidence = document.getElementById("banner-confidence");
    const bannerLocation = document.getElementById("banner-location");
    const bannerHazards = document.getElementById("banner-hazards");
    const verificationSignalsList = document.getElementById("verification-signals-list");
    const conflictsContainer = document.getElementById("conflicts-container");
    const conflictsList = document.getElementById("conflicts-list");
    const patientCardsContainer = document.getElementById("patient-cards-container");
    const fleetListContainer = document.getElementById("fleet-list-container");
    const sbarSituation = document.getElementById("sbar-situation");
    const sbarBackground = document.getElementById("sbar-background");
    const sbarAssessment = document.getElementById("sbar-assessment");
    const sbarRecommendation = document.getElementById("sbar-recommendation");
    const btnCopySbar = document.getElementById("btn-copy-sbar");
    const capHeadline = document.getElementById("cap-headline");
    const capInstruction = document.getElementById("cap-instruction");
    const capMeta = document.getElementById("cap-meta");
    const btnDownloadCap = document.getElementById("btn-download-cap");
    const latencyBadge = document.getElementById("latency-badge");
    const engineBadge = document.getElementById("engine-badge");

    // Settings Modal
    const btnSettings = document.getElementById("btn-settings");
    const settingsModal = document.getElementById("settings-modal");
    const btnCloseSettings = document.getElementById("btn-close-settings");
    const btnSaveSettings = document.getElementById("btn-save-settings");
    const userGeminiKeyInput = document.getElementById("user-gemini-key");

    // Saved Gemini Key in localStorage
    let currentApiKey = localStorage.getItem("resq_gemini_api_key") || "";
    if (userGeminiKeyInput) userGeminiKeyInput.value = currentApiKey;

    // Load initial scenario on startup
    loadSelectedScenario();

    // 1. Scenario Loader
    btnLoadScenario.addEventListener("click", (e) => {
        e.preventDefault();
        loadSelectedScenario();
    });

    async function loadSelectedScenario() {
        const scenarioId = scenarioDropdown.value;
        try {
            const res = await fetch(`/api/scenarios/${scenarioId}`);
            const json = await res.json();
            if (json.status === "success" && json.data) {
                const d = json.data.data;
                inputVoice.value = d.voice_transcript || "";
                inputMedical.value = d.medical_history || "";
                inputTraffic.value = d.traffic_feed || "";
                inputWeather.value = d.weather_data || "";
                inputNews.value = d.news_social_sos || "";
                inputPhoto.value = d.photo_description || "";
            }
        } catch (err) {
            console.error("Failed to load scenario:", err);
        }
    }

    // 2. Clear inputs
    btnClearInputs.addEventListener("click", () => {
        inputVoice.value = "";
        inputMedical.value = "";
        inputTraffic.value = "";
        inputWeather.value = "";
        inputNews.value = "";
        inputPhoto.value = "";
        inputVoice.focus();
    });

    // 3. Web Speech Recognition for Voice Stream
    let recognition = null;
    let isRecording = false;

    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onresult = (event) => {
            let transcript = "";
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                transcript += event.results[i][0].transcript;
            }
            inputVoice.value = (inputVoice.value ? inputVoice.value + " " : "") + transcript;
        };

        recognition.onerror = (event) => {
            console.warn("Speech recognition error:", event.error);
            stopRecording();
        };

        recognition.onend = () => {
            stopRecording();
        };
    }

    btnRecordAudio.addEventListener("click", () => {
        if (!recognition) {
            alert("Live Web Speech API is not supported in this browser. Please type or paste the voice transcript directly.");
            return;
        }

        if (!isRecording) {
            try {
                recognition.start();
                isRecording = true;
                btnRecordAudio.classList.add("recording");
                recordText.textContent = "Listening (Stop)...";
            } catch (err) {
                console.error("Mic error:", err);
            }
        } else {
            recognition.stop();
            stopRecording();
        }
    });

    function stopRecording() {
        isRecording = false;
        btnRecordAudio.classList.remove("recording");
        recordText.textContent = "Record Voice";
    }

    // 4. Process Multimodal Crisis Button
    btnProcessCrisis.addEventListener("click", async () => {
        const payload = {
            voice_transcript: inputVoice.value.trim(),
            medical_history: inputMedical.value.trim(),
            traffic_feed: inputTraffic.value.trim(),
            weather_data: inputWeather.value.trim(),
            news_social_sos: inputNews.value.trim(),
            photo_description: inputPhoto.value.trim()
        };

        // UI states
        emptyState.classList.add("hidden");
        outputDashboard.classList.add("hidden");
        loadingState.classList.remove("hidden");

        const headers = { "Content-Type": "application/json" };
        if (currentApiKey) {
            headers["X-Gemini-Key"] = currentApiKey;
        }

        try {
            const res = await fetch("/api/process", {
                method: "POST",
                headers: headers,
                body: JSON.stringify(payload)
            });

            const json = await res.json();
            loadingState.classList.add("hidden");

            if (json.status === "success" && json.data) {
                renderActionPlan(json.data);
                outputDashboard.classList.remove("hidden");
            } else {
                alert("Error processing crisis input: " + (json.message || "Unknown error"));
                emptyState.classList.remove("hidden");
            }
        } catch (err) {
            loadingState.classList.add("hidden");
            emptyState.classList.remove("hidden");
            console.error("API error:", err);
            alert("Failed to communicate with ResQ-Verse engine: " + err.message);
        }
    });

    // 5. Render Action Plan
    function renderActionPlan(plan) {
        // Latency & Engine
        latencyBadge.textContent = `Latency: ${plan.processing_time_ms} ms`;
        engineBadge.textContent = plan.engine_mode;

        // Incident Banner
        const sig = plan.signals;
        bannerIncidentName.textContent = sig.incident_name;
        bannerSeverity.textContent = `CRITICAL ${sig.primary_severity}`;
        bannerSeverity.className = `severity-pill ${sig.primary_severity.toLowerCase()}`;
        bannerConfidence.textContent = `${plan.verification.overall_confidence}% Corroborated`;
        bannerLocation.textContent = `📍 Epicenter: ${sig.location_name} (Lat: ${sig.latitude.toFixed(4)}, Lng: ${sig.longitude.toFixed(4)})`;

        // Hazards
        bannerHazards.innerHTML = "";
        sig.environmental_hazards.forEach(h => {
            const chip = document.createElement("span");
            chip.className = "hazard-chip";
            chip.textContent = `⚠️ ${h}`;
            bannerHazards.appendChild(chip);
        });

        // Verification Signals
        verificationSignalsList.innerHTML = "";
        plan.verification.verification_signals.forEach(vs => {
            const li = document.createElement("li");
            li.className = "ver-item";
            li.innerHTML = `
                <div>
                    <div class="ver-claim">${vs.claim}</div>
                    <div class="ver-meta">
                        <b>Origin:</b> ${vs.source_origin} | 
                        <b>Corroboration:</b> ${vs.corroborating_sources.join(", ") || "Single Stream"} | 
                        <b>Status:</b> <span style="color: #34d399">${vs.status}</span>
                    </div>
                </div>
            `;
            verificationSignalsList.appendChild(li);
        });

        // Conflicts
        if (plan.verification.conflicts_detected && plan.verification.conflicts_detected.length > 0) {
            conflictsContainer.classList.remove("hidden");
            conflictsList.innerHTML = "";
            plan.verification.conflicts_detected.forEach(c => {
                const cli = document.createElement("li");
                cli.textContent = c;
                conflictsList.appendChild(cli);
            });
        } else {
            conflictsContainer.classList.add("hidden");
        }

        // Patients (START Triage)
        patientCardsContainer.innerHTML = "";
        plan.patients.forEach(pt => {
            const card = document.createElement("div");
            card.className = `patient-card tag-${pt.triage_tag.toLowerCase()}`;
            
            const vitalsStr = Object.entries(pt.critical_vitals)
                .map(([k, v]) => `<span>${k}: <b>${v}</b></span>`)
                .join(" | ");

            card.innerHTML = `
                <div class="patient-header">
                    <strong>${pt.patient_id} (${pt.age_gender_indicator})</strong>
                    <span class="pt-tag ${pt.triage_tag}">${pt.triage_tag}</span>
                </div>
                <div class="pt-detail-line"><strong>Conditions:</strong> ${pt.identified_conditions.join(", ")}</div>
                <div class="pt-detail-line"><strong>Allergies:</strong> <span style="color:#fca5a5">${pt.known_allergies.join(", ")}</span></div>
                <div class="pt-detail-line"><strong>Vitals:</strong> ${vitalsStr}</div>
                <div class="pt-intervention">
                    <strong>⚡ Immediate Field SOP:</strong> ${pt.immediate_field_intervention}
                </div>
            `;
            patientCardsContainer.appendChild(card);
        });

        // Dispatched Fleet
        fleetListContainer.innerHTML = "";
        plan.dispatched_fleet.forEach(unit => {
            const row = document.createElement("div");
            row.className = "fleet-row";
            row.innerHTML = `
                <div>
                    <div class="fleet-unit-name">🚨 ${unit.unit_id} — ${unit.unit_type}</div>
                    <div class="fleet-route"><b>Route:</b> ${unit.assigned_route} (${unit.route_status})</div>
                    <div class="fleet-route"><b>Equipment:</b> ${unit.specialized_equipment.join(", ")}</div>
                </div>
                <div class="fleet-eta">ETA: ${unit.eta_minutes}m</div>
            `;
            fleetListContainer.appendChild(row);
        });

        // Hospital SBAR
        const sbar = plan.hospital_sbar;
        sbarSituation.textContent = sbar.situation;
        sbarBackground.textContent = sbar.background;
        sbarAssessment.textContent = sbar.assessment;
        sbarRecommendation.textContent = sbar.recommendation;

        // CAP Broadcast
        const cap = plan.cap_alert;
        capHeadline.textContent = cap.headline;
        capInstruction.textContent = cap.instruction;
        capMeta.textContent = `Broadcast Scope: ${cap.scope} | Urgency: ${cap.urgency} | Certainty: ${cap.certainty} | Identifier: ${cap.identifier}`;
        btnDownloadCap.href = `/api/export/cap/${plan.incident_id}`;

        // Initialize Tactical Map
        if (window.updateTacticalMap) {
            window.updateTacticalMap(sig.latitude, sig.longitude, sig.location_name, sig.environmental_hazards);
        }
    }

    // 6. Copy SBAR to Clipboard
    btnCopySbar.addEventListener("click", () => {
        const text = `SBAR REPORT:\n\nSITUATION: ${sbarSituation.textContent}\n\nBACKGROUND: ${sbarBackground.textContent}\n\nASSESSMENT: ${sbarAssessment.textContent}\n\nRECOMMENDATION: ${sbarRecommendation.textContent}`;
        navigator.clipboard.writeText(text).then(() => {
            btnCopySbar.textContent = "✅ Copied!";
            setTimeout(() => { btnCopySbar.textContent = "📋 Copy SBAR"; }, 2000);
        });
    });

    // 7. High Contrast Mode Toggle
    toggleContrast.addEventListener("click", () => {
        document.body.classList.toggle("high-contrast");
    });

    // 8. Settings Modal
    btnSettings.addEventListener("click", () => {
        settingsModal.classList.remove("hidden");
    });
    btnCloseSettings.addEventListener("click", () => {
        settingsModal.classList.add("hidden");
    });
    btnSaveSettings.addEventListener("click", () => {
        currentApiKey = userGeminiKeyInput.value.trim();
        localStorage.setItem("resq_gemini_api_key", currentApiKey);
        settingsModal.classList.add("hidden");
        alert(currentApiKey ? "Gemini API Key saved for session." : "Offline Heuristic Mode active.");
    });
});
