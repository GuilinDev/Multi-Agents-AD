# 🧠 Multi-Agent Alzheimer's Companion (Demo)

A dual-agent AI system for reminiscence therapy with early-stage Alzheimer's patients.

## Architecture

```
Patient (User) ←→ TherapyAgent (Gemini) ←→ Conversation
                         ↓
                   MonitorAgent (Gemini) → Real-time cognitive assessment
                         ↓
                   Caregiver Summary Report
```

- **TherapyAgent**: Conducts warm, personalized reminiscence therapy conversations
- **MonitorAgent**: Silently analyzes each exchange for emotion, engagement, memory quality, and risk flags
- **TTS Engine**: Natural voice output via edge-tts
- **Caregiver Dashboard**: Real-time monitoring + end-of-session summary

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set your API key
cp .env.example .env
# Edit .env with your GEMINI_API_KEY

python app.py
# Open http://localhost:7860
```

## Tech Stack

- **LLM**: Google Gemini 2.0 Flash (primary), Groq/Llama (failover)
- **UI**: Gradio 6
- **TTS**: edge-tts (Microsoft, free)
- **Framework**: Custom dual-agent with shared conversation state

## Synthetic Patient

Demo uses a synthetic patient profile (Margaret Thompson, 78, early-stage AD). 
No real patient data is used.

## Team

- **Guilin Zhang** — AI Systems Architecture, Agentic Framework
- **Kai [TBD]** — Project Management, Industry Connections
- **Dr. Dezhi Wu** — Domain Expertise, HCI, Clinical Validation (USC)

## License

MIT
