// Chat API client for backend chat history functionality
class ChatAPIClient {
    constructor() {
        this.token = localStorage.getItem("jwt");
        this.currentSessionId = null;
        this.currentUserId = this.getUserIdFromToken();
        this.apiBase = this.getApiBase();
    }

    getApiBase() {
        // Check if we're running locally or on a server
        const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        return isLocal ? 'http://localhost:8000' : window.location.origin;
    }

    getUserIdFromToken() {
        const token = localStorage.getItem("jwt");
        if (!token) return null;

        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.user_id || payload.sub;
        } catch (e) {
            console.error("Error decoding token:", e);
            return null;
        }
    }

    async makeAuthenticatedRequest(url, options = {}) {
        // Ensure we have a token before making requests
        const token = localStorage.getItem("jwt");
        if (!token) {
            throw new Error("No authentication token found. Please log in again.");
        }

        // Prepare headers with authorization
        const requestHeaders = {
            'Authorization': `Bearer ${token}`,
            ...options.headers
        };

        // Make the request
        const response = await fetch(url, {
            ...options,
            headers: requestHeaders
        });

        // Handle 401 Unauthorized - token might be expired
        if (response.status === 401) {
            console.error("Unauthorized access - token may be expired");
            // Clear the invalid token
            localStorage.removeItem("jwt");
            localStorage.removeItem("userRole");
            localStorage.removeItem("userId");
            localStorage.removeItem("username");
            
            // Redirect to login page
            alert("Your session has expired. Please log in again.");
            window.location.href = "login.html";
            
            throw new Error("Authentication required - token invalid/expired");
        }

        // Handle other non-success status codes
        if (!response.ok) {
            throw new Error(`Request failed: ${response.status} - ${response.statusText}`);
        }

        return response;
    }

    async createSession(title = null) {
        try {
            const response = await this.makeAuthenticatedRequest(`${this.apiBase}/chat-history/sessions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title })
            });

            const session = await response.json();
            this.currentSessionId = session.id;
            return session;
        } catch (error) {
            console.error('Error creating chat session:', error);
            throw error;
        }
    }

    async getSessions() {
        try {
            const response = await this.makeAuthenticatedRequest(`${this.apiBase}/chat-history/sessions`);
            return await response.json();
        } catch (error) {
            console.error('Error getting chat sessions:', error);
            throw error;
        }
    }

    async getChatHistory(sessionId) {
        try {
            const response = await this.makeAuthenticatedRequest(`${this.apiBase}/chat-history/sessions/${sessionId}`);
            return await response.json();
        } catch (error) {
            console.error('Error getting chat history:', error);
            throw error;
        }
    }

    async addMessage(sessionId, content, role) {
        try {
            const response = await this.makeAuthenticatedRequest(`${this.apiBase}/chat-history/sessions/${sessionId}/messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content,
                    role
                })
            });

            return await response.json();
        } catch (error) {
            console.error('Error adding message:', error);
            throw error;
        }
    }

    async updateSession(sessionId, title) {
        try {
            const response = await this.makeAuthenticatedRequest(`${this.apiBase}/chat-history/sessions/${sessionId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title })
            });

            return await response.json();
        } catch (error) {
            console.error('Error updating session:', error);
            throw error;
        }
    }

    async deleteSession(sessionId) {
        try {
            const response = await this.makeAuthenticatedRequest(`${this.apiBase}/chat-history/sessions/${sessionId}`, {
                method: 'DELETE'
            });

            return await response.json();
        } catch (error) {
            console.error('Error deleting session:', error);
            throw error;
        }
    }
}