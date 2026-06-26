# Gemma Chatbot

A fully local AI chatbot powered by **Gemma 4B** via Ollama, with a React frontend and FastAPI backend.

## Tech Stack

| Layer    | Technologies                          |
| -------- | ------------------------------------- |
| Frontend | React, TypeScript, Vite, Axios        |
| Backend  | FastAPI, Ollama Python SDK            |
| Model    | `gemma4:e2b` (via Ollama)             |

## Prerequisites

- [Node.js](https://nodejs.org/) 18+
- [Python](https://www.python.org/) 3.10+
- [Ollama](https://ollama.com/) installed and running
- Gemma model pulled locally:

```bash
ollama pull gemma4:e2b
```

## Project Structure

```
gemma-chatbot/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # HTTP endpoints
│   │   ├── models/           # Pydantic schemas
│   │   ├── services/
│   │   │   ├── llm/          # Ollama service layer
│   │   │   ├── rag/          # Future RAG pipeline
│   │   │   └── embeddings/   # Future embeddings
│   │   ├── config.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   └── src/
│       ├── api/              # Axios client
│       ├── components/       # Reusable UI components
│       ├── hooks/            # React state logic
│       └── types/            # TypeScript interfaces
└── README.md
```

## Backend Setup

1. Navigate to the backend folder:

```bash
cd backend
```

2. Activate the virtual environment:

**Windows (PowerShell)**

```powershell
.\venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source venv/bin/activate
```

3. Install dependencies (if not already installed):

```bash
pip install -r requirements.txt
```

4. Copy and configure environment variables:

```bash
cp .env.example .env
```

| Variable       | Default                  | Description              |
| -------------- | ------------------------ | ------------------------ |
| `GEMMA_MODEL`  | `gemma4:e2b`             | Ollama model name        |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API base URL   |
| `CORS_ORIGINS` | `http://localhost:5173`  | Allowed frontend origins |

See [`backend/.env.example`](backend/.env.example) for all configuration options.

5. Start the API server:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### API Endpoints

| Method | Path             | Description                    |
| ------ | ---------------- | ------------------------------ |
| GET    | `/health`        | Liveness check                 |
| GET    | `/health/model`  | Ollama connectivity and model  |
| POST   | `/chat`          | Send conversation, get reply   |
| POST   | `/chat/stream`   | Streaming reply (SSE)          |

**POST /chat** request body:

```json
{
  "messages": [
    { "role": "user", "content": "Hello!" }
  ]
}
```

**Response:**

```json
{
  "message": {
    "role": "assistant",
    "content": "Hello! How can I help you?"
  }
}
```

## Frontend Setup

1. Navigate to the frontend folder:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. (Optional) Configure the API URL:

```bash
cp .env.example .env
```

4. Start the development server:

```bash
npm run dev
```

Open `http://localhost:5173` in your browser.

## Running the Full Application

Open two terminals:

**Terminal 1 — Backend**

```bash
cd backend
.\venv\Scripts\Activate.ps1   # Windows
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — Frontend**

```bash
cd frontend
npm run dev
```

Make sure Ollama is running before sending messages. The first request may take longer while the model loads into memory.

## Deployment

For internal testing with Vercel (frontend), Railway (backend), and Ollama on your local machine:

| Doc | Description |
| --- | ----------- |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Railway + Vercel deployment steps |
| [docs/LOCAL_OLLAMA_SETUP.md](docs/LOCAL_OLLAMA_SETUP.md) | Expose Ollama via public IP |
| [docs/DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md) | Pre-flight checklist |

Verify after deploy:

```bash
BACKEND_URL=https://your-app.up.railway.app FRONTEND_URL=https://your-app.vercel.app python scripts/verify_deployment.py
```

## Features

- Multi-turn conversations with history managed in React state
- Dark-themed ChatGPT-style UI with sidebar and "New Chat"
- Markdown rendering for assistant responses
- Loading indicator and error handling
- Fully local — no authentication, database, or external API keys

## Future Extensions

The backend is structured to support adding:

- **ChromaDB** vector store (`app/services/rag/`)
- **Embeddings** service (`app/services/embeddings/`)
- **PDF uploads** and document ingestion
- **RAG** context injection in `ChatService._prepare_messages()`

No major refactoring should be needed to plug these in.
