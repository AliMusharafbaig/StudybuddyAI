# 🚀 StudyBuddy AI - Deployment & Demo Guide

## STEP 1: Pre-Deployment Checklist ✅

- [x] All code files created (75+ files)
- [x] Frontend: React with 10 pages
- [x] Backend: FastAPI with 6 AI agents
- [x] Docker configuration ready
- [x] Tests created
- [x] .env file with GEMINI_API_KEY

---

## STEP 2: Run with Docker Compose

### What is Docker Compose?
Docker Compose runs your entire application (frontend, backend, databases) with ONE command.

### Commands:

```powershell
# Navigate to project
cd d:\UserData\Desktop\StudybuddyAI

# Start everything (first time takes 5-10 mins to build)
docker-compose up -d --build

# Check if running
docker-compose ps

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

### Access Points:
| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Metrics | http://localhost:8000/metrics |

---

## STEP 3: Upload to GitHub

```powershell
# Navigate to project
cd d:\UserData\Desktop\StudybuddyAI

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "StudyBuddy AI - Complete Implementation"

# Create repo on GitHub.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/StudybuddyAI.git
git branch -M main
git push -u origin main
```

---

## STEP 4: Demo Walkthrough (10 mins)

### Minute 1-2: Introduction
- Show architecture diagram (ARCHITECTURE.md)
- Explain problem: "Students struggle with exam prep"
- Our solution: "AI-powered adaptive learning"

### Minute 3-4: User Registration
- Open http://localhost:3000
- Click "Get Started"
- Register new account
- Login

### Minute 5-6: Course & Upload
- Create new course "Machine Learning"
- Upload a PDF file
- Show AI processing (concepts extracted)

### Minute 7-8: Quiz Demo
- Start a quiz
- Answer questions
- Show adaptive difficulty
- Show confusion detection

### Minute 8-9: Cram Mode
- Open Cram Mode
- Enter "2 hours until exam"
- Show optimized study plan

### Minute 9-10: AI Chat
- Ask: "Explain neural networks"
- Show RAG in action
- Q&A

---

## STEP 5: If Docker Issues (Run Manually)

### Terminal 1: Backend
```powershell
cd d:\UserData\Desktop\StudybuddyAI\backend
pip install -r requirements.txt
python main.py
```

### Terminal 2: Frontend
```powershell
cd d:\UserData\Desktop\StudybuddyAI\frontend
npm install
npm run dev
```

Access: http://localhost:5173

---

## Final Deliverables Checklist

| Deliverable | Location | Status |
|-------------|----------|--------|
| GitHub Repository | github.com/... | ⏳ Upload needed |
| Architecture Diagram | ARCHITECTURE.md | ✅ Done |
| Dockerfile + Compose | Dockerfile, docker-compose.yml | ✅ Done |
| API Documentation | http://localhost:8000/docs | ✅ Auto-generated |
| Tests | backend/tests/ | ✅ Done |
| README | README.md | ✅ Done |

---

## Quick Reference Commands

```powershell
# Start project
docker-compose up -d

# Stop project
docker-compose down

# View logs
docker-compose logs backend

# Rebuild after changes
docker-compose up -d --build

# Run tests
cd backend && pytest tests/ -v
```
