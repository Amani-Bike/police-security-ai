const token = localStorage.getItem("jwt");
const chatContainer = document.getElementById("chatContainer");
const chatBox = document.getElementById("chatBox");

// Check if user is logged in
if (!token) {
    alert("Please login first");
    window.location.href = "login.html";
}

// Function to add a message to the chat
function addMessage(text, sender) {
    const div = document.createElement("div");
    div.classList.add("message", sender);
    div.innerText = text;
    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Send chat message
document.getElementById("sendChatBtn").addEventListener("click", async () => {
    const message = chatBox.value.trim();
    if (!message) return;

    addMessage(message, "user");
    chatBox.value = "";

    try {
        const res = await fetch("http://localhost:8000/chat/send", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ message })
        });

        const result = await res.json();
        if (res.ok) {
            addMessage(result.reply, "ai");
        } else {
            addMessage(result.detail || "Error from AI", "ai");
        }
    } catch (err) {
        console.error("Chat fetch error:", err);
        addMessage("Error: could not get response from AI.", "ai");
    }
});

// Update location with better error handling
document.getElementById("getLocationBtn").addEventListener("click", async () => {
    if (!navigator.geolocation) {
        alert("Geolocation not supported by your browser.");
        return;
    }

    const statusDiv = document.getElementById("locationStatus");
    statusDiv.innerText = "Getting your location...";

    navigator.geolocation.getCurrentPosition(async (position) => {
        const data = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
        };
        
        console.log("Sending location:", data);
        statusDiv.innerText = "Sending location to server...";

        try {
            const res = await fetch("http://localhost:8000/auth/update-location", {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(data)
            });

            console.log("Location update response status:", res.status);

            if (res.status === 401) {
                alert("Session expired. Please login again.");
                window.location.href = "login.html";
                return;
            }

            const result = await res.json();
            console.log("Update location response:", result);

            if (res.ok) {
                statusDiv.innerText = `Location updated: ${result.latitude}, ${result.longitude}`;
                statusDiv.style.color = "green";
            } else {
                statusDiv.innerText = `Failed: ${result.detail || "Unknown error"}`;
                statusDiv.style.color = "red";
            }
        } catch (err) {
            console.error("Location fetch error:", err);
            statusDiv.innerText = "Error: Could not connect to server. Check if backend is running on localhost:8000";
            statusDiv.style.color = "red";
        }
    }, (err) => {
        console.error("Geolocation error:", err);
        let errorMessage = "Could not get your location. ";
        switch(err.code) {
            case err.PERMISSION_DENIED:
                errorMessage += "Location permission denied.";
                break;
            case err.POSITION_UNAVAILABLE:
                errorMessage += "Location information unavailable.";
                break;
            case err.TIMEOUT:
                errorMessage += "Location request timed out.";
                break;
            default:
                errorMessage += "Unknown error.";
        }
        statusDiv.innerText = errorMessage;
        statusDiv.style.color = "red";
    }, {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
    });
});