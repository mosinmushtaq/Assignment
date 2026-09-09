# AI Learner Assistant 🎓

An AI-powered prototype that helps university students with academic queries using Google Gemini.

## What it does

| Feature | Description |
|---|---|
| **Q&A** | Answers academic and course-related questions using Gemini AI |
| **Resource Recommendation** | Suggests 3 relevant learning resources per query |
| **Escalation** | Detects queries that need a human (grades, admin, personal issues) and directs the student accordingly |

## How to Run Locally

### Prerequisites
- Python 3.9+
- A Google Gemini API key ([get one free here](https://aistudio.google.com/apikey))

### Steps

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd Assignment

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Set your Gemini API key as an environment variable
# On Windows (PowerShell):
$env:GEMINI_API_KEY = "your-api-key-here"

# On Mac/Linux:
export GEMINI_API_KEY="your-api-key-here"

# 4. Run the app
python api/chat.py

# 5. Open your browser and go to:
#    http://localhost:5000
```

## How to Deploy on Vercel

1. Push this repository to GitHub
2. Go to [vercel.com](https://vercel.com) → Import Project → select your repo
3. In **Environment Variables**, add:
   - Key: `GEMINI_API_KEY`
   - Value: your Gemini API key
4. Click **Deploy** — done!

## Project Structure

```
Assignment/
├── index.html        ← Main web page (dashboard UI)
├── style.css         ← All styling
├── script.js         ← Frontend logic (calls API, renders results)
├── api/
│   └── chat.py       ← Python backend (Flask + Gemini API)
├── requirements.txt  ← Python dependencies
├── vercel.json       ← Vercel deployment configuration
└── README.md         ← This file
```

## Dependencies Used

| Dependency | Version | Purpose |
|---|---|---|
| `flask` | 3.0.3 | Python web framework — handles HTTP requests |
| `google-generativeai` | 0.8.3 | Official Google SDK for Gemini API |

## How GenAI is Used

This prototype uses **Google Gemini 1.5 Flash** for two things:

1. **Classification**: Gemini reads the student's question and decides whether it can be answered by AI, or whether it needs to be escalated to a faculty member.
2. **Answer Generation**: If the question is AI-appropriate, Gemini generates a clear academic answer and identifies the topic.
3. **Resource Recommendation**: Gemini suggests 3 relevant learning resources (with URLs) based on the detected topic.

All three steps happen in a **single API call** — we send a carefully crafted prompt and ask Gemini to return a structured JSON object.

## What Makes it an AI Agent

This system qualifies as an AI Agent because it:
- **Perceives** the student's input (the question)
- **Decides** (classification step: AI or human?)
- **Acts** differently based on the decision (answer vs. escalate)
- **Uses tools** (Gemini for reasoning, resource recommender for links)

## Known Limitations

1. **Hallucination** — Gemini may occasionally generate incorrect information. Students should verify important answers.
2. **No Memory** — Each question is independent; the AI has no context from previous questions.
3. **No Access to Records** — The AI cannot see grades, timetables, or any institutional data.
4. **Resource URL Accuracy** — Suggested links are AI-generated and may occasionally be inaccurate.

## When AI Escalates to a Human

The AI will always direct the student to a faculty member when the query involves:
- Grade disputes or re-marking requests
- Exam timetable or enrollment issues
- Personal/medical extenuating circumstances
- Fee payments, financial aid, or scholarships
- Student records, transcripts, or certificates
- Harassment, wellbeing, or pastoral care concerns
