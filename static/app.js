// ============================================
// Chat UI Controller Module
// ============================================

class DOMElements {
  static questionForm = document.getElementById("questionForm");
  static questionInput = document.getElementById("questionInput");
  static submitBtn = document.getElementById("submitBtn");
  static btnIcon = this.submitBtn.querySelector(".btn-icon");
  static spinner = this.submitBtn.querySelector(".spinner");
  static chatMessages = document.getElementById("chatMessages");
  static welcomeScreen = document.getElementById("welcomeScreen");
}

class ChatMessage {
  constructor(content, sender) {
    this.content = content;
    this.sender = sender;
    this.timestamp = new Date();
  }

  getElement() {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message message-${this.sender}`;
    messageDiv.innerHTML = `
      <div>
        <div class="message-label">${this.getSenderLabel()}</div>
        <div class="message-content">${this.escapeHtml()}</div>
      </div>
    `;
    return messageDiv;
  }

  getSenderLabel() {
    return this.sender === "user" ? "You" : "AI CHAT BOT";
  }

  escapeHtml() {
    const div = document.createElement("div");
    div.textContent = this.content;
    return div.innerHTML.replace(/\n/g, "<br>");
  }
}

class TypingIndicator {
  static create() {
    const typingDiv = document.createElement("div");
    typingDiv.className = "message message-ai";
    typingDiv.id = "typingIndicator";
    typingDiv.innerHTML = `
      <div>
        <div class="message-label">AI CHAT BOT</div>
        <div class="message-content">
          <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
          </div>
        </div>
      </div>
    `;
    return typingDiv;
  }

  static remove() {
    const typingIndicator = document.getElementById("typingIndicator");
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }
}

class ErrorMessage {
  constructor(message) {
    this.message = message;
    this.duration = 5000;
  }

  create() {
    const errorDiv = document.createElement("div");
    errorDiv.className = "error-message";
    errorDiv.textContent = this.message;
    return errorDiv;
  }

  display(container) {
    const errorElement = this.create();
    container.appendChild(errorElement);
    setTimeout(() => {
      errorElement.remove();
    }, this.duration);
  }
}

class ChatUI {
  constructor() {
    this.domElements = DOMElements;
    this.conversationHistory = [];
    this.apiUrl = "/api/ask";
    this.initialize();
  }

  initialize() {
    this.setupEventListeners();
    this.focusInput();
  }

  setupEventListeners() {
    this.domElements.questionInput.addEventListener("input", (e) => this.autoResizeInput(e));
    this.domElements.questionForm.addEventListener("submit", (e) => this.handleFormSubmit(e));
    this.domElements.questionInput.addEventListener("keydown", (e) => this.handleKeyDown(e));
    window.addEventListener("load", () => this.focusInput());
  }

  autoResizeInput(event) {
    event.target.style.height = "auto";
    event.target.style.height = event.target.scrollHeight + "px";
  }

  handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      this.domElements.questionForm.dispatchEvent(new Event("submit"));
    }
  }

  focusInput() {
    this.domElements.questionInput.focus();
  }

  async handleFormSubmit(event) {
    event.preventDefault();
    const question = this.domElements.questionInput.value.trim();

    if (!question) return;

    this.hideWelcomeScreen();
    this.addMessage(new ChatMessage(question, "user"));
    this.clearInput();
    this.setLoadingState(true);
    this.domElements.chatMessages.appendChild(TypingIndicator.create());

    try {
      const answer = await this.fetchAnswer(question);
      this.handleResponse(question, answer);
    } catch (error) {
      this.handleError(error);
    } finally {
      this.setLoadingState(false);
      TypingIndicator.remove();
    }
  }

  async fetchAnswer(question) {
    const response = await fetch(this.apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || "Failed to get answer");
    }

    return await response.json();
  }

  handleResponse(question, data) {
    this.addMessage(new ChatMessage(data.answer, "ai"));
    this.conversationHistory.push({
      question: question,
      answer: data.answer,
      timestamp: new Date(),
    });
  }

  handleError(error) {
    console.error("Error:", error);
    const errorMsg = new ErrorMessage(
      "Failed to connect to the server. Please make sure the backend is running."
    );
    errorMsg.display(this.domElements.chatMessages);
  }

  addMessage(chatMessage) {
    this.domElements.chatMessages.appendChild(chatMessage.getElement());
    this.scrollToBottom();
  }

  clearInput() {
    this.domElements.questionInput.value = "";
    this.domElements.questionInput.style.height = "auto";
  }

  setLoadingState(isLoading) {
    this.domElements.submitBtn.disabled = isLoading;
    this.domElements.questionInput.disabled = isLoading;

    if (isLoading) {
      this.domElements.btnIcon.style.display = "none";
      this.domElements.spinner.style.display = "block";
    } else {
      this.domElements.btnIcon.style.display = "block";
      this.domElements.spinner.style.display = "none";
    }
  }

  hideWelcomeScreen() {
    if (this.domElements.welcomeScreen) {
      this.domElements.welcomeScreen.style.display = "none";
    }
  }

  scrollToBottom() {
    const chatMain = document.querySelector(".chat-main");
    setTimeout(() => {
      chatMain.scrollTop = chatMain.scrollHeight;
    }, 100);
  }
}

// Initialize application
document.addEventListener("DOMContentLoaded", () => {
  new ChatUI();
});

