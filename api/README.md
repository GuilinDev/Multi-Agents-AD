# Memowell API

REST API backend for the Multi-Agent Alzheimer's Companion.

## Setup

```bash
pip install -r requirements.txt
export GROQ_API_KEY=your_key_here
```

## Run

```bash
cd api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Or from project root: `make api`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/patients` | List available patient profiles |
| POST | `/api/session/start` | Start session (JSON body: `{"patient_id": "margaret"}`) |
| POST | `/api/chat` | Send message (multipart form: `session_id`, `message`, optional `audio` file) |
| POST | `/api/session/end` | End session (form: `session_id`) |
| GET | `/api/trends/{patient_id}` | Get cognitive trend data + alerts |
| GET | `/api/summary/{patient_id}` | Get latest caregiver summary |
| GET | `/api/audio/{filename}` | Serve TTS audio file |
| GET | `/api/images/{filename}` | Serve generated image |

## Chat Flow

1. `POST /api/session/start` → get `session_id`
2. `POST /api/chat` with `session_id` + `message` → get response, monitor data, audio/image URLs
3. `POST /api/session/end` with `session_id` → get caregiver summary

## Interactive Docs

Visit `http://localhost:8000/docs` for Swagger UI.
