# How to Run AI Interviewer

This guide shows you how to run both the frontend and backend servers.

## Prerequisites

- **Python 3.8+** installed
- **pip** (Python package manager)

## Quick Start (Windows)

### Option 1: Using Batch Scripts (Easiest)

1. **Open Two Terminal Windows**

2. **Terminal 1 - Backend:**
   ```bash
   run-backend.bat
   ```
   Or double-click `run-backend.bat`

3. **Terminal 2 - Frontend:**
   ```bash
   run-frontend.bat
   ```
   Or double-click `run-frontend.bat`

### Option 2: Manual Commands

#### Terminal 1 - Backend Server

```bash
cd backend
pip install Flask flask-cors
python app.py
```

The backend will start on: **http://localhost:5000**

#### Terminal 2 - Frontend Server

```bash
cd frontend
python -m http.server 8000
```

The frontend will start on: **http://localhost:8000**

Then open in your browser: **http://localhost:8000/pages/index.html**

---

## Quick Start (Mac/Linux)

### Option 1: Using Shell Scripts

1. **Make scripts executable:**
   ```bash
   chmod +x run-backend.sh run-frontend.sh
   ```

2. **Open Two Terminal Windows**

3. **Terminal 1 - Backend:**
   ```bash
   ./run-backend.sh
   ```

4. **Terminal 2 - Frontend:**
   ```bash
   ./run-frontend.sh
   ```

### Option 2: Manual Commands

#### Terminal 1 - Backend Server

```bash
cd backend
pip3 install Flask flask-cors
python3 app.py
```

The backend will start on: **http://localhost:5000**

#### Terminal 2 - Frontend Server

```bash
cd frontend
python3 -m http.server 8000
```

The frontend will start on: **http://localhost:8000**

Then open in your browser: **http://localhost:8000/pages/index.html**

---

## Step-by-Step Instructions

### Step 1: Install Backend Dependencies

Open a terminal in the project root and run:

**Windows:**
```bash
cd backend
pip install Flask flask-cors
```

**Mac/Linux:**
```bash
cd backend
pip3 install Flask flask-cors
```

### Step 2: Start Backend Server

**Windows:**
```bash
cd backend
python app.py
```

**Mac/Linux:**
```bash
cd backend
python3 app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
 * Running on http://127.0.0.1:5000
```

**Keep this terminal window open!**

### Step 3: Start Frontend Server (New Terminal)

Open a **new terminal window** (keep the backend terminal running).

**Windows:**
```bash
cd frontend
python -m http.server 8000
```

**Mac/Linux:**
```bash
cd frontend
python3 -m http.server 8000
```

You should see:
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

**Keep this terminal window open too!**

### Step 4: Open in Browser

Open your web browser and navigate to:

**http://localhost:8000/pages/index.html**

Or start from:
- **Home:** http://localhost:8000/pages/home.html
- **Interview:** http://localhost:8000/pages/interview.html
- **Aptitude:** http://localhost:8000/pages/aptitude.html
- **Analytics:** http://localhost:8000/pages/analytics.html
- **Profile:** http://localhost:8000/pages/profile.html
- **Settings:** http://localhost:8000/pages/settings.html

---

## Using Both Servers

You need **TWO terminal windows** running simultaneously:

```
Terminal 1 (Backend)          Terminal 2 (Frontend)
┌─────────────────────┐      ┌─────────────────────┐
│ cd backend          │      │ cd frontend         │
│ python app.py       │      │ python -m http.server│
│                     │      │       8000          │
│ * Running on :5000  │      │ Serving on :8000    │
└─────────────────────┘      └─────────────────────┘
```

---

## Troubleshooting

### Port Already in Use

If you see "Port already in use":

**For Backend (port 5000):**
- Kill the process: `netstat -ano | findstr :5000` (Windows) or `lsof -ti:5000 | xargs kill` (Mac/Linux)
- Or change port in `backend/app.py`: `app.run(debug=True, port=5001, host='0.0.0.0')`

**For Frontend (port 8000):**
- Use a different port: `python -m http.server 8001`
- Update API URLs in frontend JS files if backend port changes

### Module Not Found

If you see "ModuleNotFoundError":
```bash
pip install --upgrade pip
pip install Flask flask-cors
```

### CORS Errors

If you see CORS errors in the browser console, make sure:
1. Backend is running on port 5000
2. Frontend is running on port 8000
3. The Flask app has `CORS(app)` configured (already in `app.py`)

### API Not Working

Check:
1. Backend is running: Visit http://localhost:5000/api/start-interview (should return error, not "can't connect")
2. Frontend JavaScript console for errors
3. Network tab in browser DevTools to see API calls

---

## Development Tips

### Auto-reload Backend

Flask is already in debug mode (`debug=True`), so it will auto-reload on code changes.

### Check if Servers are Running

**Backend:**
```bash
curl http://localhost:5000/api/start-interview
```

**Frontend:**
Just open http://localhost:8000/pages/index.html in your browser

### Stop Servers

Press **Ctrl+C** in each terminal window to stop the servers.

---

## Alternative: Using Flask-CLI (Advanced)

If you have Flask installed globally:

**Backend:**
```bash
cd backend
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --port=5000
```

---

## Need Help?

1. Check both terminals are running
2. Check ports are correct (5000 for backend, 8000 for frontend)
3. Check browser console for errors (F12 → Console tab)
4. Make sure you're accessing `http://localhost:8000/pages/index.html` (not `file://`)

Happy coding! 🚀

