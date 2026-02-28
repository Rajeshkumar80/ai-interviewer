"""
seed_analytics.py — Seeds realistic interview analytics data for the demo user.
Run from the project root:
    .venv\Scripts\python.exe seed_analytics.py
"""

import os
import sys
import random
from datetime import datetime, timedelta

# Make sure we can import from backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "backend", ".env"))

from pymongo import MongoClient
from werkzeug.security import generate_password_hash

# ── Mongo connection ────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME   = os.getenv("MONGO_DB_NAME", "ai_interviewer")
client    = MongoClient(MONGO_URI)
db        = client[DB_NAME]

DEMO_EMAIL    = "demo@aiinterviewer.com"
DEMO_PASSWORD = "Demo1234!"

# ── Ensure demo user exists ─────────────────────────────────────
def ensure_demo_user():
    users = db.users
    user  = users.find_one({"email": DEMO_EMAIL})
    if not user:
        result = users.insert_one({
            "name"     : "Demo Candidate",
            "email"    : DEMO_EMAIL,
            "password" : generate_password_hash(DEMO_PASSWORD),
            "roles"    : ["demo", "user"],
            "created_at": datetime.utcnow(),
            "last_login": datetime.utcnow(),
        })
        user = users.find_one({"_id": result.inserted_id})
        print(f"  Created demo user: {DEMO_EMAIL}")
    else:
        print(f"  Demo user already exists: {DEMO_EMAIL}")
    return user

# ── Seed interview attempts ─────────────────────────────────────
ROLES       = ["Frontend Developer", "Backend Developer", "Full Stack Developer",
               "Data Scientist", "DevOps Engineer", "Software Engineer"]
TYPES       = ["coding", "behavioral", "system_design", "aptitude"]
TOPICS      = ["Arrays", "Dynamic Programming", "Strings", "Trees", "Graphs",
               "System Design", "React", "Python", "APIs", "Databases",
               "Logical Reasoning", "Verbal Ability", "Quantitative Aptitude"]
DIFFICULTIES = ["easy", "medium", "hard"]

def random_date(days_back_max=120):
    """Return a random UTC datetime within the past N days."""
    delta = timedelta(
        days=random.randint(0, days_back_max),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )
    return datetime.utcnow() - delta

STRENGTHS_POOL = [
    "Clear and structured explanation",
    "Strong understanding of core concepts",
    "Good use of real-world examples",
    "Excellent problem decomposition",
    "Confident communication style",
    "Efficient time management",
    "Solid knowledge of data structures",
    "Good logical reasoning",
    "Consistent coding style",
    "Strong system design intuition",
    "Well-organized answers",
    "Good edge case handling",
    "Quick to identify optimal approach",
    "Clear articulation of trade-offs",
    "Strong fundamentals in algorithms",
]

IMPROVEMENTS_POOL = [
    "Review time complexity analysis",
    "Practice more dynamic programming problems",
    "Work on explaining thought process aloud",
    "Strengthen SQL query optimization skills",
    "Practice more system design patterns",
    "Improve handling of edge cases",
    "Study graph traversal algorithms",
    "Review object-oriented design principles",
    "Practice behavioral questions using STAR method",
    "Improve speed on array manipulation problems",
    "Study advanced recursion techniques",
    "Review network fundamentals",
    "Work on concise answer delivery",
    "Practice more mock interviews",
    "Study database indexing concepts",
]

def make_answer(q_type, idx):
    """Build a realistic answer record for one question."""
    strength  = random.choice(STRENGTHS_POOL)
    improve   = random.choice(IMPROVEMENTS_POOL)

    if q_type == "aptitude":
        is_correct = random.random() > 0.35
        score = 100 if is_correct else 0
        return {
            "question_id": f"apt_{idx:03d}",
            "type": "aptitude",
            "topic": random.choice(TOPICS[-3:]),
            "difficulty": random.choice(DIFFICULTIES),
            "answer": "Option A",
            "time_taken": random.randint(15, 90),
            "evaluation": {
                "score": score,
                "correctness": score,
                "completeness": score,
                "communication": 0,
                "style": 0,
                "is_correct": is_correct,
                "remark": "Correct." if is_correct else "Incorrect.",
                "strengths": [strength] if is_correct else [],
                "improvements": [] if is_correct else [improve],
            },
        }
    else:
        correctness   = random.randint(50, 98)
        completeness  = max(30, correctness - random.randint(0, 15))
        communication = random.randint(55, 95) if q_type == "behavioral" else 0
        style         = random.randint(60, 90)
        score = round(correctness * 0.4 + completeness * 0.3 + communication * 0.2 + style * 0.1)
        # Give 1-2 strengths and 0-1 improvements based on score
        s_count = 2 if score >= 70 else 1
        i_count = 0 if score >= 80 else 1
        return {
            "question_id": f"{q_type[0]}{idx}",
            "type": q_type,
            "topic": random.choice(TOPICS[:10]),
            "difficulty": random.choice(DIFFICULTIES),
            "answer": "Candidate provided a detailed written/spoken answer.",
            "time_taken": random.randint(60, 480),
            "evaluation": {
                "score": score,
                "correctness": correctness,
                "completeness": completeness,
                "communication": communication,
                "style": style,
                "remark": "Good depth." if score >= 70 else "Needs more detail.",
                "strengths":     random.sample(STRENGTHS_POOL, min(s_count, len(STRENGTHS_POOL))),
                "improvements":  random.sample(IMPROVEMENTS_POOL, min(i_count, len(IMPROVEMENTS_POOL))),
            },
        }

def seed_interviews(user_id, user_email, count=18):
    """Insert `count` realistic interview sessions."""
    inserted = 0
    for i in range(count):
        role       = random.choice(ROLES)
        difficulty = random.choices(DIFFICULTIES, weights=[3, 5, 2])[0]
        n_questions = random.randint(5, 10)
        q_types    = random.choices(TYPES, k=n_questions)

        answers = [make_answer(q_types[j], j + 1) for j in range(n_questions)]
        scores  = [a["evaluation"]["score"] for a in answers]
        overall = round(sum(scores) / len(scores))
        total_time = sum(a["time_taken"] for a in answers)

        started_at  = random_date(120)
        finished_at = started_at + timedelta(seconds=total_time + random.randint(30, 120))

        db.interviews.insert_one({
            "user_id"    : str(user_id),
            "user_email" : user_email,
            "role"       : role,
            "difficulty" : difficulty,
            "status"     : "completed",
            "questions"  : [{"id": a["question_id"], "type": a["type"], "topic": a["topic"],
                             "difficulty": a["difficulty"]} for a in answers],
            "answers"    : answers,
            "score"      : overall,
            "total_time" : total_time,
            "started_at" : started_at,
            "finished_at": finished_at,
            "updated_at" : finished_at,
            "current_question": n_questions,
        })
        inserted += 1

    print(f"  Inserted {inserted} interview records.")

def seed_aptitude(user_id, user_email, count=12):
    """Insert `count` aptitude test results."""
    inserted = 0
    for i in range(count):
        n_q = random.randint(10, 20)
        correct = random.randint(int(n_q * 0.4), n_q)
        score   = round((correct / n_q) * 100)
        started_at = random_date(90)

        db.aptitude_results.insert_one({
            "user_id"    : str(user_id),
            "user_email" : user_email,
            "total"      : n_q,
            "correct"    : correct,
            "score"      : score,
            "time_taken" : random.randint(300, 1200),
            "difficulty" : random.choice(DIFFICULTIES),
            "topic_breakdown": {
                "Logical Reasoning"     : random.randint(50, 100),
                "Verbal Ability"        : random.randint(50, 100),
                "Quantitative Aptitude" : random.randint(50, 100),
            },
            "started_at" : started_at,
            "completed_at": started_at + timedelta(minutes=random.randint(12, 30)),
        })
        inserted += 1

    print(f"  Inserted {inserted} aptitude test records.")

# ── Main ────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n── AI Interviewer: Seeding Demo Analytics Data ──────────\n")

    user = ensure_demo_user()
    user_id    = user["_id"]
    user_email = user["email"]

    # Clear existing data for demo user (fresh seed)
    interviews_deleted = db.interviews.delete_many({"user_email": user_email}).deleted_count
    aptitude_deleted   = db.aptitude_results.delete_many({"user_email": user_email}).deleted_count
    if interviews_deleted or aptitude_deleted:
        print(f"  Cleared {interviews_deleted} interviews + {aptitude_deleted} aptitude records.")

    seed_interviews(user_id, user_email, count=18)
    seed_aptitude(user_id, user_email, count=12)

    print("\n✅ Seeding complete!")
    print(f"   Demo login: {DEMO_EMAIL} / {DEMO_PASSWORD}")
    print("   Visit /pages/analytics.html to see the data.\n")
