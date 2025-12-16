// Global variables
let map;
let emergencyMarkers = [];
const token = localStorage.getItem("jwt");

// Malawi coordinates
const MALAWI_BOUNDS = [
    [-17.5, 32.5], // Southwest
    [-9.0, 36.0]   // Northeast
];

// Emergency type colors and icons
const emergencyIcons = {
    medical: L.divIcon({
        html: '🏥',
        className: 'medical-emergency',
        iconSize: [30, 30]
    }),
    crime: L.divIcon({
        html: '🚨',
        className: 'crime-emergency',
        iconSize: [30, 30]
    }),
    fire: L.divIcon({
        html: '🔥',
        className: 'fire-emergency',
        iconSize: [30, 30]
    }),
    accident: L.divIcon({
        html: '🚑',
        className: 'accident-emergency',
        iconSize: [30, 30]
    }),
    other: L.divIcon({
        html: '⚠️',
        className: 'other-emergency',
        iconSize: [30, 30]
    })
};

// Check authentication
function checkAuth() {
    if (!token) {
        alert("Please login first");
        window.location.href = "police_login.html";
        return false;
    }
    return true;
}

function logout() {
    localStorage.removeItem("jwt");
    localStorage.removeItem("userRole");
    localStorage.removeItem("userId");
    localStorage.removeItem("username");
    window.location.href = "police_login.html";
}

// Update status message
function updateStatus(message, type = '') {
    const statusDiv = document.getElementById('status');
    if (statusDiv) {
        statusDiv.innerText = message;
        statusDiv.className = type;
    }
}

// Initialize map
function initMap() {
    console.log("Initializing Malawi emergency map...");

    if (!checkAuth()) return;

    try {
        // Ensure the map element has visible dimensions
        const mapElement = document.getElementById('map');
        if (mapElement) {
            // Set minimum dimensions to ensure visibility
            mapElement.style.height = '500px';
            mapElement.style.width = '100%';
            mapElement.style.minHeight = '400px';
        }

        // Create map centered on Malawi with bounds restriction
        map = L.map('map', {
            maxBounds: MALAWI_BOUNDS,
            maxBoundsViscosity: 1.0,
            minZoom: 6,
            maxZoom: 18
        }).setView([-13.2543, 34.3015], 7); // Center of Malawi

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            attribution: '© OpenStreetMap contributors',
            noWrap: true
        }).addTo(map);

        // Invalidate size to ensure proper rendering
        setTimeout(() => {
            if (map) {
                map.invalidateSize();
                console.log("Map size invalidated to ensure proper rendering");
            }
        }, 100);

        console.log("Malawi emergency map initialized successfully");
        updateStatus('Emergency map loaded. Fetching active emergencies...', 'success');

        // Load active emergencies
        loadActiveEmergencies();

    } catch (error) {
        console.error("Map initialization error:", error);
        updateStatus(`Map error: ${error.message}`, 'error');
    }
}

// Load active emergencies for map display
async function loadActiveEmergencies() {
    if (!map) {
        console.error("Map not initialized");
        return;
    }

    try {
        updateStatus('Loading active emergencies...');
        console.log("Fetching active emergencies...");

        const response = await makeAuthenticatedRequest("http://127.0.0.1:8000/emergency/active-emergencies", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        console.log("Response status:", response.status);

        if (response.status === 401) {
            alert("Session expired. Please login again.");
            window.location.href = "police_login.html";
            return;
        }

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const emergencies = await response.json();
        console.log("Active emergencies received:", emergencies);

        // Clear existing markers
        emergencyMarkers.forEach(marker => map.removeLayer(marker));
        emergencyMarkers = [];

        // Filter emergencies within Malawi
        const validEmergencies = emergencies.filter(emergency =>
            emergency.latitude && emergency.longitude &&
            !isNaN(emergency.latitude) && !isNaN(emergency.longitude)
        );

        console.log(`Found ${validEmergencies.length} active emergencies`);

        if (validEmergencies.length === 0) {
            updateStatus('No active emergencies found.', 'warning');
            return;
        }

        // Create bounds to fit all markers
        const bounds = L.latLngBounds();

        // Add markers for each emergency
        validEmergencies.forEach(emergency => {
            const latLng = [emergency.latitude, emergency.longitude];
            const icon = emergencyIcons[emergency.emergency_type] || emergencyIcons.other;

            const marker = L.marker(latLng, { icon: icon })
                .addTo(map)
                .bindPopup(`
                    <div style="min-width: 250px;">
                        <h3>🚨 ${emergency.emergency_type.toUpperCase()} EMERGENCY</h3>
                        <p><strong>Reporter:</strong> ${emergency.username}</p>
                        <p><strong>User ID:</strong> ${emergency.user_id}</p>
                        <p><strong>Description:</strong> ${emergency.description}</p>
                        <p><strong>Location:</strong><br>
                        Lat: ${emergency.latitude.toFixed(6)}<br>
                        Lng: ${emergency.longitude.toFixed(6)}</p>
                        <p><strong>Reported:</strong> ${new Date(emergency.created_at).toLocaleString()}</p>
                        <div style="margin-top: 10px;">
                            <button onclick="updateEmergencyStatus(${emergency.id}, 'in_progress')" style="background: #ffc107; color: black; border: none; padding: 5px 10px; border-radius: 3px; margin-right: 5px;">Mark In Progress</button>
                            <button onclick="updateEmergencyStatus(${emergency.id}, 'resolved')" style="background: #28a745; color: white; border: none; padding: 5px 10px; border-radius: 3px;">Mark Resolved</button>
                        </div>
                    </div>
                `);

            emergencyMarkers.push(marker);
            bounds.extend(latLng);
        });

        // Fit map to show all markers with padding
        if (validEmergencies.length > 0) {
            map.fitBounds(bounds, { padding: [20, 20] });
        }

        updateStatus(`✅ Loaded ${validEmergencies.length} active emergencies. Click refresh to update.`, 'success');

    } catch (err) {
        console.error("Error loading active emergencies:", err);

        if (err.message.includes('Failed to fetch')) {
            updateStatus('❌ Error: Cannot connect to server. Make sure the backend is running on 127.0.0.1:8000', 'error');
        } else {
            updateStatus(`❌ Error: ${err.message}`, 'error');
        }
    }
}

// Update emergency status
async function updateEmergencyStatus(emergencyId, newStatus) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/emergency/emergencies/${emergencyId}/status`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ status: newStatus })
        });

        if (response.ok) {
            alert(`Emergency marked as ${newStatus}`);
            // Refresh the emergencies
            loadActiveEmergencies();
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (err) {
        console.error("Error updating emergency status:", err);
        alert("Error updating emergency status");
    }
}

// Auto-refresh every 30 seconds
function startAutoRefresh() {
    setInterval(() => {
        if (map) {
            loadActiveEmergencies();
        }
    }, 30000);
}

// Profile dropdown functionality
function setupProfileDropdown() {
    const profileBtn = document.getElementById('profileDropdownBtn');
    const profileDropdown = document.getElementById('profileDropdown');

    if (!profileBtn || !profileDropdown) {
        console.warn("Profile dropdown elements not found");
        return;
    }

    // Toggle dropdown
    profileBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        profileDropdown.classList.toggle('show');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!profileBtn.contains(e.target) && !profileDropdown.contains(e.target)) {
            profileDropdown.classList.remove('show');
        }
    });
}

// Navigation function
function goToLandingPage() {
    window.location.href = "/";
}

// Wait for the page to fully load before initializing
window.addEventListener('load', function() {
    console.log("Page fully loaded, checking for map element and Leaflet...");

    // Small delay to ensure all elements are rendered
    setTimeout(() => {
        // Check if the map element exists
        const mapElement = document.getElementById('map');
        if (!mapElement) {
            console.error("Map element with id 'map' not found");
            updateStatus('❌ Error: Map element not found on page.', 'error');
            return;
        }

        // Check if Leaflet is loaded
        if (typeof L === 'undefined') {
            console.error("Leaflet library not loaded");
            updateStatus('❌ Error: Leaflet map library failed to load. Check your internet connection.', 'error');
            return;
        }

        console.log("All required elements found, initializing map...");

        // Initialize the map
        initMap();

        // Setup profile dropdown
        setupProfileDropdown();

        // Start auto-refresh
        startAutoRefresh();
    }, 100); // Small delay to ensure DOM is ready
});