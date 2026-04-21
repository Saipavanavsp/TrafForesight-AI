/**
 * TrafForesight-AI: Intelligent Dashboard & 3D Globe
 * Features: Intelligence Engine, Simulation Scenarios, Charting
 */

let map;
let directionsService;
let directionsRenderer;
let startMarker;
let destMarker;
let pinMode = 'none';
let predictionChart;

const startIconUrl = 'https://maps.google.com/mapfiles/ms/icons/red-dot.png';
const destIconUrl = 'https://maps.google.com/mapfiles/ms/icons/green-dot.png';

// Authentication Failure Handler
window.gm_authFailure = function() {
    alert("Google Maps Auth Failed. Check Billing/API Key.");
};

async function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 20.5937, lng: 78.9629 }, 
        zoom: 4,
        mapId: "DEMO_MAP_ID",
        tilt: 0,
        heading: 0,
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: true,
        polylineOptions: { strokeColor: "#f59e0b", strokeOpacity: 0.7, strokeWeight: 6 }
    });

    setupAutocomplete('start');
    setupAutocomplete('destination');
    setupPinningUI();

    map.addListener("click", (e) => handleMapClick(e.latLng));
    
    // Initialize empty chart
    initChart();

    // Cinematic Intro: Zoom in from Global view to India
    setTimeout(() => {
        map.setZoom(5);
        map.setCenter({ lat: 20.5937, lng: 78.9629 });
    }, 1000);
}

/** 1. HYBRID SEARCH ENGINE (Fixes Google Auth/Billing Errors) **/
function setupAutocomplete(inputId) {
    const input = document.getElementById(inputId);
    let suggestionBox = null;

    input.addEventListener('input', async (e) => {
        const query = e.target.value;
        if (query.length < 3) { clearSuggestions(); return; }

        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`;
        try {
            const resp = await fetch(url);
            const data = await resp.json();
            showSuggestions(data, input);
        } catch (err) { console.error("Search error:", err); }
    });

    function showSuggestions(data, targetInput) {
        clearSuggestions();
        suggestionBox = document.createElement('div');
        suggestionBox.className = 'suggestions-list';
        data.forEach(item => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.innerText = item.display_name;
            div.addEventListener('click', () => {
                targetInput.value = item.display_name;
                const latlng = new google.maps.LatLng(item.lat, item.lon);
                setMarker(latlng, targetInput.id === 'start' ? 'start' : 'end');
                map.setCenter(latlng);
                map.setZoom(12);
                clearSuggestions();
            });
            suggestionBox.appendChild(div);
        });
        targetInput.parentNode.appendChild(suggestionBox);
    }
    const clearSuggestions = () => { if (suggestionBox) { suggestionBox.remove(); suggestionBox = null; } };
    document.addEventListener('click', (e) => { if (suggestionBox && !input.contains(e.target)) clearSuggestions(); });
}

/** 2. INTELLIGENT CHARTING **/
function initChart() {
    const ctx = document.getElementById('prediction-chart').getContext('2d');
    predictionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Current', '+1h', '+3h', '+6h'],
            datasets: [{
                label: 'Predicted Volume',
                data: [0, 0, 0, 0],
                borderColor: '#60a5fa',
                backgroundColor: 'rgba(96, 165, 250, 0.2)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Simulated Data',
                data: [0, 0, 0, 0],
                borderColor: '#f59e0b',
                borderDash: [5, 5],
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.1)' } } }
        }
    });
}

function updateChart(curr, f1, f3, f6, isSim) {
    const data = [curr, f1, f3, f6];
    // If not simulating, clear the simulation dataset to avoid confusion
    if (!isSim) {
        predictionChart.data.datasets[1].data = [0, 0, 0, 0];
    }
    predictionChart.data.datasets[isSim ? 1 : 0].data = data;
    predictionChart.update();
}

/** 3. PIINNING & ROUTING **/
function setupPinningUI() {
    const dropPinBtn = document.getElementById('drop-pin-btn');
    const pinSubControls = document.getElementById('pin-sub-controls');
    const pinStartBtn = document.getElementById('pin-start-btn');
    const pinDestBtn = document.getElementById('pin-dest-btn');

    dropPinBtn.addEventListener('click', () => {
        pinSubControls.classList.toggle('hidden');
        dropPinBtn.classList.toggle('active');
    });

    pinStartBtn.addEventListener('click', () => { pinMode = 'start'; setActive(pinStartBtn, pinDestBtn); });
    pinDestBtn.addEventListener('click', () => { pinMode = 'end'; setActive(pinDestBtn, pinStartBtn); });
}

function setActive(a, i) { a.classList.add('active'); i.classList.remove('active'); }

async function handleMapClick(latLng) {
    if (pinMode === 'none') return;
    setMarker(latLng, pinMode === 'start' ? 'start' : 'end');
    await reverseGeocode(latLng, pinMode === 'start' ? 'start' : 'destination');
    pinMode = 'none';
    document.querySelectorAll('.glass-btn').forEach(b => b.classList.remove('active'));
    if (startMarker && destMarker) calculateStaticRoute();
}

function setMarker(latLng, type) {
    if (type === 'start') {
        if (startMarker) startMarker.setMap(null);
        startMarker = new google.maps.Marker({ position: latLng, map: map, draggable: true, icon: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png' });
    } else {
        if (destMarker) destMarker.setMap(null);
        destMarker = new google.maps.Marker({ position: latLng, map: map, draggable: true, icon: 'https://maps.google.com/mapfiles/ms/icons/green-dot.png' });
    }
}

async function reverseGeocode(latLng, inputId) {
    const input = document.getElementById(inputId);
    input.value = "Locating...";
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ location: latLng }, (res, status) => {
        if (status === "OK") input.value = res[0].formatted_address;
    });
}

function calculateStaticRoute() {
    directionsService.route({ origin: startMarker.getPosition(), destination: destMarker.getPosition(), travelMode: 'DRIVING' }, 
    (res, status) => { if (status === "OK") directionsRenderer.setDirections(res); });
}

/** 4. INTELLIGENCE ENGINE SUBMISSION **/
document.getElementById('routing-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const csvFile = document.getElementById('csv_upload').files[0];
    const simulationMode = document.getElementById('sim-mode').checked;
    
    if (!csvFile || !startMarker || !destMarker) { alert("Pins & CSV required."); return; }

    const computeBtn = document.getElementById('find-route-btn');
    computeBtn.innerHTML = '<span class="spinner"></span> Analyzing Worldwide Traffic...';
    computeBtn.disabled = true;
    computeBtn.classList.add('loading');

    const directions = directionsRenderer.getDirections();
    if (!directions) {
        alert("Please wait for the route to appear on the map before computing.");
        computeBtn.innerText = "Compute AI Best Route";
        computeBtn.disabled = false;
        return;
    }
    const routeMeta = directions.routes.map((r, i) => ({ id: i, base_time: r.legs[0].duration.value, distance: r.legs[0].distance.value }));

    const formData = new FormData();
    formData.append("csv_file", csvFile);
    formData.append("routes_metadata", JSON.stringify(routeMeta));
    formData.append("vehicle_type", document.getElementById('vehicle_type').value);
    formData.append("simulation_mode", simulationMode);
    formData.append("day_of_week", new Date().getDay());
    formData.append("hour", new Date().getHours());

    try {
        const resp = await fetch('/api/evaluate_routes', { method: 'POST', body: formData });
        const data = await resp.json();

        if (data.error) {
            alert("Analysis Error: " + data.error);
            computeBtn.innerText = "Compute AI Best Route";
            computeBtn.disabled = false;
            return;
        }

        // Reveal Panels
        document.getElementById('intelligence-panel').classList.remove('hidden');
        document.getElementById('output-box').classList.remove('hidden');

        // Update Intelligence Metrics
        document.getElementById('f-1h').innerText = data.forecast["t+1h"];
        document.getElementById('f-3h').innerText = data.forecast["t+3h"];
        document.getElementById('f-6h').innerText = data.forecast["t+6h"];
        document.getElementById('out-peak').innerText = `${data.peak_window} (${data.is_peak ? 'BUSY' : 'CALM'})`;
        
        // Handle Anomalies
        const anomalyAlert = document.getElementById('anomaly-alert');
        if (data.anomaly.is_detected) {
            anomalyAlert.classList.remove('hidden');
            anomalyAlert.innerText = `⚠️ ANOMALY: ${data.anomaly.reason}`;
        } else {
            anomalyAlert.classList.add('hidden');
        }

        // Update Chart with real Current prediction vs Future forecast
        updateChart(data.predicted_traffic_volume, data.forecast["t+1h"], data.forecast["t+3h"], data.forecast["t+6h"], simulationMode);

        // Update Route Summary
        document.getElementById('out-from').innerText = directions.routes[0].legs[0].start_address;
        document.getElementById('out-to').innerText = directions.routes[0].legs[0].end_address;
        document.getElementById('out-time').innerText = `${Math.round(data.adjusted_time / 60)} mins (AI Weighted)`;
        document.getElementById('out-status').innerText = `Best Route Highlighed. Level: ${data.congestion_level}`;

        // Change Map Color
        const color = data.congestion_level === 'Critical' ? '#ef4444' : '#10b981';
        directionsRenderer.setOptions({ polylineOptions: { strokeColor: color, fontWeight: 8, strokeOpacity: 1.0 } });

    } catch (err) { 
        console.error(err); 
        alert("Server Connectivity Error. Make sure the backend is running.");
    }
    finally { computeBtn.innerText = "Compute AI Best Route"; computeBtn.disabled = false; }
});

document.getElementById('reset-map-btn').addEventListener('click', () => location.reload());
// initMap is managed by Google Maps script callback
