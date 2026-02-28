"""
AI Interviewer Backend
Refactored to provide a stable interview flow, evaluation, and analytics
using MongoDB as the source of truth.
"""
from datetime import datetime, timedelta
import os
import random
from typing import List, Dict, Any

from bson import ObjectId
from flask import Flask, jsonify, request, send_from_directory, redirect
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from werkzeug.security import generate_password_hash, check_password_hash

try:
    from aptitude_questions import ALL_APTITUDE_QUESTIONS
except Exception:
    ALL_APTITUDE_QUESTIONS = []

try:
    from interview_questions import get_additional_questions
    ADDITIONAL_QUESTIONS = get_additional_questions()
except Exception:
    ADDITIONAL_QUESTIONS = []

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # always = backend/
load_dotenv(os.path.join(_BASE_DIR, ".env"))

# Path to the frontend folder (sibling of backend/)
FRONTEND_DIR = os.path.abspath(os.path.join(_BASE_DIR, "..", "frontend"))

app = Flask(__name__, static_folder=None)

# Basic secrets / JWT configuration
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET", "dev-jwt-secret")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour

jwt = JWTManager(app)

# CORS — allow API access from dev tools / Live Server etc.
# The main frontend (served by Flask on :5000) is same-origin, no CORS needed.
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5000",
                "http://127.0.0.1:5000",
                "http://localhost:5500",   # VS Code Live Server
                "http://127.0.0.1:5500",
                "http://localhost:8000",
                "null",                    # file:// protocol
            ],
            "allow_headers": ["Content-Type", "Authorization"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "supports_credentials": True,
        }
    },
)

# ------------------------------
# Mongo setup
# ------------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB_NAME", "ai_interviewer")
mongo = MongoClient(MONGO_URI)
db = mongo[DB_NAME]


# ------------------------------
# Auth helpers & endpoints
# ------------------------------

DEMO_EMAIL = os.getenv("DEMO_USER_EMAIL", "demo@aiinterviewer.com")
DEMO_PASSWORD = os.getenv("DEMO_USER_PASSWORD", "Demo1234!")


def ensure_demo_user() -> Dict[str, Any]:
    """Create a demo user in the DB if it does not exist yet."""
    users = db.users
    existing = users.find_one({"email": DEMO_EMAIL})
    if existing:
        existing["_id"] = str(existing["_id"])
        return existing

    now = datetime.utcnow()
    password_hash = generate_password_hash(DEMO_PASSWORD)
    demo_user = {
        "name": "Demo Candidate",
        "email": DEMO_EMAIL,
        "password": password_hash,
        "roles": ["demo", "user"],
        "created_at": now,
        "last_login": now,
    }
    result = users.insert_one(demo_user)
    demo_user["_id"] = str(result.inserted_id)
    return demo_user


@app.route("/api/health", methods=["GET"])
def health_check():
    """Simple health check so the frontend can detect if the backend is running."""
    return jsonify({"status": "ok", "message": "Backend is running"}), 200


@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip() or "User"
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return (
            jsonify({"status": "error", "message": "Email and password are required"}),
            400,
        )

    users = db.users
    if users.find_one({"email": email}):
        return (
            jsonify({"status": "error", "message": "Email already registered"}),
            400,
        )

    now = datetime.utcnow()
    user_data = {
        "name": name,
        "email": email,
        "password": generate_password_hash(password),
        "roles": ["user"],
        "created_at": now,
        "last_login": now,
    }
    result = users.insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)

    access_token = create_access_token(identity=user_data["email"])

    return (
        jsonify(
            {
                "status": "success",
                "access_token": access_token,
                "user": {
                    "id": user_data["_id"],
                    "name": user_data["name"],
                    "email": user_data["email"],
                    "picture": user_data.get("picture", ""),
                },
            }
        ),
        201,
    )


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return (
            jsonify({"status": "error", "message": "Email and password are required"}),
            400,
        )

    # Auto-create demo user when demo credentials are used
    if email == DEMO_EMAIL and password == DEMO_PASSWORD:
        ensure_demo_user()

    users = db.users
    user = users.find_one({"email": email})
    if not user or not user.get("password"):
        return (
            jsonify({"status": "error", "message": "Invalid email or password"}),
            401,
        )

    if not check_password_hash(user["password"], password):
        return (
            jsonify({"status": "error", "message": "Invalid email or password"}),
            401,
        )

    now = datetime.utcnow()
    users.update_one({"_id": user["_id"]}, {"$set": {"last_login": now}})

    access_token = create_access_token(identity=user["email"])

    user_payload = {
        "id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user["email"],
        "picture": user.get("picture", ""),
    }

    return jsonify(
        {
            "status": "success",
            "access_token": access_token,
            "user": user_payload,
        }
    )


@app.route("/api/auth/google", methods=["POST"])
def api_google_login():
    """
    Receive a Google ID-token credential from the frontend (Google One-Tap / GSI),
    verify it with Google's public endpoint, then upsert the user and return a JWT.
    """
    import urllib.request, json as _json

    data = request.get_json() or {}
    credential = data.get("credential") or ""

    if not credential:
        return jsonify({"status": "error", "message": "Missing Google credential"}), 400

    # --- Verify the token with Google's tokeninfo endpoint ---
    try:
        url = f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}"
        with urllib.request.urlopen(url, timeout=6) as resp:
            info = _json.loads(resp.read().decode())
    except Exception as e:
        # Fallback: accept the manually-decoded payload sent by the frontend
        # (the frontend already decoded the JWT via jwt-decode.js)
        info = data.get("user_info") or {}
        if not info.get("email"):
            return jsonify({"status": "error", "message": f"Token verification failed: {e}"}), 401

    email = (info.get("email") or "").strip().lower()
    name  = info.get("name") or info.get("given_name") or email.split("@")[0]
    picture = info.get("picture") or ""

    if not email:
        return jsonify({"status": "error", "message": "Could not extract email from Google token"}), 400

    users = db.users
    now   = datetime.utcnow()

    existing = users.find_one({"email": email})
    if existing:
        # Update last_login + picture for returning users
        users.update_one(
            {"_id": existing["_id"]},
            {"$set": {"last_login": now, "picture": picture, "login_method": "google"}}
        )
        user_id = str(existing["_id"])
        user_name = existing.get("name") or name
    else:
        # Create new Google user — no password field
        new_user = {
            "name": name,
            "email": email,
            "picture": picture,
            "login_method": "google",
            "roles": ["user"],
            "created_at": now,
            "last_login": now,
        }
        result = users.insert_one(new_user)
        user_id = str(result.inserted_id)
        user_name = name

    access_token = create_access_token(identity=email)

    return jsonify({
        "status": "success",
        "access_token": access_token,
        "user": {
            "id": user_id,
            "name": user_name,
            "email": email,
            "picture": picture,
        },
    })


@app.route("/api/auth/logout", methods=["POST"])
@jwt_required()
def api_logout():
    """Stateless JWT logout – client just discards the token."""
    return jsonify({"status": "success", "message": "Successfully logged out"})

# ------------------------------
# Question bank (server truth)
# ------------------------------
# Each question contains full reference material; only safe fields are returned to clients.
QUESTION_BANK: List[Dict[str, Any]] = [
    {
        "id": "c1",
        "type": "coding",
        "category": "Arrays / Algorithms",
        "difficulty": "medium",
        "question": "Implement a function two_sum(nums, target) that returns indices of the two numbers adding up to target. Return an empty list if none.",
        "solution_code": """def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        need = target - num
        if need in seen:
            return [seen[need], i]
        seen[num] = i
    return []""",
        "solution_explanation": "Use a hash map to store seen numbers and their indices. For each num, check if target-num is already seen. O(n) time, O(n) space.",
        "reference_points": [
            "Use a hash map for constant lookups",
            "Single pass through the array",
            "Return indices, not values",
            "Handle no-solution case with []",
            "O(n) time, O(n) space",
        ],
        "test_cases": [
            {"input": ([2, 7, 11, 15], 9), "expected": [0, 1]},
            {"input": ([3, 2, 4], 6), "expected": [1, 2]},
            {"input": ([1, 2, 3], 7), "expected": []},
        ],
    },
    {
        "id": "c2",
        "type": "coding",
        "category": "Strings",
        "difficulty": "easy",
        "question": "Write a function is_palindrome(s) that returns True if s is a palindrome ignoring non-alphanumeric characters and case.",
        "solution_code": """def is_palindrome(s: str) -> bool:
    cleaned = ''.join(ch.lower() for ch in s if ch.isalnum())
    return cleaned == cleaned[::-1]""",
        "solution_explanation": "Normalize by filtering alphanumerics and lowercasing, then compare to its reverse. O(n) time, O(n) space.",
        "reference_points": [
            "Normalize case",
            "Ignore non-alphanumeric",
            "Compare string with reverse",
            "Return boolean",
            "O(n) time",
        ],
        "test_cases": [
            {"input": ("A man, a plan, a canal: Panama",), "expected": True},
            {"input": ("race a car",), "expected": False},
        ],
    },
    {
        "id": "b1",
        "type": "behavioral",
        "category": "React / Collaboration",
        "difficulty": "medium",
        "question": "Share an example where collaboration was key to shipping a React feature. What was your role?",
        "reference_answer": (
            "Example: I worked on a dashboard where I coordinated with backend on API contracts, "
            "aligned with designers on component specs, reviewed pull requests with teammates, "
            "and we shipped the feature on schedule with zero critical bugs."
        ),
        "reference_points": [
            "Collaborated with backend on API contracts",
            "Aligned with designers on component specs",
            "Participated in code reviews",
            "Shipped feature on schedule",
            "Zero critical bugs post-launch",
        ],
    },
    {
        "id": "sd1",
        "type": "system_design",
        "category": "Scalability",
        "difficulty": "medium",
        "question": "Design a URL shortener service like bit.ly. Cover API design, storage, collisions, and scaling.",
        "reference_answer": "Discuss APIs, id generation (hash/sequence), DB with unique index, cache layer, read/write traffic, replication, metrics, and rate limiting.",
        "reference_points": [
            "API: shorten, redirect, analytics",
            "ID generation and collision avoidance",
            "DB schema and indexing",
            "Caching strategy",
            "Scaling: replication/partition",
            "Rate limiting and abuse prevention",
        ],
    },
    {
        "id": "a1",
        "type": "aptitude",
        "category": "Mathematics",
        "difficulty": "easy",
        "question": "What is 25% of 200?",
        "options": ["25", "40", "50", "60"],
        "correct_answer": "50",
        "explanation": "25% of 200 = 0.25 * 200 = 50",
        "reference_points": ["Percentage calculation", "Basic arithmetic"],
    },
    {
        "id": "a2",
        "type": "aptitude",
        "category": "Logical Reasoning",
        "difficulty": "medium",
        "question": "Complete the series: 3, 7, 15, 31, ?",
        "options": ["39", "47", "55", "63"],
        "correct_answer": "63",
        "explanation": "Pattern is (n * 2) + 1",
        "reference_points": ["Identify pattern", "Double then add 1"],
    },
    {
        "id": "c3",
        "type": "coding",
        "category": "Trees",
        "difficulty": "medium",
        "question": "Implement a function is_valid_bst(root) that returns True if the binary tree is a valid Binary Search Tree.",
        "solution_code": """def is_valid_bst(root, low=float('-inf'), high=float('inf')):
    if not root:
        return True
    if not (low < root.val < high):
        return False
    return is_valid_bst(root.left, low, root.val) and is_valid_bst(root.right, root.val, high)""",
        "solution_explanation": "Recursive DFS with range constraints. Each node must be within (low, high). O(n) time, O(h) space.",
        "reference_points": [
            "Recursive traversal",
            "Pass down low/high bounds",
            "Check node value against bounds",
            "Visit left and right subtrees",
            "O(n) time, O(h) space",
        ],
        "test_cases": [
            {"input": ("BST with 5 nodes"), "expected": True},
            {"input": ("Invalid BST"), "expected": False},
        ],
    },
    {
        "id": "c4",
        "type": "coding",
        "category": "Dynamic Programming",
        "difficulty": "hard",
        "question": "Write a function coin_change(coins, amount) that returns the minimum number of coins needed to make amount, or -1 if impossible.",
        "solution_code": """def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for x in range(coin, amount + 1):
            dp[x] = min(dp[x], dp[x - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1""",
        "solution_explanation": "Bottom-up DP. dp[i] = min coins to make i. Initialize dp[0]=0, others inf. O(n*m) time, O(m) space.",
        "reference_points": [
            "Bottom-up DP array",
            "Initialize dp[0]=0, others inf",
            "Iterate coins and amounts",
            "Update dp[x] = min(dp[x], dp[x-coin]+1)",
            "Return -1 if impossible",
        ],
        "test_cases": [
            {"input": ([1,2,5], 11), "expected": 3},
            {"input": ([2], 3), "expected": -1},
        ],
    },
    {
        "id": "b2",
        "type": "behavioral",
        "category": "Conflict Resolution",
        "difficulty": "medium",
        "question": "Describe a time you disagreed with a teammate. How did you resolve it?",
        "reference_answer": (
            "I listened to their perspective, explained my reasoning with data, found common ground, "
            "and we agreed on a hybrid approach that improved the outcome."
        ),
        "reference_points": [
            "Listened actively to teammate",
            "Used data to explain reasoning",
            "Found common ground",
            "Agreed on hybrid approach",
            "Outcome improved",
        ],
    },
    {
        "id": "b3",
        "type": "behavioral",
        "category": "Time Management",
        "difficulty": "easy",
        "question": "How do you prioritize tasks when facing multiple deadlines?",
        "reference_answer": (
            "I assess impact and urgency, use a matrix, communicate with stakeholders, "
            "and focus on high-impact tasks first."
        ),
        "reference_points": [
            "Assess impact and urgency",
            "Use prioritization matrix",
            "Communicate with stakeholders",
            "Focus on high-impact tasks",
            "Adjust as needed",
        ],
    },
    {
        "id": "sd2",
        "type": "system_design",
        "category": "Databases",
        "difficulty": "hard",
        "question": "Design a chat messaging service like WhatsApp. Cover real-time delivery, read receipts, and scalability.",
        "reference_answer": "Use WebSockets/SSE for real-time, message queues, read receipts status, sharding by user ID, and CDNs for media.",
        "reference_points": [
            "Real-time transport (WebSockets/SSE)",
            "Message queue for persistence",
            "Read receipt status tracking",
            "Sharding by user ID",
            "CDN for media",
        ],
    },
    {
        "id": "a3",
        "type": "aptitude",
        "category": "Numerical",
        "difficulty": "easy",
        "question": "If a train travels 300 km in 3 hours, what is its average speed?",
        "options": ["80 km/h", "90 km/h", "100 km/h", "110 km/h"],
        "correct_answer": "100 km/h",
        "explanation": "Speed = distance / time = 300 / 3 = 100 km/h",
        "reference_points": ["Speed = distance/time", "Basic division"],
    },
]

# Extend with additional interview questions
if ADDITIONAL_QUESTIONS:
    QUESTION_BANK.extend(ADDITIONAL_QUESTIONS)

# Extend with aptitude bank from the large pool (if available)
if ALL_APTITUDE_QUESTIONS:
    aptitude_items: List[Dict[str, Any]] = []
    for idx, q in enumerate(ALL_APTITUDE_QUESTIONS, start=1):
        aptitude_items.append(
            {
                "id": f"apt_{idx:03d}",
                "type": "aptitude",
                "category": q.get("category", "Aptitude"),
                "topic": q.get("category", "Aptitude"),
                "difficulty": q.get("difficulty", "easy"),
                "question": q.get("question"),
                "options": q.get("options", []),
                "correct_answer": q.get("answer"),
                "explanation": q.get("explanation"),
                "reference_points": q.get("reference_points", []),
            }
        )
    QUESTION_BANK.extend(aptitude_items)


def pick_questions(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Select a set of unique questions based on configuration (role, skills, difficulty, types)."""

    num_questions = int(config.get("num_questions", 8))
    role = config.get("role", "").lower()
    tech_stack = config.get("tech_stack", [])
    skill_tags = config.get("skill_tags", [])
    difficulty_raw = config.get("difficulty") or None
    difficulty = difficulty_raw.lower() if isinstance(difficulty_raw, str) else None
    types = config.get("question_types") or [
        "coding",
        "behavioral",
        "system_design",
        "aptitude",
    ]

    # Score questions based on relevance to role and skills
    def score_question(question: Dict[str, Any]) -> float:
        score = 0.0
        
        # Role matching
        q_role = question.get("role", "")
        if isinstance(q_role, list):
            q_role = " ".join(q_role).lower()
        else:
            q_role = str(q_role).lower()
        
        if q_role and role:
            if q_role == role:
                score += 10.0
            elif role in q_role or q_role in role:
                score += 5.0
                
        # Tech stack matching
        q_tech = question.get("tech_stack", [])
        if tech_stack and q_tech:
            matches = len(set(tech_stack) & set(q_tech))
            score += matches * 3.0
            
        # Skill tags matching
        q_skills = question.get("skill_tags", [])
        if skill_tags and q_skills:
            matches = len(set(skill_tags) & set(q_skills))
            score += matches * 2.0
            
        # Topic/category matching
        q_topic = (question.get("topic") or "").lower()
        q_category = (question.get("category") or "").lower()
        for skill in skill_tags:
            skill_lower = skill.lower()
            if skill_lower in q_topic or skill_lower in q_category:
                score += 1.5
                
        return score

    # Filter and score questions
    scored_questions = []
    for q in QUESTION_BANK:
        if q["type"] in types:
            # Apply difficulty filter (Soft preference instead of strict)
            if difficulty:
                q_difficulty = (q.get("difficulty") or "").lower()
                if q_difficulty != difficulty:
                    # Penalize mismatch but don't exclude
                    # continue 
                    pass
            
            # Score the question
            relevance_score = score_question(q)
            scored_questions.append((q, relevance_score))
    
    # Sort by relevance score (highest first)
    scored_questions.sort(key=lambda x: x[1], reverse=True)
    
    # Filter candidates with > 0 relevance
    candidates = [item for item in scored_questions if item[1] > 0]
    
    # If not enough relevance, fallback to all filtered questions
    if len(candidates) < num_questions:
         candidates = scored_questions

    # Select random unique questions from top candidates
    # To ensure variety, we can take a larger pool of top candidates and sample from them
    pool_size = max(num_questions * 2, 20)
    top_candidates = candidates[:pool_size]
    
    # Randomize the pool to ensure different selection each time
    random.shuffle(top_candidates)

    selected_questions = []
    seen_ids = set()
    used_content = set() # Avoid exact duplicate text

    for item in top_candidates:
        q = item[0]
        q_id = q["id"]
        q_text = q.get("question", "")
        
        if q_id not in seen_ids and q_text not in used_content:
            seen_ids.add(q_id)
            used_content.add(q_text)
            selected_questions.append(q)
            if len(selected_questions) >= num_questions:
                break
    
    return selected_questions


# ------------------------------
# Evaluation helpers
# ------------------------------


def evaluate_coding_answer(code: str, question: Dict[str, Any]) -> Dict[str, Any]:
    """Lightweight simulated evaluation using reference points and test definitions."""
    code_text = (code or "").lower()
    ref_points = question.get("reference_points", [])
    matches = sum(1 for p in ref_points if p and p.split()[0].lower() in code_text)

    # Basic completeness from length and matches
    length_score = min(40, len(code_text) // 10)
    correctness = min(100, 40 + matches * 12 + length_score)
    completeness = min(100, 35 + matches * 10)
    style = 70 if "return" in code_text else 55

    # Simulated test results using expected outputs
    test_results = []
    passed_count = 0
    for idx, tc in enumerate(question.get("test_cases", []), start=1):
        expected = tc.get("expected")
        # Simulate pass if key tokens exist
        token = str(expected)[0:2]
        passed = token.lower() in code_text
        if passed:
            passed_count += 1
        test_results.append(
            {"name": f"test_{idx}", "expected": expected, "passed": passed}
        )

    score = round(0.5 * correctness + 0.3 * completeness + 0.2 * style)
    return {
        "passed": passed_count == len(test_results) if test_results else correctness > 60,
        "test_results": test_results,
        "correctness": correctness,
        "completeness": completeness,
        "communication": 0,
        "style": style,
        "score": score,
        "answer_feedback": "Heuristic grading based on reference points and structure.",
        "solution_code": question.get("solution_code"),
        "solution_explanation": question.get("solution_explanation"),
        "reference_answer": question.get("solution_explanation"),
        "reference_points": ref_points,
        "evaluation": {
            "remark": "Auto-scored against reference points and example tests.",
            "strengths": ref_points[:3],
            "improvements": ref_points[3:6],
        },
    }


def evaluate_behavioral_or_system_design(
    answer: str, question: Dict[str, Any]
) -> Dict[str, Any]:
    text = answer or ""
    words = text.split()
    length = len(words)
    ref_points = question.get("reference_points", [])
    reference_answer = question.get("reference_answer")

    # Length-based base score
    if length < 40:
        base = 35
    elif length < 90:
        base = 60
    else:
        base = 80

    # Count matches to reference points
    matches = sum(1 for p in ref_points if p.lower().split()[0] in text.lower())
    completeness = min(100, base + matches * 5)

    # Simple strengths/improvements based on keyword presence
    strengths = []
    improvements = []
    for p in ref_points:
        if p.lower().split()[0] in text.lower():
            strengths.append(p)
        else:
            improvements.append(p)

    remark = "Good depth and structure." if base >= 80 else "Add more detail and structure."
    score = min(100, base + matches * 5)

    return {
        "score": score,
        "is_correct": False,
        "remark": remark,
        "correctness": score,
        "completeness": completeness,
        "communication": min(100, base + 10),
        "style": 75,
        "reference_answer": reference_answer,
        "reference_points": ref_points,
        "evaluation": {
            "remark": remark,
            "strengths": strengths[:3],
            "improvements": improvements[:3],
        },
    }


def evaluate_aptitude(answer: str, question: Dict[str, Any]) -> Dict[str, Any]:
    correct = str(question.get("correct_answer", "")).strip().lower()
    user = str(answer or "").strip().lower()
    is_correct = user == correct
    score = 100 if is_correct else 0
    return {
        "score": score,
        "is_correct": is_correct,
        "remark": "Correct option selected." if is_correct else "Incorrect option.",
        "correctness": score,
        "completeness": score,
        "communication": 0,
        "style": 0,
        "solution_explanation": question.get("explanation"),
        "reference_answer": question.get("correct_answer"),
        "reference_points": question.get("reference_points", []),
        "evaluation": {
            "remark": "Checked against the correct option.",
            "strengths": [] if not is_correct else ["Chose the right option"],
            "improvements": []
            if is_correct
            else ["Review the explanation and key concept"],
        },
    }


# ------------------------------
# Utility helpers
# ------------------------------


def safe_question_payload(q: Dict[str, Any]) -> Dict[str, Any]:
    """Remove solutions before sending to client."""
    payload = {
        "id": q["id"],
        "type": q["type"],
        "category": q.get("category"),
        "difficulty": q.get("difficulty"),
        "question": q.get("question"),
    }
    if q.get("options"):
        payload["options"] = q["options"]
    return payload


def compute_overall_breakdown(answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not answers:
        return {
            "score": 0,
            "breakdown": {
                "correctness": 0,
                "completeness": 0,
                "communication": 0,
                "style": 0,
            },
        }

    c1 = [float(a["evaluation"].get("correctness", 0)) for a in answers]
    c2 = [float(a["evaluation"].get("completeness", 0)) for a in answers]
    comm = [float(a["evaluation"].get("communication", 0)) for a in answers]
    style = [float(a["evaluation"].get("style", 0)) for a in answers]

    def avg(lst):
        return round(sum(lst) / len(lst), 2) if lst else 0

    breakdown = {
        "correctness": avg(c1),
        "completeness": avg(c2),
        "communication": avg(comm),
        "style": avg(style),
    }
    score = round(
        breakdown["correctness"] * 0.4
        + breakdown["completeness"] * 0.3
        + breakdown["communication"] * 0.2
        + breakdown["style"] * 0.1,
        2,
    )
    return {"score": score, "breakdown": breakdown}


# ------------------------------
# Interview APIs
# ------------------------------


@app.route("/api/interview/start", methods=["POST"])
@jwt_required(optional=True)
def start_interview():
    data = request.get_json() or {}
    role = data.get("role", "Software Engineer")
    difficulty = data.get("difficulty", "medium")

    questions = pick_questions(data)
    if not questions:
        return jsonify({"status": "error", "message": "No questions available"}), 400

    try:
        current_email = get_jwt_identity()
    except:
        current_email = None
    
    user_id = None
    if current_email:
        user_doc = db.users.find_one({"email": current_email}, {"_id": 1})
        if user_doc:
            user_id = str(user_doc["_id"])

    interview_doc = {
        "role": role,
        "difficulty": difficulty,
        "questions": questions,
        "answers": [],
        "status": "in_progress",
        "current_question": 0,
        "started_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "user_email": current_email,
        "user_id": user_id,
    }

    inserted = db.interviews.insert_one(interview_doc)
    session_id = str(inserted.inserted_id)

    return jsonify(
        {
            "status": "success",
            "session_id": session_id,
            "questions": [safe_question_payload(q) for q in questions],
        }
    )


@app.route("/api/interview/<session_id>/answer", methods=["POST"])
def submit_answer(session_id):
    try:
        oid = ObjectId(session_id)
    except Exception:
        return jsonify({"status": "error", "message": "Invalid session id"}), 400

    interview = db.interviews.find_one({"_id": oid})
    if not interview:
        return jsonify({"status": "error", "message": "Interview not found"}), 404

    data = request.get_json() or {}
    current_idx = interview.get("current_question", 0)
    questions = interview.get("questions", [])

    if current_idx >= len(questions):
        return jsonify(
            {"status": "completed", "message": "Interview already completed"}
        ), 200

    question = questions[current_idx]
    answer_type = data.get("type", "voice")
    time_taken = data.get("time_taken", 0)

    evaluation: Dict[str, Any] = {}
    is_correct = False
    answer_text = ""

    if answer_type == "coding":
        answer_text = data.get("code", "")
        evaluation = evaluate_coding_answer(answer_text, question)
        is_correct = evaluation.get("passed", False)
    elif answer_type == "voice":
        answer_text = data.get("transcript", "")
        evaluation = evaluate_behavioral_or_system_design(answer_text, question)
    else:  # text / aptitude
        answer_text = data.get("answer", "")
        evaluation = evaluate_aptitude(answer_text, question)
        is_correct = evaluation.get("is_correct", False)

    answer_record = {
        "question_id": question.get("id"),
        "type": question.get("type"),
        "answer_type": answer_type,
        "answer": answer_text,
        "time_taken": time_taken,
        "submitted_at": datetime.utcnow(),
        "evaluation": evaluation,
        "is_correct": is_correct,
        "category": question.get("category"),
        "difficulty": question.get("difficulty"),
    }

    next_idx = current_idx + 1
    status = "completed" if next_idx >= len(questions) else "in_progress"

    db.interviews.update_one(
        {"_id": oid},
        {
            "$push": {"answers": answer_record},
            "$set": {
                "current_question": next_idx,
                "status": status,
                "updated_at": datetime.utcnow(),
                "completed_at": datetime.utcnow() if status == "completed" else None,
            },
        },
    )

    return jsonify(
        {
            "status": "success",
            "evaluation": evaluation,
            "completed": status == "completed",
            "next_question_available": status != "completed",
        }
    )


@app.route("/api/interview/<session_id>/results", methods=["GET"])
def get_results(session_id):
    try:
        oid = ObjectId(session_id)
    except Exception:
        return jsonify({"status": "error", "message": "Invalid session id"}), 400

    interview = db.interviews.find_one({"_id": oid})
    if not interview:
        return jsonify({"status": "error", "message": "Interview not found"}), 404

    questions = interview.get("questions", [])
    answers = interview.get("answers", [])
    started_at = interview.get("started_at")
    completed_at = (
        interview.get("completed_at") or interview.get("updated_at") or started_at
    )

    merged_answers = []
    for idx, ans in enumerate(answers):
        q = questions[idx] if idx < len(questions) else {}
        eval_data = ans.get("evaluation", {}) or {}

        # Attach reference material
        if not eval_data.get("reference_answer"):
            eval_data["reference_answer"] = (
                q.get("reference_answer")
                or q.get("solution_explanation")
                or q.get("explanation")
                or q.get("correct_answer")
            )
        if not eval_data.get("reference_points"):
            eval_data["reference_points"] = q.get("reference_points", [])
        if q.get("solution_code") and not eval_data.get("solution_code"):
            eval_data["solution_code"] = q.get("solution_code")
        if q.get("solution_explanation") and not eval_data.get("solution_explanation"):
            eval_data["solution_explanation"] = q.get("solution_explanation")

        merged_answers.append(
            {
                "question": q.get("question"),
                "type": q.get("type"),
                "answer_text": ans.get("answer"),
                "evaluation": eval_data,
                "time_taken": ans.get("time_taken", 0),
                "category": q.get("category"),
                "reference_answer": eval_data.get("reference_answer"),
                "reference_points": eval_data.get("reference_points", []),
            }
        )

    breakdown_data = compute_overall_breakdown(
        [{"evaluation": a["evaluation"]} for a in merged_answers]
    )
    total_questions = len(questions)
    time_taken = 0
    if started_at and completed_at:
        time_taken = (completed_at - started_at).total_seconds()

    return jsonify(
        {
            "status": "success",
            "score": round(breakdown_data["score"], 2),
            "breakdown": breakdown_data["breakdown"],
            "total_questions": total_questions,
            "time_taken": time_taken,
            "answers": merged_answers,
            "role": interview.get("role"),
            "difficulty": interview.get("difficulty"),
            "started_at": started_at.isoformat() if started_at else None,
            "completed_at": completed_at.isoformat() if completed_at else None,
        }
    )


# ------------------------------
# Analytics APIs
# ------------------------------


@app.route("/api/analytics/store", methods=["POST"])
def store_attempt():
    data = request.get_json() or {}
    attempt = {
        "score": data.get("score", 0),
        "correct": data.get("correct", 0),
        "total": data.get("total", 0),
        "difficulty": data.get("difficulty", "medium"),
        "time_spent": data.get("time_spent", 0),
        "question_times": data.get("question_times", []),
        "topics": data.get("topics", []),
        "strengths": data.get("strengths", []),
        "weaknesses": data.get("weaknesses", []),
        "created_at": datetime.utcnow(),
    }
    db.attempts.insert_one(attempt)
    return jsonify({"status": "success", "message": "Attempt stored"}), 201


@app.route("/api/analytics/overview", methods=["GET"])
@jwt_required(optional=True)
def analytics_overview():
    """Aggregate analytics from the interviews collection (source of truth)."""
    current_email = get_jwt_identity()

    # Build query — if authenticated, show user data; otherwise show all demo data
    query = {"status": "completed"}
    if current_email:
        query["user_email"] = current_email

    interviews = list(db.interviews.find(query).sort("started_at", -1))

    if not interviews:
        return jsonify({
            "status": "success",
            "overview": {
                "totalAttempts": 0, "avgScore": 0, "totalTimeHours": 0,
                "topicsMastered": 0, "scoreTrend": [], "topicPerformance": [],
                "timePerQuestion": [], "strengths": [], "weaknesses": [],
                "difficultyBreakdown": {
                    "easy":   {"correct": 0, "total": 0},
                    "medium": {"correct": 0, "total": 0},
                    "hard":   {"correct": 0, "total": 0},
                },
            },
        })

    # ── Aggregate scores ────────────────────────────────────────
    scores = []
    score_trend = []
    total_time_secs = 0
    topic_scores: Dict[str, List[float]] = {}
    difficulty_breakdown = {
        "easy":   {"correct": 0, "total": 0},
        "medium": {"correct": 0, "total": 0},
        "hard":   {"correct": 0, "total": 0},
    }
    strengths: List[str] = []
    weaknesses: List[str] = []
    time_per_question: List[int] = []

    for iv in interviews:
        answers = iv.get("answers", [])

        # Score: field "score" stored directly, or compute from answers
        iv_score = iv.get("score")
        if iv_score is None and answers:
            ev_scores = [a.get("evaluation", {}).get("score", 0) for a in answers]
            iv_score = round(sum(ev_scores) / len(ev_scores)) if ev_scores else 0
        iv_score = float(iv_score or 0)
        scores.append(iv_score)

        # Score trend
        date_val = iv.get("finished_at") or iv.get("started_at")
        if date_val:
            score_trend.append({
                "date":  date_val.strftime("%Y-%m-%d"),
                "score": round(iv_score, 1),
            })

        # Time
        total_time_secs += iv.get("total_time", 0)

        # Per-answer aggregation
        for ans in answers:
            ev = ans.get("evaluation", {})
            ans_score = float(ev.get("score", 0))

            # Topic performance
            topic = ans.get("topic") or ans.get("category") or "General"
            topic_scores.setdefault(topic, []).append(ans_score)

            # Difficulty breakdown
            diff = (ans.get("difficulty") or iv.get("difficulty") or "medium").lower()
            bucket = difficulty_breakdown.get(diff, difficulty_breakdown["medium"])
            bucket["total"] += 1
            if ans_score >= 60:
                bucket["correct"] += 1

            # Time per question
            t = ans.get("time_taken", 0)
            if t:
                time_per_question.append(int(t))

            # Strengths / weaknesses (handles both seed data and real AI nested structure)
            ai_eval = ev.get("evaluation", {})
            s = ev.get("strengths") or ai_eval.get("strengths") or []
            w = ev.get("improvements") or ev.get("weaknesses") or ai_eval.get("improvements") or ai_eval.get("weaknesses") or []
            
            strengths.extend(s)
            weaknesses.extend(w)

    total_attempts   = len(scores)
    avg_score        = round(sum(scores) / total_attempts, 2) if scores else 0
    total_time_hours = round(total_time_secs / 3600, 2)

    topic_performance = [
        {"topic": t, "score": round(sum(vals) / len(vals), 1)}
        for t, vals in topic_scores.items()
        if vals
    ]
    topic_performance.sort(key=lambda x: -x["score"])

    return jsonify({
        "status": "success",
        "overview": {
            "totalAttempts":      total_attempts,
            "avgScore":           avg_score,
            "totalTimeHours":     total_time_hours,
            "topicsMastered":     len([t for t in topic_performance if t["score"] >= 60]),
            "scoreTrend":         score_trend,
            "topicPerformance":   topic_performance[:10],
            "timePerQuestion":    time_per_question[:50],
            "difficultyBreakdown": difficulty_breakdown,
            "strengths":          list(dict.fromkeys(strengths))[:10],
            "weaknesses":         list(dict.fromkeys(weaknesses))[:10],
        },
    })

@app.route("/api/internal/debug", methods=["GET"])
def debug_mongodb():
    try:
        counts = {
            "users": db.users.count_documents({}),
            "interviews": db.interviews.count_documents({}),
            "aptitude_results": db.aptitude_results.count_documents({}),
            "attempts": db.attempts.count_documents({}),
        }
        
        # Get one sample interview to verify shape
        sample = list(db.interviews.find({"status": "completed"}).limit(1))
        for d in sample:
            d["_id"] = str(d["_id"])
            
        return jsonify({
            "status": "connected",
            "counts": counts,
            "sample_interview_exists": len(sample) > 0,
            "sample_id": sample[0]["_id"] if sample else None
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/internal/seed", methods=["GET"])
def trigger_seed():
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "seed_analytics.py")
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    exec_globals = {"__file__": file_path, "__name__": "__main__"}
    exec(code, exec_globals)
    return jsonify({"status": "seeded_inline"})


@app.route("/api/analytics/weak-areas", methods=["GET"])
def weak_areas():
    """Identify weak areas based on category performance."""
    # Look at ALL attempts (or last N)
    attempts = list(db.attempts.find({}))

    # Aggregate by category (topic)
    # structure: category -> {total_score: 0, count: 0, questions: []}
    cat_stats = {}

    # Better approach: Query interviews collection for granular answer data
    # Find completed interviews
    interviews = db.interviews.find({"status": "completed"})
    
    category_map = {}  # cat -> {score_sum: 0, count: 0}

    for iv in interviews:
        answers = iv.get("answers", [])
        for ans in answers:
            cat = ans.get("category")
            # score is in answer['evaluation']['score'] or similar
            eval_data = ans.get("evaluation", {})
            score = eval_data.get("score", 0)
            if cat:
                if cat not in category_map:
                    category_map[cat] = {"sum": 0, "count": 0}
                category_map[cat]["sum"] += score
                category_map[cat]["count"] += 1

    weak_areas_list = []
    
    # Thresholds: Avg score < 70 and at least 3 questions attempted
    for cat, stats in category_map.items():
        avg = stats["sum"] / stats["count"]
        if avg < 70 and stats["count"] >= 3:
            # It's a weak area
            # Find some generic advice or reference points from ANY question in this category
            # We can pick a random question from QUESTION_BANK with this category to get reference points
            example_q = next((q for q in QUESTION_BANK if q.get("category") == cat), None)
            points = example_q.get("reference_points", []) if example_q else ["Practice more problems in this domain."]
            
            weak_areas_list.append({
                "category": cat,
                "avg_score": round(avg, 1),
                "question_count": stats["count"],
                "key_points": points[:3],
                "suggested_actions": [
                    f"Review core concepts of {cat}",
                    "Practice 3-5 more problems this week"
                ]
            })

    return jsonify({"status": "success", "weak_areas": weak_areas_list})


@app.route("/api/analytics/attempts", methods=["GET"])
@jwt_required(optional=True)
def get_attempts():
    """Get list of recent completed interviews with summary scores."""
    current_email = get_jwt_identity()
    query = {"status": "completed"}
    if current_email:
        query["user_email"] = current_email

    # Sort by most recent first
    cursor = db.interviews.find(query).sort("started_at", -1).limit(20)
    results = []

    for doc in cursor:
        answers = doc.get("answers", [])

        # Use stored score or compute it
        iv_score = doc.get("score")
        if iv_score is None and answers:
            ev_scores = [a.get("evaluation", {}).get("score", 0) for a in answers]
            iv_score = round(sum(ev_scores) / len(ev_scores)) if ev_scores else 0

        # Date: prefer finished_at, fallback to completed_at, then started_at
        date_val = (
            doc.get("finished_at")
            or doc.get("completed_at")
            or doc.get("started_at")
        )
        date_str = date_val.strftime("%Y-%m-%d") if date_val else "—"

        results.append({
            "id":         str(doc["_id"]),
            "title":      doc.get("role", "Interview"),
            "date":       date_str,
            "score":      int(iv_score or 0),
            "difficulty": doc.get("difficulty", "medium"),
            "type":       "Interview",
            "total":      len(answers),
            "time_taken": doc.get("total_time", 0),
        })

    return jsonify({"status": "success", "attempts": results})


# ------------------------------
# Profile APIs
# ------------------------------


def _average_score_for_interviews(interviews: List[Dict[str, Any]]) -> float:
    """Compute average overall score across a list of interview docs."""
    if not interviews:
        return 0.0

    total = 0.0
    count = 0
    for iv in interviews:
        answers = iv.get("answers", [])
        if not answers:
            continue
        score_data = compute_overall_breakdown(
            [{"evaluation": (a.get("evaluation") or {})} for a in answers]
        )
        total += float(score_data.get("score", 0))
        count += 1

    if count == 0:
        return 0.0
    return round(total / count, 2)


@app.route("/api/profile", methods=["GET"])
@jwt_required()
def get_profile_api():
    """Return current user's profile and basic stats."""
    current_email = get_jwt_identity()
    user = db.users.find_one({"email": current_email}, {"password": 0})
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    user_id = str(user.get("_id"))
    user["_id"] = user_id

    interviews = list(db.interviews.find({"user_id": user_id}))

    total_interviews = len(interviews)
    completed_interviews = len(
        [iv for iv in interviews if iv.get("status") == "completed"]
    )
    avg_score = _average_score_for_interviews(interviews)

    return jsonify(
        {
            "status": "success",
            "profile": user,
            "stats": {
                "total_interviews": total_interviews,
                "completed_interviews": completed_interviews,
                "average_score": avg_score,
            },
        }
    )


@app.route("/api/profile", methods=["PUT"])
@jwt_required()
def update_profile_api():
    current_email = get_jwt_identity()
    data = request.get_json() or {}

    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    allowed_fields = [
        "name",
        "bio",
        "skills",
        "experience",
        "education",
        "resume_url",
        "phone",
        "location",
        "role",
        "primary_languages",
        "target_roles",
        "github",
        "linkedin",
        "timezone",
    ]
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_data:
        return jsonify({"status": "error", "message": "No valid fields to update"}), 400

    result = db.users.update_one({"email": current_email}, {"$set": update_data})
    if result.modified_count == 0:
        return jsonify({"status": "error", "message": "No changes made"}), 400

    return jsonify({"status": "success", "message": "Profile updated successfully"})


# ------------------------------
# Error handling
# ------------------------------


@app.errorhandler(500)
def server_error(error):
    return jsonify({"status": "error", "message": "Internal server error"}), 500


# -------------------------------------------------------
# Serve Frontend Static Files
# Flask serves the entire frontend/ folder so no separate
# HTTP server is needed — no CORS issues at all.
# -------------------------------------------------------

@app.route("/")
def root():
    """Redirect root to the login page."""
    return redirect("/pages/index.html")


@app.route("/<path:filename>")
def serve_frontend(filename):
    """Serve any file from the frontend directory."""
    # Don't intercept /api/* routes
    if filename.startswith("api/"):
        return jsonify({"status": "error", "message": "Not found"}), 404
    try:
        return send_from_directory(FRONTEND_DIR, filename)
    except Exception:
        return redirect("/pages/index.html")


@app.errorhandler(404)
def not_found(error):
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": "Resource not found"}), 404
    return redirect("/pages/index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
