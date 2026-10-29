# EduAI — AI-Powered University Learning Platform

EduAI is a full-stack, enterprise-grade university Learning Management System (LMS) that enables professors and teachers to design and generate accredited courses using generative AI, and empowers students with structured lesson scripts, video lecture players, downloadable Smart Notes (PDF and Word DOCX), adaptive interactive quizzes, personalized diagnostic feedback, and in-context AI tutor support.

---

## 🌟 Key Highlights & Architectural Features

1. **Role-Based Workspaces & Dynamic Navigation**:
   - **Faculty / Teacher**: AI Course Generator, Course Builder & Script Editor, 6-Artifact Pipeline Inspector, Quiz Question Manager, and Academic Analytics.
   - **Student Learner**: Course Catalog & Instant Enrollment, Modular Lesson Player with sequential unlocking, Interactive Quiz Player with instant grading, Smart Notes downloads, and Grounded AI Teaching Assistant.
   - **University Administrator (Dean)**: System-wide KPI telemetry, User Directory management (role changes & status deactivation with self-demotion protection), and platform audit logging.

2. **Complete Light Mode & Dark Mode System**:
   - Centralized Theme Provider with zero-flash early head initialization.
   - Instant Sun/Moon toggle with smooth CSS icon transitions and keyboard accessibility.
   - Tailwind `dark` class support + CSS variables (`--background`, `--surface`, `--primary`, `--border`, `--text-primary`, `--text-secondary`).
   - Dynamic Recharts theme synchronization for optimal contrast in both modes.
   - Seamless persistence across browser refreshes via `localStorage` with OS `prefers-color-scheme` fallback.

3. **Six-Artifact AI Learning Pipeline**:
   - **Artifact 1: Structured Lesson Script** (objectives, definitions, LaTeX formulas, practical code, exam tips).
   - **Artifact 2: Main Lesson Video** (HD lecture stream with speed control [0.75x–1.5x] and progress tracking).
   - **Artifact 3: Summary Video** (concise micro-lecture summarizing key concepts).
   - **Artifact 4: Smart Notes PDF** (genuine ReportLab PDF with headers, page numbers, callout boxes, and exam checklist).
   - **Artifact 5: Smart Notes DOCX** (genuine python-docx Microsoft Word document).
   - **Artifact 6: Section Quiz** (multi-question interactive diagnostic assessment).

4. **Dual AI Operating Mode**:
   - **Mode A (Groq Cloud AI)**: When `GROQ_API_KEY` is provided, calls Groq Llama 3.3 70B for course syllabus creation, quiz synthesis, and student Q&A.
   - **Mode B (Deterministic Local University Demo Engine)**: Automatically activates when no API key is set. Generates rich, curriculum-aligned academic courses, notes, and quiz questions with no external internet or token dependencies.

5. **Personalized Learning & Post-Quiz Diagnostic**:
   - Automatic grading on backend (multiple choice, true/false, fill-in-blank, short answer).
   - Identifies **Weak Concepts** and **Strong Concepts**.
   - Generates an actionable personalized study plan with direct **"Review This Concept"** navigation.
   - Enforces backend attempt limits and passing score thresholds.

6. **Official ReportLab Certificate Generation**:
   - Landscape PDF certificate automatically conferred upon achieving 100% course completion and passing assessments.
   - Includes unique verification ID (`EDUAI-XXXXXXXX`), student name, course title, and academic seal.

---

## 🛠️ Technology Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, React Router v6, Lucide React icons, Recharts, React Hot Toast.
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, SQLite with multi-thread connection pooling.
- **Security**: Direct `bcrypt` password hashing, HS256 JWT bearer token authentication, role-based route guards.
- **Document Rendering**: ReportLab 5.1+ (PDFs & Certificates), python-docx 1.2+ (Word documents).
- **AI Engine**: Groq SDK + Local Subject-Aware Deterministic Curriculum Generator.

---

## 👥 Seeded Demonstration Accounts

EduAI comes pre-seeded with coherent demonstration accounts sharing the password **`password123`**:

| Role | Name | Email Address | Password | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Faculty / Teacher** | Prof. Sarah Jenkins | `teacher@eduai.demo` | `password123` | Curates curricula, inspects 6-artifact pipelines, manages quizzes |
| **Student (Primary)** | Alex Rivera | `student@eduai.demo` | `password123` | Pre-enrolled in Machine Learning (60% complete) with quiz attempt history |
| **Student 2** | Jordan Chen | `student2@eduai.demo` | `password123` | Completed Machine Learning (100%) with conferred certificate |
| **Student 3** | Maya Patel | `student3@eduai.demo` | `password123` | Enrolled learner starting Section 1 |
| **Administrator (Dean)** | Dean Marcus Vance | `admin@eduai.demo` | `password123` | Oversees platform metrics, role promotions, and user directory |

> **Pro Tip**: The Login screen features **One-Click Demo Account Buttons** for instant one-click login during live demonstrations.

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- Node.js 18+ and npm

### 2. Backend Setup
```bash
# Navigate to project root
cd /path/to/GenAI

# Create Python virtual environment
python3 -m venv backend/venv

# Activate virtual environment
source backend/venv/bin/activate  # On macOS/Linux
# .\backend\venv\Scripts\activate   # On Windows

# Install backend dependencies
pip install -r backend/requirements.txt

# (Optional) Seed / Reset Database
PYTHONPATH=backend python backend/app/database/reset.py

# Start FastAPI backend server
PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*The backend API will be available at `http://localhost:8000` with interactive Swagger docs at `http://localhost:8000/docs`.*

### 3. Frontend Setup
```bash
# In a new terminal window:
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```
*The web application will be accessible at `http://localhost:3000`.*

---

## 🧪 Automated Testing

Run the automated backend test suite covering authentication, role-based authorization, course generation, PDF/DOCX downloads, quiz scoring, and admin endpoints:

```bash
PYTHONPATH=backend backend/venv/bin/pytest backend/tests
```

---

## 🤖 Configuring Groq AI API Key (Optional)

EduAI runs locally in **Demo Mode** out of the box with zero external configuration. If you wish to enable live cloud LLM inference:

1. Obtain an API key from [Groq Console](https://console.groq.com/).
2. Open `backend/.env` (or set the environment variable):
   ```env
   GROQ_API_KEY="gsk_your_groq_api_key_here"
   GROQ_MODEL="llama-3.3-70b-versatile"
   ```
3. Restart the backend server. The top navigation bar will update the Engine badge to **`Groq AI (Llama 3.3)`**.

---

## 📋 Comprehensive Demonstration Workflow

### Workflow 1: Teacher Journey
1. Open `http://localhost:3000` and click **"Teacher Demo (Prof. Sarah Jenkins)"**.
2. Switch between **Light Mode** and **Dark Mode** using the sun/moon button in the top navigation bar.
3. On the Faculty Dashboard, review KPI statistics and course enrollment charts.
4. Click **"Generate Course with AI"**, select a preset (e.g. *Autonomous Robotics & Control*), and select **"Generate Full Course & Materials"**.
5. Watch the 4-step progress stepper synthesize the syllabus, lesson text, notes, and quiz.
6. In the **Course Builder**, inspect the **6-Artifact Pipeline**, preview or download the generated **Smart Notes PDF** and **DOCX**, and review the assessment questions.
7. Click **"Publish to Students"** to make the course live in the university catalog.

### Workflow 2: Student Journey
1. Click the profile avatar and select **"Sign Out"**, then click **"Student Demo (Alex Rivera)"**.
2. On the Student Dashboard, review enrolled courses, learning progress, and study streak (5 Days 🔥).
3. Click **"Resume: Introduction to Machine Learning"** to enter the interactive workspace.
4. Read the lesson markdown, switch to the **Video Lecture** tab, and test playback rate controls (1.25x, 1.5x).
5. Switch to the **Smart Notes** tab and click **"Download PDF"** to verify genuine ReportLab document rendering.
6. Open the **Ask Tutor AI** tab, click a prompt pill (e.g. *"Explain this in simple terms"*), and receive an instant, grounded response.
7. Open the **Interactive Quiz** tab, answer the questions, and submit:
   - Observe instant scoring, pass/fail status, question-by-question explanations, and the personalized improvement plan highlighting strong vs. weak concepts.
   - Click **"Review Lesson Concept"** to navigate directly back to the relevant section!
8. Click **"Mark Lesson Completed & Unlock Next"** to unlock the subsequent module.
9. Navigate to **"Earned Certificates"** in the sidebar to view and download the official PDF Certificate.

### Workflow 3: Administrator Journey
1. Log in as **"Administrator Demo (Dean Marcus)"**.
2. Inspect platform metrics, user role distribution chart, and live activity feed.
3. Open **"User Directory"** from the sidebar.
4. Search for students or filter by role.
5. Click **"Change Role"** on an account, select a new role, and confirm the update.
6. Attempt to deactivate your own administrator account to confirm backend safety rules prevent accidental lockouts.

---

## 🗄️ Project Structure

```text
GenAI/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   └── generator.py          # Groq LLM integration & Local Subject-Aware Demo Engine
│   │   ├── api/
│   │   │   ├── admin.py              # User management & system metrics
│   │   │   ├── analytics.py          # Recharts payloads & CSV export
│   │   │   ├── auth.py               # Registration, Login, and Session Me
│   │   │   ├── certificates.py       # Certificate listing & downloads
│   │   │   ├── courses.py            # Course CRUD & AI generator endpoint
│   │   │   ├── deps.py               # Database session & role authorization guards
│   │   │   ├── notifications.py      # In-app notifications
│   │   │   ├── quizzes.py            # Quiz submission, grading & feedback
│   │   │   ├── sections.py           # Sections, artifacts & grounded Q&A chat
│   │   │   └── student.py            # Enrollment & learning progress
│   │   ├── core/
│   │   │   ├── config.py             # App settings & directory initialization
│   │   │   └── security.py           # Bcrypt password hashing & JWT encoding
│   │   ├── database/
│   │   │   ├── init_db.py            # University demo seed generator
│   │   │   ├── reset.py              # CLI database restoration script
│   │   │   └── session.py            # SQLAlchemy SQLite engine
│   │   ├── models/
│   │   │   └── models.py             # 11 SQLAlchemy database entities
│   │   ├── schemas/
│   │   │   └── schemas.py            # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── docx_generator.py     # python-docx Smart Notes generator
│   │   │   └── pdf_generator.py      # ReportLab Smart Notes & Certificates
│   │   └── main.py                   # FastAPI application & router mounting
│   ├── tests/
│   │   └── test_api.py               # Pytest automated test suite
│   ├── requirements.txt              # Pinned Python package dependencies
│   ├── .env.example
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/               # Navbar, Sidebar, ThemeToggle, NotificationDropdown, ProtectedRoute
│   │   ├── contexts/                 # AuthContext & ThemeContext
│   │   ├── layouts/                  # AppLayout
│   │   ├── pages/                    # Login, Register, Teacher, Student, and Admin pages
│   │   ├── services/                 # Typed API client
│   │   ├── types/                    # TypeScript interfaces
│   │   ├── App.tsx                   # Route definitions
│   │   ├── main.tsx
│   │   └── index.css                 # Theme CSS variables & custom scrollbars
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
├── storage/                          # Persistent storage for SQLite, Notes, and Certificates
│   ├── certificates/
│   ├── notes/
│   └── eduai.db
└── README.md
```

---

## 🔒 Security & Data Integrity

- **Password Hashing**: Passwords are encrypted using salted `bcrypt` hashes.
- **Authorization Enforcement**: Endpoints validate JWT claims and enforce role restrictions on the backend.
- **Data Protection**: Students cannot modify curriculum materials, access administrator APIs, or access drafts of unpublished courses.
- **Path Traversal Protection**: Document endpoints strictly sanitize filenames and serve files from designated storage directories.

---

## 📄 Academic License & Acknowledgments

EduAI was developed for college academic curriculum demonstrations and modern higher-education learning environments. Powered by Google Antigravity.
