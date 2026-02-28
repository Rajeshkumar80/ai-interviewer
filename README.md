# 🎯 AI Interviewer — Full Stack Mock Interview Platform

> **An adaptive, AI-powered mock interview platform** that simulates real technical interviews, evaluates answers intelligently, tracks performance analytics, and helps candidates prepare smarter.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running the App](#running-the-app)
- [Pages & Modules](#pages--modules)
- [API Reference](#api-reference)
- [Database Schema](#database-schema)
- [Authentication](#authentication)
- [Interview Flow](#interview-flow)
- [Analytics Dashboard](#analytics-dashboard)
- [Google Sign-In Setup](#google-sign-in-setup)
- [Seeding Demo Data](#seeding-demo-data)
- [Scripts Reference](#scripts-reference)
- [Demo Credentials](#demo-credentials)
- [Screenshots](#screenshots)
- [License](#license)

---

## Overview

**AI Interviewer** is a production-grade, full-stack web application designed to simulate and evaluate technical job interviews. It supports adaptive question generation based on the candidate's selected **domain**, **technologies**, **difficulty level**, and **number of questions**. After each interview session, it provides detailed per-answer feedback (Strong / Average / Weak), a final score, strength areas, and improvement suggestions — all stored persistently in MongoDB.

The platform also includes:
- A timed **Aptitude Test** module
- A personal **Analytics Dashboard** with charts
- **Profile management**
- **Google Sign-In** support
- **Tab-switch detection** with overlay warnings during interviews

---

## Key Features

| Feature | Description |
|---|---|
| 🧠 **Adaptive AI Interview** | Questions generated based on selected domain, tech stack, difficulty & count |
| 🎤 **Voice Answer Support** | Record spoken answers using browser's Web Speech API |
| 💻 **Live Code Editor** | Monaco-based code editor for coding questions |
| 📊 **Analytics Dashboard** | Score trends, performance by topic, difficulty breakdown, interview history |
| 📝 **Aptitude Tests** | Timed multiple-choice aptitude assessments |
| 🔐 **JWT Authentication** | Secure login/register with bcrypt password hashing |
| 🔑 **Google Sign-In** | One-tap Google authentication (OAuth 2.0) |
| 🚨 **Tab-Switch Detection** | Real-time proctoring overlay with 3-strike auto-submit |
| 📈 **Per-Answer Feedback** | Strong / Average / Weak classification + AI remark per question |
| 🌑 **Dark Enterprise UI** | Modern dark theme with emerald accent — glassmorphism panels |
| 📦 **MongoDB Storage** | All users, interviews, answers, evaluations, and analytics persisted |
| 🌱 **Demo Data Seeding** | One-click realistic dataset seeding for testing |

---

## Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| **HTML5** | Semantic page structure |
| **Vanilla CSS** | Custom dark enterprise design system |
| **Vanilla JavaScript** | All interactivity, no framework |
| **Chart.js** | Analytics charts (line, bar, doughnut) |
| **Monaco Editor** | In-browser code editor |
| **Web Speech API** | Voice recording for voice answers |
| **Google GSI SDK** | Google One-Tap / Sign-In button |

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.9+** | Runtime |
| **Flask 2.3** | Web framework & API server |
| **Flask-JWT-Extended** | JWT authentication |
| **Flask-CORS** | Cross-origin request handling |
| **PyMongo 4.5** | MongoDB driver |
| **Werkzeug** | Password hashing (bcrypt) |
| **Google Generative AI** | AI answer evaluation (Gemini) |
| **python-dotenv** | Environment variable loading |

### Database
| Technology | Purpose |
|---|---|
| **MongoDB Atlas** | Cloud-hosted NoSQL database |

---

## Project Structure

```
mini project final/
│
├── 📁 backend/                    # Python Flask API
│   ├── app.py                     # Main application — all routes & logic
│   ├── aptitude_questions.py      # Aptitude question bank (300+ questions)
│   ├── interview_questions.py     # Interview question bank (domain-specific)
│   ├── requirements.txt           # Python dependencies
│   └── .env                       # Environment variables (DO NOT COMMIT)
│
├── 📁 frontend/                   # Static frontend
│   ├── 📁 pages/                  # HTML pages
│   │   ├── index.html             # Login / Register page
│   │   ├── home.html              # Dashboard / Home page
│   │   ├── interview.html         # AI Interview setup & session
│   │   ├── analytics.html         # Performance Analytics
│   │   ├── aptitude.html          # Aptitude test module
│   │   ├── profile.html           # User profile management
│   │   └── settings.html          # App settings & export
│   │
│   ├── 📁 assets/css/             # Stylesheet modules
│   │   ├── theme.css              # Global design tokens & base styles
│   │   ├── layout.css             # Navbar, sidebar, main-content layout
│   │   ├── login.css              # Login/Register page styles
│   │   ├── home.css               # Home/Dashboard styles
│   │   ├── interview.css          # Interview page styles
│   │   ├── result.css             # Results screen styles
│   │   ├── analytics.css          # Analytics dashboard styles
│   │   ├── profile.css            # Profile page styles
│   │   └── settings.css           # Settings page styles
│   │
│   └── 📁 assets/js/              # JavaScript modules
│       ├── login.js               # Auth logic (login, register, Google)
│       ├── home.js                # Dashboard & quick stats
│       ├── interview.js           # Full interview engine
│       ├── analytics.js           # Charts & analytics rendering
│       ├── aptitude.js            # Aptitude test logic (timer, scoring)
│       ├── questions.js           # Question bank utilities
│       ├── profile.js             # Profile CRUD
│       ├── settings.js            # Settings & PDF/CSV export
│       └── navigation.js          # Shared navbar/sidebar logic
│
├── seed_analytics.py              # Database seeder script
├── SETUP.bat                      # One-click setup (Windows)
├── START.bat                      # Start backend server (Windows)
├── STOP.bat                       # Stop backend server (Windows)
├── SEED.bat                       # Run database seeder (Windows)
└── README.md                      # This file
```

---

## Getting Started

### Prerequisites

- **Python 3.9 or higher** — [Download](https://www.python.org/downloads/)  
  ✅ Check "Add Python to PATH" during installation
- **MongoDB Atlas account** — [Free tier](https://www.mongodb.com/cloud/atlas/register)
- **Google Cloud Project** (optional, for Google Sign-In) — [Console](https://console.cloud.google.com)
- A modern web browser (Chrome, Edge, Firefox)

---

### Installation

**Option A — Automatic (Windows):**
```batch
# Double-click SETUP.bat
# This will: create venv → install requirements → verify MongoDB
SETUP.bat
```

**Option B — Manual:**
```bash
# 1. Navigate to the backend folder
cd "mini project final/backend"

# 2. Create a virtual environment
python -m venv ../.venv

# 3. Activate the virtual environment
# Windows:
../.venv/Scripts/activate
# macOS/Linux:
source ../.venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

---

### Environment Variables

Create or edit `backend/.env` with the following values:

```env
# ── Flask ──────────────────────────────────────────────────
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-random-secret-key-here

# ── MongoDB ────────────────────────────────────────────────
# Get this from MongoDB Atlas → Connect → Drivers
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/ai_interviewer?retryWrites=true&w=majority
MONGO_DB_NAME=ai_interviewer

# ── JWT ────────────────────────────────────────────────────
JWT_SECRET=your-long-random-jwt-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# ── Google OAuth (optional — for Google Sign-In) ───────────
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# ── AI (Gemini) ────────────────────────────────────────────
# Get from: https://makersuite.google.com/app/apikey
OPENAI_API_KEY=your-gemini-api-key
```

> ⚠️ **Never commit `.env` to git.** It contains secrets and database credentials.

---

### Running the App

**Windows — One Click:**
```batch
START.bat
```

**Manual:**
```bash
# From the backend/ directory with venv activated:
cd "mini project final/backend"
python app.py
```

The app will be available at:
```
http://localhost:5000
```

The Flask server serves **both** the API (`/api/*`) and the frontend pages (`/pages/*`) from a single port.

---

## Pages & Modules

| Page | URL | Description |
|---|---|---|
| **Login / Register** | `/pages/index.html` | Email + password auth, Google Sign-In |
| **Home** | `/pages/home.html` | Welcome dashboard, quick-start cards |
| **Interview** | `/pages/interview.html` | Full AI interview setup & session |
| **Analytics** | `/pages/analytics.html` | Score trends, charts, interview history |
| **Aptitude Test** | `/pages/aptitude.html` | Timed MCQ aptitude test |
| **Profile** | `/pages/profile.html` | Edit name, role, skills, avatar |
| **Settings** | `/pages/settings.html` | Preferences, export data (PDF/CSV) |

---

## API Reference

All API endpoints are prefixed with `/api/`.

### Authentication

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register` | Create new account | ❌ |
| `POST` | `/api/auth/login` | Email/password login | ❌ |
| `POST` | `/api/auth/google` | Google OAuth login | ❌ |
| `POST` | `/api/auth/logout` | Invalidate session | ✅ JWT |
| `GET` | `/api/auth/me` | Get current user profile | ✅ JWT |

### Interview

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/interview/start` | Start interview session | ✅ JWT |
| `POST` | `/api/interview/<session_id>/answer` | Submit an answer | ✅ JWT |
| `GET` | `/api/interview/<session_id>/results` | Get session results | ✅ JWT |
| `GET` | `/api/interview/history` | List past interviews | ✅ JWT |

#### Start Interview — Request Body
```json
{
  "role": "Frontend Developer",
  "domain": "frontend",
  "tech_stack": ["React", "JavaScript", "CSS"],
  "difficulty": "medium",
  "num_questions": 5,
  "question_types": ["coding", "behavioral"],
  "mode": "practice"
}
```

### Analytics

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/analytics/overview` | Score stats, strengths, weaknesses | ✅ JWT |
| `GET` | `/api/analytics/attempts` | Paginated attempt history | ✅ JWT |
| `POST` | `/api/analytics/store` | Save completed attempt | ✅ JWT |

### Aptitude

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/aptitude/questions` | Get question set | ✅ JWT |
| `POST` | `/api/aptitude/submit` | Submit test & get score | ✅ JWT |

### User / Profile

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/user/profile` | Get profile data | ✅ JWT |
| `PUT` | `/api/user/profile` | Update profile | ✅ JWT |

### Health & Debug

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Backend health check |
| `GET` | `/api/internal/debug` | MongoDB connection info & collection counts |
| `POST` | `/api/internal/seed` | Seed demo analytics data |

---

## Database Schema

### `users` Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string (unique)",
  "password": "string (bcrypt hash, absent for Google users)",
  "picture": "string (URL)",
  "login_method": "email | google",
  "roles": ["user"],
  "created_at": "datetime",
  "last_login": "datetime"
}
```

### `interviews` Collection
```json
{
  "_id": "ObjectId",
  "session_id": "string",
  "user_email": "string",
  "config": {
    "role": "string",
    "domain": "frontend | backend | fullstack | language",
    "tech_stack": ["string"],
    "difficulty": "easy | medium | hard",
    "num_questions": "number",
    "question_types": ["coding", "behavioral", "system_design"],
    "mode": "practice | exam"
  },
  "questions": [{ "id": "string", "text": "string", "type": "string" }],
  "answers": [{
    "question_id": "string",
    "answer_text": "string",
    "evaluation": {
      "score": 0-100,
      "is_correct": "boolean",
      "remark": "string",
      "strengths": ["string"],
      "weaknesses": ["string"]
    }
  }],
  "status": "in_progress | completed",
  "started_at": "datetime",
  "completed_at": "datetime"
}
```

### `attempts` Collection
```json
{
  "_id": "ObjectId",
  "user_email": "string",
  "session_id": "string",
  "role": "string",
  "score": "number (0-100)",
  "difficulty": "string",
  "tech_stack": ["string"],
  "question_count": "number",
  "timestamp": "datetime"
}
```

### `aptitude_results` Collection
```json
{
  "_id": "ObjectId",
  "user_email": "string",
  "score": "number",
  "total": "number",
  "percentage": "number",
  "topic": "string",
  "timestamp": "datetime"
}
```

---

## Authentication

The app uses **JWT (JSON Web Tokens)** for session management.

**Flow:**
1. User logs in → Backend returns `access_token`
2. Token stored in `localStorage`
3. All protected API calls include `Authorization: Bearer <token>`
4. Token expires after 60 minutes (configurable via `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`)

**Password Security:**
- Passwords hashed with **bcrypt** via Werkzeug's `generate_password_hash`
- Plaintext passwords never stored

---

## Interview Flow

```
1. User configures interview:
   └── Role → Domain → Technologies → Difficulty → # Questions → Types

2. Backend generates targeted questions:
   └── Strictly scoped to selected domain + tech stack + difficulty

3. Interview session begins:
   └── One question at a time
   └── Timer per question
   └── Tab-switch detection (3 warnings → auto-submit)

4. User answers each question:
   └── Text answer  (behavioral/theory)
   └── Code editor  (coding questions)
   └── Voice input  (spoken answers via Web Speech API)

5. Each answer is evaluated:
   └── AI scores it 0-100
   └── Classifies as Strong (≥75) / Average (≥50) / Weak (<50)
   └── Provides a remark

6. Final Results screen:
   └── Overall score %, performance rating
   └── Strong / Average / Weak answer counts
   └── Strength Areas & Areas for Improvement
   └── Per-question review with reference answers

7. Session saved to MongoDB
8. Analytics dashboard updated
```

---

## Analytics Dashboard

The Analytics page renders **4 Chart.js visualisations**:

| Chart | Type | Description |
|---|---|---|
| Score Trend | Line chart | Score progression over time |
| Performance by Topic | Bar chart | Score per technology/topic |
| Time per Question | Bar chart | Average time spent per Q |
| Difficulty Breakdown | Doughnut | Distribution: Easy / Medium / Hard |

**Stats cards** display:
- Total Interviews
- Average Score
- Best Score
- Total Questions Answered

---

## Google Sign-In Setup

To enable Google Sign-In:

### Step 1 — Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Navigate to **APIs & Services → Credentials**
4. Click **Create Credentials → OAuth 2.0 Client ID**
5. Select **Web application**
6. Add Authorized JavaScript origins:
   ```
   http://localhost:5000
   http://127.0.0.1:5000
   ```
7. Copy the **Client ID**

### Step 2 — Add to `.env`
```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

### Step 3 — Add to `login.js`
```javascript
var GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com";
```

### Step 4 — Add to `index.html`
In the `g_id_onload` div:
```html
data-client_id="your-client-id.apps.googleusercontent.com"
```

✅ After this, the "Continue with Google" button becomes active.

---

## Seeding Demo Data

To populate the database with realistic interview history and analytics:

**Windows:**
```batch
SEED.bat
```

**Manual:**
```bash
cd "mini project final/backend"
python -c "
import requests
r = requests.post('http://localhost:5000/api/internal/seed')
print(r.json())
"
```

Or simply visit: `http://localhost:5000/api/internal/seed` (POST request)

This seeds:
- 5 demo users
- 41 interview sessions with evaluated answers
- 14 analytics attempts
- 12 aptitude results

---

## Scripts Reference

| Script | Description |
|---|---|
| `SETUP.bat` | First-time setup: creates venv, installs pip packages, verifies MongoDB |
| `START.bat` | Starts the Flask backend server on port 5000 |
| `STOP.bat` | Kills the running Flask server process |
| `SEED.bat` | Seeds demo data into MongoDB |

---

## Demo Credentials

Use these to log in without creating an account:

| Field | Value |
|---|---|
| **Email** | `demo@aiinterviewer.com` |
| **Password** | `Demo1234!` |

The demo account is auto-created in MongoDB on first login.

---

## Design System

The UI uses a **Dark Enterprise Design System** with the following tokens:

| Token | Value | Usage |
|---|---|---|
| Background | `#171A21` | Page background |
| Panel Surface | `#0D0F14` | Cards, sidebar, navbar |
| Primary Accent | `#059669` | Buttons, active states, highlights |
| Text Primary | `#D1D5DB` | Main text |
| Text Secondary | `rgba(209,213,219,0.65)` | Labels, descriptions |
| Border | `rgba(5,150,105,0.15)` | Panel borders |
| Glow | `rgba(5,150,105,0.25)` | Active button glow, focus rings |

**Effects:**
- Glassmorphism panels: `backdrop-filter: blur(10px)`  
- Soft emerald glow on hover/active: `box-shadow: 0 0 10px rgba(5,150,105,0.25)`
- Smooth transitions: `300ms cubic-bezier(0.4, 0, 0.2, 1)`

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `Python is not installed` | Install Python 3.9+ and check "Add to PATH" |
| `Cannot connect to MongoDB` | Check `MONGO_URI` in `.env`; ensure Atlas IP whitelist includes your IP |
| `Backend not running on port 5000` | Run `START.bat` or `python app.py` from `/backend` |
| `Google Sign-In button not working` | Add your real `GOOGLE_CLIENT_ID` to `.env`, `login.js`, and `index.html` |
| `No analytics data visible` | Run `SEED.bat` to populate demo data |
| `Interview questions not loading` | Check backend is running; verify `OPENAI_API_KEY` (Gemini key) in `.env` |
| `JWT token expired` | Log out and log back in; token validity is 60 minutes |

---

## License

This project was built as a **Mini Project** for academic purposes.

> Built with ❤️ using Python, Flask, MongoDB, and Vanilla JavaScript.
