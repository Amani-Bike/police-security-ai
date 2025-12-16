// Variable to store uploaded photo data
let uploadedPhotoData = null;

// Toggle password visibility
const togglePassword = document.getElementById('togglePassword');
const passwordInput = document.getElementById('password');

togglePassword.addEventListener('click', () => {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);

    const icon = togglePassword.querySelector('i');
    if (type === 'text') {
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
});

// Photo upload functionality - Click on circle to upload
const photoPreview = document.getElementById("photoPreview");
const uploadedPhoto = document.getElementById("previewImage");
const photoPlaceholder = document.getElementById("photoPlaceholder");
const photoUpload = document.getElementById("badgeUpload");
const removePhotoBtn = document.getElementById("removePhotoBtn");

photoPreview.addEventListener("click", () => {
    photoUpload.click();
});

photoUpload.addEventListener("change", (e) => {
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
});

// Remove photo functionality
removePhotoBtn.addEventListener("click", (e) => {
    e.stopPropagation(); // Prevent triggering the photo preview click
    uploadedPhoto.src = "";
    uploadedPhoto.style.display = "none";
    photoPlaceholder.style.display = "flex";
    removePhotoBtn.style.display = "none";
    photoUpload.value = "";
    uploadedPhotoData = null;
    photoPreview.style.boxShadow = "none";
});

// Navigation function
function goToLandingPage() {
    window.location.href = "/";
}

// Function to show alert message
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    alertContainer.innerHTML = '';

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${type}`;
    alertDiv.innerHTML = `
        <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : type === 'success' ? 'fa-check-circle' : 'fa-info-circle'}"></i>
        ${message}
    `;
    alertDiv.style.display = 'block';

    alertContainer.appendChild(alertDiv);

    if (type !== 'error') {
        setTimeout(() => {
            alertDiv.style.display = 'none';
        }, 5000);
    }
}

// Form submission
document.getElementById("signupForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const registerButton = document.getElementById('registerButton');
    const originalText = registerButton.textContent;

    // Set loading state
    registerButton.classList.add('loading');
    registerButton.textContent = 'Registering...';
    registerButton.disabled = true;

    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const badgeId = document.getElementById("badgeId").value;
    const age = document.getElementById("age").value;
    const district = document.getElementById("district").value;

    // Basic validation
    if (!username || !email || !password || !badgeId || !age || !district) {
        showAlert("Please fill in all required fields", "error");

        registerButton.classList.remove('loading');
        registerButton.textContent = originalText;
        registerButton.disabled = false;
        return;
    }

    if (password.length < 8) {
        showAlert("Password must be at least 8 characters", "error");

        registerButton.classList.remove('loading');
        registerButton.textContent = originalText;
        registerButton.disabled = false;
        return;
    }

    const data = {
        username,
        identifier: email,
        password,
        full_name: username, // Use the username as full_name
        badge_id: badgeId,
        age: parseInt(age),
        district
    };

    try {
        const res = await fetch("http://127.0.0.1:8000/users/signup/police", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        if (res.ok) {
            showAlert("Signup successful! Redirecting to login...", "success");

            // Clear inputs
            document.getElementById("username").value = "";
            document.getElementById("email").value = "";
            document.getElementById("password").value = "";
            document.getElementById("badgeId").value = "";
            document.getElementById("age").value = "";
            document.getElementById("district").value = "";

            // Reset photo
            uploadedPhoto.src = "";
            uploadedPhoto.style.display = "none";
            photoPlaceholder.style.display = "flex";
            removePhotoBtn.style.display = "none";
            photoUpload.value = "";
            uploadedPhotoData = null;
            photoPreview.style.boxShadow = "none";

            // Redirect after 2 seconds
            setTimeout(() => {
                window.location.href = "police_login.html";
            }, 2000);

        } else {
            showAlert(result.detail || "Signup failed", "error");

            registerButton.classList.remove('loading');
            registerButton.textContent = originalText;
            registerButton.disabled = false;
        }
    } catch (err) {
        console.error(err);
        showAlert("Error connecting to server.", "error");

        registerButton.classList.remove('loading');
        registerButton.textContent = originalText;
        registerButton.disabled = false;
    }
});