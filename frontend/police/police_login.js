// Toggle password visibility
const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("password");

togglePassword.addEventListener("click", () => {
    const type =
        passwordInput.getAttribute("type") === "password"
        ? "text"
        : "password";
    passwordInput.setAttribute("type", type);

    const icon = togglePassword.querySelector("i");
    if (type === "text") {
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
});

// Function to show alert message
function showAlert(message, type = "info") {
    const alertContainer = document.getElementById("alertContainer");
    alertContainer.innerHTML = "";

    const alertDiv = document.createElement("div");
    alertDiv.className = `alert ${type}`;
    alertDiv.innerHTML = `
        <i class="fas ${
            type === "error"
            ? "fa-exclamation-circle"
            : type === "success"
            ? "fa-check-circle"
            : "fa-info-circle"
        }"></i>
        ${message}
    `;
    alertDiv.style.display = "block";

    alertContainer.appendChild(alertDiv);

    if (type !== "error") {
        setTimeout(() => {
            alertDiv.style.display = "none";
        }, 5000);
    }
}

// Navigation function
function goToLandingPage() {
    window.location.href = "/";
}

// Login form submission
document
    .getElementById("loginForm")
    .addEventListener("submit", async (e) => {
        e.preventDefault();

        const loginButton = document.getElementById("loginButton");
        const originalText = loginButton.textContent;

        // Set loading state
        loginButton.classList.add("loading");
        loginButton.textContent = "Logging in...";
        loginButton.disabled = true;

        const data = {
            identifier: document.getElementById("email").value,
            password: document.getElementById("password").value,
        };

        // Basic validation
        if (!data.identifier || !data.password) {
            showAlert("Please fill in all fields", "error");

            loginButton.classList.remove("loading");
            loginButton.textContent = originalText;
            loginButton.disabled = false;
            return;
        }

        try {
            const res = await fetch("http://127.0.0.1:8000/users/login/police", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });

            const result = await res.json();

            if (res.ok) {
                showAlert(
                    `Welcome Officer ${result.message.split(" ")[1]}!`,
                    "success"
                );

                // Store user data in localStorage
                localStorage.setItem("jwt", result.access_token);
                localStorage.setItem("refreshToken", result.refresh_token); // Store refresh token
                localStorage.setItem("userRole", result.role);
                localStorage.setItem("userId", result.user_id);
                localStorage.setItem("username", result.message.split(" ")[1]);

                document.getElementById("loginForm").reset();

                // Redirect to police dashboard after 2 seconds
                setTimeout(() => {
                    if (result.role === "police") {
                        window.location.href = "../police/map_dashboard.html";
                    } else {
                        window.location.href = "../landing.html";
                    }
                }, 2000);
            } else {
                showAlert(result.detail || "Login failed", "error");

                loginButton.classList.remove("loading");
                loginButton.textContent = originalText;
                loginButton.disabled = false;
            }
        } catch (err) {
            console.error(err);
            showAlert("Error connecting to server.", "error");

            loginButton.classList.remove("loading");
            loginButton.textContent = originalText;
            loginButton.disabled = false;
        }
    });

// Forgot password link
document
    .querySelector(".forgot-password")
    .addEventListener("click", (e) => {
        e.preventDefault();
        showAlert(
            "Please contact your department administrator for password reset.",
            "info"
        );
    });