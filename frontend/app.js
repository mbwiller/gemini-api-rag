/**
 * YouTube Channel RAG Tool - Frontend Application
 * Vanilla JavaScript implementation for scraping YouTube channels and querying transcripts
 */

// ============================================================================
// CONFIGURATION & STATE
// ============================================================================

const CONFIG = {
    API_BASE_URL: window.location.origin,
    ENDPOINTS: {
        HEALTH: '/api/health',
        SCRAPE: '/api/scrape',
        QUERY: '/api/query'
    },
    VALIDATION: {
        MIN_VIDEOS: 1,
        MAX_VIDEOS: 100,
        YOUTUBE_PATTERNS: [
            /^https?:\/\/(www\.)?youtube\.com\/@[\w-]+/i,
            /^https?:\/\/(www\.)?youtube\.com\/channel\/[\w-]+/i,
            /^https?:\/\/(www\.)?youtube\.com\/c\/[\w-]+/i,
            /^https?:\/\/(www\.)?youtube\.com\/user\/[\w-]+/i
        ]
    },
    PROGRESS: {
        PHASES: [
            { name: 'Connecting to YouTube...', start: 0, end: 30 },
            { name: 'Scraping videos...', start: 30, end: 70 },
            { name: 'Processing transcripts...', start: 70, end: 95 },
            { name: 'Uploading to Gemini...', start: 95, end: 100 }
        ],
        UPDATE_INTERVAL: 500 // milliseconds
    }
};

const APP_STATE = {
    storeName: null,
    channelName: null,
    videoCount: 0,
    isProcessing: false,
    progressInterval: null,
    currentPhase: 0
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Validates a YouTube channel URL
 * @param {string} url - The URL to validate
 * @returns {boolean} - Whether the URL is valid
 */
function validateYouTubeURL(url) {
    if (!url || typeof url !== 'string') {
        return false;
    }

    const trimmedUrl = url.trim();
    return CONFIG.VALIDATION.YOUTUBE_PATTERNS.some(pattern => pattern.test(trimmedUrl));
}

/**
 * Validates video count
 * @param {number} count - The video count to validate
 * @returns {boolean} - Whether the count is valid
 */
function validateVideoCount(count) {
    const num = parseInt(count, 10);
    return !isNaN(num) &&
           num >= CONFIG.VALIDATION.MIN_VIDEOS &&
           num <= CONFIG.VALIDATION.MAX_VIDEOS;
}

/**
 * Shows a section by ID
 * @param {string} sectionId - The ID of the section to show
 */
function showSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.remove('hidden');
        section.setAttribute('aria-hidden', 'false');
    }
}

/**
 * Hides a section by ID
 * @param {string} sectionId - The ID of the section to hide
 */
function hideSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('hidden');
        section.setAttribute('aria-hidden', 'true');
    }
}

/**
 * Displays an error message in a specific element
 * @param {string} message - The error message to display
 * @param {HTMLElement} element - The element to display the error in
 */
function displayError(message, element) {
    if (element) {
        element.textContent = message;
        element.style.display = 'block';
    }
}

/**
 * Clears all error messages
 */
function clearErrors() {
    const errorElements = document.querySelectorAll('.error-message');
    errorElements.forEach(element => {
        element.textContent = '';
        element.style.display = 'none';
    });
}

/**
 * Creates a chat message element
 * @param {string} content - The message content
 * @param {string} type - The message type ('user' or 'ai')
 * @param {Array} citations - Optional array of citations
 * @returns {HTMLElement} - The created message element
 */
function createMessageElement(content, type = 'user', citations = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const textP = document.createElement('p');
    textP.className = 'message-text';
    textP.textContent = content;
    contentDiv.appendChild(textP);

    // Add timestamp
    const timestamp = document.createElement('span');
    timestamp.className = 'message-timestamp';
    timestamp.textContent = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
    contentDiv.appendChild(timestamp);

    messageDiv.appendChild(contentDiv);

    // Add citations if available
    if (citations && citations.length > 0) {
        const citationsDiv = document.createElement('div');
        citationsDiv.className = 'message-citations';

        const citationsTitle = document.createElement('p');
        citationsTitle.className = 'citations-title';
        citationsTitle.textContent = 'Sources:';
        citationsDiv.appendChild(citationsTitle);

        const citationsList = document.createElement('ul');
        citationsList.className = 'citations-list';

        citations.forEach(citation => {
            const li = document.createElement('li');
            const link = document.createElement('a');
            link.href = citation.url || '#';
            link.textContent = citation.title || 'Video Source';
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            li.appendChild(link);
            citationsList.appendChild(li);
        });

        citationsDiv.appendChild(citationsList);
        messageDiv.appendChild(citationsDiv);
    }

    return messageDiv;
}

/**
 * Creates a thinking indicator element
 * @returns {HTMLElement} - The thinking indicator element
 */
function createThinkingIndicator() {
    const thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'message message-ai thinking-indicator';
    thinkingDiv.id = 'thinkingIndicator';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const dotsDiv = document.createElement('div');
    dotsDiv.className = 'thinking-dots';
    dotsDiv.innerHTML = '<span>.</span><span>.</span><span>.</span>';

    contentDiv.appendChild(dotsDiv);
    thinkingDiv.appendChild(contentDiv);

    return thinkingDiv;
}

/**
 * Scrolls a container to the bottom
 * @param {HTMLElement} container - The container to scroll
 */
function scrollToBottom(container) {
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

/**
 * Updates the progress bar and status
 * @param {number} percent - The progress percentage (0-100)
 * @param {string} message - The status message
 * @param {number} step - The current step number
 */
function updateProgress(percent, message, step) {
    const progressFill = document.getElementById('progressFill');
    const statusMessage = document.getElementById('statusMessage');
    const currentStep = document.getElementById('currentStep');
    const progressPercent = document.getElementById('progressPercent');
    const progressBar = document.querySelector('.progress-bar');

    if (progressFill) {
        progressFill.style.width = `${percent}%`;
    }

    if (statusMessage) {
        statusMessage.textContent = message;
    }

    if (currentStep) {
        currentStep.textContent = `Step ${step} of ${CONFIG.PROGRESS.PHASES.length}`;
    }

    if (progressPercent) {
        progressPercent.textContent = `${Math.round(percent)}%`;
    }

    if (progressBar) {
        progressBar.setAttribute('aria-valuenow', percent);
    }
}

/**
 * Enables or disables a button
 * @param {HTMLElement} button - The button element
 * @param {boolean} enabled - Whether to enable or disable
 */
function setButtonState(button, enabled) {
    if (button) {
        button.disabled = !enabled;
        if (enabled) {
            button.classList.remove('disabled');
        } else {
            button.classList.add('disabled');
        }
    }
}

/**
 * Simulates progress through phases
 */
function simulateProgress() {
    if (APP_STATE.currentPhase >= CONFIG.PROGRESS.PHASES.length) {
        clearProgressInterval();
        return;
    }

    const phase = CONFIG.PROGRESS.PHASES[APP_STATE.currentPhase];
    let currentPercent = phase.start;

    APP_STATE.progressInterval = setInterval(() => {
        currentPercent += 1;

        if (currentPercent >= phase.end) {
            updateProgress(phase.end, phase.name, APP_STATE.currentPhase + 1);
            APP_STATE.currentPhase++;
            clearProgressInterval();

            if (APP_STATE.currentPhase < CONFIG.PROGRESS.PHASES.length) {
                setTimeout(simulateProgress, 500);
            }
        } else {
            updateProgress(currentPercent, phase.name, APP_STATE.currentPhase + 1);
        }
    }, CONFIG.PROGRESS.UPDATE_INTERVAL);
}

/**
 * Clears the progress interval
 */
function clearProgressInterval() {
    if (APP_STATE.progressInterval) {
        clearInterval(APP_STATE.progressInterval);
        APP_STATE.progressInterval = null;
    }
}

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Makes an API request
 * @param {string} endpoint - The API endpoint
 * @param {object} options - Fetch options
 * @returns {Promise} - The fetch promise
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;

    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        }
    };

    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...(options.headers || {})
        }
    };

    try {
        const response = await fetch(url, mergedOptions);

        // Handle non-JSON responses
        const contentType = response.headers.get('content-type');
        const isJson = contentType && contentType.includes('application/json');

        if (!response.ok) {
            let errorMessage = `API Error: ${response.status} ${response.statusText}`;

            if (isJson) {
                const errorData = await response.json();
                errorMessage = errorData.error || errorData.message || errorMessage;
            } else {
                const errorText = await response.text();
                if (errorText) {
                    errorMessage = errorText;
                }
            }

            throw new Error(errorMessage);
        }

        if (isJson) {
            return await response.json();
        } else {
            return await response.text();
        }

    } catch (error) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Network error: Unable to connect to the server. Please check your connection.');
        }
        throw error;
    }
}

/**
 * Checks API health
 * @returns {Promise<boolean>} - Whether the API is healthy
 */
async function checkHealth() {
    try {
        const response = await apiRequest(CONFIG.ENDPOINTS.HEALTH);
        return response && (response.status === 'ok' || response.status === 'healthy');
    } catch (error) {
        console.error('Health check failed:', error);
        return false;
    }
}

/**
 * Scrapes a YouTube channel
 * @param {string} channelUrl - The channel URL
 * @param {number} videoCount - Number of videos to scrape
 * @returns {Promise<object>} - The scrape response
 */
async function scrapeChannel(channelUrl, videoCount) {
    return await apiRequest(CONFIG.ENDPOINTS.SCRAPE, {
        method: 'POST',
        body: JSON.stringify({
            channel_url: channelUrl,
            video_count: videoCount
        })
    });
}

/**
 * Queries the RAG system
 * @param {string} query - The user query
 * @param {string} storeName - The vector store name
 * @returns {Promise<object>} - The query response
 */
async function queryRAG(query, storeName) {
    return await apiRequest(CONFIG.ENDPOINTS.QUERY, {
        method: 'POST',
        body: JSON.stringify({
            query: query,
            store_name: storeName
        })
    });
}

// ============================================================================
// FORM HANDLERS
// ============================================================================

/**
 * Handles channel form submission
 * @param {Event} event - The form submit event
 */
async function handleChannelFormSubmit(event) {
    event.preventDefault();

    if (APP_STATE.isProcessing) {
        return;
    }

    clearErrors();

    const channelUrlInput = document.getElementById('channelUrl');
    const videoCountInput = document.getElementById('videoCount');
    const channelUrlError = document.getElementById('channelUrlError');
    const videoCountError = document.getElementById('videoCountError');
    const formError = document.getElementById('formError');
    const submitButton = document.getElementById('submitButton');

    const channelUrl = channelUrlInput.value.trim();
    const videoCount = parseInt(videoCountInput.value, 10);

    let hasError = false;

    // Validate channel URL
    if (!channelUrl) {
        displayError('Please enter a YouTube channel URL', channelUrlError);
        hasError = true;
    } else if (!validateYouTubeURL(channelUrl)) {
        displayError('Please enter a valid YouTube channel URL', channelUrlError);
        hasError = true;
    }

    // Validate video count
    if (!videoCount || isNaN(videoCount)) {
        displayError('Please enter a valid number', videoCountError);
        hasError = true;
    } else if (!validateVideoCount(videoCount)) {
        displayError(`Please enter a number between ${CONFIG.VALIDATION.MIN_VIDEOS} and ${CONFIG.VALIDATION.MAX_VIDEOS}`, videoCountError);
        hasError = true;
    }

    if (hasError) {
        return;
    }

    // Start processing
    APP_STATE.isProcessing = true;
    setButtonState(submitButton, false);

    // Show loading section
    hideSection('inputSection');
    showSection('loadingSection');

    // Reset and start progress simulation
    APP_STATE.currentPhase = 0;
    updateProgress(0, 'Initializing...', 1);
    simulateProgress();

    try {
        const response = await scrapeChannel(channelUrl, videoCount);

        // Stop progress simulation
        clearProgressInterval();
        updateProgress(100, 'Processing complete!', CONFIG.PROGRESS.PHASES.length);

        // Store response data
        APP_STATE.storeName = response.store_name;
        APP_STATE.channelName = response.channel_name || 'Unknown Channel';
        APP_STATE.videoCount = response.videos_processed || videoCount;

        // Wait a moment to show completion
        setTimeout(() => {
            // Hide loading and show chat
            hideSection('loadingSection');
            showSection('chatSection');

            // Update channel info
            const channelNameElement = document.getElementById('channelName');
            const videoCountDisplay = document.getElementById('videoCountDisplay');

            if (channelNameElement) {
                channelNameElement.textContent = APP_STATE.channelName;
            }

            if (videoCountDisplay) {
                videoCountDisplay.textContent = `${APP_STATE.videoCount} videos processed`;
            }

            // Reset form
            channelUrlInput.value = '';
            videoCountInput.value = '20';

            // Reset processing state
            APP_STATE.isProcessing = false;
            setButtonState(submitButton, true);

        }, 1000);

    } catch (error) {
        console.error('Scraping error:', error);

        // Stop progress simulation
        clearProgressInterval();

        // Show error
        displayError(error.message || 'An error occurred while processing the channel. Please try again.', formError);

        // Return to input section
        hideSection('loadingSection');
        showSection('inputSection');

        APP_STATE.isProcessing = false;
        setButtonState(submitButton, true);
    }
}

/**
 * Handles chat form submission
 * @param {Event} event - The form submit event
 */
async function handleChatFormSubmit(event) {
    event.preventDefault();

    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');
    const chatMessages = document.getElementById('chatMessages');
    const chatError = document.getElementById('chatError');

    const query = chatInput.value.trim();

    if (!query) {
        displayError('Please enter a question', chatError);
        return;
    }

    if (!APP_STATE.storeName) {
        displayError('No channel data available. Please process a channel first.', chatError);
        return;
    }

    clearErrors();

    // Disable input
    setButtonState(sendButton, false);
    chatInput.disabled = true;

    // Display user message
    const userMessage = createMessageElement(query, 'user');
    chatMessages.appendChild(userMessage);
    scrollToBottom(chatMessages);

    // Clear input
    chatInput.value = '';

    // Show thinking indicator
    const thinkingIndicator = createThinkingIndicator();
    chatMessages.appendChild(thinkingIndicator);
    scrollToBottom(chatMessages);

    try {
        const response = await queryRAG(query, APP_STATE.storeName);

        // Remove thinking indicator
        const indicator = document.getElementById('thinkingIndicator');
        if (indicator) {
            indicator.remove();
        }

        // Display AI response
        const citations = response.citations || [];
        const aiMessage = createMessageElement(response.answer || response.response, 'ai', citations);
        chatMessages.appendChild(aiMessage);
        scrollToBottom(chatMessages);

    } catch (error) {
        console.error('Query error:', error);

        // Remove thinking indicator
        const indicator = document.getElementById('thinkingIndicator');
        if (indicator) {
            indicator.remove();
        }

        // Display error message in chat
        const errorMessage = createMessageElement(
            'Sorry, an error occurred while processing your question. Please try again.',
            'ai'
        );
        errorMessage.classList.add('message-error');
        chatMessages.appendChild(errorMessage);
        scrollToBottom(chatMessages);

        displayError(error.message || 'An error occurred. Please try again.', chatError);
    } finally {
        // Re-enable input
        setButtonState(sendButton, true);
        chatInput.disabled = false;
        chatInput.focus();
    }
}

/**
 * Handles reset button click
 */
function handleReset() {
    // Clear state
    APP_STATE.storeName = null;
    APP_STATE.channelName = null;
    APP_STATE.videoCount = 0;
    APP_STATE.isProcessing = false;
    APP_STATE.currentPhase = 0;

    clearProgressInterval();
    clearErrors();

    // Clear chat messages except welcome message
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <p class="welcome-text">
                    Ask questions about the video content from this channel.
                    The AI will search through all transcripts to provide accurate answers.
                </p>
            </div>
        `;
    }

    // Reset chat input
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.value = '';
    }

    // Hide chat section, show input section
    hideSection('chatSection');
    showSection('inputSection');
}

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initializes the application
 */
async function initializeApp() {
    console.log('Initializing YouTube Channel RAG Tool...');

    // Get form elements
    const channelForm = document.getElementById('channelForm');
    const chatForm = document.getElementById('chatForm');
    const resetButton = document.getElementById('resetButton');
    const chatInput = document.getElementById('chatInput');

    // Add form submit listeners
    if (channelForm) {
        channelForm.addEventListener('submit', handleChannelFormSubmit);
    }

    if (chatForm) {
        chatForm.addEventListener('submit', handleChatFormSubmit);
    }

    if (resetButton) {
        resetButton.addEventListener('click', handleReset);
    }

    // Add enter key support for chat input
    if (chatInput) {
        chatInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }

    // Clear any existing errors
    clearErrors();

    // Check API health
    try {
        const isHealthy = await checkHealth();
        if (!isHealthy) {
            console.warn('Backend API health check failed');
            const formError = document.getElementById('formError');
            displayError(
                'Warning: Unable to connect to the backend API. Please ensure the server is running.',
                formError
            );
        } else {
            console.log('Backend API is healthy');
        }
    } catch (error) {
        console.error('Health check error:', error);
        const formError = document.getElementById('formError');
        displayError(
            'Warning: Unable to connect to the backend API. Please ensure the server is running.',
            formError
        );
    }

    // Ensure input section is visible by default
    showSection('inputSection');
    hideSection('loadingSection');
    hideSection('chatSection');

    console.log('Application initialized successfully');
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

// Initialize app when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    // DOM already loaded
    initializeApp();
}

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, pause any intervals
        clearProgressInterval();
    }
});

// Handle beforeunload to warn about ongoing processes
window.addEventListener('beforeunload', (event) => {
    if (APP_STATE.isProcessing) {
        event.preventDefault();
        event.returnValue = 'Processing is in progress. Are you sure you want to leave?';
        return event.returnValue;
    }
});
