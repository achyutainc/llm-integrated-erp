# Local ERP AI Platform

This project combines a lightweight ERP system (FastAPI + Vue 3) with a local AI Agent (LangGraph + Ollama).

## Architecture

- **Backend**: FastAPI with SQLModel (PostgreSQL/SQLite). Handles Inventory, Orders, Users.
- **AI Engine**: Python service using LangGraph and LangChain to interact with Ollama and the Backend API.
- **Frontend**: Vue 3 + Tailwind CSS + Vite.
- **Database**: PostgreSQL (or SQLite for dev).
- **AI Model**: Ollama running locally (Llama 3 recommended).

## Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local frontend dev if not using Docker)
- Python 3.12+ (for local backend dev)

## Getting Started

1.  **Start Services**:
    ```bash
    docker-compose up --build
    ```

2.  **Pull AI Model**:
    Once the `ollama` service is running, you need to pull the model:
    ```bash
    docker exec -it <ollama_container_id> ollama pull llama3
    ```

3.  **Seed Data**:
    Run the seed script to populate initial inventory:
    ```bash
    docker-compose exec backend python backend/seed_data.py
    ```

4.  **Access the App**:
    - Frontend: http://localhost:5173
    - Backend API Docs: http://localhost:8000/docs
    - AI Engine Docs: http://localhost:8001/docs

## Development

- **Backend**:
  - Code changes in `backend/` auto-reload.
  - Tests: `pytest tests/`

- **AI Engine**:
  - Code changes in `ai_engine/` auto-reload.

- **Frontend**:
  - Code changes in `frontend/` auto-reload.

## Features

- **Inventory Management**: Add/Edit products, track stock.
- **AI Assistant**: Chat with the system to query inventory ("Do we have milk?") or create orders.
- **Order Management**: Create orders via API or AI.
