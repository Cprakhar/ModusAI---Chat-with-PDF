# ModusAI - Chat-with-PDF

A full-stack application for secure, real-time, and streaming chat with your PDF documents. Features include PDF upload, sidebar-driven chat/conversation management, and a robust "deep-dive" mode for comprehensive document analysis.

## Features
- **PDF Upload & Management:** Upload, list, and delete PDF documents. Deleting a PDF also deletes its associated conversations.
- **Sidebar-Driven UI:** Manage PDFs and chat conversations from a modern sidebar interface.
- **Multi-Turn Chat:** Chat with your PDF using a streaming WebSocket connection.
- **Deep-Dive Mode:** Toggle for single-turn, comprehensive answers with extensive citations, streamed via WebSocket.
- **Authentication:** All endpoints and WebSocket connections require JWT authentication.
- **Citations Panel:** View and navigate citations for each AI response.
- **Robust Error Handling:** Graceful handling of authentication, connection, and backend errors.

## Tech Stack
- **Frontend:** Next.js, React, Tailwind CSS
- **Backend:** FastAPI, WebSockets, ChromaDB (vector store), SQLite (for conversations)
- **LLM Integration:** Pluggable LLM client for chat and deep-dive modes

## Local Development

### Prerequisites
- Node.js (v18+ recommended)
- Python 3.10+
- [ChromaDB](https://docs.trychroma.com/) (or compatible vector store)

### Backend Setup
1. Create a Python virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Set environment variables (for JWT and GROQ):
   ```bash
   export JWT_SECRET=your-secret-key
   export JWT_ALGORITHM=HS256
   export GROQ_API_KEY=your-groq-api-key-here
   export GROQ_API_BASE=https://api.groq.com/v1
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup
1. Install dependencies:
   ```bash
   cd frontend
   pnpm install
   # or
   npm install
   ```
2. Start the Next.js dev server:
   ```bash
   pnpm dev
   # or
   npm run dev
   ```
3. The app will be available at [http://localhost:3000](http://localhost:3000)

### WebSocket Development Note
- For WebSocket endpoints (`/chat/stream` and `/chat/deep-query/stream`), the frontend connects directly to the backend (`ws://localhost:8000/api/v1/...`) in development to avoid Next.js proxy issues.

## Quick Start: Run the Entire Stack with Docker Compose

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd ModusAI-Chat-with-PDF
   ```
2. **Copy and edit environment variables:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env and set your GROQ_API_KEY, JWT_SECRET, etc.
   ```
3. **Build and start all services:**
   ```bash
   docker compose up --build
   ```
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000
   - ChromaDB: http://localhost:8001 (if exposed)

**Note:** The first build may take several minutes (especially for Python dependencies and model downloads).

### Stopping the stack
Press `Ctrl+C` in the terminal running Docker Compose, or run:
```bash
docker compose down
```

---

## Manual Setup (For Development)

1. **Backend:**
   ```bash
   cd backend
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env  # and edit as needed
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
2. **Frontend:**
   ```bash
   cd frontend
   pnpm install  # or npm install
   pnpm dev      # or npm run dev
   # App at http://localhost:3000
   ```
3. **ChromaDB:**
   - Start ChromaDB as a service (see ChromaDB docs or use Docker Compose).

---

## Usage
1. Register and log in to obtain a JWT token (stored in localStorage).
2. Upload a PDF document.
3. Start a new chat or select an existing conversation from the sidebar.
4. Use multi-turn chat or toggle deep-dive mode for comprehensive answers.
5. View citations in citation panel.

---

## Troubleshooting
- **First build is slow:** This is normal due to model and dependency downloads. Subsequent builds are faster unless you use `--no-cache`.
- **Frontend can't reach backend:** Make sure you use `backend:8000` (not `localhost:8000`) in Docker Compose/Next.js rewrites.
- **PyTorch/SentenceTransformers meta tensor error:** The Dockerfile is set up to avoid this. If you see it, rebuild with `docker compose build --no-cache`.
- **ChromaDB errors:** Ensure ChromaDB is running and accessible.

---

## Project Structure
- `backend/` — FastAPI app, API endpoints, vector store, LLM integration
- `frontend/` — Next.js app, React components, sidebar, chat interface

## License
MIT

## ChromaDB Usage: Local vs Docker Compose

- **Local development:**
  - The backend uses ChromaDB in embedded (in-process) mode, storing vectors in the `chroma_db` directory.
  - No separate ChromaDB server is required.

- **Docker Compose:**
  - ChromaDB runs as a separate service (`chromadb`), and the backend connects to it via HTTP.
  - This is controlled by the `CHROMA_SERVER=true` environment variable set in `docker-compose.yml` for the backend service.
  - The backend will auto-detect and use the correct mode based on this variable.

No code changes are needed to switch between modes—just run locally or with Docker Compose as described above.
