const API_URL = '/api/chat';

// DOM Elements
const questionInput = document.getElementById('question-input');
const askBtn = document.getElementById('ask-btn');
const loadingEl = document.getElementById('loading');
const chatHistoryEl = document.getElementById('chat-history');
const heroHeader = document.getElementById('hero-header');
const exampleChips = document.getElementById('example-chips');

const sidebarPlaceholder = document.getElementById('sidebar-placeholder');
const cardResources = document.getElementById('card-resources');
const cardStatus = document.getElementById('card-status');

const imageInput = document.getElementById('image-input');
const imagePreviewWrap = document.getElementById('image-preview-wrap');
const imagePreview = document.getElementById('image-preview');
const uploadBtn = document.getElementById('upload-btn');

let currentImageDataUrl = null;
let chatHistory = []; // Stores conversation context for Gemini

// Allow Enter to submit (Shift+Enter for new line)
questionInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleAsk();
  }
});

function setQuestion(q) {
  questionInput.value = q;
  handleAsk();
}

// ── Image Upload Handling ──────────────────────────────────────────
async function handleImageUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  if (file.size > 5 * 1024 * 1024) {
    alert("Image is too large. Please upload an image smaller than 5MB.");
    return;
  }

  const reader = new FileReader();
  reader.onload = (evt) => {
    currentImageDataUrl = evt.target.result;
    imagePreview.src = currentImageDataUrl;
    imagePreviewWrap.classList.remove('hidden');
    uploadBtn.classList.add('has-image');
    questionInput.focus();
  };
  reader.readAsDataURL(file);
}

function removeImage() {
  currentImageDataUrl = null;
  imageInput.value = '';
  imagePreview.src = '';
  imagePreviewWrap.classList.add('hidden');
  uploadBtn.classList.remove('has-image');
}

// ── Chat Interaction ───────────────────────────────────────────────
async function handleAsk() {
  const question = questionInput.value.trim();
  
  if (!question && !currentImageDataUrl) {
    questionInput.focus();
    return;
  }

  // 1. Hide welcome text & chips on first message
  if (chatHistory.length === 0) {
    heroHeader.style.display = 'none';
    exampleChips.style.display = 'none';
  }

  // 2. Add User Message to UI
  appendUserMessage(question || "Attached an image.", currentImageDataUrl);
  
  // 3. Update internal chat history for NIM
  // We only send text in the history array, the image is passed separately to be injected into the latest message by the backend.
  chatHistory.push({
    role: "user",
    content: question || "Describe and explain what is shown in this image."
  });

  const payloadImage = currentImageDataUrl; // Capture it before clearing

  // Clear inputs
  questionInput.value = '';
  removeImage();
  questionInput.style.height = 'auto'; // reset textarea height

  // 4. Show Loading
  setLoading(true);

  try {
    const payload = { 
      messages: chatHistory 
    };
    if (payloadImage) {
      payload.image = payloadImage;
    }

    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const msg = data?.error || `Server error ${response.status}`;
      appendSystemError(msg);
      // Remove the last user message from history so they can retry
      chatHistory.pop();
      return;
    }

    if (data?.error) {
      appendSystemError(data.error);
      chatHistory.pop();
    } else {
      // Success!
      // Add assistant's answer to internal history
      chatHistory.push({
        role: "assistant",
        content: JSON.stringify(data) // Storing JSON back so it remembers its decisions
      });

      // Update UI
      appendModelMessage(data);
      updateSidebar(data);
    }

  } catch (err) {
    appendSystemError('Network error — could not reach the server.');
    console.error(err);
    chatHistory.pop();
  } finally {
    setLoading(false);
    scrollToBottom();
  }
}

// ── UI Appending Functions ────────────────────────────────────────
function appendUserMessage(text, imageDataUrl) {
  const div = document.createElement('div');
  div.className = 'message-wrapper user';
  
  let imgHtml = '';
  if (imageDataUrl) {
    imgHtml = `<img src="${imageDataUrl}" class="chat-image-attachment" alt="User upload" />`;
  }

  div.innerHTML = `
    <div class="message user">
      ${imgHtml}
      <p>${escapeHtml(text).replace(/\n/g, '<br>')}</p>
    </div>
  `;
  chatHistoryEl.appendChild(div);
  scrollToBottom();
}

function appendModelMessage(data) {
  const div = document.createElement('div');
  div.className = 'message-wrapper model';

  let contentHtml = '';
  if (data.can_ai_answer) {
    contentHtml = `<p>${escapeHtml(data.answer).replace(/\n/g, '<br>')}</p>`;
  } else {
    // Escalate style
    contentHtml = `
      <p><strong>Query Escalated</strong></p>
      <p class="message-escalated">This requires attention from your academic team. See the Query Status panel for next steps.</p>
    `;
  }

  div.innerHTML = `
    <div class="message model">
      ${contentHtml}
    </div>
  `;
  chatHistoryEl.appendChild(div);
}

function appendSystemError(text) {
  const div = document.createElement('div');
  div.className = 'message-wrapper model';
  div.innerHTML = `
    <div class="message model" style="border-color: #EF4444; background: #FEF2F2;">
      <p style="color: #B91C1C;"><strong>Error:</strong> ${escapeHtml(text)}</p>
    </div>
  `;
  chatHistoryEl.appendChild(div);
}

// ── Sidebar Updating ─────────────────────────────────────────────
function updateSidebar(data) {
  sidebarPlaceholder.classList.add('hidden');
  cardResources.classList.remove('hidden');
  cardStatus.classList.remove('hidden');

  renderResourcesPanel(data);
  renderStatusPanel(data);
}

function renderResourcesPanel(data) {
  const body = document.getElementById('resources-body');
  const topicBadge = document.getElementById('topic-badge');

  if (data.topic) {
    topicBadge.textContent = data.topic;
    topicBadge.style.display = 'inline-block';
  } else {
    topicBadge.style.display = 'none';
  }

  if (data.resources && data.resources.length > 0) {
    const items = data.resources.map(r => `
      <li class="resource-item">
        <a href="${escapeHtml(r.url)}" target="_blank" rel="noopener noreferrer">
          ${escapeHtml(r.title)} ↗
        </a>
        <p>${escapeHtml(r.description)}</p>
      </li>
    `).join('');
    body.innerHTML = `<ul class="resource-list">${items}</ul>`;
  } else {
    body.innerHTML = '<p style="color:#64748B;font-size:0.85rem;font-style:italic;">None needed (general knowledge or conversational chat).</p>';
  }
}

function renderStatusPanel(data) {
  const body = document.getElementById('status-body');
  const iconEl = document.getElementById('status-icon');

  if (data.can_ai_answer) {
    cardStatus.className = 'result-card card-status safe';
    iconEl.textContent = '✅';
    body.innerHTML = `
      <div class="status-content">
        <div class="status-indicator">
          <span class="status-dot dot-green"></span>
          AI can handle this
        </div>
        <div class="status-reason">You do not need a faculty member for this question.</div>
      </div>
    `;
  } else {
    cardStatus.className = 'result-card card-status escalate';
    iconEl.textContent = '🚨';
    body.innerHTML = `
      <div class="status-content">
        <div class="status-indicator" style="color: #EF4444;">
          <span class="status-dot dot-red"></span>
          Escalate to Faculty
        </div>
        <div class="status-reason">
          <strong>Reason:</strong> ${escapeHtml(data.escalate_reason || 'Administrative or personal matter.')}
        </div>
        <div class="contact-info">
          <strong>What to do next:</strong>
          Contact your course lecturer, module tutor, or the student services office directly.
        </div>
      </div>
    `;
  }
}

// ── Utils ────────────────────────────────────────────────────────
function setLoading(isLoading) {
  if (isLoading) {
    loadingEl.classList.remove('hidden');
    askBtn.disabled = true;
    questionInput.disabled = true;
  } else {
    loadingEl.classList.add('hidden');
    askBtn.disabled = false;
    questionInput.disabled = false;
    questionInput.focus();
  }
}

function scrollToBottom() {
  chatHistoryEl.scrollTo({
    top: chatHistoryEl.scrollHeight,
    behavior: 'smooth'
  });
}

function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.innerText = str;
  return div.innerHTML;
}
