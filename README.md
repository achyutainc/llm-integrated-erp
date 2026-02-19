# Local ERP AI Platform

This project combines a lightweight ERP system (FastAPI + Vue 3) with a local AI Agent (LangGraph + Ollama), customized for a Grocery & Takeout business.

## Architecture

- **Backend**: FastAPI with SQLModel (PostgreSQL/SQLite). Handles Inventory, Orders, Users, Marketing.
- **AI Engine**: Python service using LangGraph and LangChain to interface with Ollama and the Backend API.
- **Frontend**: Vue 3 + Tailwind CSS + Vite. Includes Staff Dashboard & Customer Shop.
- **Database**: PostgreSQL (or SQLite for dev).
- **AI Model**: Ollama running locally (Llama 3 recommended).

## Deployment (Render)

This project includes a `render.yaml` for easy deployment on [Render](https://render.com).

**⚠️ Important Constraints for Free Tier:**
1.  **AI Engine**: The Free Tier (512MB RAM) **cannot** run the local LLM (Ollama/Llama 3) required by `ai_engine`.
    *   *Workaround:* For cloud deployment, you must modify `ai_engine/agent.py` to use a remote API (like OpenAI or Anthropic) instead of `ChatOllama`, OR host Ollama on a machine with GPU/RAM and expose it via a tunnel (e.g., Ngrok) to the Render service.
2.  **Spin Down**: Free web services spin down after 15 minutes of inactivity.

## Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local frontend dev if not using Docker)
- Python 3.12+ (for local backend dev)

## Getting Started (Local)

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
    Run the seed script to populate initial inventory and marketing drafts:
    ```bash
    docker-compose exec backend python backend/seed_data.py
    ```

4.  **Access the App**:
    - **Frontend**: http://localhost:5173
      - **Staff Dashboard**: http://localhost:5173/#/ (Default)
      - **Customer Shop**: http://localhost:5173/#/shop
      - **POS**: http://localhost:5173/#/pos
    - **Backend API Docs**: http://localhost:8000/docs
    - **AI Engine Docs**: http://localhost:8001/docs

## Features

- **Inventory Management**:
  - Track stock levels and *Expiry Dates* (FEFO logic).
  - AI Alerts for expiring items.
- **Point of Sale (POS)**:
  - Modern touch-friendly interface.
  - Barcode scanning support.
  - Customer tracking.
- **AI Staff Assistant**:
  - Chat interface to query stock ("Do we have milk?").
  - *Marketing Assistant*: Draft social media posts.
- **Customer Experience**:
  - **Online Shop**: Browse products.
  - **Chef AI**: Specialized chat bot for Indian cuisine advice.

## Guides

- [Staff Guide (AI Usage)](STAFF_GUIDE.md)
