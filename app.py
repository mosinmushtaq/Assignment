"""
AI Learner Assistant - Main Application
=========================================
Flask app served at the project root.
Vercel auto-detects app.py as the Flask entrypoint.

Uses Google Gemini (gemini-3.8-flash) to:
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

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')

# --- Gemini API Setup ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GROQ_API_KEY") # Fallback just in case
MODEL = "gemini-3.8-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_API_KEY}"

SYSTEM_PROMPT = """You are an AI Learner Assistant helping university students with academic and course-related queries.

When a student asks a question, respond ONLY with a valid JSON object in this exact format (no extra text, no markdown):
{
  "can_ai_answer": true,
  "escalate_reason": "",
  "answer": "A detailed, helpful academic answer here... (be conversational if they just say hello)",
  "topic": "2-4 word topic label",
  "resources": [
    {
      "title": "Resource Title",
      "url": "https://real-url.com",
      "description": "One sentence about why this resource helps."
    }
  ]
}

CRITICAL: DO NOT ESCALATE conversational chat or general academic questions!
You MUST set "can_ai_answer": true for:
- Greetings, small talk, or conversational questions (e.g., "hello", "how are you", "who made you").
- Explaining concepts, theories, or definitions (e.g., Recursion, Big O, Math, Science).
- Programming, coding help, or debugging.
- Describing or explaining an uploaded image.
Only escalate if the request STRICTLY falls into the specific administrative/personal categories below.

ESCALATION RULES - set can_ai_answer to false and fill escalate_reason ONLY if the question involves:
- Grade disputes, re-marking requests, or academic appeals
- Exam timetable issues, enrollment, or registration problems
- Personal, medical, or extenuating circumstances
- Fee payments, scholarships, or financial aid
- Student records, transcripts, or certificates
- Harassment, wellbeing, or pastoral care concerns
- Any matter requiring institutional authority or student-specific data

RESOURCE RULES:
- Include exactly 3 resources if the topic is academic and resources are helpful.
- If the user is just saying a greeting or asking a casual question, return an empty array [] for resources.
- Use real, well-known URLs (e.g., Khan Academy, Coursera, MDN, Wikipedia, YouTube, etc.).

If a user asks about sensitive but general topics (like extreme self-isolation), provide a thoughtful, empathetic answer, but include a safety net phrase: "If you or someone you know is struggling, please reach out to a professional or your institution's support service."

Keep answers clear, conversational, and appropriate for a university student."""

def extract_json(raw: str) -> str:
    raw = re.sub(r'^```(?:json)?\s*', '', raw.strip())
    raw = re.sub(r'\s*```$', '', raw)
    return raw.strip()

def call_gemini(question: str, image_data: str = None) -> str:
    parts = [{"text": f"Student question: {question}"}]
    
    if image_data:
        # image_data is "data:image/jpeg;base64,/9j/4AAQ..."
        if "," in image_data:
            mime_part, b64_part = image_data.split(",", 1)
            mime_type = mime_part.split(":")[1].split(";")[0]
            parts.append({
                "inlineData": {
                    "mimeType": mime_type,
                    "data": b64_part
                }
            })

    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.4
        }
    }
    
    resp = http_requests.post(API_URL, json=payload, timeout=60)
    resp.raise_for_status()
    
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return _cors_response(jsonify({}))

    data = request.get_json(silent=True)
    if not data or not data.get('question', '').strip():
        return _cors_response(jsonify({'error': 'Please provide a question.'}), 400)

    question = data['question'].strip()
    image_data = data.get('image')

    try:
        raw_text = call_gemini(question, image_data)
        cleaned  = extract_json(raw_text)
        result   = json.loads(cleaned)
        return _cors_response(jsonify(result))

    except json.JSONDecodeError:
        return _cors_response(jsonify({'error': 'The AI returned an unexpected response. Please try again.'}), 500)
    except Exception as e:
        return _cors_response(jsonify({'error': f'Something went wrong: {str(e)}'}), 500)

def _cors_response(response, status=200):
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.status_code = status
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
