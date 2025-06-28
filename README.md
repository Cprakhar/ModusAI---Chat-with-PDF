# Chat-with-PDF: Advanced RAG System

A Retrieval-Augmented Generation (RAG) application that allows users to upload large PDFs and interact with them via chat or deep-dive queries, with answers grounded in the document and source citations.

## Features
- Upload and process PDFs (500+ pages, structured/unstructured)
- Multi-turn chat and single-turn deep-dive research modes
- Answers cite page numbers or text snippets from the PDF
- Local, privacy-friendly vector search (ChromaDB)
- FastAPI backend, React frontend, Dockerized stack

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
├── frontend/          # React frontend
├── docker-compose.yml # Orchestration
├── README.md
├── roadmap.md         # Development plan
└── design-doc.md      # Architecture/design
```

## Environment Variables
- Copy `backend/.env.example` to `backend/.env` and fill in required values (API keys, etc).

## Citation & Grounding
- All answers include page numbers and/or text snippets from the PDF for transparency.

## License
MIT
