# 💰 Multimodal Expense Assistant

> A full-stack intelligent expense tracking application that combines natural language processing, computer vision, and RAG (Retrieval-Augmented Generation) to simplify expense management.

**Chat to add expenses, upload receipt images for automatic data extraction, and visualize spending patterns with interactive charts** — all powered by Google's Gemini AI, Neon Postgres, and a local RAG index.

[![Tech Stack](https://img.shields.io/badge/Stack-Next.js%20%7C%20FastAPI%20%7C%20PostgreSQL-blue)](#tech-stack)
[![AI Powered](https://img.shields.io/badge/AI-Google%20Gemini%202.5-orange)](#features)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)

---

## 🚀 Quick Start (Local Development)

### Backend Setup (Port 8001)

```bash
cd backend

# Create .env file (see Configuration section below)
# DATABASE_URL=postgresql+psycopg://USER:PASS@HOST/neondb?sslmode=require

# Install dependencies and run server
PYTHONPATH=. uv run uvicorn app.main:app --reload --port 8001
```

### Frontend Setup (Port 3000)

```bash
cd frontend

# Create .env.local file
# NEXT_PUBLIC_API_BASE=http://localhost:8001

# Install dependencies and run development server
npm install
npm run dev
```

**🌐 Access the application:** Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 💬 **Natural Language Chat** | Add expenses conversationally with automatic extraction of amount, category, vendor, and date |
| 📸 **Receipt Vision Processing** | Drag-and-drop receipt images for AI-powered structured data extraction including vendor, date, total, line items, and confidence scores |
| 📊 **Smart Insights Dashboard** | Interactive charts and analytics with date range filters, category breakdowns, and spending trends |
| 🧠 **RAG-Powered Knowledge Base** | Local knowledge index for intelligent responses to app-related queries (e.g., "What categories do you support?") |
| 🏭 **Production-Ready Architecture** | Enterprise-grade setup with Neon Postgres, robust database engine configuration, CORS handling, and fully typed APIs |

---

## 🛠️ Tech Stack

### **Frontend**
- **Framework:** Next.js (App Router)
- **Styling:** Tailwind CSS
- **Animations:** Framer Motion
- **Charts:** Recharts
- **Icons:** lucide-react

### **Backend**
- **API Framework:** FastAPI
- **AI Runtime:** Google ADK (Agent Development Kit with function tools)
- **ORM:** SQLAlchemy 2.x (async)
- **Database Driver:** psycopg (PostgreSQL)

### **Database**
- **Primary:** Neon Postgres (serverless PostgreSQL)
- **Fallback:** SQLite (local development)

### **RAG System**
- **Vector Store:** Chroma (lightweight local store)
- **Knowledge Base:** Auto-seeded from `rag/data/*.md` files

---

## ⚙️ Configuration

### Backend Configuration (`backend/.env`)

Create your `.env` file based on `.env.example`:

```bash
# ===== DATABASE CONFIGURATION =====
# Primary: Neon Postgres (recommended for production)
DATABASE_URL=postgresql+psycopg://USER:PASS@HOST/neondb?sslmode=require&channel_binding=require

# Fallback: SQLite (local development only)
SQLITE_PATH=./db/expenses.sqlite

# ===== AI CONFIGURATION =====
# Google Gemini API credentials
GOOGLE_API_KEY=your_google_api_key_here
GENAI_MODEL=gemini-2.5-flash

# ===== RAG CONFIGURATION =====
# Path to RAG vector index (defaults are fine)
RAG_INDEX_DIR=rag/index
```

#### 🔑 Important Notes:
- Use the `psycopg` driver format for Neon Postgres (not `psycopg2`)
- Enable `sslmode=require` and `channel_binding=require` for secure connections
- Get your Google API key from [Google AI Studio](https://aistudio.google.com/)

### Frontend Configuration (`frontend/.env.local`)

```bash
# Backend API endpoint
NEXT_PUBLIC_API_BASE=http://localhost:8001
```

---

## 📁 Project Structure

```
Multimodal-Expense-Assistant/
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── models/              # SQLAlchemy database models
│   │   ├── routes/              # API route handlers
│   │   └── services/            # Business logic & AI agents
│   ├── rag/
│   │   ├── data/                # Knowledge base markdown files
│   │   └── index/               # Vector store indexes
│   ├── .env.example             # Environment template
│   └── requirements.txt         # Python dependencies
│
├── frontend/
│   ├── app/                     # Next.js app directory
│   ├── components/              # React components
│   ├── public/                  # Static assets
│   ├── .env.local.example       # Environment template
│   └── package.json             # Node dependencies
│
└── README.md
```

---

## 🎯 Use Cases

1. **Personal Finance Management** – Track daily expenses with minimal effort
2. **Small Business Accounting** – Digitize receipts and categorize business expenses
3. **Travel Expense Reporting** – Quick expense logging during business trips
4. **Budget Analysis** – Understand spending patterns with visual insights
5. **Receipt Digitization** – Convert paper receipts to structured digital records

---

## 🏗️ Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Next.js UI    │ ◄─────► │   FastAPI Server │ ◄─────► │  Neon Postgres  │
│   (Frontend)    │         │    (Backend)     │         │   (Database)    │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                     │
                          ┌──────────┴──────────┐
                          ▼                     ▼
                    ┌──────────┐         ┌──────────┐
                    │  Google  │         │  Chroma  │
                    │  Gemini  │         │   RAG    │
                    │    AI    │         │  Vector  │
                    └──────────┘         └──────────┘
```

---

## 🔒 Security Considerations

- ✅ SSL/TLS enforced for database connections
- ✅ Environment variables for sensitive credentials
- ✅ CORS configuration for API security
- ✅ API key authentication for AI services
- ⚠️ **Note:** Add user authentication for production deployments

---

## 🐛 Troubleshooting

### Database Connection Issues
- Verify your `DATABASE_URL` format matches the psycopg driver syntax
- Ensure your Neon database is active and accessible
- Check firewall/network settings if using cloud databases

### API Key Errors
- Confirm your `GOOGLE_API_KEY` is valid and active
- Check API quota limits in Google Cloud Console
- Verify the model name matches available models (e.g., `gemini-2.5-flash`)

### Frontend Connection Errors
- Verify `NEXT_PUBLIC_API_BASE` points to the running backend
- Ensure backend is running on the specified port (default: 8001)
- Check CORS settings if running on different domains

### RAG Index Issues
- Ensure `rag/data/*.md` files exist and contain valid markdown
- Delete and regenerate the `rag/index` directory if corrupted
- Check file permissions on the index directory

---

## 📝 API Documentation

Once the backend is running, visit:
- **Interactive API Docs:** http://localhost:8001/docs (Swagger UI)
- **Alternative Docs:** http://localhost:8001/redoc (ReDoc)

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 🚀 Deployment

### Backend (Railway/Render/Fly.io)
1. Set environment variables in your hosting platform
2. Ensure `DATABASE_URL` points to your production Neon instance
3. Deploy using your platform's CLI or Git integration

### Frontend (Vercel/Netlify)
1. Connect your GitHub repository
2. Set `NEXT_PUBLIC_API_BASE` to your production backend URL
3. Deploy with automatic builds on push

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- **Google Gemini AI** for multimodal capabilities
- **Neon** for serverless Postgres
- **Vercel** for Next.js framework
- **FastAPI** for modern Python APIs

---

## 📧 Contact & Support

For questions, issues, or feature requests, please [open an issue](https://github.com/jayanth922/Multimodal-Expense-Assistant/issues) on GitHub.

---

**Built with ❤️ using Google Gemini AI, Neon Postgres, and modern web technologies**
