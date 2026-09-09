# AI Learner Assistant 🎓

A simple web-based prototype that uses a Large Language Model (LLM) to help university students get quick answers to academic questions — without having to wait for a lecturer to reply to an email.

---

## The Idea

Students constantly have questions. Some are simple ("What does polymorphism mean?"), some need a resource ("Where can I learn Big O notation?"), and some genuinely need a human ("Can I appeal my grade?"). The problem is — most of the time, students either give up or spam their lecturers with questions that could have been answered in 30 seconds.

This tool tries to fix that by acting as a first point of contact. It uses an LLM to understand what a student is asking and decide what to do next.

---

## What It Does

When you type a question, three things happen:

1. **The LLM classifies your question** — it reads what you wrote and decides: *"Is this something I can actually answer, or does this student need to talk to a real person?"*
2. **If it can answer** — it generates a clear, academic-level response and also picks 3 relevant learning resources based on the topic.
3. **If it can't answer** — it tells you why and directs you to contact your faculty or student services. Things like grade appeals, medical circumstances, or anything involving your personal records are always escalated to a human.

---

## How the LLM Actually Works Here

We use **Groq** (which hosts open-weight models and runs them insanely fast) with the **Qwen 3.8 27B** model.

The way we use the LLM is through **prompt engineering**. Every time a student asks something, we don't just forward the question to the model raw. We wrap it in a carefully written **system prompt** that:

- Tells the model its role (a university learner assistant)
- Gives it strict rules on what counts as an escalation case
- Instructs it to respond **only** in a structured JSON format

That last point is important. We use `response_format: json_object` to force the model to return machine-readable output every time, rather than free-form text. This makes our backend able to reliably parse the answer, the resources, and the escalation flag without any guesswork.

So the LLM is doing three jobs in a single call:
- **Classification** (can AI handle this?)
- **Generation** (write the answer)
- **Extraction** (identify the topic, find resources)

This is what makes it more than just a chatbot — it's making decisions, not just responding.

---

## Why This Qualifies as an AI Agent

An AI Agent is a system that perceives its environment, makes decisions, and takes different actions based on those decisions.

Our system does exactly that:
- It **perceives** the student's question
- It **reasons** about whether the question is AI-appropriate or not (the classification step)
- It **acts** differently based on that decision — either answering with resources, or escalating to a human

The routing logic (answer vs. escalate) is what makes this agentic. It's not just a search engine or a chatbot wrapper — it decides what to do.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Vanilla JavaScript |
| Backend | Python + Flask |
| LLM | Qwen 3.8 27B via Groq API |
| Hosting | Vercel (frontend + Flask serverless) |

---

## How to Run It Locally

**You'll need:**
- Python 3.9 or above
- A Groq API key (free at [console.groq.com](https://console.groq.com))

```bash
# Clone the repo
git clone https://github.com/mosinmushtaq/Assignment.git
cd Assignment

# Install dependencies
pip install -r requirements.txt

# Add your API key
# Create a .env file and add:
# GROQ_API_KEY=your_key_here

# Run the app
python app.py

# Open http://localhost:5000
```

---

## Project Structure

```
Assignment/
├── app.py            ← Flask backend + all LLM logic
├── index.html        ← The web UI
├── style.css         ← Styling
├── script.js         ← Handles API calls and renders results
├── requirements.txt  ← Python dependencies
└── .env              ← Your API key (never committed to git)
```

---

## Limitations We Know About

**Hallucination** — Like all LLMs, the model can confidently say something that is wrong. We add a disclaimer in the UI, but students should always double-check important information.

**No memory** — Each question is treated independently. The model has no idea what you asked 10 seconds ago. This keeps things simple but means it can't handle follow-up questions well.

**No access to real data** — The model knows nothing about your actual grades, timetable, or enrolled modules. It only knows what you type. That's why anything student-record-related is always escalated.

**Resource links** — The model suggests real-sounding URLs but it doesn't browse the web. Links are based on its training data and are usually correct, but occasionally they may not lead exactly where expected.

---

## When the AI Steps Back

The system is explicitly designed to refuse certain questions and push them to a human. This includes:

- Grade disputes or re-marking requests
- Exam or coursework deadline extensions
- Personal or medical extenuating circumstances
- Anything about fees, enrolment, or student records
- Wellbeing or pastoral concerns

This is a deliberate design choice. An LLM should not be making judgements on sensitive academic or personal matters. Those need a real person with context, authority, and accountability.

---

## Dependencies

```
flask==3.0.3          # Python web framework
groq==0.11.0          # Groq SDK for LLM API calls
httpx==0.27.2         # HTTP client (pinned for Python 3.14 compatibility)
python-dotenv==1.0.1  # Loads .env file for local development
```
