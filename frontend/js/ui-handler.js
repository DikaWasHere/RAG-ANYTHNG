// ============= UI HANDLER MODULE =============
const UIHandler = {
  elements: {
    sidebar: null,
    hamburger: null,
    welcomeScreen: null,
    chatInterface: null,
    pdfInput: null,
    newChatBtn: null,
    chatTitle: null,
    chatList: null,
    pdfViewerColumn: null,
    chatColumn: null,
    resizer: null
  },

  isResizing: false,
  startX: 0,
  startLeftWidth: 0,

  init() {
    this.elements.sidebar = document.getElementById('sidebar');
    this.elements.hamburger = document.getElementById('hamburgerBtn');
    this.elements.welcomeScreen = document.getElementById('welcomeScreen');
    this.elements.chatInterface = document.getElementById('chatInterface');
    this.elements.pdfInput = document.getElementById('pdfInput');
    this.elements.newChatBtn = document.getElementById('newChatBtn');
    this.elements.chatTitle = document.getElementById('chatTitle');
    this.elements.chatList = document.getElementById('chatList');
    this.elements.pdfViewerColumn = document.getElementById('pdfViewerColumn');
    this.elements.chatColumn = document.getElementById('chatColumn');
    this.elements.resizer = document.getElementById('resizer');

    this.attachEvents();
    this.checkMobile();
  },

  attachEvents() {
    // Hamburger menu
    this.elements.hamburger.addEventListener('click', () => this.toggleSidebar());

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
      if (STATE.isMobile && 
          this.elements.sidebar.classList.contains('active') &&
          !this.elements.sidebar.contains(e.target) &&
          !this.elements.hamburger.contains(e.target)) {
        this.toggleSidebar();
      }
    });

    // New chat button
    this.elements.newChatBtn.addEventListener('click', () => {
      this.elements.pdfInput.click();
    });

    // PDF upload
    this.elements.pdfInput.addEventListener('change', async (e) => {
      await this.handleFileUpload(e);
    });

    // Drag and drop
    this.setupDragDrop();

    // Resizer for PDF viewer
    this.setupResizer();

    // Window resize handler
    window.addEventListener('resize', Utils.debounce(() => {
      this.checkMobile();
    }, 250));
  },

  async handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.includes('pdf')) {
      this.showError('Harap upload file PDF!');
      this.elements.pdfInput.value = '';
      return;
    }

    // Validate file size
    if (file.size > CONFIG.MAX_FILE_SIZE) {
      this.showError(`Ukuran file maksimal ${Utils.formatFileSize(CONFIG.MAX_FILE_SIZE)}!`);
      this.elements.pdfInput.value = '';
      return;
    }

    await this.processPDF(file);
    this.elements.pdfInput.value = '';
  },

  setupDragDrop() {
    const uploadArea = document.getElementById('uploadArea');
    if (!uploadArea) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      uploadArea.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
      });
    });

    ['dragenter', 'dragover'].forEach(eventName => {
      uploadArea.addEventListener(eventName, () => {
        uploadArea.classList.add('drag-over');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      uploadArea.addEventListener(eventName, () => {
        uploadArea.classList.remove('drag-over');
      });
    });

    uploadArea.addEventListener('drop', async (e) => {
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        const file = files[0];
        if (file.type.includes('pdf')) {
          this.elements.pdfInput.files = files;
          await this.handleFileUpload({ target: { files: [file] } });
        } else {
          this.showError('Harap upload file PDF!');
        }
      }
    });
  },

  toggleSidebar() {
    this.elements.sidebar.classList.toggle('active');
    this.elements.hamburger.classList.toggle('active');
  },

  checkMobile() {
    STATE.isMobile = window.innerWidth <= 1024;
    
    if (!STATE.isMobile) {
      this.elements.sidebar.classList.remove('active');
      this.elements.hamburger.classList.remove('active');
    }
  },

  async processPDF(file) {
    try {
      // Switch to chat interface
      this.elements.welcomeScreen.style.display = 'none';
      this.elements.chatInterface.classList.add('active');
      
      // Update title
      STATE.currentPdfName = file.name;
      this.elements.chatTitle.textContent = `📄 ${file.name}`;
      
      // Clear previous chat
      ChatHandler.clearMessages();
      ChatHandler.enableInput(false);
      
      // Show processing animation
      await ChatHandler.showProcessing();
      
      // Add to chat list
      this.addToChatList(file.name);
      
      // Load PDF for viewing
      await PDFHandler.loadPDF(file);
      
      // Add welcome message
      const welcomeMsg = `Halo! Saya sudah membaca dokumen "${file.name}". File berhasil diproses. Silakan tanyakan apapun tentang isi dokumen ini.`;
      ChatHandler.addMessage('bot', welcomeMsg);
      
      // Enable input
      ChatHandler.enableInput(true);
      
      // Upload to backend (non-blocking)
      this.uploadToBackend(file).catch(error => {
        console.error('Background upload error:', error);
      });
      
    } catch (error) {
      console.error('Error processing PDF:', error);
      this.showError('Terjadi kesalahan saat memproses PDF.');
      ChatHandler.addMessage('bot', 'Maaf, terjadi kesalahan saat memproses PDF. Silakan coba lagi.');
      ChatHandler.enableInput(true);
    }
  },

  async uploadToBackend(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', STATE.userId);
      
      const response = await fetch(`${CONFIG.API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'success') {
        console.log('✅ PDF uploaded successfully:', data);
        
        // Update doc ID if provided
        if (data.doc_id) {
          STATE.docId = data.doc_id;
        }
        
        STATE.chatId = null;
        
        // Show success notification (optional)
        // this.showSuccess('PDF berhasil diupload ke server');
      } else {
        throw new Error(data.message || 'Gagal memproses PDF');
      }
    } catch (error) {
      console.error('❌ Error upload PDF:', error);
      // Don't show error to user since PDF viewer still works
      // ChatHandler.addMessage('bot', '⚠️ Upload ke server gagal, tapi Anda masih bisa melihat PDF.');
    }
  },

  addToChatList(fileName) {
    // Remove active from all items
    document.querySelectorAll('.chat-item').forEach(item => {
      item.classList.remove('active');
    });

    // Create new chat item
    const chatItem = document.createElement('div');
    chatItem.className = 'chat-item active';
    chatItem.textContent = fileName;
    chatItem.title = fileName;
    
    // Add click handler
    chatItem.addEventListener('click', () => {
      document.querySelectorAll('.chat-item').forEach(item => {
        item.classList.remove('active');
      });
      chatItem.classList.add('active');
      this.elements.chatTitle.textContent = `📄 ${fileName}`;
    });
    
    this.elements.chatList.prepend(chatItem);
  },

  setupResizer() {
    const resizer = this.elements.resizer;
    if (!resizer) return;

    const leftPanel = this.elements.pdfViewerColumn;
    const rightPanel = this.elements.chatColumn;

    resizer.addEventListener('mousedown', (e) => {
      this.isResizing = true;
      this.startX = e.clientX;
      this.startLeftWidth = leftPanel.offsetWidth;
      
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
      
      e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
      if (!this.isResizing) return;
      
      const container = leftPanel.parentElement;
      const deltaX = e.clientX - this.startX;
      const containerWidth = container.offsetWidth;
      const newLeftWidth = this.startLeftWidth + deltaX;
      const minWidth = 300;
      const maxWidth = containerWidth - minWidth - 5;
      
      if (newLeftWidth >= minWidth && newLeftWidth <= maxWidth) {
        const leftPercent = (newLeftWidth / containerWidth) * 100;
        const rightPercent = 100 - leftPercent - (5 / containerWidth * 100);
        
        leftPanel.style.width = `${leftPercent}%`;
        rightPanel.style.width = `${rightPercent}%`;
      }
    });

    document.addEventListener('mouseup', () => {
      if (this.isResizing) {
        this.isResizing = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      }
    });
  },

  showError(message) {
    alert(message);
    // You can replace this with a custom toast notification
  },

  showSuccess(message) {
    console.log('✅', message);
    // You can replace this with a custom toast notification
  }
};