let map;
let directionsService;
let directionsRenderer;
let startAutocomplete;
let destAutocomplete;
let startMarker;
let destMarker;
let pinMode = 'none';

const startIconUrl = 'https://maps.google.com/mapfiles/ms/icons/red-dot.png';
const destIconUrl = 'https://maps.google.com/mapfiles/ms/icons/green-dot.png';

// Global error handler for Google Maps
window.gm_authFailure = function() {
    alert("Google Maps Authentication Failed!\n\nPossible reasons:\n1. Billing is not enabled in Google Cloud Console.\n2. The API Key is restricted.\n3. Places/Directions APIs are not enabled.");
};

function initMap() {
    try {
        // Initialize Map with Globe Projection
        map = new google.maps.Map(document.getElementById("map"), {
            center: { lat: 20.5937, lng: 78.9629 }, // India
            zoom: 4,
            mapId: "DEMO_MAP_ID",
            tilt: 0,
            heading: 0,
        });

        directionsService = new google.maps.DirectionsService();
        directionsRenderer = new google.maps.DirectionsRenderer({
            map: map,
            suppressMarkers: true,
            polylineOptions: {
                strokeColor: "#f59e0b",
                strokeOpacity: 0.7,
                strokeWeight: 6
            }
        });

        // --- Autocomplete Setup (Hybrid Fix) ---
        setupAutocomplete('start');
        setupAutocomplete('destination');

        // --- Pinning UI ---
        setupPinningUI();

        // --- Map Click ---
        map.addListener("click", (e) => {
            handleMapClick(e.latLng);
        });

        console.log("3D Google Globe Active.");
    } catch (err) {
        console.error("Map initialization failed:", err);
    }
}

// --- Hybrid Autocomplete Implementation (Fixes Google "Oops" Error) ---

function setupAutocomplete(inputId) {
    const input = document.getElementById(inputId);
    let suggestionBox = null;

    input.addEventListener('input', async (e) => {
        const query = e.target.value;
        if (query.length < 3) {
            clearSuggestions();
            return;
        }

        // Use free global suggestions to avoid Google Billing/API errors
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`;
        try {
            const resp = await fetch(url);
            const data = await resp.json();
            showSuggestions(data, input);
        } catch (err) {
            console.error("Suggestion fetch error:", err);
        }
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

    function clearSuggestions() {
        if (suggestionBox) {
            suggestionBox.remove();
            suggestionBox = null;
        }
    }

    document.addEventListener('click', (e) => {
        if (suggestionBox && !input.contains(e.target) && !suggestionBox.contains(e.target)) {
            clearSuggestions();
        }
    });
}

function setupPinningUI() {
    const dropPinBtn = document.getElementById('drop-pin-btn');
    const pinSubControls = document.getElementById('pin-sub-controls');
    const pinStartBtn = document.getElementById('pin-start-btn');
    const pinDestBtn = document.getElementById('pin-dest-btn');

    dropPinBtn.addEventListener('click', () => {
        pinSubControls.classList.toggle('hidden');
        dropPinBtn.classList.toggle('active');
    });

    pinStartBtn.addEventListener('click', () => {
        pinMode = (pinMode === 'start') ? 'none' : 'start';
        toggleBtn(pinStartBtn, pinMode === 'start');
        toggleBtn(pinDestBtn, false);
    });

    pinDestBtn.addEventListener('click', () => {
        pinMode = (pinMode === 'end') ? 'none' : 'end';
        toggleBtn(pinDestBtn, pinMode === 'end');
        toggleBtn(pinStartBtn, false);
    });
}

function toggleBtn(btn, active) {
    if (active) btn.classList.add('active');
    else btn.classList.remove('active');
}

async function handleMapClick(latLng) {
    if (pinMode === 'none') return;

    if (pinMode === 'start') {
        setMarker(latLng, 'start');
        await reverseGeocode(latLng, 'start');
    } else if (pinMode === 'end') {
        setMarker(latLng, 'end');
        await reverseGeocode(latLng, 'destination');
    }

    pinMode = 'none';
    const pinStartBtn = document.getElementById('pin-start-btn');
    const pinDestBtn = document.getElementById('pin-dest-btn');
    toggleBtn(pinStartBtn, false);
    toggleBtn(pinDestBtn, false);
    
    if (startMarker && destMarker) calculateStaticRoute();
}

function setMarker(latLng, type) {
    if (type === 'start') {
        if (startMarker) startMarker.setMap(null);
        startMarker = new google.maps.Marker({ position: latLng, map: map, draggable: true, icon: startIconUrl });
        startMarker.addListener('dragend', () => { 
            reverseGeocode(startMarker.getPosition(), 'start'); 
            calculateStaticRoute();
        });
    } else {
        if (destMarker) destMarker.setMap(null);
        destMarker = new google.maps.Marker({ position: latLng, map: map, draggable: true, icon: destIconUrl });
        destMarker.addListener('dragend', () => { 
            reverseGeocode(destMarker.getPosition(), 'destination'); 
            calculateStaticRoute();
        });
    }
}

async function reverseGeocode(latLng, inputId) {
    const geocoder = new google.maps.Geocoder();
    const input = document.getElementById(inputId);
    input.value = "Locating...";
    geocoder.geocode({ location: latLng }, (results, status) => {
        if (status === "OK" && results[0]) input.value = results[0].formatted_address;
        else input.value = `${latLng.lat().toFixed(5)}, ${latLng.lng().toFixed(5)}`;
    });
}

function calculateStaticRoute() {
    if (!startMarker || !destMarker) return;
    directionsService.route({
        origin: startMarker.getPosition(),
        destination: destMarker.getPosition(),
        travelMode: google.maps.TravelMode.DRIVING
    }, (response, status) => {
        if (status === "OK") directionsRenderer.setDirections(response);
    });
}

// AI Analysis Submission
document.getElementById('routing-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const csvFile = document.getElementById('csv_upload').files[0];
    const vehicleType = document.getElementById('vehicle_type').value;

    if (!csvFile || !startMarker || !destMarker) {
        alert("Please select points and upload traffic data.");
        return;
    }

    const computeBtn = document.getElementById('find-route-btn');
    computeBtn.innerText = "Analyzing 3D Globe Traffic...";
    computeBtn.disabled = true;

    const directions = directionsRenderer.getDirections();
    if (!directions) { alert("Calculate route first."); computeBtn.disabled = false; return; }

    const route = directions.routes[0].legs[0];
    const routesMetadata = directions.routes.map((r, i) => ({
        id: i,
        distance: r.legs[0].distance.value,
        base_time: r.legs[0].duration.value
    }));

    const formData = new FormData();
    formData.append("csv_file", csvFile);
    formData.append("routes_metadata", JSON.stringify(routesMetadata));
    formData.append("vehicle_type", vehicleType);
    formData.append("day_of_week", new Date().getDay());
    formData.append("hour", new Date().getHours());

    try {
        const resp = await fetch('/api/evaluate_routes', { method: 'POST', body: formData });
        const data = await resp.json();

        document.getElementById('output-box').classList.remove('hidden');
        document.getElementById('out-from').innerText = route.start_address;
        document.getElementById('out-to').innerText = route.end_address;
        document.getElementById('out-distance').innerText = route.distance.text;
        document.getElementById('out-time').innerText = `${Math.round(data.adjusted_time / 60)} mins (AI Optimized)`;
        document.getElementById('out-weather').innerText = data.weather_condition;
        document.getElementById('out-vehicle').innerText = vehicleType.toUpperCase();
        document.getElementById('out-status').innerText = `Best Route Colored GREEN. Confidence: ${(data.ml_confidence * 100).toFixed(1)}%`;

        directionsRenderer.setOptions({ polylineOptions: { strokeColor: "#10b981", strokeOpacity: 1.0, strokeWeight: 8 } });
        
    } catch (err) { console.error(err); }
    finally { computeBtn.innerText = "Compute AI Best Route"; computeBtn.disabled = false; }
});

document.getElementById('reset-map-btn').addEventListener('click', () => { location.reload(); });
