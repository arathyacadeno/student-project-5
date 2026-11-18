# StudyMatch AI

> **"Learn Together. Teach Each Other. Improve Faster. Plan Your Future."**

StudyMatch AI is an intelligent web application designed for peer-learning study group matching and personalized higher-studies/career guidance. It tracks student topic proficiencies in real-time via an adaptive **Skill Profile Engine** (labelling topics as *weak*, *average*, or *strong*), connecting test performance directly to learning materials, course roadmaps, AI personal mentoring, and peer-teaching study groups.

---

## 🛠️ Technology Stack

- **Frontend**: React 19, React Router v7, Recharts, Axios, CSS3 (Modern Responsive UI with Desktop Sidebar & Mobile Bottom Navigation)
- **Backend**: Python 3.12, FastAPI (REST APIs, JWT authentication, PBKDF2 password hashing, Pydantic v2 schemas)
- **Database**: PostgreSQL (SQLAlchemy 2.0 ORM, psycopg2)
- **Machine Learning & Analytics**: scikit-learn, Pandas, NumPy, SciPy
- **AI Mentoring**: Multi-turn academic mentor supporting backend LLM APIs (Gemini / OpenAI) with intelligent domain-knowledge retrieval fallback

---

## 🚀 The 6 Student Support Features

### 1. Study Materials & Weak-Topic Prioritization
- Browse comprehensive study notes, formula sheets, important questions, and learning resources by Subject (`Biology`, `Mathematics`, `Computer Science`) and Topic.
- **Weak Topic Prioritization**: Automatically prioritizes materials for a student's identified weak topics to the top of the feed with a distinct visual badge.
- Search, filter by type, bookmark/save materials for fast review.
- Teacher role capability to publish, edit, and delete materials.

### 2. Future Course Guidance
- Suggests higher-study programs (e.g. *B.Tech CS & AI*, *Bioinformatics*, *Data Science & Statistics*, *MBBS*) matched against student strengths, academic profile, and interests.
- Interactive 5-question Interest Questionnaire calculating personalized match percentages (0–100%).
- Deep-dive roadmaps with degree level, eligibility criteria, fees range, career scope, and required entrance exams.

### 3. Personal Mentoring through AI Assistance
- 24/7 dedicated academic mentor that retrieves the student's real-time weak/strong topics, test scores, and learning goals.
- Provides concept breakdowns, study timetables, and targeted exam advice.
- Includes dynamic suggested-question chips, persistent chat history per student, and secure backend-only API key handling.

### 4. Mock Tests Based on Student Level (Adaptive)
- Timed practice tests with automatic scoring and countdown timer.
- **Adaptive Level Selection**: Automatically chooses questions based on student skill levels (rebuilding foundations for weak topics and challenging strong topics), with manual override (`Easy`, `Medium`, `Difficult`).
- **Skill Profile Automatic Update**: Test results immediately recalculate topic proficiencies in the database and update topic ratings.
- Recharts topic-wise accuracy analytics and question-by-question review with step-by-step solutions.

### 5. Course Summaries & Rapid Revision
- High-yield summaries, formulas, and key points for Biology, Mathematics, and Computer Science (extensible to any subject).
- Fast revision view with concise cheat sheets and an interactive 3-question rapid concept retention quiz with instant scoring.
- Teachers can edit summaries or generate new ones.

### 6. Previous Question Papers (Solved) with Remediation Links
- Solved past board and entrance examinations with step-by-step methods and verified answers.
- Filter by subject and year (2024, 2023, 2022).
- **Two Modes**: *Study Mode* (learn step-by-step answers) vs *Timed Exam Mode* (exam simulation).
- **Remediation**: Every wrong answer directly links back to the related study material topic to close learning gaps immediately.

---

## 🔄 Connecting Everything: The Skill Profile Engine

```
       [ Mock Tests / Paper Attempts ]
                      │
                      ▼
            [ Topic Evaluation ]
     (Score <50%: Weak | 50-75%: Avg | >75%: Strong)
                      │
                      ▼
             [ Skill Profile ]
                      │
    ┌─────────────────┼─────────────────┐
    ▼                 ▼                 ▼
[ Study Materials ]  [ Course Guidance ]  [ AI Mentor ]
(Weak topics first)  (Strength alignment) (Focuses advice)
```

1. **Assessments** (adaptive mock tests and past paper attempts) evaluate topic accuracy.
2. The **Skill Profile** dynamically updates topic mastery scores.
3. **Study Materials** sort weak-topic notes to the top of the feed.
4. **Mock Tests** calibrate question difficulty based on weak vs strong ratings.
5. **Course Guidance** maps strong subjects to career roadmaps and flags prerequisites.
6. **AI Mentor** proactively addresses weak topics in conversation.
7. **Student Dashboard** provides real-time progress charts and action recommendations.
8. **Teacher Dashboard** highlights class-wide difficulty heatmaps and at-risk student alerts.

---

## ⚙️ Environment Variables

### Backend (`backend/.env` or system environment):
```env
# Database URL (Default matches local PostgreSQL)
DB_USER=postgres
DB_PASSWORD=admin123
DB_HOST=localhost
DB_PORT=5432
DB_NAME=studymatch_db

# Security & Authentication
JWT_SECRET=studymatch_jwt_secret_key_change_in_production_2026

# Optional: Language Model API Keys (Kept strictly on backend)
# If omitted, intelligent contextual retrieval engine powers mentor & summaries
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### Frontend (`frontend/.env`):
```env
VITE_API_URL=http://127.0.0.1:8000
```

---

## 🚀 Setup & Installation Steps

### Prerequisites
- Node.js 18+ & npm
- Python 3.10+
- PostgreSQL server running on port 5432 with database `studymatch_db`

### 1. Database Setup
```sql
CREATE DATABASE studymatch_db;
```

### 2. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations and seed sample data (Biology, Math, CS, papers, questions)
python seed_data.py

# Start FastAPI backend server
uvicorn main:app --reload --port 8000
```
Backend will be live at: `http://127.0.0.1:8000`  
Swagger API Documentation: `http://127.0.0.1:8000/docs`

### 3. Frontend Setup
```bash
cd frontend

# Install packages
npm install

# Start Vite development server
npm run dev
```
Frontend will be live at: `http://localhost:5173`

---

## 👤 Pre-Seeded Test Accounts

| Account | Email | Password | Role | Description |
|---|---|---|---|---|
| **Student** | `student@studymatch.ai` | `password123` | `student` | Alex Morgan (Pre-seeded with weak topics in Calculus & Genetics) |
| **Teacher** | `teacher@studymatch.ai` | `password123` | `teacher` | Dr. Sarah Jenkins (Full access to Teacher Analytics & Materials Upload) |

*(Quick 1-click login buttons for both accounts are available directly on the login screen).*

---

## 📡 Key REST API Routes

### Authentication
- `POST /login` - Student / Teacher login (returns JWT token and profile)
- `POST /register` - Register new user account
- `GET /auth/me` - Get current authenticated user details

### Skill Profile & Dashboards
- `GET /skill-profile` - Student's subject-by-subject topic proficiency
- `GET /skill-profile/summary` - Aggregate counts (weak, average, strong) and mastery percentages
- `GET /profile/me` - Academic level and learning goals
- `GET /teacher/dashboard` - Class-wide weak topics heatmap and at-risk student alerts

### Feature 1: Study Materials
- `GET /materials` - List materials (supports search, filters, pagination, weak topic priority)
- `GET /materials/{id}` - Single material details
- `POST /materials` - Teacher upload new material
- `PUT /materials/{id}` - Teacher edit material
- `DELETE /materials/{id}` - Teacher delete material
- `POST /materials/{id}/bookmark` - Toggle bookmark status

### Feature 2: Future Course Guidance
- `GET /guidance/courses` - Ranked recommendations with match percentages
- `POST /guidance/questionnaire` - Submit 5-question interest questionnaire
- `GET /guidance/courses/{id}` - Course detail, eligibility, entrance exams, and roadmap

### Feature 3: Personal AI Mentor
- `POST /mentor/chat` - Chat with personal mentor (context-injected)
- `GET /mentor/history` - Retrieve student conversation history and suggested chips
- `DELETE /mentor/history` - Clear conversation thread

### Feature 4: Mock Tests
- `POST /mock-tests/generate` - Generate adaptive or level-overridden mock test
- `POST /mock-tests/{id}/submit` - Auto-grade test and update student Skill Profile
- `GET /mock-tests/history` - Past test history and scores

### Feature 5: Course Summaries
- `GET /summaries` - List course summaries by subject
- `GET /summaries/{id}` - Summary, key points, and quick revision notes
- `PUT /summaries/{id}` - Teacher edit summary
- `POST /summaries/{id}/quiz-submit` - Submit rapid concept retention quiz

### Feature 6: Previous Question Papers
- `GET /papers` - Solved previous papers filtered by subject & year
- `GET /papers/{id}` - Paper questions with step-by-step solutions
- `POST /papers/{id}/attempt` - Submit timed exam attempt with **wrong answer remediation links**

---

## 🧪 Running Automated Tests

Run the full end-to-end backend test suite:
```bash
python backend/test_api.py
```
*Executes all 10 feature test suites verifying JWT auth, weak topic prioritization, questionnaire scoring, AI mentoring, adaptive mock test grading, skill profile updates, course summaries, past paper remediation, and teacher dashboard analytics.*

Frontend build verification:
```bash
cd frontend
npm run build
```
