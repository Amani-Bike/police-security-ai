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
                    session_id: sessionId,  // Include session_id in request body
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

// Enhanced chat functionality using backend storage
class EnhancedChatManager {
    constructor() {
        this.apiClient = new ChatAPIClient();
        this.currentSessionId = null;
        this.messages = [];
        this.isTyping = false;
        this.lastEmergencyMessage = '';
        
        // DOM Elements - these will be accessed when the page is ready
        this.chatMessagesElement = null;
        this.emptyStateElement = null;
        this.chatHistoryElement = null;
        this.emergencyStatusElement = null;
        this.messageInput = null;
        this.sendButton = null;
        this.emergencyAlert = null;
        
        this.initialize();
    }

    async initialize() {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', async () => {
                this.setupElements();
                await this.loadOrCreateSession();
                await this.loadChatHistory();
                await this.loadUserSessionHistory();
            });
        } else {
            this.setupElements();
            await this.loadOrCreateSession();
            await this.loadChatHistory();
            await this.loadUserSessionHistory();
        }
    }
    
    setupElements() {
        this.chatMessagesElement = document.getElementById('chatMessages');
        this.emptyStateElement = document.getElementById('emptyState');
        this.chatHistoryElement = document.getElementById('chatHistory');
        this.emergencyStatusElement = document.getElementById('emergencyStatus');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.emergencyAlert = document.getElementById('emergencyAlert');
        
        // Set up event listeners
        if (this.messageInput && this.sendButton) {
            this.messageInput.addEventListener('input', () => {
                if (this.sendButton) {
                    this.sendButton.disabled = !this.messageInput.value.trim();
                }
            });
            
            // Disable send button initially
            if (this.sendButton) {
                this.sendButton.disabled = true;
            }
        }
        
        // Emergency alert click handler
        if (this.emergencyAlert) {
            this.emergencyAlert.addEventListener('click', () => {
                // Store emergency message and redirect
                if (this.lastEmergencyMessage) {
                    sessionStorage.setItem('emergency_message', this.lastEmergencyMessage);
                }
                window.location.href = 'report.html?emergency=true';
            });
        }
    }

    async loadOrCreateSession() {
        // Get session ID from URL params or create new
        const urlParams = new URLSearchParams(window.location.search);
        const sessionIdParam = parseInt(urlParams.get('session_id'));
        
        if (sessionIdParam) {
            this.currentSessionId = sessionIdParam;
        } else {
            // Create a new session
            try {
                const session = await this.apiClient.createSession();
                this.currentSessionId = session.id;
                
                // Update URL with session ID
                const newUrl = new URL(window.location);
                newUrl.searchParams.set('session_id', this.currentSessionId);
                window.history.replaceState({}, '', newUrl);
            } catch (error) {
                console.error('Failed to create chat session:', error);
                // Fallback to creating a temporary ID
                this.currentSessionId = Date.now();
            }
        }
    }

    async loadChatHistory() {
        if (!this.currentSessionId) return;

        try {
            const history = await this.apiClient.getChatHistory(this.currentSessionId);
            
            if (history && history.messages) {
                this.messages = history.messages;
                
                // Clear chat container
                if (this.chatMessagesElement) {
                    this.chatMessagesElement.innerHTML = '';
                    
                    // Add all messages to display
                    history.messages.forEach(msg => {
                        this.addMessageToDisplay(msg.content, msg.role === 'user', false);
                    });
                    
                    if (this.messages.length > 0) {
                        this.hideEmptyState();
                    }
                }
            }
        } catch (error) {
            console.error('Failed to load chat history:', error);
            // Initialize with empty array if failed to load
            this.messages = [];
        }
    }

    async loadUserSessionHistory() {
        try {
            const sessions = await this.apiClient.getSessions();
            await this.updateSessionHistoryDisplay(sessions);
        } catch (error) {
            console.error('Failed to load user session history:', error);
        }
    }

    async updateSessionHistoryDisplay(sessions) {
        if (!this.chatHistoryElement) return;

        this.chatHistoryElement.innerHTML = '';

        if (sessions.length === 0) {
            this.chatHistoryElement.innerHTML = `
                <div style="text-align: center; padding: 20px; opacity: 0.5; font-size: 0.9rem;">
                    No chat history yet
                </div>
            `;
            return;
        }

        // Filter sessions to only include those with messages and get recent message for preview
        const sessionItems = [];

        for (const session of sessions) {
            try {
                // Get the chat history for this session to get the most recent message
                const history = await this.apiClient.getChatHistory(session.id);

                if (history && history.messages && history.messages.length > 0) {
                    // Get the most recent message (last in the array since they are ordered)
                    const mostRecentMessage = history.messages[history.messages.length - 1];

                    sessionItems.push({
                        session: session,
                        previewMessage: mostRecentMessage.content,
                        timestamp: mostRecentMessage.timestamp || session.created_at
                    });
                }
            } catch (error) {
                console.error(`Failed to load messages for session ${session.id}:`, error);
                // Still add the session with basic info if we can't get messages
                sessionItems.push({
                    session: session,
                    previewMessage: session.title || 'New Session',
                    timestamp: session.created_at
                });
            }
        }

        // Only display sessions that have messages or fallback content
        if (sessionItems.length === 0) {
            this.chatHistoryElement.innerHTML = `
                <div style="text-align: center; padding: 20px; opacity: 0.5; font-size: 0.9rem;">
                    No recent chats yet
                </div>
            `;
            return;
        }

        sessionItems.forEach(item => {
            const chatItem = document.createElement('div');
            chatItem.className = `chat-item ${item.session.id === this.currentSessionId ? 'active' : ''}`;

            // Use the most recent message as preview
            const preview = item.previewMessage || (item.session.title || `Session ${item.session.id}`);

            chatItem.innerHTML = `
                <div>${preview.substring(0, 30)}${preview.length > 30 ? '...' : ''}</div>
                <div class="time">${new Date(item.timestamp).toLocaleDateString()} • ${new Date(item.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
            `;

            chatItem.onclick = () => this.loadSession(item.session.id);
            this.chatHistoryElement.appendChild(chatItem);
        });
    }

    async loadSession(sessionId) {
        this.currentSessionId = sessionId;
        
        // Update URL with new session ID
        const newUrl = new URL(window.location);
        newUrl.searchParams.set('session_id', sessionId);
        window.history.replaceState({}, '', newUrl);
        
        // Update active class
        document.querySelectorAll('.chat-item').forEach(item => {
            item.classList.remove('active');
        });
        event.target.closest('.chat-item').classList.add('active');
        
        // Load the chat history for this session
        await this.loadChatHistory();
        
        // Close sidebar on mobile after selecting a chat
        if (window.innerWidth <= 768) {
            document.getElementById('sidebar').classList.remove('active');
            document.getElementById('sidebarOverlay').classList.remove('active');
        }
    }

    async sendMessage(text = null) {
        const message = text || this.messageInput?.value.trim();

        if (!message) return;
        if (!this.apiClient.token) {
            alert("Please login first");
            window.location.href = "login.html";
            return;
        }

        // Hide empty state
        this.hideEmptyState();

        // Add user message to display immediately
        this.addMessageToDisplay(message, true);

        // Clear input and reset height
        if (!text && this.messageInput) {
            this.messageInput.value = '';
            this.messageInput.style.height = 'auto';
            if (this.sendButton) {
                this.sendButton.disabled = true;
            }
        }

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send message to backend API
            const response = await fetch(`${this.apiClient.apiBase}/chat/send`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${this.apiClient.token}`,
                },
                body: JSON.stringify({ message: message }),
            });

            if (response.ok) {
                const result = await response.json();

                // Hide typing indicator
                this.hideTypingIndicator();

                // Add AI response
                this.addMessageToDisplay(result.reply, false);

                // Check if emergency detected
                if (result.is_emergency) {
                    // Store the emergency message for pre-filling
                    this.lastEmergencyMessage = message;

                    // Update emergency status
                    this.updateEmergencyStatus(message, true);

                    // Show emergency alert
                    this.showEmergencyAlert();

                    // Highlight emergency status
                    if (this.emergencyStatusElement) {
                        this.emergencyStatusElement.className = 'emergency-status high';
                        this.emergencyStatusElement.textContent = 'Emergency Detected';
                    }
                } else {
                    this.updateEmergencyStatus(message, false);
                }

                // Save both user and AI messages to backend
                if (this.currentSessionId) {
                    try {
                        // Save user message
                        await this.apiClient.addMessage(this.currentSessionId, message, 'user');
                        // Save AI response
                        await this.apiClient.addMessage(this.currentSessionId, result.reply, 'assistant');
                    } catch (saveError) {
                        console.error('Failed to save messages to backend:', saveError);
                    }
                }
            } else {
                this.hideTypingIndicator();
                this.addMessageToDisplay("Sorry, I encountered an error. Please try again or use the emergency reporting feature for urgent matters.", false);
            }
        } catch (error) {
            console.error("Chat error:", error);
            this.hideTypingIndicator();
            this.addMessageToDisplay("Network error. Please check your connection. For emergencies, use the emergency button above.", false);
        }
    }

    addMessageToDisplay(message, isUser = false, isEmergency = false) {
        if (this.emptyStateElement && this.emptyStateElement.parentNode && this.emptyStateElement.style.display !== 'none') {
            this.emptyStateElement.style.display = 'none';
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'ai'}`;

        const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        const formattedMessage = message.replace(/\n/g, "<br>");

        messageDiv.innerHTML = `
            <div class="message-content">${formattedMessage}</div>
            <div class="message-time">${time}</div>
        `;

        if (this.chatMessagesElement) {
            this.chatMessagesElement.appendChild(messageDiv);
            this.chatMessagesElement.scrollTop = this.chatMessagesElement.scrollHeight;
        }
    }

    showTypingIndicator() {
        if (this.isTyping || !this.chatMessagesElement) return;

        this.isTyping = true;
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <span style="margin-left: 10px; font-size: 0.85rem;">AI Assistant is analyzing...</span>
        `;
        this.chatMessagesElement.appendChild(typingDiv);
        this.chatMessagesElement.scrollTop = this.chatMessagesElement.scrollHeight;
    }

    hideTypingIndicator() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    hideEmptyState() {
        if (this.emptyStateElement) {
            this.emptyStateElement.style.display = 'none';
        }
    }

    updateEmergencyStatus(message, isEmergency) {
        const messageLower = message.toLowerCase();

        if (isEmergency || messageLower.includes('fire') || messageLower.includes('accident') ||
            messageLower.includes('urgent') || messageLower.includes('immediate') ||
            messageLower.includes('trapped') || messageLower.includes('danger') ||
            messageLower.includes('dying') || messageLower.includes('bleeding')) {

            if (this.emergencyStatusElement) {
                this.emergencyStatusElement.className = 'emergency-status high';
                this.emergencyStatusElement.textContent = 'High Priority';
            }

            // Trigger emergency report pre-fill
            if (isEmergency) {
                this.lastEmergencyMessage = message;
            }

        } else if (messageLower.includes('medical') || messageLower.includes('help') ||
                messageLower.includes('suspicious') || messageLower.includes('crime') ||
                messageLower.includes('injured')) {

            if (this.emergencyStatusElement) {
                this.emergencyStatusElement.className = 'emergency-status medium';
                this.emergencyStatusElement.textContent = 'Medium Priority';
            }

        } else {
            if (this.emergencyStatusElement) {
                this.emergencyStatusElement.className = 'emergency-status';
                this.emergencyStatusElement.textContent = 'Low Priority';
            }
        }
    }

    showEmergencyAlert() {
        if (this.emergencyAlert) {
            this.emergencyAlert.style.display = 'block';
            this.emergencyAlert.onclick = () => {
                // Store the emergency message for pre-filling in report page
                if (this.lastEmergencyMessage) {
                    sessionStorage.setItem('emergency_message', this.lastEmergencyMessage);
                }
                window.location.href = 'report.html?emergency=true';
            };

            // Hide after 10 seconds
            setTimeout(() => {
                if (this.emergencyAlert) {
                    this.emergencyAlert.style.display = 'none';
                }
            }, 10000);
        }
    }

    async startNewChat() {
        try {
            // Create a new session
            const session = await this.apiClient.createSession();
            this.currentSessionId = session.id;

            // Clear the chat display
            if (this.chatMessagesElement) {
                this.chatMessagesElement.innerHTML = '';
            }

            // Show empty state again
            if (this.chatMessagesElement) {
                const newEmptyState = document.createElement('div');
                newEmptyState.className = 'empty-state';
                newEmptyState.id = 'emptyState';
                newEmptyState.innerHTML = `
                    <i class="fas fa-comments"></i>
                    <h3>How can I help you today?</h3>
                    <p>Describe your emergency or ask for assistance. I'm here to help coordinate emergency response and provide guidance.</p>
                    <div style="display: flex; gap: 10px; margin-top: 1rem;">
                        <button class="quick-action-btn" onclick="chatManager.sendMessage('There has been an accident with injuries')">
                            <i class="fas fa-car-crash"></i>
                            Accident
                        </button>
                        <button class="quick-action-btn" onclick="chatManager.sendMessage('Medical emergency, need ambulance')">
                            <i class="fas fa-ambulance"></i>
                            Medical
                        </button>
                        <button class="quick-action-btn" onclick="chatManager.sendMessage('Reporting suspicious activity')">
                            <i class="fas fa-eye"></i>
                            Suspicious
                        </button>
                    </div>
                `;
                this.chatMessagesElement.appendChild(newEmptyState);
            }

            // Reset emergency status
            if (this.emergencyStatusElement) {
                this.emergencyStatusElement.className = 'emergency-status';
                this.emergencyStatusElement.textContent = 'Low Priority';
            }

            // Hide emergency alert
            if (this.emergencyAlert) {
                this.emergencyAlert.style.display = 'none';
            }

            // Update URL with new session ID
            const newUrl = new URL(window.location);
            newUrl.searchParams.set('session_id', this.currentSessionId);
            window.history.replaceState({}, '', newUrl);

            // Update session history list
            await this.loadUserSessionHistory();

            // Close sidebar on mobile
            if (window.innerWidth <= 768) {
                document.getElementById('sidebar').classList.remove('active');
                document.getElementById('sidebarOverlay').classList.remove('active');
            }
        } catch (error) {
            console.error('Failed to start new chat:', error);
            alert('Failed to start a new chat. Please try again.');
        }
    }

    async quickAction(type) {
        const actions = {
            medical: 'Medical emergency, need ambulance immediately',
            accident: 'There has been a serious accident with injuries',
            crime: 'Reporting a crime in progress, need police assistance',
            fire: 'Fire emergency, need fire department'
        };

        await this.sendMessage(actions[type]);

        // Close sidebar on mobile
        if (window.innerWidth <= 768) {
            document.getElementById('sidebar').classList.remove('active');
            document.getElementById('sidebarOverlay').classList.remove('active');
        }
    }

    handleKeyPress(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.sendMessage();
        }
    }
}

// Initialize the chat manager when DOM is loaded
let chatManager;

document.addEventListener('DOMContentLoaded', () => {
    chatManager = new EnhancedChatManager();
    
    // Update send button state based on input
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    
    if (messageInput && sendButton) {
        messageInput.addEventListener('input', () => {
            sendButton.disabled = !messageInput.value.trim();
        });
        
        // Disable send button initially
        sendButton.disabled = true;
    }

    // Emergency alert click handler
    const emergencyAlert = document.getElementById('emergencyAlert');
    if (emergencyAlert) {
        emergencyAlert.addEventListener('click', () => {
            // Store emergency message and redirect
            if (chatManager && chatManager.lastEmergencyMessage) {
                sessionStorage.setItem('emergency_message', chatManager.lastEmergencyMessage);
            }
            window.location.href = 'report.html?emergency=true';
        });
    }
});

// Expose functions globally to be used by HTML onclick attributes
function sendMessage(text = null) {
    if (chatManager) {
        chatManager.sendMessage(text);
    }
}

function startNewChat() {
    if (chatManager) {
        chatManager.startNewChat();
    }
}

function quickAction(type) {
    if (chatManager) {
        chatManager.quickAction(type);
    }
}

function handleKeyPress(event) {
    if (chatManager) {
        chatManager.handleKeyPress(event);
    }
}