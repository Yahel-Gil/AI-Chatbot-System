// Global state holding the active conversation ID (Starts as null - Lazy Creation)
let currentConversationId = null;

// DOM Elements cache
const chatMessages = document.getElementById("chatMessages");
const chatWelcome = document.getElementById("chatWelcome");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

// Initialize view state without calling the backend DB layout prematurely
function resetChatWindow() {
    currentConversationId = null;
    chatMessages.innerHTML = "";
    chatWelcome.style.display = "flex";
    userInput.value = "";
    toggleInputState(false);
}

// Toggle loading state of input fields during API calls
function toggleInputState(isLoading) {
    userInput.disabled = isLoading;
    sendBtn.disabled = isLoading;
    if (isLoading) {
        sendBtn.classList.add("disabled");
    } else {
        sendBtn.classList.remove("disabled");
        userInput.focus();
    }
}

// Append message bubbles dynamically inside the chat window
function appendMessage(sender, content) {
    if (chatWelcome.style.display !== "none") {
        chatWelcome.style.display = "none";
    }

    const messageWrapper = document.createElement("div");
    messageWrapper.classList.add("message-wrapper", sender);

    const messageBubble = document.createElement("div");
    messageBubble.classList.add("message-bubble");
    
    // Evaluate if content is a native DOM Node or plain text payload
    if (content instanceof HTMLElement) {
        messageBubble.appendChild(content);
    } else {
        messageBubble.textContent = content;
    }

    messageWrapper.appendChild(messageBubble);
    chatMessages.appendChild(messageWrapper);

    // Force strict scrolling containment to keep recent messages visible
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return messageBubble;
}

// Create a modern animated typing indicator using classes from CSS
function createTypingIndicator() {
    const container = document.createElement("div");
    container.classList.add("typing-container");

    for (let index = 0; index < 3; index++) {
        const dot = document.createElement("div");
        dot.classList.add("loading-dot");
        container.appendChild(dot);
    }

    return container;
}

// Handle the user message submission flow with Lazy Session Creation
async function handleFormSubmit() {
    const text = userInput.value.trim();
    if (!text) return;

    // Display user message instantly and block further input
    appendMessage("user", text);
    userInput.value = "";
    toggleInputState(true);

    const indicatorContainer = createTypingIndicator();
    const loadingBubble = appendMessage("assistant", indicatorContainer);

    try {
        // LAZY CREATION LOGIC: If this is the first message, provision the ID now
        if (!currentConversationId) {
            const sessionResponse = await fetch("/api/chat/new", { method: "POST" });
            if (!sessionResponse.ok) throw new Error("Failed to initialize remote database session.");
            
            const sessionData = await sessionResponse.json();
            currentConversationId = sessionData.conversationId;
        }

        // Post the message context to the newly established or existing ID
        const response = await fetch(`/api/chat/${currentConversationId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content: text })
        });

        if (!response.ok) throw new Error("Server rejected message context.");

        // Swap the temporary typing wrapper with the concrete AI reply
        const data = await response.json();
        loadingBubble.textContent = data.reply;
        
    } catch (error) {
        console.error("Message Processing Error:", error);
        loadingBubble.textContent = "An error occurred while processing your request. Please try again.";
    } finally {
        // Release UI locks and ensure layout alignment
        toggleInputState(false);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Form event listeners with meaningful event naming
chatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    handleFormSubmit();
});

// Capture keystroke bounds to allow smooth non-submit multiline inputs
userInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        handleFormSubmit();
    }
});

// Check URL parameters on page mount to handle navigation triggers
window.addEventListener("DOMContentLoaded", () => {
    const urlParams = new URLSearchParams(window.location.search);
    
    // If we just navigated via "New Chat" or did a normal refresh, reset smoothly
    if (urlParams.get("action") === "new" || window.location.pathname === "/home") {
        resetChatWindow();
        
        // Clean up URL parameter dynamically without refreshing the page
        if (urlParams.get("action") === "new") {
            window.history.replaceState({}, document.title, "/home");
        }
    }
});