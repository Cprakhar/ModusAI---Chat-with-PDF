# ModusAI - Chat-with-PDF: Design Document

## Overview
ModusAI - Chat-with-PDF is a full-stack Retrieval-Augmented Generation (RAG) system that enables users to upload, manage, and chat with PDF documents. It supports both multi-turn conversational chat and a deep-dive mode for comprehensive, citation-rich answers. The system is designed for real-time, secure, and scalable document analysis.

## Architecture

### 1. Frontend (Next.js + React)
- **Sidebar-Driven UI:** Users manage PDFs and conversations from a sidebar.
- **Chat Interface:** Supports multi-turn and deep-dive chat modes, with real-time streaming via WebSockets.
- **Citation Panel:** Displays and navigates citations for each AI response.
- **Authentication:** JWT-based, stored in localStorage and sent with all API/WebSocket requests.

### 2. Backend (FastAPI)
- **REST API:** For PDF upload, document management, and conversation history.
- **WebSocket API:**
  - `/chat/stream`: Multi-turn chat with streaming responses.
  - `/chat/deep-query/stream`: Deep-dive, single-turn, citation-rich answers.
- **Authentication:** All endpoints require JWT validation.
- **Vector Store:** ChromaDB for document chunk storage and retrieval.
- **LLM Client:** Pluggable interface for chat and deep-dive generation.
- **Database:** SQLite for conversation/session persistence.

### 3. Data Flow
1. **User uploads PDF** → Backend processes, chunks, and stores in ChromaDB; creates a conversation session.
2. **User starts chat** → Frontend opens WebSocket, sends JWT; backend streams LLM responses and citations.
3. **Deep-dive mode** → Frontend sends query and document_id; backend streams comprehensive answer and citations.

## Key Design Decisions
- **WebSocket Streaming:** Enables real-time, token-by-token LLM responses for both chat and deep-dive, improving UX.
- **JWT Everywhere:** All API and WebSocket endpoints require JWT, ensuring security for all user actions.
- **Sidebar-Driven UX:** Centralizes document and conversation management, making the app intuitive and scalable.
- **ChromaDB for RAG:** Chosen for its local, privacy-friendly, and scalable vector search capabilities.
- **Modular Backend:** Each API concern (auth, chat, documents, conversations) is a separate router for maintainability.
- **Direct WebSocket Dev Connection:** In development, frontend connects directly to backend WebSocket endpoints to avoid Next.js proxy limitations.

## Security Considerations
- JWT validation on every request and WebSocket message.
- All document and conversation actions are user-scoped.
- CORS and rate limiting enabled by default.

## Extensibility
- LLM client is pluggable for easy swap/upgrade.
- Vector store abstraction allows for future migration from ChromaDB.
- UI components are modular and reusable.

## Limitations & Future Work
- No multi-user document sharing yet.
- No cloud deployment scripts (Docker Compose provided for local/dev).
- LLM and vector store must be running locally or configured for remote access.

## Diagram
```
[User] ⇄ [Next.js Frontend] ⇄ [FastAPI Backend] ⇄ [ChromaDB] ⇄ [LLM API]
```

---

For more, see the code and README.md in this repository.
