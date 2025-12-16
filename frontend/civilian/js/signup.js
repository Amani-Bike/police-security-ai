// Variable to store uploaded photo data
let uploadedPhotoData = null;

// DOM elements
let photoPreview, uploadedPhoto, photoPlaceholder, photoUpload, removePhotoBtn;
let togglePassword, passwordInput;

// Initialize DOM elements when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing elements...');
    
    // Initialize photo upload elements
    photoPreview = document.getElementById("photoPreview");
    uploadedPhoto = document.getElementById("uploadedPhoto");
    photoPlaceholder = document.getElementById("photoPlaceholder");
    photoUpload = document.getElementById("photoUpload");
    removePhotoBtn = document.getElementById("removePhotoBtn");
    
    // Initialize password toggle
    togglePassword = document.getElementById("togglePassword");
    passwordInput = document.getElementById("password");
    
    // Set up event listeners
    setupEventListeners();
    
    console.log('Elements initialized successfully');
});

// Set up all event listeners
function setupEventListeners() {
    // Toggle password visibility
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener("click", togglePasswordVisibility);
    }
    
    // Photo upload functionality
    if (photoPreview) {
        photoPreview.addEventListener("click", () => {
            if (photoUpload) photoUpload.click();
        });
    }
    
    if (photoUpload) {
        photoUpload.addEventListener("change", handlePhotoUpload);
    }
    
    if (removePhotoBtn) {
        removePhotoBtn.addEventListener("click", removePhoto);
    }
    
    // Full name validation
    const usernameInput = document.getElementById('username');
    const usernameStatus = document.getElementById('usernameStatus');
    
    if (usernameInput && usernameStatus) {
        usernameInput.addEventListener('input', validateFullName);
    }
    
    // Form submission
    const signupForm = document.getElementById("signupForm");
    if (signupForm) {
        signupForm.addEventListener("submit", handleFormSubmit);
    }
}

// Toggle password visibility
function togglePasswordVisibility() {
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
}

// Full name validation
function validateFullName() {
    const usernameInput = document.getElementById('username');
    const usernameStatus = document.getElementById('usernameStatus');
    
    if (!usernameInput || !usernameStatus) return;
    
    const fullName = usernameInput.value.trim();
    const namePattern = /^[A-Za-zÀ-ÿ\s\-'.]+$/;
    
    if (fullName === '') {
        usernameStatus.textContent = '';
        usernameStatus.style.color = '';
        return;
    }
    
    // Check for minimum length (at least 2 characters)
    if (fullName.length < 2) {
        usernameStatus.textContent = 'Too short';
        usernameStatus.style.color = '#fbbf24';
        return;
    }
    
    // Check for maximum length
    if (fullName.length > 50) {
        usernameStatus.textContent = 'Too long (max 50)';
        usernameStatus.style.color = '#f87171';
        return;
    }
    
    // Check for valid characters
    if (!namePattern.test(fullName)) {
        usernameStatus.textContent = 'Invalid characters';
        usernameStatus.style.color = '#f87171';
        return;
    }
    
    // Check for consecutive spaces
    if (/\s{2,}/.test(fullName)) {
        usernameStatus.textContent = 'Remove extra spaces';
        usernameStatus.style.color = '#fbbf24';
        return;
    }
    
    // Check if name contains at least one space (for first and last name)
    if (!/\s/.test(fullName)) {
        usernameStatus.textContent = 'Consider adding last name';
        usernameStatus.style.color = '#fbbf24';
    } else {
        usernameStatus.textContent = '✓ Valid';
        usernameStatus.style.color = '#4ade80';
    }
}

// Handle photo upload
function handlePhotoUpload(e) {
    if (e.target.files.length > 0) {
        const file = e.target.files[0];

        // Validate file type
        if (!file.type.match("image.*")) {
            showAlert("Please select an image file (JPG, PNG, etc.)", "error");
            return;
        }

        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            showAlert("Image size should be less than 5MB", "error");
            return;
        }

        const reader = new FileReader();

        reader.onload = function (event) {
            // Display the uploaded image
            uploadedPhoto.src = event.target.result;
            uploadedPhoto.style.display = "block";
            photoPlaceholder.style.display = "none";
            removePhotoBtn.style.display = "flex";

            // Store the base64 image data for later use
            uploadedPhotoData = event.target.result;

            // Add border glow effect
            photoPreview.style.boxShadow = "0 0 20px rgba(59, 130, 246, 0.5)";
        };

        reader.readAsDataURL(file);
    }
}

// Remove photo
function removePhoto(e) {
    e.stopPropagation();
    uploadedPhoto.src = "";
    uploadedPhoto.style.display = "none";
    photoPlaceholder.style.display = "flex";
    removePhotoBtn.style.display = "none";
    photoUpload.value = "";
    uploadedPhotoData = null;
    photoPreview.style.boxShadow = "none";
}

// Show alert message
function showAlert(message, type = "info") {
    const alertContainer = document.getElementById("alertContainer");
    if (!alertContainer) {
        console.log("Alert container not found, using browser alert:", message);
        alert(message);
        return;
    }
    
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

    // Auto remove after 5 seconds for non-error alerts
    if (type !== "error") {
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    }
}

// Save user data to localStorage
function saveUserData(userData) {
    try {
        // Store user data in localStorage
        localStorage.setItem("safetynet_user", JSON.stringify(userData));

        // If there's a photo, also store it separately for easy access
        if (userData.photo) {
            localStorage.setItem("safetynet_profile_photo", userData.photo);
        }

        // Also store in sessionStorage for immediate use
        sessionStorage.setItem("current_user", JSON.stringify(userData));
        
        console.log("User data saved to localStorage");
    } catch (error) {
        console.error("Error saving user data:", error);
    }
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    console.log("Form submission started");

    // Get form values
    const fullName = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const age = document.getElementById("age").value;
    const gender = document.getElementById("gender").value;
    const district = document.getElementById("district").value.trim();

    // Basic validation
    if (!fullName || !email || !password || !district) {
        showAlert("Please fill in all required fields (Full Name, Email, Password, District)", "error");
        return;
    }

    if (password.length < 8) {
        showAlert("Password must be at least 8 characters", "error");
        return;
    }

    // Email validation
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
        showAlert("Please enter a valid email address", "error");
        return;
    }

    // Full name validation pattern
    const namePattern = /^[A-Za-zÀ-ÿ\s\-'.]+$/;
    if (!namePattern.test(fullName)) {
        showAlert('Full name can only contain letters, spaces, hyphens, apostrophes, and periods.', 'error');
        return;
    }

    // Show loading state
    const registerButton = document.getElementById("registerButton");
    const originalText = registerButton.textContent;
    registerButton.classList.add("loading");
    registerButton.textContent = "Creating Account...";
    registerButton.disabled = true;

    // Create data object for civilian signup
    const data = {
        username: fullName,
        email: email,
        password: password,
        full_name: fullName,  // Backend expects this field for CivilianSignupRequest
        role: "civilian",
        age: parseInt(age), // Convert to integer
        gender: gender,
        district: district
        // Note: We're NOT sending photo to backend - it's stored in localStorage only
    };

    console.log("Sending data to backend:", { ...data, password: "***" });

    try {
        const res = await fetch("http://127.0.0.1:8000/users/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        console.log("Response status:", res.status);
        
        // Check if response is JSON
        const contentType = res.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            const text = await res.text();
            console.error("Non-JSON response:", text);
            throw new Error("Server returned non-JSON response");
        }

        const result = await res.json();
        console.log("Response data:", result);

        if (res.ok) {
            showAlert(`Signup successful! Welcome ${result.username}. Redirecting to login...`, "success");
            
            // Save user data to localStorage (including photo)
            const userData = {
                user_id: result.user_id,
                username: result.username,
                email: result.email,
                role: result.role,
                age: data.age,
                gender: data.gender,
                district: data.district,
                photo: uploadedPhotoData  // Store photo locally only
            };
            
            saveUserData(userData);
            
            // Reset form
            document.getElementById("signupForm").reset();
            
            // Reset photo preview
            if (uploadedPhoto) {
                uploadedPhoto.src = "";
                uploadedPhoto.style.display = "none";
            }
            if (photoPlaceholder) {
                photoPlaceholder.style.display = "flex";
            }
            if (removePhotoBtn) {
                removePhotoBtn.style.display = "none";
            }
            if (photoPreview) {
                photoPreview.style.boxShadow = "none";
            }
            uploadedPhotoData = null;
            
            // Reset validation status
            const usernameStatus = document.getElementById('usernameStatus');
            if (usernameStatus) {
                usernameStatus.textContent = '';
                usernameStatus.style.color = '';
            }
            
            // Redirect to login page after 2 seconds
            setTimeout(() => {
                console.log("Redirecting to login.html");
                window.location.href = "login.html";
            }, 2000);
            
        } else {
            // Handle error response
            let errorMessage = "Signup failed";
            if (result.detail) {
                errorMessage = typeof result.detail === 'string' ? result.detail : JSON.stringify(result.detail);
            } else if (result.message) {
                errorMessage = result.message;
            } else if (typeof result === 'string') {
                errorMessage = result;
            }
            showAlert(errorMessage, "error");
            console.error("Signup failed:", result);
            
            // Reset button state
            registerButton.classList.remove("loading");
            registerButton.textContent = originalText;
            registerButton.disabled = false;
        }
    } catch (err) {
        console.error("Signup error:", err);
        
        if (err instanceof SyntaxError) {
            showAlert("Server returned invalid response format. Please try again.", "error");
        } else if (err.name === 'TypeError' && err.message.includes('fetch')) {
            showAlert("Unable to connect to the server. Please make sure the backend is running at http://127.0.0.1:8000", "error");
        } else {
            showAlert("An unexpected error occurred: " + err.message, "error");
        }
        
        // Reset button state
        registerButton.classList.remove("loading");
        registerButton.textContent = originalText;
        registerButton.disabled = false;
    }
}

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Page fully loaded');
    });
} else {
    console.log('DOM already loaded');
}