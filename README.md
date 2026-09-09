# AI Learner Assistant 🎓

A robust, multimodal web-based prototype that uses a Large Language Model (LLM) to help university students get quick answers to academic questions — without having to wait for a lecturer to reply to an email.

---

## 💡 The Idea

Students constantly have questions. Some are simple ("What does polymorphism mean?"), some need a visual explanation ("What does this diagram mean?"), and some genuinely need a human ("Can I appeal my grade?"). Most of the time, students either give up or spam their lecturers with questions that could have been answered in 30 seconds.

This tool acts as an **intelligent first point of contact**. It uses an LLM to perceive what a student is asking (via text or image) and makes a definitive decision on what to do next.

---

## 🛠️ What It Does

When you type a question or upload an image, the AI Agent kicks in:

1. **Classification (Perception)** — It reads the text and/or analyzes the uploaded image to understand the core intent. *"Is this something an AI can safely answer, or does this student need to talk to a real person?"*
2. **Academic Answer & Resources (Action)** — If it can answer, it generates a clear, conversational, and academic-level response. It also extracts the core topic and dynamically picks 3 relevant learning resources.
3. **Escalation (Action)** — If it cannot answer, it explicitly refuses and directs the student to the correct human channel (e.g., student services, module leader).
4. **Conversational Fallback** — It handles conversational inputs ("hello", "how are you?") gracefully without forcing irrelevant academic links, making it feel like a natural chat.

---

## 🧠 How the LLM Actually Works

We use **Google Gemini (gemini-3.8-flash)**, accessed natively via the Gemini REST API for ultra-fast, reliable, and multimodal inference.

The true intelligence comes from **Strict Prompt Engineering & JSON Forcing**:
Every student query is wrapped in a robust **system prompt** that defines the assistant's persona, its exact escalation boundaries, and its output schema.

We enforce `responseMimeType: application/json` to make the model return **machine-readable JSON every single time**. This means the AI is performing three complex tasks in a single API call:
- **Classification** (Boolean: `can_ai_answer`)
- **Generation** (String: `answer`)
- **Extraction** (Array: `resources`, String: `topic`)

This is what makes it an **AI Agent** rather than just a chatbot wrapper. It perceives its environment, reasons about the intent, and takes structured action based on its own reasoning.

---

## 👁️ Multimodal Capabilities (Vision)

The system doesn't just read text; it can see.
Students can click the 🖼️ icon to upload a photo of a textbook, a handwritten math problem, or a lecture diagram. 

In the browser, the image is converted to a base64 string and sent directly to the Gemini vision model alongside the text prompt. The model analyzes both modalities simultaneously to provide an accurate, context-aware answer.

---

## 🛑 When the AI Steps Back (Safety Nets)

The system is explicitly designed to refuse certain questions and push them to a human. Escalation is triggered by:

- Grade disputes or re-marking requests
- Exam or coursework deadline extensions
- Personal, medical, or extenuating circumstances
- Anything about fees, enrolment, or student records

This is a deliberate, ethical design choice. An LLM should not make judgements on sensitive academic or personal matters. 

Additionally, we built in an **empathy safety net**. If a student asks about a sensitive psychological topic (e.g., extreme isolation), the AI provides an empathetic academic answer but appends a hardcoded safety phrase advising them to seek professional support.

---

## 💻 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML, Vanilla CSS, JavaScript (Vanilla DOM manipulation) |
| **Backend** | Python + Flask |
| **LLM Engine** | Google Gemini (gemini-3.8-flash) via REST API |
| **Hosting** | Vercel (Static frontend + Serverless Flask backend) |

---

## 🚀 How to Run It Locally

**Prerequisites:**
- Python 3.9+
- A Google Gemini API key

```bash
# Clone the repository
git clone https://github.com/mosinmushtaq/Assignment.git
cd Assignment

# Install dependencies
pip install -r requirements.txt

# Add your API key
# Create a .env file in the root directory and add:
# GEMINI_API_KEY=your_key_here

# Run the backend
python app.py

# Open http://localhost:5000 in your browser
```

---

## ⚠️ Known Limitations

- **Hallucination:** Like all LLMs, the model can confidently state incorrect facts. A disclaimer is prominently displayed in the UI.
- **No Memory:** The current implementation is stateless. Each question is treated independently, keeping the architecture simple but limiting deep follow-up conversations.
- **No Institutional Access:** The model knows nothing about a specific university's systems, meaning it cannot access real grades, timetables, or student records.
- **AI-Generated URLs:** The suggested resource links are generated by the model based on its training data. While typically accurate (e.g., Wikipedia, Khan Academy), they are not verified by a live search engine.
