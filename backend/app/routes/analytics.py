from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from bson import ObjectId

bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

# ======================================================
# 1. STORE ATTEMPT (used by frontend after interview)
# ======================================================
@bp.route("/store", methods=["POST"])
@jwt_required()
def store_attempt():
    """
    Frontend stores interview results here.
    Saves into 'attempts' collection.
    """
    try:
        current_user_email = get_jwt_identity()
        user = current_app.db.users.find_one({"email": current_user_email})

        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        data = request.json

        attempt = {
            "user_id": str(user["_id"]),
            "score": data.get("score", 0),
            "time_spent": data.get("time_spent", 0),
            "topics": data.get("topics", []),
            "difficulty": data.get("difficulty", "medium"),
            "correct": data.get("correct", 0),
            "total": data.get("total", 1),
            "question_times": data.get("question_times", []),
            "strengths": data.get("strengths", []),
            "weaknesses": data.get("weaknesses", []),
            "date": datetime.utcnow()
        }

        current_app.db.attempts.insert_one(attempt)

        return jsonify({"status": "success", "message": "Attempt saved"}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ======================================================
# 2. FETCH ALL ATTEMPTS (for analytics.js)
# ======================================================
@bp.route("/user", methods=["GET"])
@jwt_required()
def get_attempts():
    """
    Fetch all stored attempts for the analytics dashboard.
    """
    try:
        current_user_email = get_jwt_identity()
        user = current_app.db.users.find_one({"email": current_user_email})

        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        attempts = list(current_app.db.attempts.find({"user_id": str(user["_id"])}))

        for a in attempts:
            a["_id"] = str(a["_id"])

        return jsonify({"status": "success", "attempts": attempts})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ======================================================
# 3. ANALYTICS OVERVIEW (based on interviews collection)
# ======================================================
@bp.route('/overview', methods=['GET'])
@jwt_required()
def get_analytics_overview():
    """
    Computes accuracy, category performance, daily performance (last 30 days)
    from completed interviews.
    """
    current_user_email = get_jwt_identity()
    user = current_app.db.users.find_one({'email': current_user_email}, {'_id': 1})

    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    # Fetch interviews
    interviews = list(current_app.db.interviews.find({
        'user_id': str(user['_id']),
        'status': 'completed'
    }))

    if not interviews:
        return jsonify({
            'status': 'success',
            'message': 'No interview data available',
            'overview': {}
        })

    total_interviews = len(interviews)
    total_questions = sum(len(i.get('questions', [])) for i in interviews)

    total_correct = sum(
        sum(1 for a in i.get("answers", []) if a.get("is_correct", False))
        for i in interviews
    )

    accuracy = round((total_correct / total_questions) * 100, 2) if total_questions > 0 else 0

    # Average time per question
    avg_time_per_question = statistics.mean(
        [a.get('time_taken', 0) for i in interviews for a in i.get('answers', [])]
    ) if any(i.get('answers') for i in interviews) else 0

    # Performance by category
    category_stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'avg_time': []})

    for interview in interviews:
        for q, a in zip(interview.get('questions', []), interview.get('answers', [])):
            category = q.get("category", "Uncategorized")
            category_stats[category]["total"] += 1
            if a.get("is_correct", False):
                category_stats[category]["correct"] += 1
            category_stats[category]["avg_time"].append(a.get("time_taken", 0))

    category_performance = []
    for category, stats in category_stats.items():
        acc = (stats["correct"] / stats["total"]) * 100 if stats["total"] else 0
        avg_time = sum(stats["avg_time"]) / len(stats["avg_time"]) if stats["avg_time"] else 0

        category_performance.append({
            "category": category,
            "total_questions": stats["total"],
            "accuracy": round(acc, 2),
            "average_time": round(avg_time, 2)
        })

    # DAILY PERFORMANCE (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    def normalize_date(val):
        if isinstance(val, datetime):
            return val
        try:
            return datetime.fromisoformat(str(val))
        except:
            return datetime.min

    recent = [i for i in interviews if normalize_date(i.get("started_at")) >= thirty_days_ago]

    daily = defaultdict(lambda: {"date": None, "total": 0, "correct": 0})

    for interview in recent:
        d = normalize_date(interview.get("started_at"))
        day = d.strftime("%Y-%m-%d")

        daily[day]["date"] = day
        daily[day]["total"] += len(interview.get("questions", []))
        daily[day]["correct"] += sum(1 for a in interview.get("answers", []) if a.get("is_correct", False))

    daily_list = sorted(daily.values(), key=lambda x: x["date"])

    for day in daily_list:
        day["accuracy"] = round((day["correct"] / day["total"]) * 100, 2) if day["total"] else 0

    return jsonify({
        "status": "success",
        "overview": {
            "total_interviews": total_interviews,
            "total_questions_answered": total_questions,
            "overall_accuracy": accuracy,
            "average_time_per_question": round(avg_time_per_question, 2),
            "category_performance": category_performance,
            "daily_performance": daily_list
        }
    })


# ======================================================
# 4. WEAK AREAS ANALYSIS
# ======================================================
@bp.route('/weak-areas', methods=['GET'])
@jwt_required()
def get_weak_areas():
    """
    Identify user's weakest categories & subcategories.
    """
    current_user_email = get_jwt_identity()
    user = current_app.db.users.find_one({'email': current_user_email}, {'_id': 1})

    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    interviews = list(current_app.db.interviews.find({
        'user_id': str(user['_id']),
        'status': 'completed'
    }))

    if not interviews:
        return jsonify({"status": "success", "weak_areas": []})

    category_stats = defaultdict(lambda: {
        "total": 0,
        "correct": 0,
        "questions": [],
        "subcategories": defaultdict(lambda: {"total": 0, "correct": 0})
    })

    for interview in interviews:
        for q, a in zip(interview.get("questions", []), interview.get("answers", [])):
            category = q.get("category", "Uncategorized")
            subcat = q.get("subcategory", "General")

            category_stats[category]["total"] += 1
            if a.get("is_correct", False):
                category_stats[category]["correct"] += 1

            category_stats[category]["questions"].append({
                "question": q.get("question"),
                "your_answer": a.get("answer"),
                "correct_answer": q.get("answer"),
                "difficulty": q.get("difficulty"),
                "timestamp": interview.get("started_at")
            })

            category_stats[category]["subcategories"][subcat]["total"] += 1
            if a.get("is_correct", False):
                category_stats[category]["subcategories"][subcat]["correct"] += 1

    weak_areas = []

    for category, stats in category_stats.items():
        acc = (stats["correct"] / stats["total"]) * 100 if stats["total"] else 0

        weak_subcats = []
        for subcat, s in stats["subcategories"].items():
            a = (s["correct"] / s["total"]) * 100 if s["total"] else 0
            if a < 70:
                weak_subcats.append({
                    "name": subcat,
                    "accuracy": round(a, 2),
                    "total_questions": s["total"]
                })

        weak_subcats.sort(key=lambda x: x["accuracy"])

        if acc < 70:
            recent_wrong = sorted(
                [q for q in stats["questions"] if q["your_answer"] != q["correct_answer"]],
                key=lambda x: x["timestamp"],
                reverse=True
            )[:3]

            weak_areas.append({
                "category": category,
                "accuracy": round(acc, 2),
                "weak_subcategories": weak_subcats,
                "recent_incorrect": recent_wrong
            })

    weak_areas.sort(key=lambda x: x["accuracy"])

    return jsonify({"status": "success", "weak_areas": weak_areas})


# ======================================================
# 5. PROGRESS TIMELINE
# ======================================================
@bp.route('/progress', methods=['GET'])
@jwt_required()
def get_progress_timeline():
    """
    Provides accuracy timeline for progress chart.
    """
    current_user_email = get_jwt_identity()
    user = current_app.db.users.find_one({'email': current_user_email}, {'_id': 1})

    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    interviews = list(current_app.db.interviews.find({
        "user_id": str(user["_id"]),
        "status": "completed"
    }).sort("started_at", 1))

    if not interviews:
        return jsonify({"status": "success", "progress": []})

    progress = []

    for idx, i in enumerate(interviews):
        correct = sum(1 for a in i.get("answers", []) if a.get("is_correct"))
        total = len(i.get("questions", []))
        accuracy = (correct / total * 100) if total else 0

        progress.append({
            "date": i["started_at"].strftime("%Y-%m-%d"),
            "interview_number": idx + 1,
            "accuracy": round(accuracy, 2),
            "total_questions": total,
            "correct_answers": correct,
            "role": i.get("role", "Unknown"),
            "difficulty": i.get("difficulty", "medium")
        })

    # MOVING AVERAGE
    window = 3
    for i in range(len(progress)):
        start = max(0, i - window + 1)
        span = progress[start:i + 1]
        progress[i]["moving_average"] = round(
            sum(p["accuracy"] for p in span) / len(span), 2
        )

    return jsonify({"status": "success", "progress": progress})
