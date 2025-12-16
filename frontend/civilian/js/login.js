// Toggle password visibility
const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("password");

if (togglePassword && passwordInput) {
    togglePassword.addEventListener("click", () => {
        const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
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
}

// Function to show alert message
function showAlert(message, type = "info") {
    const alertContainer = document.getElementById("alertContainer");
    if (!alertContainer) return;

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

    // Auto remove after 5 seconds for non-error messages
    if (type !== "error") {
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.style.display = "none";
            }
        }, 5000);
    }
}

// Login form submission
document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const loginButton = document.getElementById("loginButton");
    if (!loginButton) return;

    const originalText = loginButton.textContent;

    // Set loading state
    loginButton.classList.add("loading");
    loginButton.textContent = "Logging in...";
    loginButton.disabled = true;

    const data = {
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
    };

    // Basic client-side validation
    if (!data.email || !data.password) {
        showAlert("Please fill in all fields", "error");

        // Reset button state
        loginButton.classList.remove("loading");
        loginButton.textContent = originalText;
        loginButton.disabled = false;
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:8000/users/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        if (res.ok) {
            showAlert(`Welcome ${result.message.split(" ")[1]}!`, "success");

            // Store user data in localStorage
            localStorage.setItem("jwt", result.access_token);
            localStorage.setItem("refreshToken", result.refresh_token); // Store refresh token
            localStorage.setItem("userRole", result.role);
            localStorage.setItem("userId", result.user_id);
            localStorage.setItem("username", result.message.split(" ")[1]);

            // Reset form
            document.getElementById("loginForm").reset();

            // Show the "already logged in" section instead of immediate redirect
            showLoggedInState(result.message.split(" ")[1], result.role);
        } else {
            showAlert(result.detail || "Login failed", "error");

            // Reset button state
            loginButton.classList.remove("loading");
            loginButton.textContent = originalText;
            loginButton.disabled = false;
        }
    } catch (err) {
        console.error(err);
        showAlert(
          "Error connecting to server. Please try again later.",
          "error"
        );

        // Reset button state
        loginButton.classList.remove("loading");
        loginButton.textContent = originalText;
        loginButton.disabled = false;
    }
});

// Show logged in state (user has option to continue or logout)
function showLoggedInState(username, role) {
    // Hide login form
    const loginForm = document.getElementById("loginForm");
    if (loginForm) loginForm.style.display = "none";

    // Show already logged in section
    const loggedInSection = document.getElementById("alreadyLoggedIn");
    if (loggedInSection) {
        document.getElementById("loggedInUsername").textContent = username;
        loggedInSection.style.display = "block";

        // Store role for later use
        loggedInSection.dataset.userRole = role;
    }

    // Reset login button
    const loginButton = document.getElementById("loginButton");
    if (loginButton) {
        loginButton.classList.remove("loading");
        loginButton.textContent = "Login";
        loginButton.disabled = false;
    }
}

// Continue to dashboard button
const continueButton = document.getElementById("continueToDashboard");
if (continueButton) {
    continueButton.addEventListener("click", () => {
        const loggedInSection = document.getElementById("alreadyLoggedIn");
        if (loggedInSection) {
            const role = loggedInSection.dataset.userRole;

            if (role === "police") {
                window.location.href = "../police/map_dashboard.html";
            } else {
                window.location.href = "./chat.html";
            }
        }
    });
}

// Logout button
const logoutButton = document.getElementById("logoutButton");
if (logoutButton) {
    logoutButton.addEventListener("click", () => {
        // Clear localStorage
        localStorage.removeItem("jwt");
        localStorage.removeItem("userRole");
        localStorage.removeItem("userId");
        localStorage.removeItem("username");

        // Show login form again
        const loginForm = document.getElementById("loginForm");
        const loggedInSection = document.getElementById("alreadyLoggedIn");
        if (loginForm) loginForm.style.display = "block";
        if (loggedInSection) loggedInSection.style.display = "none";

        showAlert("You have been logged out successfully.", "success");
    });
}

// Forgot password link
const forgotPasswordLink = document.querySelector(".forgot-password");
if (forgotPasswordLink) {
    forgotPasswordLink.addEventListener("click", (e) => {
        e.preventDefault();
        showAlert(
          "Password reset functionality will be available soon.",
          "info"
        );
    });
}

// Create account button
const createAccountBtn = document.querySelector(".create-account-btn");
if (createAccountBtn) {
    createAccountBtn.addEventListener("click", (e) => {
        showAlert("Navigating to Account creation page...", "info");
        // The browser's default action (navigation) will now proceed.
    });
}

// Check if user is already logged in on page load
function checkAuthStatus() {
    const jwt = localStorage.getItem("jwt");
    const username = localStorage.getItem("username");
    const role = localStorage.getItem("userRole");

    if (jwt && username && role) {
        // User is already logged in, show the logged in state
        showLoggedInState(username, role);
    }
}

// Check auth status on page load (but don't auto-redirect)
window.addEventListener("load", checkAuthStatus);

// Mobile Menu Toggle (if needed)
const mobileMenuBtn = document.getElementById("mobileMenuBtn");
const navLinks = document.getElementById("navLinks");

if (mobileMenuBtn && navLinks) {
    mobileMenuBtn.addEventListener("click", () => {
      navLinks.classList.toggle("active");
      const icon = mobileMenuBtn.querySelector("i");
      if (navLinks.classList.contains("active")) {
        icon.classList.remove("fa-bars");
        icon.classList.add("fa-times");
      } else {
        icon.classList.remove("fa-times");
        icon.classList.add("fa-bars");
      }
    });

    // Close mobile menu when clicking on a link
    document.querySelectorAll(".nav-links a").forEach((link) => {
      link.addEventListener("click", () => {
        navLinks.classList.remove("active");
        mobileMenuBtn.querySelector("i").classList.remove("fa-times");
        mobileMenuBtn.querySelector("i").classList.add("fa-bars");
      });
    });
}