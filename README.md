## AI Voice Assistant

An end-to-end voice assistant with a FastAPI backend and a React + Vite frontend. It supports:
- Speech-to-Text (STT) via `SpeechRecognition` (Google Web Speech API; optional CMU Sphinx fallback)
- LLM-powered responses with conversation memory (LangChain + OpenAI client compatible with GitHub Models)
- Text-to-Speech (TTS) via `gTTS`

### Features
- Voice pipeline: Audio (webm/mp3/wav/ogg/flac/m4a) → STT → LLM → TTS → MP3
- Chat API with session-scoped conversation memory
- Optional Redis persistence for chat history
- Frontend UI with recording, chat, and playback

---

## Project Structure

```text
AI-Voice Assistant/
  backend/
    app/
      api/
        chat.py           # POST /api/v1/chat/reply
        voice.py          # POST /api/v1/voice/process
      core/
        llm_client.py     # LangChain ConversationChain + custom LLM wrapper
        buffer_manager.py  # In-memory + optional Redis conversation history
        redis_client.py    # Redis connector (optional)
      models/
        schema.py         # Chat pydantic models
        voice.py          # Voice pydantic models
      main.py             # FastAPI app, CORS, router mount
    requirements.txt
  frontend/
    src/
      api/chat.ts         # Chat API client
      api/voice.ts        # Voice API client
      components/...      # UI components (Recorder, ChatBox, Message)
    package.json
```

---

## Requirements

- Python 3.11+
- Node.js 20+ and npm
- Optional: Redis (for persistent conversation history)

---

## Backend Setup (FastAPI)

1) Create and activate a virtual environment (recommended)

```bash
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2) Environment variables

Create a `.env` file in `backend/` (same folder as `requirements.txt`):

```bash
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-4.1
BASE_URL=https://models.github.ai/inference

# Optional Redis (only if you want persistent memory)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_USERNAME=
REDIS_PASSWORD=

# Optional, used for CORS allowlist in backend/app/main.py
VERCEL_URL=https://your-frontend-url.example.com
```

Notes:
- The backend uses a custom `GithubLLM` wrapper with the `openai` SDK and a configurable `BASE_URL`. Provide either a GitHub Models-compatible endpoint or OpenAI-compatible endpoint.
- If Redis is not available, the app falls back to in-process memory.

3) Run the server

```bash
uvicorn app.main:app --reload --port 8000
```

The server will be available at `http://localhost:8000`.

---

## Frontend Setup (React + Vite + TypeScript)

1) Install dependencies

```bash
cd frontend
npm install
```

2) Configure API URL for production builds

Create `frontend/.env` (or `.env.production`) if you deploy the frontend separately:

```bash
VITE_API_URL=https://your-backend-domain.com
```

During development, the frontend uses `http://localhost:8000` automatically.

3) Run the frontend

```bash
npm run dev
```

Open the app at `http://localhost:5173`.

---

## API Reference

Base URL during development: `http://localhost:8000`

### POST /api/v1/chat/reply

Request body:

```json
{
  "prompt": "Hello there!",
  "session_id": "your-session-id"
}
```

Response body:

```json
{
  "response": "Hi! How can I help you today?"
}
```

### POST /api/v1/voice/process

Accepts a base64-encoded audio payload, converts to WAV, performs STT, runs the LLM, and returns text plus base64 MP3 audio.

Request body:

```json
{
  "audio_base64": "<base64-audio>",
  "session_id": "your-session-id"
}
```

Response body:

```json
{
  "text": "Here's the AI response.",
  "audio_base64": "<base64-mp3>"
}
```

Supported input formats: wav, mp3, webm, ogg, flac, m4a (auto-detected).

---

## Testing

### cURL Examples

Chat:

```bash
curl -X POST http://localhost:8000/api/v1/chat/reply \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello","session_id":"demo-123"}'
```

Voice (assuming you have `AUDIO_BASE64` prepared):

```bash
curl -X POST http://localhost:8000/api/v1/voice/process \
  -H "Content-Type: application/json" \
  -d '{"audio_base64":"'"$AUDIO_BASE64"'","session_id":"demo-123"}'
```

---

## Implementation Notes

- STT is done in `app/api/voice.py` using `SpeechRecognition`. Primary path is Google Web Speech API with fallback to CMU Sphinx where available.
- TTS is done via `gTTS` and returns an MP3 base64 string; middleware saves `response.mp3` locally as a convenience.
- The LLM pipeline uses LangChain `ConversationChain` with a custom `GithubLLM` that leverages the `openai` client against a configurable `BASE_URL` and `MODEL_NAME`.
- Conversation memory is managed via `buffer_manager.MemoryManager` with optional Redis persistence (enabled if Redis is reachable).
- CORS is configured in `app/main.py`. For deployments, ensure your frontend origin is included.

---

## Troubleshooting

- 400 Invalid audio format: Ensure the uploaded audio is valid and encoded correctly as base64. Try a common format like WAV or MP3.
- STT failures: Background noise and low volume can cause `UnknownValueError`. Normalize audio or re-record.
- Redis connection failed: If you don’t need persistence, you can ignore this; in-memory history will still work.
- CORS errors: Add your deployed frontend origin to `allow_origins` in `app/main.py` or set `VERCEL_URL`.

---

## Scripts

Backend:
- `uvicorn app.main:app --reload --port 8000`

Frontend:
- `npm run dev`
- `npm run build`
- `npm run preview`

---
