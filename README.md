# Chat-with-PDF: Advanced RAG System

A Retrieval-Augmented Generation (RAG) application that allows users to upload large PDFs and interact with them via chat or deep-dive queries, with answers grounded in the document and source citations.

## Features
- Upload and process PDFs (500+ pages, structured/unstructured)
- Multi-turn chat and single-turn deep-dive research modes
- Answers cite page numbers or text snippets from the PDF
- Local, privacy-friendly vector search (ChromaDB)
- FastAPI backend, React frontend, Dockerized stack
- Real-time chat streaming via WebSocket (`/api/v1/chat/stream`)
- Modular, production-grade backend with JWT authentication
- All request/response models in `backend/app/models/`

## Quickstart (Local)

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd ModusAI-Chat-with-PDF
```

### 2. Build and run with Docker Compose
```bash
docker-compose up --build
```
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

### 3. Development (manual)
- Backend:
  ```bash
  cd backend
  python3 -m venv venv && source venv/bin/activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload
  ```
- Frontend:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

## Project Structure
```
chat-with-pdf/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/  # Modular API routes (REST & WebSocket)
│   │   ├── models/         # All Pydantic models (REST & WebSocket)
│   │   ├── services/       # PDF, vector, LLM, RAG logic
│   │   ├── utils/          # Chunking, citations, etc.
│   │   └── main.py         # FastAPI app entrypoint
├── frontend/          # React frontend
├── docker-compose.yml # Orchestration
├── README.md
├── roadmap.md         # Development plan
└── design-doc.md      # Architecture/design
```

## Environment Variables

Create a `.env` file in `backend/` (see `.env.example`):

```
GROQ_API_KEY=your-groq-api-key-here
GROQ_API_BASE=https://api.groq.com/v1
JWT_SECRET=your-jwt-secret
```
- `GROQ_API_KEY`: Your Groq API key for Llama-3.1-70B-Versatile.
- `GROQ_API_BASE`: (Optional) Override for Groq API base URL.
- `JWT_SECRET`: Secret for JWT authentication (required for all chat/conversation endpoints).

The backend will automatically load these variables for LLM and authentication integration.

## API Overview

### REST Endpoints
- `POST /api/v1/documents/upload` - PDF upload and processing
- `GET /api/v1/documents` - List uploaded documents
- `DELETE /api/v1/documents/{document_id}` - Remove document
- `POST /api/v1/chat/message` - Multi-turn conversation
- `POST /api/v1/chat/deep-query` - Single deep-dive question
- `GET /api/v1/conversations/{conversation_id}` - Get conversation history
- `DELETE /api/v1/conversations/{conversation_id}` - Reset conversation
- `GET /api/v1/health` - Health check

### WebSocket Endpoints
- `WS /api/v1/chat/stream` - Real-time chat streaming (token-by-token)

### Models
- All request/response models are in `backend/app/models/` (REST and WebSocket)

## Citation & Grounding
- All answers include page numbers and/or text snippets from the PDF for transparency.

## License
MIT
