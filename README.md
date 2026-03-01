# 🧠 Memowell.ai

**Text-first AI Copilot for Dementia Behavioral Events**

Memowell.ai helps caregivers in nursing facilities document behavioral events, retrieve evidence-based care protocols, and generate structured shift handoff reports — all with zero hallucination by design.

## What It Does

```
Caregiver describes behavioral event (text or voice)
        ↓
LLM parses → event type, severity, trigger, location
        ↓
RAG retrieves → matched protocols from CMS/APA/NICE/Alzheimer's Association
        ↓
LLM summarizes → 2-3 actionable steps with source citations
        ↓
Caregiver records intervention → outcome → auto-generates C→I→O log
        ↓
Shift handoff report with signature
```

## Architecture

```
┌─────────────────────────────────────────────┐
│  Frontend (Expo + Next.js + Solito)         │
│  Three platforms: PWA / Android / iOS       │
└──────────────────┬──────────────────────────┘
                   │ REST API
┌──────────────────▼──────────────────────────┐
│  FastAPI Backend                             │
│  ├─ Event Router    (report → intervene → outcome)
│  ├─ Handoff Router  (generate → acknowledge)
│  ├─ Patient Router  (CRUD)
│  ├─ RAG Router      (search → summarize)
│  └─ LLM Service     (Groq: Whisper STT + Llama 3.3 70B)
├──────────────────────────────────────────────┤
│  SQLite (events, patients, handoffs, staff)  │
│  ChromaDB (5951 chunks, 8 guideline PDFs)    │
└──────────────────────────────────────────────┘
```

## Key Design Decisions

- **RAG, not generation** — Protocol suggestions come from retrieval only. Zero tolerance for hallucination in medical compliance context.
- **Text-first, voice-optional** — Privacy concerns in nursing facilities make text input the primary modality.
- **C→I→O structured data** — Every behavioral event captures Context → Intervention → Outcome, building a structured dataset for future analytics.
- **Handwritten signature** — Shift handoffs require legal-compliant signature capture.

## Knowledge Base

| Source | Documents | Chunks |
|--------|-----------|--------|
| CMS (Centers for Medicare & Medicaid) | Appendix PP, GUIDE Model, F-Tags | ~3,500 |
| Alzheimer's Association | Care Practice, Assisted Living, Clinical 2024 | ~1,200 |
| APA | Dementia Evaluation Guidelines | ~200 |
| NICE | NG97 Dementia Management | ~100 |
| **Total** | **8 PDFs** | **5,951 chunks** |

## Quick Start

```bash
# Backend
cd api
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key" > ../.env
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend (PWA)
cd apps/next
npm install
npm run dev
# Open http://localhost:3000
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Expo + Solito + Next.js (PWA/Android/iOS) |
| Backend | FastAPI + SQLAlchemy |
| Database | SQLite (structured) + ChromaDB (vector) |
| LLM | Groq — Whisper Large v3 (STT) + Llama 3.3 70B (parsing/summarization) |
| Embeddings | all-MiniLM-L6-v2 (384-dim, cosine) |
| Deployment | Railway (API) + Vercel (PWA) |

## Product Roadmap

- **Phase 1 (Current)**: Behavioral event copilot + auto-handoff (SaaS, $5-15/bed/month)
- **Phase 2**: Structured C→I→O data asset across multiple facilities
- **Phase 3**: Intervention ranking, risk prediction, digital twin

## Team

- **Guilin Zhang** — AI Systems Architecture, Full-Stack Engineering
- **Kai Zhao** — Product Strategy, Industry Partnerships
- **Dr. Dezhi Wu** — Domain Expertise, HCI × AI in Healthcare (USC)

## License

MIT
