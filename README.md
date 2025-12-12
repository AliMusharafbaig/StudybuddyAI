# 🎓 StudyBuddy AI

An AI-powered educational platform that helps students learn smarter, not harder.

## ✨ Features

- **📚 Smart Content Processing** - Upload PDFs, videos, audio, and more
- **🧠 6 Specialized AI Agents** - Working together for optimal learning
- **📝 Adaptive Quizzes** - Questions that adjust to your level
- **🚨 Emergency Cram Mode** - Optimized study plans when time is short
- **💬 AI Chat** - Ask questions, get instant answers
- **📊 Analytics** - Track progress and identify weak areas
- **🔮 Exam Predictions** - Know what topics to focus on

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11, PostgreSQL, MongoDB
- **AI**: Google Gemini 2.0, LangChain, FAISS
- **Frontend**: React 18, Vite, Framer Motion
- **Infra**: Docker, Redis

## 🚀 Quick Start

### 1. Set Environment Variables
```bash
cp backend/.env.example backend/.env
# Edit .env and add your GEMINI_API_KEY
```

### 2. Run with Docker
```bash
docker-compose up -d
```

### 3. Access the App
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## 🏗️ Manual Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
StudybuddyAI/
├── backend/
│   ├── agents/          # 6 AI agents
│   ├── api/             # Routes, models, schemas
│   ├── core/            # Config, database, LLM, RAG
│   ├── services/        # Background processors
│   └── main.py          # FastAPI entry point
├── frontend/
│   ├── src/
│   │   ├── pages/       # React pages
│   │   ├── components/  # Shared components
│   │   └── store/       # Zustand state
│   └── index.html
└── docker-compose.yml
```

## 👥 Team

Ali Musharaf, Ali Farooq, Fahad Jameel, Laraib noor, Abbas

## 📄 License

MIT
