// Token management utility for automatic refresh
class TokenManager {
    constructor() {
        this.refreshThreshold = 5 * 60 * 1000; // 5 minutes before expiration
        this.refreshInterval = null;
    }

    // Check if access token is expired or will expire soon
    isTokenExpiringSoon() {
        const token = localStorage.getItem("jwt");
        if (!token) return true;

        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const exp = payload.exp * 1000; // Convert to milliseconds
            const now = Date.now();
            const timeUntilExpiry = exp - now;

            console.log(`Time until expiry: ${timeUntilExpiry / 1000 / 60} minutes`);
            return timeUntilExpiry < this.refreshThreshold;
        } catch (error) {
            console.error("Error checking token expiry:", error);
            return true;
        }
    }

    // Refresh the access token using the refresh token
    async refreshToken() {
        const refreshToken = localStorage.getItem("refreshToken");
        if (!refreshToken) {
            console.error("No refresh token available");
            this.logout();
            return false;
        }

        try {
            console.log("Refreshing token...");
            const response = await fetch("http://127.0.0.1:8000/auth/refresh", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            console.log("Refresh response:", response.status);

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem("jwt", data.access_token);
                console.log("Token refreshed successfully");
                return true;
            } else {
                console.error("Token refresh failed:", response.status);
                const errorText = await response.text();
                console.error("Error response:", errorText);
                this.logout();
                return false;
            }
        } catch (error) {
            console.error("Error refreshing token:", error);
            this.logout();
            return false;
        }
    }

    // Logout the user and clear tokens
    logout() {
        console.log("Logging out user");
        localStorage.removeItem("jwt");
        localStorage.removeItem("refreshToken");
        localStorage.removeItem("userRole");
        localStorage.removeItem("userId");
        localStorage.removeItem("username");
        // Redirect to login page appropriate for context
        const currentPath = window.location.pathname;
        if (currentPath.includes('/police/')) {
            window.location.href = "police_login.html";
        } else {
            window.location.href = "login.html";
        }
    }

    // Initialize token refresh mechanism
    async init() {
        console.log("Token manager initializing...");
        if (this.isTokenExpiringSoon()) {
            console.log("Token needs refresh, attempting to refresh");
            await this.refreshToken();
        }

        // Set up periodic check
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        this.refreshInterval = setInterval(async () => {
            if (this.isTokenExpiringSoon()) {
                console.log("Periodic check: Token needs refresh");
                await this.refreshToken();
            }
        }, 60000); // Check every minute

        console.log("Token manager initialized");
    }

    // Clean up interval on demand
    cleanup() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// Global token manager instance
const tokenManager = new TokenManager();

// Initialize the token manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    tokenManager.init();
});

// Function to make authenticated requests with automatic token refresh
async function makeAuthenticatedRequest(url, options = {}) {
    // Check if token needs refresh before making request
    if (tokenManager.isTokenExpiringSoon()) {
        console.log("Token needs refresh before making request to:", url);
        const refreshed = await tokenManager.refreshToken();
        if (!refreshed) {
            console.log("Token refresh failed, cannot make request");
            return null; // Token refresh failed
        }
    }

    const token = localStorage.getItem("jwt");
    if (!token) {
        console.log("No token available, logging out");
        tokenManager.logout();
        return null;
    }

    const requestHeaders = {
        "Authorization": `Bearer ${token}`,
        ...options.headers
    };

    console.log("Making authenticated request to:", url);
    const response = await fetch(url, {
        ...options,
        headers: requestHeaders
    });

    console.log("Response status:", response.status);

    // Handle 401 Unauthorized
    if (response.status === 401) {
        console.log("Received 401, logging out user");
        tokenManager.logout();
        return null;
    }

    return response;
}