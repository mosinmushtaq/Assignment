/**
 * AI Learner Assistant — Frontend Logic
 * =========================================
 * This file handles:
 *  1. Sending the student's question to our backend API (/api/chat)
 *  2. Receiving the structured JSON response
 *  3. Rendering the results in the 3 dashboard panels
 */

// ── Configuration ──────────────────────────────────────────────
// When running locally via Flask: backend is at http://localhost:5000
// When deployed on Vercel: use a relative path (same domain)
const API_URL = '/api/chat';

// ── DOM References ──────────────────────────────────────────────
const questionInput = document.getElementById('question-input');
const askBtn        = document.getElementById('ask-btn');
const loadingEl     = document.getElementById('loading');
const resultsEl     = document.getElementById('results');

// ── Utility: set an example question from a chip ───────────────
function setQuestion(text) {
  questionInput.value = text;
  questionInput.focus();
}

// ── Main Handler: called when "Ask AI" is clicked ──────────────
async function handleAsk() {
  const question = questionInput.value.trim();

  // Don't proceed if empty
  if (!question) {
    questionInput.focus();
    questionInput.style.borderColor = '#EF4444';
    setTimeout(() => { questionInput.style.borderColor = ''; }, 1500);
    return;
  }

  // Show loading, hide old results
  setLoading(true);
  hideResults();

  try {
    // Send question to our Python backend
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();

    if (data.error) {
      showError(data.error);
    } else {
      renderResults(data);
    }

  } catch (err) {
    showError('Could not connect to the AI. Please check your connection and try again.');
    console.error(err);
  } finally {
    setLoading(false);
  }
}

// ── Render: populate the 3 dashboard panels ────────────────────
function renderResults(data) {
  renderAnswerPanel(data);
  renderResourcesPanel(data);
  renderStatusPanel(data);

  // Show the results section with animation
  resultsEl.classList.remove('hidden');
  resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Panel 1: AI Answer
function renderAnswerPanel(data) {
  const body  = document.getElementById('answer-body');
  const badge = document.getElementById('answer-badge');

  if (data.can_ai_answer) {
    // Convert newlines to <br> for readability
    const formatted = escapeHtml(data.answer).replace(/\n/g, '<br>');
    body.innerHTML = `<p>${formatted}</p>`;
    badge.textContent = 'AI Generated';
    badge.className = 'badge badge-ai';
  } else {
    body.innerHTML = `
      <p class="escalate-note">
        This question involves matters that require attention from your academic team.
        The AI has escalated your query — please see the <strong>Query Status</strong> panel for next steps.
      </p>`;
    badge.textContent = 'Escalated';
    badge.className = 'badge badge-escalate';
  }
}

// Panel 2: Resources
function renderResourcesPanel(data) {
  const body        = document.getElementById('resources-body');
  const topicBadge  = document.getElementById('topic-badge');

  // Show the topic label
  if (data.topic) {
    topicBadge.textContent = data.topic;
    topicBadge.className = 'badge badge-topic';
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
    body.innerHTML = '<p style="color:#94A3B8;font-size:0.875rem;">No resources available for this query.</p>';
  }
}

// Panel 3: Escalation / Status
function renderStatusPanel(data) {
  const body      = document.getElementById('status-body');
  const card      = document.getElementById('card-status');
  const iconEl    = document.getElementById('status-icon');

  if (data.can_ai_answer) {
    // AI handled it — all green
    card.className = 'result-card card-status safe';
    iconEl.textContent = '✅';
    body.innerHTML = `
      <div class="status-content">
        <div class="status-indicator">
          <span class="status-dot dot-green"></span>
          AI can handle this
        </div>
        <div class="status-reason">
          Your question has been answered by the AI assistant above. No human intervention is required.
        </div>
      </div>`;
  } else {
    // Escalation needed — show reason and contact info
    card.className = 'result-card card-status escalate';
    iconEl.textContent = '🚨';
    body.innerHTML = `
      <div class="status-content">
        <div class="status-indicator">
          <span class="status-dot dot-red"></span>
          Escalate to Faculty
        </div>
        <div class="status-reason">
          ${escapeHtml(data.escalate_reason || 'This query requires a human academic team member.')}
        </div>
        <div class="contact-info">
          <strong>What to do next:</strong>
          Contact your course lecturer, module tutor, or the student services office directly.
          You can also raise a formal query through your institution's student portal.
        </div>
      </div>`;
  }
}

// ── UI State Helpers ───────────────────────────────────────────
function setLoading(isLoading) {
  loadingEl.classList.toggle('hidden', !isLoading);
  askBtn.disabled = isLoading;
  askBtn.querySelector('.btn-text').textContent = isLoading ? 'Thinking...' : 'Ask AI';
}

function hideResults() {
  resultsEl.classList.add('hidden');
  // Remove any previous error
  const oldErr = document.querySelector('.error-msg');
  if (oldErr) oldErr.remove();
}

function showError(message) {
  const main = document.querySelector('main');
  const err = document.createElement('div');
  err.className = 'error-msg';
  err.textContent = `⚠️ ${message}`;
  // Insert after the loading state
  loadingEl.after(err);
}

// ── Security: prevent XSS when inserting user/AI content ───────
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Allow pressing Enter (+ Shift+Enter for newline) ──────────
questionInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleAsk();
  }
});
