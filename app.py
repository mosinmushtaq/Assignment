"""
AI Learner Assistant - Main Application
=========================================
Flask app served at the project root.
Vercel auto-detects app.py as the Flask entrypoint.

Uses NVIDIA NIM (Nemotron Nano Omni) to:
  1. Classify whether a question can be answered by AI or needs a human
  2. Generate an academic answer (if AI can handle it)
  3. Recommend relevant learning resources based on the topic
  4. Understand images (diagrams, notes, questions) via multimodal input
"""

import os
import json
import re
import requests as http_requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load .env file automatically when running locally
# On Vercel, environment variables are set in the dashboard instead
load_dotenv()

# --- App Setup ---
# static_folder='.' means Flask serves index.html, style.css, script.js
# from the same root directory as app.py
app = Flask(__name__, static_folder='.', static_url_path='')

# --- NVIDIA NIM Setup ---
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
NIM_URL        = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL          = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"

def nim_headers():
    """Build request headers for the NVIDIA NIM API."""
    return {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept":        "application/json",
        "Content-Type":  "application/json",
    }

# --- System Prompt ---
# This is the instruction we give the AI every time a student asks a question.
# We ask it to return structured JSON so our code can parse and display it cleanly.
SYSTEM_PROMPT = """You are an AI Learner Assistant helping university students with academic and course-related queries.

When a student asks a question, respond ONLY with a valid JSON object in this exact format (no extra text, no markdown, no thinking):
{
  "can_ai_answer": true,
  "escalate_reason": "",
  "answer": "A detailed, helpful academic answer here...",
  "topic": "2-4 word topic label",
  "resources": [
    {
      "title": "Resource Title",
      "url": "https://real-url.com",
      "description": "One sentence about why this resource helps."
    }
  ]
}

ESCALATION RULES - set can_ai_answer to false and fill escalate_reason if the question involves:
- Grade disputes, re-marking requests, or academic appeals
- Exam timetable issues, enrollment, or registration problems
- Personal, medical, or extenuating circumstances
- Fee payments, scholarships, or financial aid
- Student records, transcripts, or certificates
- Harassment, wellbeing, or pastoral care concerns
- Any matter requiring institutional authority or student-specific data

RESOURCE RULES:
- Always include exactly 3 resources relevant to the topic
- Use real, well-known URLs (e.g., Khan Academy, Coursera, MDN, Wikipedia, YouTube, etc.)
- Provide resources even when escalating, so the student can still self-study

Keep answers clear, structured, and appropriate for a university student."""


def extract_json(raw: str) -> str:
    """
    Clean up the model output before JSON parsing.
    Reasoning models (like Nemotron) often prefix their answer with <think>...</think> blocks.
    We strip those, then strip any markdown code fences.
    """
    # Remove <think>...</think> reasoning sections
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL)
    # Remove markdown code fences (```json ... ```)
    raw = re.sub(r'^```(?:json)?\s*', '', raw.strip())
    raw = re.sub(r'\s*```$', '', raw)
    return raw.strip()


def call_nim(messages: list) -> str:
    """
    Send a chat request to NVIDIA NIM and return the model's response text.
    Works for both text-only and multimodal (image + text) messages.
    """
    payload = {
        "model":            MODEL,
        "messages":         messages,
        "max_tokens":       4096,       # Enough for a detailed academic answer
        "reasoning_budget": 1024,       # Controls how much the model "thinks" before answering
        "stream":           False,
        "temperature":      0.6,
        "top_p":            0.95,
    }
    resp = http_requests.post(NIM_URL, headers=nim_headers(), json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


@app.route('/')
def index():
    """Serve the main HTML page."""
    return app.send_static_file('index.html')


@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """
    Main API endpoint.
    Accepts: POST { "question": "...", "image": "data:image/...;base64,..." (optional) }
    Returns: JSON { can_ai_answer, answer, escalate_reason, topic, resources }
    """

    # Handle browser preflight CORS requests
    if request.method == 'OPTIONS':
        return _cors_response(jsonify({}))

    # Parse the incoming request body
    data = request.get_json(silent=True)
    if not data or not data.get('question', '').strip():
        return _cors_response(jsonify({'error': 'Please provide a question.'}), 400)

    question   = data['question'].strip()
    image_data = data.get('image')  # Optional: base64 data URL e.g. "data:image/jpeg;base64,..."

    try:
        if image_data:
            # -- VISION REQUEST: image + text ---------------------------
            # Nemotron Omni is multimodal — pass image as base64 data URL
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text",      "text": f"Student question: {question}"},
                        {"type": "image_url", "image_url": {"url": image_data}}
                    ]
                }
            ]
        else:
            # -- TEXT-ONLY REQUEST --------------------------------------
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Student question: {question}"}
            ]

        raw_text = call_nim(messages)
        cleaned  = extract_json(raw_text)
        result   = json.loads(cleaned)

        return _cors_response(jsonify(result))

    except json.JSONDecodeError:
        return _cors_response(jsonify({
            'error': 'The AI returned an unexpected response. Please try again.'
        }), 500)

    except Exception as e:
        return _cors_response(jsonify({
            'error': f'Something went wrong: {str(e)}'
        }), 500)


def _cors_response(response, status=200):
    """Add CORS headers so the browser frontend can call this API."""
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.status_code = status
    return response


# Entry point for local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)
