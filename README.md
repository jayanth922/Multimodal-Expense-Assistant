A full-stack demo that lets you chat to add expenses, upload receipt images for structured extraction, and view summaries by date & category — backed by Neon Postgres and a tiny RAG index for deterministic guidance (e.g., supported categories).

TL;DR (Local Run)

# Backend (port 8001)
cd backend
# .env (see below): DATABASE_URL=postgresql+psycopg://USER:PASS@HOST/neondb?sslmode=require
PYTHONPATH=. uv run uvicorn app.main:app --reload --port 8001

# Frontend (port 3000)
cd frontend
# .env.local: NEXT_PUBLIC_API_BASE=http://localhost:8001
npm run dev
Open http://localhost:3000



Features

Chat: Add expenses in natural language (amount, category, vendor, date).

Vision: Drag-and-drop receipt images → vendor/date/total/category (+ line items, confidence).

Insights: Totals & by-category chart with date range filters.

RAG: Auto-seeded local knowledge (e.g., “What categories do you support?”).

Production-ish: Postgres via Neon, robust DB engine settings, CORS, typed APIs.




Tech Stack

Frontend: Next.js (App Router), Tailwind, Framer Motion, Recharts, lucide-react

Backend: FastAPI, Google ADK (agent runtime + function tools), SQLAlchemy 2.x (async)

DB: Neon Postgres (via psycopg driver)

RAG: Lightweight local store (Chroma) seeded from rag/data/*.md




Configuration
Backend – backend/.env

Copy .env.example → .env and set:


# Recommended psycopg DSN (Neon-style)
DATABASE_URL=postgresql+psycopg://USER:PASS@HOST/neondb?sslmode=require&channel_binding=require

# Optional (local fallback if DATABASE_URL is unset)
SQLITE_PATH=./db/expenses.sqlite

# Google ADK / Gemini
GOOGLE_API_KEY=xxxx
GENAI_MODEL=gemini-2.5-flash

# RAG (defaults are fine)
RAG_INDEX_DIR=rag/index




Frontend – frontend/.env.local


NEXT_PUBLIC_API_BASE=http://localhost:8001
