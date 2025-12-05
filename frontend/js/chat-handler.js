// ============= CHAT HANDLER MODULE =============
const ChatHandler = {
  elements: {
    messages: null,
    input: null,
    sendBtn: null,
    processingIndicator: null,
    fastBtn: null,
    qualityBtn: null
  },

  currentMode: 'quality', // 'fast' or 'quality'

  init() {
    this.elements.messages = document.getElementById('chatMessages');
    this.elements.input = document.getElementById('chatInput');
    this.elements.sendBtn = document.getElementById('sendBtn');
    this.elements.processingIndicator = document.getElementById('processingIndicator');
    this.elements.fastBtn = document.getElementById('fastBtn');
    this.elements.qualityBtn = document.getElementById('qualityBtn');

    this.attachEvents();
  },

  attachEvents() {
    // Send message
    this.elements.sendBtn.addEventListener('click', () => this.sendMessage());
    
    this.elements.input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    // Auto-resize textarea
    this.elements.input.addEventListener('input', function() {
      this.style.height = 'auto';
      this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });

    // Mode buttons
    this.elements.fastBtn.addEventListener('click', () => this.setMode('fast'));
    this.elements.qualityBtn.addEventListener('click', () => this.setMode('quality'));

    // Focus input when clicking on messages area
    this.elements.messages.addEventListener('click', () => {
      this.elements.input.focus();
    });
  },

  setMode(mode) {
    this.currentMode = mode;
    
    if (mode === 'fast') {
      this.elements.fastBtn.classList.add('active');
      this.elements.qualityBtn.classList.remove('active');
    } else {
      this.elements.fastBtn.classList.remove('active');
      this.elements.qualityBtn.classList.add('active');
    }
  },

  async sendMessage() {
    const question = this.elements.input.value.trim();
    if (!question) return;

    // Add user message
    this.addMessage('user', question);
    this.elements.input.value = '';
    this.elements.input.style.height = 'auto';
    
    // Disable send button
    this.elements.sendBtn.disabled = true;

    try {
      const params = new URLSearchParams({
        question: question,
        doc_id: STATE.docId,
        user_id: STATE.userId,
        mode: this.currentMode
      });
      
      if (STATE.chatId) {
        params.append('chat_id', STATE.chatId);
      }
      
      const response = await fetch(`${CONFIG.API_BASE_URL}/chat/send?${params.toString()}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Update chat ID from response
      if (data.chat_id) {
        STATE.chatId = data.chat_id;
      }
      
      // Add bot response
      if (data.answer) {
        await Utils.sleep(500); // Simulate typing delay
        this.addMessage('bot', data.answer);
      } else {
        throw new Error('Tidak ada jawaban dari server');
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
      this.addMessage('bot', 'Maaf, terjadi kesalahan: ' + error.message);
    } finally {
      this.elements.sendBtn.disabled = false;
      this.elements.input.focus();
    }
  },

  addMessage(role, text) {
    const message = document.createElement('div');
    message.className = `message ${role}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'bot' ? '🤖' : '👤';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;
    
    message.appendChild(avatar);
    message.appendChild(content);
    this.elements.messages.appendChild(message);
    
    // Smooth scroll to bottom
    this.scrollToBottom();
  },

  scrollToBottom() {
    this.elements.messages.scrollTo({
      top: this.elements.messages.scrollHeight,
      behavior: 'smooth'
    });
  },

  async showProcessing() {
    this.elements.processingIndicator.classList.add('active');
    
    for (let i = 0; i < CONFIG.PROCESSING_STEPS.length; i++) {
      const step = CONFIG.PROCESSING_STEPS[i];
      const stepEl = document.getElementById(step.id);
      
      // Remove completed class from all steps first
      document.querySelectorAll('.process-step').forEach(s => {
        s.classList.remove('active', 'completed');
      });
      
      // Add active to current step
      stepEl.classList.add('active');
      
      await Utils.sleep(step.duration);
      
      // Mark as completed
      stepEl.classList.remove('active');
      stepEl.classList.add('completed');
      
      if (i < CONFIG.PROCESSING_STEPS.length - 1) {
        await Utils.sleep(300);
      }
    }
    
    await Utils.sleep(500);
    this.elements.processingIndicator.classList.remove('active');
    
    // Reset all steps
    document.querySelectorAll('.process-step').forEach(s => {
      s.classList.remove('active', 'completed');
    });
  },

  clearMessages() {
    this.elements.messages.innerHTML = '';
    STATE.chatId = null;
  },

  enableInput(enable = true) {
    this.elements.input.disabled = !enable;
    this.elements.sendBtn.disabled = !enable;
    
    if (enable) {
      this.elements.input.focus();
    }
  }
};