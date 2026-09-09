"""
AI Learner Assistant - Backend API
===================================
This Flask app runs as a Vercel Python serverless function at /api/chat.
It uses Google Gemini to:
  1. Classify whether a question can be answered by AI or needs a human
  2. Generate an academic answer (if AI can handle it)
  3. Recommend relevant learning resources based on the topic
"""

import os
import json
import re
from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env file automatically when running locally
# On Vercel, environment variables are set in the dashboard instead
load_dotenv()

# --- App Setup ---
# When running locally: serves static files from the parent folder too
app = Flask(__name__, static_folder='..', static_url_path='')

# --- Gemini Setup ---
# The API key is stored as an environment variable (never hardcoded)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# --- System Prompt ---
# This is the instruction we give Gemini every time a student asks a question.
# We ask it to return structured JSON so our code can parse and display it cleanly.
SYSTEM_PROMPT = """You are an AI Learner Assistant helping university students with academic and course-related queries.

When a student asks a question, respond ONLY with a valid JSON object in this exact format (no extra text, no markdown):
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


@app.route('/')
def index():
    """Serve the main HTML page when running locally."""
    return app.send_static_file('index.html')


@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """
    Main API endpoint.
    Accepts: POST { "question": "..." }
    Returns: JSON { can_ai_answer, answer, escalate_reason, topic, resources }
    """

    # Handle browser preflight CORS requests
    if request.method == 'OPTIONS':
        return _cors_response(jsonify({}))

    # Parse the incoming question
    data = request.get_json(silent=True)
    if not data or not data.get('question', '').strip():
        return _cors_response(jsonify({'error': 'Please provide a question.'}), 400)

    question = data['question'].strip()

    try:
        # Build the full prompt: system instructions + student question
        full_prompt = f"{SYSTEM_PROMPT}\n\nStudent question: {question}"

        # Call Gemini
        response = model.generate_content(full_prompt)
        raw_text = response.text.strip()

        # Gemini sometimes wraps JSON in markdown code blocks - clean that up
        raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text)
        raw_text = re.sub(r'\s*```$', '', raw_text)

        # Parse the JSON response from Gemini
        result = json.loads(raw_text)

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
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.status_code = status
    return response


# Entry point for local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)
