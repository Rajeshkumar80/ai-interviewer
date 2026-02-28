/**
 * Interview Page JavaScript (Enhanced, JWT + Backend)
 * - Uses Flask backend /api/interview/* with JWT from localStorage.token
 * - Backend returns questions; frontend uses only those (no hardcoded demo)
 * - Local evaluation heuristics as fallback; backend evaluation overrides when present
 * - Per-question timing + overall timing
 * - Saves analytics attempt to /api/analytics/store (JWT required)
 */

class InterviewManager {
  constructor() {
    // IMPORTANT: backend base URL
    this.apiBaseUrl = 'http://localhost:5000/api';

    // Editor / audio / video
    this.editor = null;
    this.recognition = null;
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.videoStream = null;

    // Interview state
    this.currentSession = null;
    this.currentQuestion = null;
    this.questionIndex = 0;
    this.demoQuestions = []; // questions from backend

    // Timers
    this.overallTimer = null;
    this.questionTimer = null;
    this.isPaused = false;

    // Voice answer
    this.recordedAudio = null;
    this.transcript = '';

    // Tracking answers & times
    this.answers = []; // { question, type, answer_text, audio, evaluation, time_taken, category, topic }
    this.questionStartTime = null;
    this.overallStartTime = null;
    this.question_times = [];

    // Interview metadata used for analytics
    this.difficulty = 'medium';

    // Tab switching tracking
    this.tabSwitchCount = 0;
    this.maxTabSwitches = 3;
    this.tabWarnings = [];
    this.isInterviewActive = false;

    this.init();
  }

  /* ==========================
   *  INIT & BASIC HELPERS
   * ========================== */

  async init() {
    this.setupEventListeners();
    this.initializeMonaco();
    this.initializeSpeechRecognition();
    this.initializeVideoPreview();
    this.loadPresets();
    this.setupTabSwitchDetection();
  }

  stopTimers() {
    if (this.overallTimer) {
      clearInterval(this.overallTimer);
      this.overallTimer = null;
    }
    if (this.questionTimer) {
      clearInterval(this.questionTimer);
      this.questionTimer = null;
    }
    this.isPaused = true;
  }

  setupEventListeners() {
    const configForm = document.getElementById('interview-config-form');
    if (configForm) {
      configForm.addEventListener('submit', (e) => this.handleConfigSubmit(e));
    }

    document.querySelectorAll('.preset-btn').forEach((btn) => {
      btn.addEventListener('click', (e) => this.applyPreset(e.target.dataset.preset));
    });

    this.setupTagInput('tech-stack-input', 'tech-stack-tags');
    this.setupTagInput('skill-tags-input', 'skill-tags-container');

    // Tech chip quick-select
    document.querySelectorAll('.tech-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const tech = chip.dataset.tech;
        const container = document.getElementById('tech-stack-tags');
        if (!container) return;

        // Toggle: remove if already added
        const existing = Array.from(container.querySelectorAll('.tag span:first-child'))
          .find(s => s.textContent === tech)?.closest('.tag');
        if (existing) {
          existing.remove();
          chip.classList.remove('active');
        } else {
          this.addTag(tech, container);
          chip.classList.add('active');
        }
      });
    });

    document.getElementById('submit-answer-btn')?.addEventListener('click', () => this.submitAnswer());
    document.getElementById('prev-question-btn')?.addEventListener('click', () => this.previousQuestion());
    document.getElementById('end-interview-btn')?.addEventListener('click', () => this.endInterview());
    document.getElementById('pause-btn')?.addEventListener('click', () => this.pauseTimers());
    document.getElementById('resume-btn')?.addEventListener('click', () => this.resumeTimers());

    document.getElementById('start-recording-btn')?.addEventListener('click', () => this.startRecording());
    document.getElementById('stop-recording-btn')?.addEventListener('click', () => this.stopRecording());
    document.getElementById('playback-btn')?.addEventListener('click', () => this.playbackRecording());

    document.getElementById('play-audio-btn')?.addEventListener('click', () => this.playQuestionAudio());

    document.getElementById('run-code-btn')?.addEventListener('click', () => this.runCode());
    document.getElementById('test-code-btn')?.addEventListener('click', () => this.testCode());
    document.getElementById('language-select')?.addEventListener('change', (e) => this.changeLanguage(e.target.value));

    // Tab switch overlay buttons
    document.getElementById('tab-resume-btn')?.addEventListener('click', () => this.hideTabWarning());
    document.getElementById('tab-end-btn')?.addEventListener('click', () => {
      this.hideTabWarning();
      this.endInterview();
    });
  }

  setupTagInput(inputId, containerId) {
    const input = document.getElementById(inputId);
    const container = document.getElementById(containerId);
    if (!input || !container) return;

    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && input.value.trim()) {
        e.preventDefault();
        this.addTag(input.value.trim(), container);
        input.value = '';
      }
    });
  }

  addTag(text, container) {
    const tag = document.createElement('div');
    tag.className = 'tag';
    tag.innerHTML = `
      <span>${this.escapeHtml(text)}</span>
      <span class="tag-remove" data-tag="${this.escapeHtml(text)}">×</span>
    `;
    tag.querySelector('.tag-remove').addEventListener('click', () => tag.remove());
    container.appendChild(tag);
  }

  getTags(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return [];
    return Array.from(container.querySelectorAll('.tag span:first-child')).map((tag) => tag.textContent);
  }

  escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  async blobToBase64(blob) {
    return new Promise((resolve, reject) => {
      if (!blob) return resolve(null);
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  /* ==========================
   *  MONACO EDITOR
   * ========================== */

  initializeMonaco() {
    if (typeof require === 'undefined') {
      console.warn('Monaco loader (require) not found');
      return;
    }

    require.config({
      paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs' },
    });

    require(['vs/editor/editor.main'], () => {
      const editorContainer = document.getElementById('code-editor');
      if (!editorContainer) return;

      if (this.editor) this.editor.dispose();

      this.editor = monaco.editor.create(editorContainer, {
        value: '// Write your code here\n',
        language: 'javascript',
        theme: document.documentElement.getAttribute('data-mode') === 'dark' ? 'vs-dark' : 'vs',
        fontSize: 14,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        automaticLayout: true,
      });
    });
  }

  changeLanguage(language) {
    if (this.editor) monaco.editor.setModelLanguage(this.editor.getModel(), language);
  }

  async runCode() {
    const code = this.editor?.getValue();
    const terminal = document.getElementById('terminal-content');
    if (terminal) {
      terminal.innerHTML = '<div class="success">Running code (client simulation)...</div>';
      setTimeout(() => {
        terminal.innerHTML = '<div class="success">Code executed successfully (simulated)!</div>';
      }, 800);
    }
  }

  async testCode() {
    const terminal = document.getElementById('terminal-content');
    if (terminal) {
      terminal.innerHTML = '<div>Running tests (client simulated)...</div>';
      setTimeout(() => {
        terminal.innerHTML = `
          <div class="success">✓ Test 1 passed</div>
          <div class="success">✓ Test 2 passed</div>
          <div class="error">✗ Test 3 failed: Expected 5, got 4 (simulated)</div>
        `;
      }, 1200);
    }
  }

  /* ==========================
   *  SPEECH & CAMERA
   * ========================== */

  initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = 'en-US';

      this.recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) finalTranscript += transcript + ' ';
          else interimTranscript += transcript;
        }

        this.transcript = (finalTranscript + interimTranscript).trim();
        const transcriptText = document.getElementById('transcript-text');
        if (transcriptText) transcriptText.textContent = this.transcript || 'Your spoken answer will appear here.';
      };

      this.recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        this.updateRecorderStatus('Error: ' + event.error, false);
      };
    } else {
      console.warn('Speech recognition not supported');
    }
  }

  setupTabSwitchDetection() {
    // Listen for tab visibility changes
    document.addEventListener('visibilitychange', () => {
      if (document.hidden && this.isInterviewActive) {
        this.handleTabSwitch();
      }
    });

    // Also detect window blur (switching to another app or window)
    window.addEventListener('blur', () => {
      if (this.isInterviewActive) {
        this.handleTabSwitch();
      }
    });
  }

  handleTabSwitch() {
    this.tabSwitchCount++;
    this.pauseTimers();

    const remaining = Math.max(0, this.maxTabSwitches - this.tabSwitchCount);
    let message = '';

    if (this.tabSwitchCount === 1) {
      message = `⚠️ Warning: Tab switching detected! You have ${remaining} warning(s) remaining before auto-submit.`;
    } else if (this.tabSwitchCount === 2) {
      message = `⚠️ Final Warning: Tab switch #${this.tabSwitchCount} detected! One more switch will end and submit the interview.`;
    } else {
      message = `🚫 Interview auto-submitted: You switched tabs ${this.tabSwitchCount} times. Please complete the interview without switching.`;
    }

    this.showTabWarning(message);

    if (this.tabSwitchCount >= this.maxTabSwitches) {
      setTimeout(() => {
        this.hideTabWarning();
        this.endInterview();
      }, 3000);
    }
  }

  showTabWarning(message) {
    const overlay = document.getElementById('tab-switch-overlay');
    const msgEl = document.getElementById('tab-warning-msg');
    if (overlay) {
      if (msgEl) msgEl.textContent = message;
      overlay.style.display = 'flex';
    }
  }

  hideTabWarning() {
    const overlay = document.getElementById('tab-switch-overlay');
    if (overlay) overlay.style.display = 'none';
    this.resumeTimers();
  }

  cancelInterviewDueToTabSwitching() {
    this.isInterviewActive = false;
    this.stopTimers();

    const message = 'Interview canceled due to multiple tab switches. This action has been recorded.';
    alert(message);

    // Log the incident
    console.warn('Interview canceled due to tab switching', {
      tabSwitchCount: this.tabSwitchCount,
      timestamp: new Date().toISOString()
    });

    // Return to configuration screen
    this.returnToConfig();
  }

  returnToConfig() {
    document.getElementById('interview-screen').classList.remove('active');
    document.getElementById('config-screen').classList.add('active');
    this.isInterviewActive = false;
    this.cleanupProctoring();
  }

  cleanupProctoring() {
    // Clear camera movement detection
    if (this.movementCheckInterval) {
      clearInterval(this.movementCheckInterval);
      this.movementCheckInterval = null;
    }

    // Reset proctoring state
    this.isInterviewActive = false;
    this.tabSwitchCount = 0;
    this.movementWarnings = 0;
    this.noMovementCount = 0;
    this.lastBrightness = null;
  }

  async initializeVideoPreview() {
    const video = document.getElementById('user-video');
    if (!video || !navigator.mediaDevices?.getUserMedia) {
      console.warn('Camera preview not supported');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      this.videoStream = stream;

      // Setup camera movement detection
      // DISABLED per user request (User Absence flags removed)
      // this.setupCameraMovementDetection(video, stream);
      video.srcObject = stream;
    } catch (error) {
      console.error('Error accessing camera:', error);
      const hint = document.querySelector('.video-hint');
      if (hint) hint.textContent = 'Camera access denied. Please allow camera permissions for preview.';
    }
  }

  setupCameraMovementDetection(video, stream) {
    // Simple movement detection using video frames
    this.lastFrameTime = Date.now();
    this.movementWarnings = 0;
    this.maxMovementWarnings = 3;
    this.noMovementCount = 0;
    this.lastPosition = { x: 0, y: 0 };

    // Create canvas for frame analysis
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Check for movement every 2 seconds
    this.movementCheckInterval = setInterval(() => {
      if (!this.isInterviewActive) return;

      try {
        canvas.width = video.videoWidth || 320;
        canvas.height = video.videoHeight || 240;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Get frame data for analysis
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const movement = this.detectMovement(imageData);

        if (!movement) {
          this.noMovementCount++;
          if (this.noMovementCount >= 3) {
            this.handleNoMovement();
            this.noMovementCount = 0;
          }
        } else {
          this.noMovementCount = 0;
        }

      } catch (error) {
        console.warn('Movement detection error:', error);
      }
    }, 2000);
  }

  detectMovement(imageData) {
    // Simple movement detection using frame difference
    const data = imageData.data;
    let brightness = 0;
    let pixelCount = 0;

    // Calculate average brightness
    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      brightness += (r + g + b) / 3;
      pixelCount++;
    }

    const avgBrightness = brightness / pixelCount;

    // If brightness changes significantly, assume movement
    if (!this.lastBrightness) {
      this.lastBrightness = avgBrightness;
      return true;
    }

    const brightnessChange = Math.abs(avgBrightness - this.lastBrightness);
    this.lastBrightness = avgBrightness;

    // Consider movement if brightness changes by more than 5%
    return brightnessChange > 12;
  }

  handleNoMovement() {
    this.movementWarnings++;

    if (this.movementWarnings <= this.maxMovementWarnings) {
      const message = this.movementWarnings < this.maxMovementWarnings
        ? `Warning: No user movement detected! Please ensure you are visible in the camera. (${this.movementWarnings}/${this.maxMovementWarnings})`
        : 'Final warning: User visibility required! Please position yourself in front of the camera.';

      this.showMovementWarning(message);

      if (this.movementWarnings >= this.maxMovementWarnings) {
        this.handleExcessiveNoMovement();
      }
    }
  }

  showMovementWarning(message) {
    const warningDiv = document.createElement('div');
    warningDiv.style.cssText = `
      position: fixed;
      top: 80px;
      right: 20px;
      background: #ffa726;
      color: white;
      padding: 15px 20px;
      border-radius: 8px;
      z-index: 10000;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      font-weight: bold;
      max-width: 400px;
    `;
    warningDiv.textContent = message;

    document.body.appendChild(warningDiv);

    setTimeout(() => {
      if (warningDiv.parentNode) {
        warningDiv.parentNode.removeChild(warningDiv);
      }
    }, 5000);

    console.warn('Camera movement warning:', message);
  }

  handleExcessiveNoMovement() {
    const message = 'Interview flagged due to extended user absence. Please ensure you remain visible during the interview.';
    alert(message);

    console.warn('User visibility issue detected', {
      movementWarnings: this.movementWarnings,
      timestamp: new Date().toISOString()
    });
  }

  async startRecording() {
    try {
      if (this.recognition) this.recognition.start();

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);
      this.audioChunks = [];

      this.mediaRecorder.ondataavailable = (event) => { this.audioChunks.push(event.data); };
      this.mediaRecorder.onstop = () => {
        this.recordedAudio = new Blob(this.audioChunks, { type: 'audio/webm' });
        const playbackBtn = document.getElementById('playback-btn');
        if (playbackBtn) playbackBtn.style.display = 'inline-flex';
      };

      this.mediaRecorder.start();
      this.updateRecorderStatus('Recording...', true);
      document.getElementById('start-recording-btn').style.display = 'none';
      document.getElementById('stop-recording-btn').style.display = 'inline-flex';

      // Don't clear transcript when starting new recording - preserve existing content
      const transcriptText = document.getElementById('transcript-text');
      if (transcriptText && !this.transcript) {
        transcriptText.textContent = 'Your spoken answer will appear here.';
      }
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  }

  stopRecording() {
    if (this.recognition) this.recognition.stop();
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
      this.mediaRecorder.stream.getTracks().forEach((t) => t.stop());
    }
    this.updateRecorderStatus('Recording stopped', false);
    document.getElementById('start-recording-btn').style.display = 'inline-flex';
    document.getElementById('stop-recording-btn').style.display = 'none';
  }

  playbackRecording() {
    if (this.recordedAudio) {
      const audio = new Audio(URL.createObjectURL(this.recordedAudio));
      audio.play();
    }
  }

  updateRecorderStatus(text, isRecording) {
    const statusText = document.getElementById('recorder-status-text');
    const statusIndicator = document.querySelector('.status-indicator');
    if (statusText) statusText.textContent = text;
    if (statusIndicator) statusIndicator.classList.toggle('recording', isRecording);
  }

  playQuestionAudio() {
    if (!('speechSynthesis' in window)) {
      alert('Text-to-speech not supported in this browser.');
      return;
    }

    const text = this.currentQuestion?.question || this.currentQuestion?.question_text;
    if (!text) return;
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 1; utter.pitch = 1; utter.lang = 'en-US';
    window.speechSynthesis.speak(utter);
  }

  /* ==========================
   *  VALIDATION HELPERS
   * ========================== */

  validateCode(code) {
    if (!code || !code.trim()) {
      return 'Please write some code before submitting.';
    }

    const lines = code.split('\n').filter(line => line.trim().length > 0);
    if (lines.length < 2) {
      return 'Please write more substantial code (at least 2 lines).';
    }

    const hasFunction = /\bfunction\b|\bdef\b|\bclass\b|\bpublic\b|\bprivate\b|=>/.test(code);
    const hasLoop = /\bfor\b|\bwhile\b|\bdo\b/.test(code);
    const hasConditional = /\bif\b|\belse\b|\bswitch\b|\bcase\b/.test(code);

    if (!hasFunction && !hasLoop && !hasConditional) {
      return 'Please include at least one function, loop, or conditional statement.';
    }

    const openBraces = (code.match(/\{/g) || []).length;
    const closeBraces = (code.match(/\}/g) || []).length;
    const openParens = (code.match(/\(/g) || []).length;
    const closeParens = (code.match(/\)/g) || []).length;

    if (openBraces !== closeBraces) {
      return 'Please check your code - mismatched braces detected.';
    }

    if (openParens !== closeParens) {
      return 'Please check your code - mismatched parentheses detected.';
    }

    return null;
  }

  showValidationError(message) {
    let errorDiv = document.getElementById('validation-error');
    if (!errorDiv) {
      errorDiv = document.createElement('div');
      errorDiv.id = 'validation-error';
      errorDiv.style.cssText = `
        background: #fee;
        border: 1px solid #fcc;
        color: #c33;
        padding: 10px;
        margin: 10px 0;
        border-radius: 4px;
        font-size: 14px;
      `;

      const submitBtn = document.getElementById('submit-answer-btn');
      if (submitBtn && submitBtn.parentNode) {
        submitBtn.parentNode.insertBefore(errorDiv, submitBtn);
      }
    }

    errorDiv.textContent = message;
    errorDiv.style.display = 'block';

    setTimeout(() => {
      if (errorDiv) {
        errorDiv.style.display = 'none';
      }
    }, 5000);

    alert(message);
  }

  /* ==========================
   *  INTERVIEW START & FLOW
   * ========================== */

  async handleConfigSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const numQuestionsRaw = formData.get('num_questions');
    let numQuestions = numQuestionsRaw ? parseInt(numQuestionsRaw, 10) : 8;
    if (Number.isNaN(numQuestions) || numQuestions <= 0) {
      numQuestions = 8;
    }
    const config = {
      role: formData.get('role'),
      domain: formData.get('domain') || 'frontend',
      tech_stack: this.getTags('tech-stack-tags'),
      skill_tags: this.getTags('skill-tags-container'),
      difficulty: formData.get('difficulty'),
      num_questions: numQuestions,
      question_types: Array.from(document.querySelectorAll('input[name="question_types"]:checked')).map(cb => cb.value),
      mode: formData.get('mode'),
    };
    await this.startInterview(config);
  }

  async startInterview(config) {
    try {
      const token = localStorage.getItem('token');
      // Allow interview without token for testing (optional JWT)
      if (!token) {
        console.warn('No JWT token found, proceeding without authentication');
      }

      this.difficulty = config.difficulty || 'medium';

      const headers = {
        'Content-Type': 'application/json',
      };

      // Only add Authorization header if token exists
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else {
        console.log('No token found, proceeding without authentication');
      }

      const apiUrl = `${this.apiBaseUrl}/interview/start`;
      console.log('Starting interview with config:', config);
      console.log('API URL:', apiUrl);
      console.log('Headers:', headers);

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(config),
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (!response.ok) {
        if (response.status === 401) {
          console.warn('JWT Token expired or invalid');
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          alert('Your session has expired. Please log in again to save your progress.');
          // Optional: redirect to login if strictly required, or allow guest mode
          // window.location.href = 'index.html'; 
          // For now, we will just clear the token so they can try again or continue as guest if backed supports it
        }

        console.error('startInterview response not OK:', response.status);
        const errorText = await response.text();
        console.error('Error response body:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      this.currentSession = data.session_id || 'local-ai-session';
      this.demoQuestions = data.questions || [];
      this.questionIndex = 0;
      this.answers = [];
      this.question_times = [];

      if (!this.demoQuestions.length) {
        alert('Backend did not return any questions.');
        return;
      }

      document.getElementById('config-screen').classList.remove('active');
      document.getElementById('interview-screen').classList.add('active');

      if (!this.editor) this.initializeMonaco();
      else setTimeout(() => this.editor.layout(), 0);

      document.getElementById('interview-role').textContent = config.role;
      document.getElementById('interview-mode').textContent =
        config.mode === 'practice' ? 'Practice Mode' : 'Exam Mode';
      document.getElementById('total-q-num').textContent = this.demoQuestions.length;

      // Reset and activate tab switching detection
      this.tabSwitchCount = 0;
      this.isInterviewActive = true;

      this.overallStartTime = Date.now();
      this.startTimers();
      this.showQuestion();
    } catch (error) {
      console.error('Error starting interview:', error);
      console.error('Error details:', error.message);
      console.error('Error stack:', error.stack);
      alert(`Failed to start interview: ${error.message}. Check console for details.`);
    }
  }

  getQuestionTypeLabel(type) {
    const labels = { coding: 'Coding', behavioral: 'Behavioral', system_design: 'System Design' };
    return labels[type] || 'Question';
  }

  showQuestion() {
    const q = this.demoQuestions[this.questionIndex];
    if (!q) {
      this.showResults();
      return;
    }

    this.currentQuestion = q;
    this.questionStartTime = Date.now();

    document.getElementById('current-q-num').textContent = this.questionIndex + 1;
    document.getElementById('question-text').textContent =
      q.question || q.question_text || 'Question not found';
    document.getElementById('question-type-badge').textContent =
      this.getQuestionTypeLabel(q.type);

    const remarkText = document.getElementById('ai-remark-text');
    if (remarkText) {
      remarkText.textContent = 'After you submit, AI remarks about your answer will appear here.';
    }

    const isCoding = q.type === 'coding';
    const isAptitude = q.type === 'aptitude';

    document.getElementById('coding-answer-container').style.display = isCoding ? 'block' : 'none';
    document.getElementById('aptitude-answer-container').style.display = isAptitude ? 'block' : 'none';
    document.getElementById('voice-answer-container').style.display = (!isCoding && !isAptitude) ? 'block' : 'none';

    if (isAptitude) {
      this.selectedOption = null;
      const optionsContainer = document.getElementById('aptitude-options');
      if (optionsContainer) {
        optionsContainer.innerHTML = '';
        const options = q.options || [];
        options.forEach((opt, idx) => {
          const btn = document.createElement('div');
          btn.className = 'aptitude-option-btn';
          btn.textContent = opt;
          btn.onclick = () => this.selectAptitudeOption(opt, btn);
          optionsContainer.appendChild(btn);
        });
      }
    }

    if (isCoding && this.editor) {
      this.editor.setValue('// Write your code here\n');
    } else {
      // Only clear transcript if it's a new question (not when returning to previous question)
      if (this.questionIndex >= this.answers.length) {
        this.transcript = '';
        const transcriptText = document.getElementById('transcript-text');
        if (transcriptText) transcriptText.textContent = 'Your spoken answer will appear here.';
      }
      const textArea = document.getElementById('text-answer');
      if (textArea && this.questionIndex >= this.answers.length) {
        textArea.value = '';
      }
    }

    const progress = (this.questionIndex / this.demoQuestions.length) * 100 || 0;
    document.getElementById('interview-progress-bar').style.width = `${progress}%`;
    document.getElementById('progress-percent').textContent = Math.round(progress);

    this.resetQuestionTimer();
  }

  /* ==========================
   *  TIMERS
   * ========================== */

  selectAptitudeOption(option, btnElement) {
    this.selectedOption = option;
    // Visually update buttons
    document.querySelectorAll('.aptitude-option-btn').forEach(b => b.classList.remove('selected'));
    if (btnElement) btnElement.classList.add('selected');
  }

  /* ==========================
   *  TIMERS
   * ========================== */

  startTimers() {
    let overallSeconds = 0;
    if (this.overallTimer) clearInterval(this.overallTimer);
    this.overallTimer = setInterval(() => {
      if (!this.isPaused) {
        overallSeconds++;
        this.updateOverallTimer(overallSeconds);
      }
    }, 1000);
    this.resetQuestionTimer();
  }

  resetQuestionTimer() {
    if (this.questionTimer) clearInterval(this.questionTimer);
    let questionSeconds = 0;
    this.questionTimer = setInterval(() => {
      if (!this.isPaused) {
        questionSeconds++;
        this.updateQuestionTimer(questionSeconds);
      }
    }, 1000);
  }

  updateOverallTimer(seconds) {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    const timerText = document.querySelector('.timer-text');
    if (timerText) {
      timerText.textContent = `${String(hours).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(
        secs
      ).padStart(2, '0')}`;
    }
  }

  updateQuestionTimer(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    const questionTime = document.getElementById('question-time');
    if (questionTime) {
      questionTime.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
  }

  pauseTimers() {
    this.isPaused = true;
    document.getElementById('pause-btn').style.display = 'none';
    document.getElementById('resume-btn').style.display = 'inline-flex';
  }

  resumeTimers() {
    this.isPaused = false;
    document.getElementById('pause-btn').style.display = 'inline-flex';
    document.getElementById('resume-btn').style.display = 'none';
  }

  /* ==========================
   *  SUBMIT ANSWER
   * ========================== */

  async submitAnswer() {
    const submitBtn = document.getElementById('submit-answer-btn');
    if (submitBtn && submitBtn.disabled) return; // Prevent double clicks

    if (!this.currentQuestion) return;

    // Temporarily disable button to prevent double submission
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerText = 'Submitting...';
    }

    try {

      const isCoding = this.currentQuestion.type === 'coding';
      const isAptitude = this.currentQuestion.type === 'aptitude';
      let answerData = {};
      let answerText = '';
      let audioBase64 = null;

      if (isCoding) {
        const code = this.editor?.getValue() || '';
        if (!code.trim()) {
          this.showValidationError('Please write some code before submitting.');
          return;
        }

        // Enhanced code validation
        const validationError = this.validateCode(code);
        if (validationError) {
          this.showValidationError(validationError);
          return;
        }

        answerData = {
          type: 'coding',
          code,
          language: document.getElementById('language-select').value,
        };
        answerText = code;
      } else if (isAptitude) {
        const selected = this.selectedOption;
        if (!selected) {
          alert('Please select an option before submitting.');
          this.showValidationError('Please select an option.');
          if (submitBtn) { submitBtn.disabled = false; submitBtn.innerText = 'Submit Answer'; }
          return;
        }
        answerData = { type: 'aptitude', answer: selected };
        answerText = selected;
      } else {
        const textArea = document.getElementById('text-answer');
        const typedAnswer = textArea ? textArea.value.trim() : '';
        const finalTranscript = typedAnswer || this.transcript;

        if (!finalTranscript) {
          alert('Please either speak or type your answer before submitting.');
          return;
        }

        audioBase64 = await this.blobToBase64(this.recordedAudio);
        answerData = {
          type: 'voice',
          transcript: finalTranscript,
          audio: audioBase64,
        };
        answerText = finalTranscript;
      }

      const now = Date.now();
      const timeTakenSec = Math.max(1, Math.round((now - (this.questionStartTime || now)) / 1000));
      this.question_times.push(timeTakenSec);

      let evaluation = null;
      let completed = false;
      const token = localStorage.getItem('token');
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers.Authorization = `Bearer ${token}`;

      try {
        const resp = await fetch(`${this.apiBaseUrl}/interview/${this.currentSession}/answer`, {
          method: 'POST',
          headers,
          body: JSON.stringify({ ...answerData, time_taken: timeTakenSec }),
        });
        const serverData = await resp.json();
        evaluation = serverData?.evaluation || null;
        completed = !!serverData?.completed;

        const remarkText = document.getElementById('ai-remark-text');
        if (remarkText && evaluation) {
          const innerEval = evaluation.evaluation || {};
          remarkText.textContent =
            innerEval.remark ||
            evaluation.feedback ||
            evaluation.remark ||
            'Answer submitted. Backend evaluation received.';
        }
      } catch (err) {
        console.warn('Failed to send answer to backend; proceeding without evaluation.', err);
      }

      this.answers.push({
        question_id: this.currentQuestion.id || this.currentQuestion._id || this.questionIndex,
        question: this.currentQuestion.question || this.currentQuestion.question_text,
        type: this.currentQuestion.type,
        answer_text: answerText,
        audio: audioBase64,
        category: this.currentQuestion.category || this.currentQuestion.topic || null,
        difficulty: this.currentQuestion.difficulty || this.difficulty,
        time_taken: timeTakenSec,
        submitted_at: new Date().toISOString(),
        evaluation,
      });

      this.questionIndex++;

      // Check if interview is completed
      const isInterviewCompleted = completed || this.questionIndex >= this.demoQuestions.length;

      if (isInterviewCompleted) {
        // Stop timers and cleanup proctoring before showing results
        this.stopTimers();
        this.cleanupProctoring();

        // Show completion message briefly
        const submitBtn = document.getElementById('submit-answer-btn');
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.textContent = 'Interview Completed';
          submitBtn.style.background = '#28a745';
          submitBtn.style.cursor = 'default';

          // Add final submission functionality
        }

        // Brief delay then show results automatically
        setTimeout(() => {
          this.showResults();
        }, 100); // reduced delay for faster feedback
      } else {// Reset validation error display
        const errorDiv = document.getElementById('validation-error');
        if (errorDiv) {
          errorDiv.style.display = 'none';
        }

        // Clear editor for next coding question
        if (this.currentQuestion.type === 'coding' && this.editor) {
          this.editor.setValue('');
        }

        // Clear transcript for next question
        this.transcript = '';
        const textArea = document.getElementById('text-answer');
        if (textArea) {
          textArea.value = '';
        }

        this.showQuestion();
      }

      // Re-enable button if we are continuing or if there was an error that didn't complete the interview
      if (!isInterviewCompleted && submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerText = 'Submit Answer';
      }

      // FIX: Ensure progress bar hits 100% if completed
      if (isInterviewCompleted) {
        const progressBar = document.getElementById('interview-progress-bar');
        const progressPercent = document.getElementById('progress-percent');
        if (progressBar) progressBar.style.width = '100%';
        if (progressPercent) progressPercent.textContent = '100';
      }

    } catch (error) {
      console.error("Error submitting answer:", error);
      const submitBtn = document.getElementById('submit-answer-btn');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerText = 'Submit Answer';
      }
      // Only alert if it's a real error, not a successful completion disguised as error
      if (error.message !== 'Interview Completed') {
        alert(`Failed to submit: ${error.message || 'Unknown error'}`);
      }
    }
  }

  previousQuestion() {
    if (this.questionIndex > 0) {
      this.questionIndex--;
      this.answers.pop();
      this.question_times.pop();
      this.showQuestion();
    }
  }

  async endInterview() {
    if (confirm('Are you sure you want to end the interview?')) {
      this.cleanupProctoring();
      await this.showResults();
    }
  }

  /* ==========================
   *  RESULTS
   * ========================== */

  async showResults() {
    const token = localStorage.getItem('token');

    let results = null;
    if (token && this.currentSession) {
      try {
        const resp = await fetch(
          `${this.apiBaseUrl}/interview/${this.currentSession}/results`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        if (resp.ok) {
          results = await resp.json();
        } else {
          console.warn('Server results not available; status:', resp.status);
        }
      } catch (err) {
        console.warn('Error fetching server results, using local results.', err);
      }
    }

    if (!results || !Array.isArray(results.answers) || results.answers.length === 0) {
      const total_time_seconds = Math.max(
        0,
        Math.round((Date.now() - (this.overallStartTime || Date.now())) / 1000)
      );
      results = {
        answers: this.answers.map((a) => ({
          question: a.question,
          type: a.type,
          answer_text: a.answer_text,
          evaluation: a.evaluation,
          time_taken: a.time_taken,
          category: a.category,
          reference_answer: a.evaluation?.reference_answer,
          reference_points: a.evaluation?.reference_points,
        })),
        difficulty: this.difficulty || 'medium',
        time_spent: total_time_seconds,
        question_times: this.question_times.slice(),
      };
    }

    // Derive strengths and weaknesses from evaluations for both server and fallback paths
    const summaryAnswers = results.answers || [];
    const strengths = [];
    const weaknesses = [];
    summaryAnswers.forEach((a) => {
      const ev = a.evaluation || {};
      const inner = ev.evaluation || ev;
      if (Array.isArray(inner.strengths)) {
        strengths.push(...inner.strengths);
      }
      if (Array.isArray(inner.improvements)) {
        weaknesses.push(...inner.improvements);
      }
    });
    results.strengths = strengths.slice(0, 15);
    results.weaknesses = weaknesses.slice(0, 15);

    if (results && results.time_taken && !results.time_spent) {
      results.time_spent = results.time_taken;
    }

    if (this.overallTimer) clearInterval(this.overallTimer);
    if (this.questionTimer) clearInterval(this.questionTimer);
    if (this.videoStream) this.videoStream.getTracks().forEach((t) => t.stop());

    this.displayResults(results);

    try {
      await this.saveAnalyticsAttempt(results);
    } catch (err) {
      console.warn('Failed to save analytics attempt:', err);
    }
  }

  displayResults(results) {
    const resultsContent = document.getElementById('results-content');
    if (!resultsContent) return;

    const answers = results.answers || [];
    let earnedPoints = 0;

    const questionCards = answers.map((ans, index) => {
      const ev = ans.evaluation || {};
      const score = typeof ev.score === 'number' ? ev.score : 0;
      const isCorrect = ev.is_correct === true || ev.passed === true || score >= 50;
      if (isCorrect) earnedPoints += 1;

      // Per-answer strength classification
      const classification = score >= 75 ? 'Strong' : score >= 50 ? 'Average' : 'Weak';
      const classColor = score >= 75 ? '#2D6A4F' : score >= 50 ? '#B7791F' : '#C0392B';
      const classBg = score >= 75 ? 'rgba(45,106,79,0.12)' : score >= 50 ? 'rgba(183,121,31,0.12)' : 'rgba(192,57,43,0.10)';

      const type = ans.type || 'coding';
      const referenceAnswer = ev.reference_answer || ans.reference_answer || '';
      const referencePoints = ev.reference_points || ans.reference_points || [];
      const solutionCode = ev.solution_code || '';
      const solutionExplanation = ev.solution_explanation || '';
      const feedback = ev.answer_feedback || '';
      const questionText = ans.question || '';
      const userAnswer = ans.answer_text || '';
      const typeLabel = this.getQuestionTypeLabel(type);

      // Determine what to show in "Reference Search / Solution" block based on type
      let solutionBlockHtml = '';

      if (type === 'coding') {
        // CODING: Show Code + Explanation + Points
        if (solutionCode) {
          solutionBlockHtml += `<div class="code-answer"><pre>${this.escapeHtml(solutionCode)}</pre></div>`;
        }
        if (solutionExplanation) {
          solutionBlockHtml += `<p class="solution-explanation">${this.escapeHtml(solutionExplanation)}</p>`;
        }
        // specific points
        if (referencePoints && referencePoints.length) {
          solutionBlockHtml += `<ul class="explanation-points">${referencePoints.map(p => `<li>${this.escapeHtml(p)}</li>`).join('')}</ul>`;
        }
      } else if (type === 'behavioral' || type === 'system_design') {
        // BEHAVIORAL: Show Reference Answer Text + Points
        if (referenceAnswer) {
          solutionBlockHtml += `<p class="ref-answer-text">${this.escapeHtml(referenceAnswer)}</p>`;
        }
        if (referencePoints && referencePoints.length) {
          solutionBlockHtml += `<ul class="explanation-points">${referencePoints.map(p => `<li>${this.escapeHtml(p)}</li>`).join('')}</ul>`;
        }
      } else if (type === 'aptitude') {
        // APTITUDE: Show Correct Answer + Explanation
        // referenceAnswer usually holds the correct option text here
        if (referenceAnswer) {
          solutionBlockHtml += `<div class="correct-option-display"><strong>Correct Answer:</strong> ${this.escapeHtml(referenceAnswer)}</div>`;
        }
        if (solutionExplanation) {
          solutionBlockHtml += `<p class="solution-explanation">${this.escapeHtml(solutionExplanation)}</p>`;
        }
        // Use explanation from backend if specifically present (sometimes mapped to solutionExplanation)
      } else {
        // Fallback
        if (referenceAnswer) solutionBlockHtml += `<p>${this.escapeHtml(referenceAnswer)}</p>`;
      }


      return `
        <div class="question-review-card ${isCorrect ? 'correct' : 'incorrect'}">
          <div class="question-top-row">
            <div class="question-main">
              <span class="question-number">Q${index + 1}.</span>
              <span class="question-text">${this.escapeHtml(questionText)}</span>
            </div>
            <div class="question-meta">
              <span class="question-type-pill">${typeLabel}</span>
              <span class="question-point-pill">${isCorrect ? '1 / 1 point' : '0 / 1 point'
        }</span>
            </div>
          </div>

          <div class="question-body">
            <div class="question-section">
              <div class="question-section-title">Your answer</div>
              <div class="user-answer-block">
                ${type === 'coding'
          ? `<pre>${this.escapeHtml(userAnswer || '// No answer')}</pre>`
          : `<p>${this.escapeHtml(userAnswer || 'No answer')}</p>`
        }
              </div>
            </div>

            <div class="question-section">
              <div class="question-section-title">Result</div>
              <div class="question-result-line">
                ${isCorrect
          ? `<span class="correct-text">✔ Correct (1 point)</span>`
          : `<span class="incorrect-text">✘ Incorrect (0 points)</span>`
        }
                <span style="margin-left:10px; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; background:${classBg}; color:${classColor};">${classification}</span>
                ${ev.remark || (ev.evaluation && ev.evaluation.remark)
          ? `<span style="margin-left:10px; font-size:0.82rem; color:#6B3A2A;">${this.escapeHtml(ev.remark || ev.evaluation?.remark || '')}</span>`
          : ''
        }
              </div>
            </div>

            <div class="question-section">
              <div class="question-section-title">Reference answer / solution</div>
              <div class="reference-answer-block">
                ${solutionBlockHtml || '<p class="text-muted">No reference solution available.</p>'}
              </div>
            </div>
          </div>
        </div>
      `;
    });

    const totalPoints = answers.length || 0;
    const gradePercent =
      totalPoints > 0 ? Math.round((earnedPoints / totalPoints) * 100) : 0;
    const passed = gradePercent >= 80;

    const resultsHtml = `
      <div class="results-banner ${passed ? 'pass' : 'fail'}">
        <div class="results-banner-left">
          <div class="banner-icon">${passed ? '✔' : '✺'}</div>
          <div>
            <div class="banner-title">
              ${passed ? 'Congratulations! You passed!' : 'Good try! Keep practicing!'}
            </div>
            <div class="banner-subtitle">To pass: 80% or higher</div>
          </div>
        </div>
        <div class="results-banner-right">
          <button class="btn btn-primary" onclick="window.location.href='interview.html'">Keep Learning</button>
          <div class="grade-box">
            <div class="grade-label">Grade</div>
            <div class="grade-value">${gradePercent}%</div>
          </div>
        </div>
      </div>

      <section class="results-overview">
        <h1 class="results-title">Overview</h1>
        <div class="results-subtitle">
          Total points ${totalPoints} • You scored ${earnedPoints} / ${totalPoints}
        </div>
      </section>

      <!-- Final Analysis -->
      ${(() => {
        const strengths = results.strengths || [];
        const weaknesses = results.weaknesses || [];
        const improvements = results.improvements || weaknesses;

        // Compute strong/average/weak counts
        const strongCount = answers.filter(a => { const s = a.evaluation?.score || 0; return s >= 75; }).length;
        const averageCount = answers.filter(a => { const s = a.evaluation?.score || 0; return s >= 50 && s < 75; }).length;
        const weakCount = answers.filter(a => { const s = a.evaluation?.score || 0; return s < 50; }).length;

        const overallRating = gradePercent >= 75 ? 'Strong' : gradePercent >= 50 ? 'Average' : 'Needs Improvement';
        const ratingColor = gradePercent >= 75 ? '#2D6A4F' : gradePercent >= 50 ? '#B7791F' : '#C0392B';

        const strengthsHtml = strengths.length
          ? strengths.map(s => `<li style="margin-bottom:4px;">✅ ${this.escapeHtml(s)}</li>`).join('')
          : '<li style="color:#9B6B5A;">Keep practicing to build more strengths!</li>';

        const weakHtml = improvements.length
          ? improvements.map(w => `<li style="margin-bottom:4px;">📌 ${this.escapeHtml(w)}</li>`).join('')
          : '<li style="color:#9B6B5A;">Great job — no major weak areas identified!</li>';

        return `
        <div style="background:rgba(255,255,255,0.7); border:1px solid rgba(97,33,15,0.12); border-radius:16px; padding:28px; margin-bottom:24px;">
          <h2 style="font-size:1.1rem; font-weight:700; color:#61210F; margin-bottom:20px; padding-bottom:10px; border-bottom:1px solid rgba(97,33,15,0.12);">📊 Final Analysis</h2>

          <!-- Overall Score + Rating -->
          <div style="display:flex; gap:16px; margin-bottom:20px; flex-wrap:wrap;">
            <div style="flex:1; min-width:120px; background:rgba(97,33,15,0.06); border-radius:12px; padding:16px; text-align:center;">
              <div style="font-size:2rem; font-weight:700; color:#61210F;">${gradePercent}%</div>
              <div style="font-size:0.8rem; color:#6B3A2A; margin-top:4px;">Overall Score</div>
            </div>
            <div style="flex:1; min-width:120px; background:rgba(97,33,15,0.06); border-radius:12px; padding:16px; text-align:center;">
              <div style="font-size:1.4rem; font-weight:700; color:${ratingColor};">${overallRating}</div>
              <div style="font-size:0.8rem; color:#6B3A2A; margin-top:4px;">Performance Rating</div>
            </div>
            <div style="flex:1; min-width:120px; background:rgba(45,106,79,0.08); border-radius:12px; padding:16px; text-align:center;">
              <div style="font-size:1.4rem; font-weight:700; color:#2D6A4F;">${strongCount}</div>
              <div style="font-size:0.8rem; color:#2D6A4F; margin-top:4px;">Strong Answers</div>
            </div>
            <div style="flex:1; min-width:120px; background:rgba(183,121,31,0.08); border-radius:12px; padding:16px; text-align:center;">
              <div style="font-size:1.4rem; font-weight:700; color:#B7791F;">${averageCount}</div>
              <div style="font-size:0.8rem; color:#B7791F; margin-top:4px;">Average Answers</div>
            </div>
            <div style="flex:1; min-width:120px; background:rgba(192,57,43,0.08); border-radius:12px; padding:16px; text-align:center;">
              <div style="font-size:1.4rem; font-weight:700; color:#C0392B;">${weakCount}</div>
              <div style="font-size:0.8rem; color:#C0392B; margin-top:4px;">Weak Answers</div>
            </div>
          </div>

          <!-- Strengths & Improvements in 2 columns -->
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(240px,1fr)); gap:16px;">
            <div style="background:rgba(45,106,79,0.06); border-radius:12px; padding:16px;">
              <div style="font-weight:600; color:#2D6A4F; margin-bottom:10px;">💪 Strength Areas</div>
              <ul style="margin:0; padding-left:18px; font-size:0.9rem; color:#2A140E; line-height:1.7;">${strengthsHtml}</ul>
            </div>
            <div style="background:rgba(192,57,43,0.06); border-radius:12px; padding:16px;">
              <div style="font-weight:600; color:#C0392B; margin-bottom:10px;">📈 Areas for Improvement</div>
              <ul style="margin:0; padding-left:18px; font-size:0.9rem; color:#2A140E; line-height:1.7;">${weakHtml}</ul>
            </div>
          </div>
        </div>`;
      })()}

      <div class="score-breakdown">
        <div class="breakdown-card">
          <div class="breakdown-label">Coding</div>
          <div class="breakdown-value">${(() => {
        const coding = answers.filter((a) => a.type === 'coding');
        if (!coding.length) return '—';
        const got = coding.filter(
          (a) =>
            a.evaluation &&
            (a.evaluation.is_correct === true ||
              a.evaluation.passed === true ||
              a.evaluation.score >= 50)
        ).length;
        return `${got} / ${coding.length}`;
      })()
      }</div>
        </div>
        <div class="breakdown-card">
          <div class="breakdown-label">Behavioral</div>
          <div class="breakdown-value">${(() => {
        const beh = answers.filter((a) => a.type === 'behavioral');
        if (!beh.length) return '—';
        const got = beh.filter(
          (a) =>
            a.evaluation &&
            (a.evaluation.is_correct === true ||
              a.evaluation.passed === true ||
              a.evaluation.score >= 50)
        ).length;
        return `${got} / ${beh.length}`;
      })()
      }</div>
        </div>
        <div class="breakdown-card">
          <div class="breakdown-label">System Design</div>
          <div class="breakdown-value">${(() => {
        const sd = answers.filter((a) => a.type === 'system_design');
        if (!sd.length) return '—';
        const got = sd.filter(
          (a) =>
            a.evaluation &&
            (a.evaluation.is_correct === true ||
              a.evaluation.passed === true ||
              a.evaluation.score >= 50)
        ).length;
        return `${got} / ${sd.length}`;
      })()
      }</div>
        </div>
      </div>

      <section class="per-question-review">
        <h3>Question-wise Review</h3>
        ${questionCards.join('')}
      </section>

      <div class="results-actions">
        <a href="interview.html" class="btn btn-secondary">Retake interview</a>
        <a href="analytics.html" class="btn btn-primary">View detailed analytics</a>
      </div>
    `;

    resultsContent.innerHTML = resultsHtml;
  }

  /* ==========================
   *  SAVE ANALYTICS ATTEMPT
   * ========================== */

  async saveAnalyticsAttempt(results) {
    try {
      const answers = results.answers || [];
      const total = answers.length;
      const correct = answers.filter((a) => {
        const ev = a.evaluation || {};
        if (ev.is_correct === true || ev.passed === true) return true;
        return typeof ev.score === 'number' ? ev.score >= 50 : false;
      }).length;
      const finalScore = results.score ?? (total ? Math.round((correct / total) * 100) : 0);

      const topics = Array.from(
        new Set(answers.map((a) => a.category).filter(Boolean))
      );
      let question_times =
        results.question_times || answers.map((a) => a.time_taken || 0);
      if (question_times.length !== total) {
        console.warn('question_times length mismatch', {
          expected: total,
          actual: question_times.length,
        });
      }

      let timeSpentSeconds = 0;
      if (typeof results.time_taken === 'number' && results.time_taken > 0) {
        timeSpentSeconds = Math.round(results.time_taken);
      } else if (typeof results.time_spent === 'number' && results.time_spent > 0) {
        timeSpentSeconds = Math.round(results.time_spent);
      } else {
        timeSpentSeconds = Math.max(
          0,
          Math.round((Date.now() - (this.overallStartTime || Date.now())) / 1000)
        );
      }

      const payload = {
        score: finalScore,
        correct,
        total,
        difficulty: results.difficulty || this.difficulty || 'medium',
        time_spent: timeSpentSeconds,
        question_times,
        topics,
        strengths: results.strengths || [],
        weaknesses: results.weaknesses || [],
      };

      const res = await fetch(`${this.apiBaseUrl}/analytics/store`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        console.warn('Analytics store request failed', await res.text());
      } else {
        console.log('Analytics attempt saved successfully');
      }
    } catch (err) {
      console.error('Failed to save analytics attempt:', err);
    }
  }

  /* ==========================
   *  PRESETS
   * ========================== */

  applyPreset(presetName) {
    const presets = {
      'frontend-react': {
        role: 'Frontend Developer',
        tech_stack: ['React', 'JavaScript', 'HTML', 'CSS'],
        skill_tags: ['React Hooks', 'Redux', 'TypeScript'],
        difficulty: 'medium',
        num_questions: 8,
        question_types: ['coding', 'behavioral'],
        mode: 'practice',
      },
      'backend-node': {
        role: 'Backend Developer',
        tech_stack: ['Node.js', 'Express', 'MongoDB'],
        skill_tags: ['REST APIs', 'Database Design'],
        difficulty: 'medium',
        num_questions: 10,
        question_types: ['coding', 'system_design'],
        mode: 'practice',
      },
      fullstack: {
        role: 'Full Stack Developer',
        tech_stack: ['React', 'Node.js', 'PostgreSQL'],
        skill_tags: ['Full Stack', 'Architecture'],
        difficulty: 'medium',
        num_questions: 12,
        question_types: ['coding', 'behavioral', 'system_design'],
        mode: 'practice',
      },
      senior: {
        role: 'Senior Software Engineer',
        tech_stack: ['Multiple'],
        skill_tags: ['Architecture', 'Leadership'],
        difficulty: 'hard',
        num_questions: 15,
        question_types: ['coding', 'system_design'],
        mode: 'exam',
      },
    };

    const preset = presets[presetName];
    if (!preset) return;

    document.getElementById('role').value = preset.role;
    document.querySelector(
      `input[name="difficulty"][value="${preset.difficulty}"]`
    ).checked = true;
    document.getElementById('num-questions').value = preset.num_questions;
    document.querySelector(`input[name="mode"][value="${preset.mode}"]`).checked =
      true;

    document.getElementById('tech-stack-tags').innerHTML = '';
    preset.tech_stack.forEach((tag) =>
      this.addTag(tag, document.getElementById('tech-stack-tags'))
    );

    document.getElementById('skill-tags-container').innerHTML = '';
    preset.skill_tags.forEach((tag) =>
      this.addTag(tag, document.getElementById('skill-tags-container'))
    );

    document
      .querySelectorAll('input[name="question_types"]')
      .forEach((cb) => {
        cb.checked = preset.question_types.includes(cb.value);
      });
  }

  loadPresets() {
    // nothing extra yet
  }
}

/* ==========================
 *  BOOTSTRAP
 * ========================== */

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new InterviewManager());
} else {
  new InterviewManager();
}
