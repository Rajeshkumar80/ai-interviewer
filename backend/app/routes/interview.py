from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import random
from bson import ObjectId

bp = Blueprint('interview', __name__, url_prefix='/api/interview')

"""
QUESTION BANK FORMAT

Each question should follow this structure (extend as you like):

type:
  - "coding"
  - "behavioral"
  - "system_design"
  - "aptitude" / "mcq" (if you later want)

Fields:
  - id: unique int or string
  - type: "coding"/"behavioral"/"system_design"
  - category: topic name ("Algorithms", "React", etc.)
  - question: string (the prompt)
  - difficulty: "easy"/"medium"/"hard"

For coding:
  - solution_code: string (sample correct code)
  - solution_explanation: string
  - reference_points: [list of key bullet points] (optional)

For conceptual / MCQ / aptitude:
  - options: [ "A...", "B...", ... ] (optional)
  - correct_answer: string (exact correct text OR option label like "A")
  - explanation: string
  - reference_points: [list of key bullet points] (optional)
"""

QUESTION_BANK = [
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
            {"input": ([1, 2, 5], 11), "expected": 3},
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


def pick_questions(config):
    """Select questions based on configuration.

    Priority:
    1) Match requested types AND difficulty.
    2) Then same types with any difficulty.
    3) Then any remaining questions in the bank.
    4) If still fewer than num_questions, allow repeats as last resort.
    """

    num_questions = int(config.get("num_questions", 8))
    difficulty_raw = config.get("difficulty") or None
    difficulty = difficulty_raw.lower() if isinstance(difficulty_raw, str) else None
    types = config.get("question_types") or [
        "coding",
        "behavioral",
        "system_design",
        "aptitude",
    ]

    # Base pool: only requested types
    base_pool = [q for q in QUESTION_BANK if q["type"] in types]
    if not base_pool:
        return []

    # Primary pool: requested difficulty within those types
    if difficulty:
        primary_pool = [
            q
            for q in base_pool
            if (q.get("difficulty") or "").lower() == difficulty
        ]
    else:
        primary_pool = list(base_pool)

    # Secondary: same types, any difficulty but not already selected
    secondary_pool = [q for q in base_pool if q not in primary_pool]

    # Tertiary: anything else in the bank
    tertiary_pool = [
        q
        for q in QUESTION_BANK
        if q not in primary_pool and q not in secondary_pool
    ]

    random.shuffle(primary_pool)
    random.shuffle(secondary_pool)
    random.shuffle(tertiary_pool)

    combined = []
    combined.extend(primary_pool)
    combined.extend(secondary_pool)
    combined.extend(tertiary_pool)

    if not combined:
        return []

    if len(combined) >= num_questions:
        return combined[:num_questions]

    # Not enough unique questions overall: allow repeats to fill.
    # Use random.choice in a loop instead of random.choices for
    # compatibility with older Python versions.
    needed = num_questions - len(combined)
    extra = []
    for _ in range(needed):
        extra.append(random.choice(combined))
    return combined + extra


def find_question_by_id(qid):
    for q in QUESTION_BANK:
        if q["id"] == qid:
            return q
    return None


@bp.route('/start', methods=['POST'])
@jwt_required(optional=True)
def start_interview():
    """Start a new interview session.

    Uses JWT if available to attach user, but will still work without a token.
    Always falls back to sensible defaults for role/difficulty so normal
    frontend usage does not see 4xx errors.
    """
    current_user_email = get_jwt_identity()
    data = request.get_json() or {}

    # Fallbacks so we don't reject the request if fields are missing
    raw_role = data.get('role') or ''
    role = raw_role.strip() or 'Software Engineer'

    raw_diff = (data.get('difficulty') or 'medium').strip().lower()
    if raw_diff not in ['easy', 'medium', 'hard']:
        difficulty = 'medium'
    else:
        difficulty = raw_diff

    # User is optional: if JWT is present and matches a user, attach it
    user = None
    if current_user_email:
        user = current_app.db.users.find_one({'email': current_user_email})

    num_questions = int(data.get('num_questions', 10))
    question_types = data.get('question_types') or ['coding', 'behavioral']

    config = {
        'num_questions': num_questions,
        'difficulty': difficulty,
        'question_types': question_types,
    }

    selected_questions = pick_questions(config)

    if not selected_questions:
        return jsonify({
            'status': 'error',
            'message': 'No questions available for the selected configuration'
        }), 400

    # Normalize question objects for storing in interview + sending to client
    questions_for_session = []
    for q in selected_questions:
        questions_for_session.append({
            "id": q["id"],
            "type": q["type"],
            "category": q.get("category"),
            "difficulty": q.get("difficulty", difficulty),
            "question": q["question"],
            # The following are kept in DB, but answer text will not be sent to frontend as "answer"
            "reference_answer": q.get("reference_answer"),
            "reference_points": q.get("reference_points", []),
            "solution_code": q.get("solution_code"),
            "solution_explanation": q.get("solution_explanation"),
            "options": q.get("options"),
            "correct_answer": q.get("correct_answer"),
            "explanation": q.get("explanation")
        })

    # Create interview session document
    session_data = {
        'user_id': str(user['_id']) if user else None,
        'user_email': current_user_email,
        'role': role,
        'difficulty': difficulty,
        'questions': questions_for_session,
        'answers': [],
        'started_at': datetime.utcnow(),
        'status': 'in_progress',
        'current_question': 0
    }

    result = current_app.db.interviews.insert_one(session_data)
    session_id = str(result.inserted_id)

    # Send questions to frontend but DO NOT send correct_answer directly
    safe_questions = []
    for q in questions_for_session:
        safe_q = {
            "id": q["id"],
            "type": q["type"],
            "category": q.get("category"),
            "difficulty": q.get("difficulty"),
            "question": q.get("question"),
        }
        if q.get("options"):
            safe_q["options"] = q["options"]
        safe_questions.append(safe_q)

    return jsonify({
        'status': 'success',
        'session_id': session_id,
        'questions': safe_questions
    }), 200


@bp.route('/<session_id>/answer', methods=['POST'])
@jwt_required()
def submit_answer(session_id):
    """
    Submit an answer to the current question.
    Backend:
      - Finds interview & current question
      - Evaluates (coding / behavioral / mcq)
      - Stores answer with evaluation and solution info
      - Returns evaluation for immediate UI display
    """
    data = request.get_json() or {}

    try:
        oid = ObjectId(session_id)
    except Exception:
        return jsonify({'status': 'error', 'message': 'Invalid session id'}), 400

    interview = current_app.db.interviews.find_one({'_id': oid})
    if not interview:
        return jsonify({'status': 'error', 'message': 'Interview not found'}), 404

    current_question_idx = interview.get('current_question', 0)
    questions = interview.get('questions', [])

    if current_question_idx >= len(questions):
        return jsonify({
            'status': 'completed',
            'message': 'Interview already completed'
        }), 200

    question = questions[current_question_idx]
    answer_type = data.get('type', 'voice')  # 'coding' or 'voice'
    time_taken = data.get('time_taken', 0)

    answer_record = {
        'question_id': question.get('id'),
        'question_type': question.get('type'),
        'time_taken': time_taken,
        'submitted_at': datetime.utcnow(),
    }

    # ---- CODING ANSWER ----
    if answer_type == 'coding':
        code = data.get('code', '') or ''
        language = data.get('language', 'javascript')

        answer_record['type'] = 'coding'
        answer_record['code'] = code
        answer_record['language'] = language

        evaluation = evaluate_code_with_solution(code, language, question)
        answer_record['evaluation'] = evaluation
        answer_record['is_correct'] = evaluation.get('passed', False)

    # ---- VOICE / TEXT ANSWER ----
    elif answer_type == 'voice':
        transcript = data.get('transcript', '') or ''

        answer_record['type'] = 'behavioral'
        answer_record['transcript'] = transcript

        evaluation = evaluate_behavioral_or_mcq(transcript, question)
        answer_record['evaluation'] = evaluation
        answer_record['score'] = evaluation.get('score', 0)
        answer_record['is_correct'] = evaluation.get('is_correct', False)

    else:
        # Fallback if some other type is used
        raw_answer = data.get('answer', '')
        answer_record['type'] = 'text'
        answer_record['answer'] = raw_answer
        # If we have a correct_answer in the question, compare
        correct_answer = question.get('correct_answer')
        is_correct = bool(correct_answer and raw_answer.strip().lower() == str(correct_answer).strip().lower())
        answer_record['is_correct'] = is_correct
        evaluation = {
            'score': 100 if is_correct else 0,
            'remark': 'Exact match with correct answer.' if is_correct else 'Does not match the correct answer.',
            'reference_answer': correct_answer,
            'reference_points': [],
            'evaluation': {}
        }
        answer_record['evaluation'] = evaluation

    # Move to next question or mark completed
    next_question_idx = current_question_idx + 1
    status = 'in_progress'
    completed = False
    if next_question_idx >= len(questions):
        status = 'completed'
        completed = True

    current_app.db.interviews.update_one(
        {'_id': oid},
        {
            '$set': {
                'current_question': next_question_idx,
                'status': status,
                'updated_at': datetime.utcnow()
            },
            '$push': {'answers': answer_record}
        }
    )

    return jsonify({
        'status': 'success',
        'evaluation': answer_record.get('evaluation', {}),
        'completed': completed,
        'next_question_available': not completed
    }), 200


@bp.route('/<session_id>/results', methods=['GET'])
@jwt_required()
def get_results(session_id):
    """
    Return full results for an interview.
    This merges questions + answers and includes:
      - question text
      - type
      - user answer text
      - evaluation (with score, remark, etc.)
      - reference_answer
      - reference_points
      - solution_code / explanation for coding
    """
    try:
        oid = ObjectId(session_id)
    except Exception:
        return jsonify({'status': 'error', 'message': 'Invalid session id'}), 400

    interview = current_app.db.interviews.find_one({'_id': oid})
    if not interview:
        return jsonify({'status': 'error', 'message': 'Interview not found'}), 404

    questions = interview.get('questions', [])
    answers = interview.get('answers', [])
    started_at = interview.get('started_at')
    completed_at = interview.get('completed_at', interview.get('updated_at', started_at))

    merged_answers = []
    correctness_scores = []
    completeness_scores = []
    communication_scores = []
    style_scores = []

    # Merge by index (Q1 -> A1, Q2 -> A2, ...)
    for idx, ans in enumerate(answers):
        q = questions[idx] if idx < len(questions) else {}
        eval_data = ans.get('evaluation', {}) or {}

        # attach reference fields from question if not present
        if 'reference_answer' not in eval_data or not eval_data.get('reference_answer'):
            eval_data['reference_answer'] = (
                q.get('reference_answer')
                or q.get('correct_answer')
                or q.get('explanation')
            )

        if 'reference_points' not in eval_data or not eval_data.get('reference_points'):
            eval_data['reference_points'] = q.get('reference_points', [])

        if q.get('solution_code') and 'solution_code' not in eval_data:
            eval_data['solution_code'] = q['solution_code']
        if q.get('solution_explanation') and 'solution_explanation' not in eval_data:
            eval_data['solution_explanation'] = q['solution_explanation']

        ans_type = ans.get('type') or q.get('type') or 'coding'
        user_text = ans.get('code') or ans.get('transcript') or ans.get('answer', '')

        merged = {
            'question': q.get('question', 'Question text not available'),
            'type': ans_type,
            'answer_text': user_text,
            'evaluation': eval_data,
            'time_taken': ans.get('time_taken', 0),
            'category': q.get('category'),
            'reference_answer': eval_data.get('reference_answer'),
            'reference_points': eval_data.get('reference_points', [])
        }

        # For breakdown stats
        correctness_scores.append(float(eval_data.get('correctness', 0)))
        completeness_scores.append(float(eval_data.get('completeness', 0)))
        communication_scores.append(float(eval_data.get('communication', 0)))
        style_scores.append(float(eval_data.get('style', 0)))

        merged_answers.append(merged)

    # Safeguard if empty
    if not correctness_scores:
        correctness_scores = [0]
    if not completeness_scores:
        completeness_scores = [0]
    if not communication_scores:
        communication_scores = [0]
    if not style_scores:
        style_scores = [0]

    avg_correctness = sum(correctness_scores) / len(correctness_scores)
    avg_completeness = sum(completeness_scores) / len(completeness_scores)
    avg_communication = sum(communication_scores) / len(communication_scores)
    avg_style = sum(style_scores) / len(style_scores)

    overall_score = (
        avg_correctness * 0.4
        + avg_completeness * 0.3
        + avg_communication * 0.2
        + avg_style * 0.1
    )

    time_taken_sec = 0
    if started_at and completed_at:
        time_taken_sec = (completed_at - started_at).total_seconds()

    return jsonify({
        'status': 'success',
        'score': round(overall_score, 2),
        'breakdown': {
            'correctness': round(avg_correctness, 2),
            'completeness': round(avg_completeness, 2),
            'communication': round(avg_communication, 2),
            'style': round(avg_style, 2)
        },
        'total_questions': len(questions),
        'time_taken': time_taken_sec,
        'answers': merged_answers
    }), 200


# ========== HELPER EVALUATORS ==========

def evaluate_code_with_solution(code, language, question):
    """
    Simple mock evaluation for coding questions that also returns solution.
    In real life, you would run test cases etc.
    """
    base_score = 70
    extra = 0
    code_lower = (code or '').lower()

    # Tiny heuristic: reward if some key tokens from the question's reference points are present
    ref_points = question.get('reference_points', [])
    matches = 0
    for p in ref_points:
        token = str(p).split()[0].lower()
        if token and token in code_lower:
            matches += 1

    if matches:
        extra = min(30, matches * 10)

    correctness = base_score + extra
    completeness = min(100, base_score + extra / 2)
    style = 70

    solution_code = question.get('solution_code')
    solution_explanation = question.get('solution_explanation')

    return {
        'passed': correctness >= 60,
        'test_results': [],
        'correctness': correctness,
        'completeness': completeness,
        'communication': 0,  # not used for coding here
        'style': style,
        'score': correctness,
        'answer_feedback': "This is a heuristic score; focus on matching the reference solution structure.",
        'solution_code': solution_code,
        'solution_explanation': solution_explanation,
        'reference_answer': solution_explanation,
        'reference_points': question.get('reference_points', []),
        'evaluation': {
            'remark': 'Scored with simple static heuristics.',
            'strengths': ref_points[:3],
            'improvements': ref_points[3:6]
        }
    }


def evaluate_behavioral_or_mcq(text, question):
    """
    Evaluate behavioral or conceptual answer.
    If question has correct_answer -> do strict check.
    Else -> STAR-style / heuristic evaluation.
    """
    text = text or ''
    correct_answer = question.get('correct_answer')
    ref_points = question.get('reference_points', [])
    reference_answer = question.get('reference_answer') or question.get('explanation')

    is_mcq = correct_answer is not None

    if is_mcq:
        # Strict text comparison for now
        user_clean = text.strip().lower()
        correct_clean = str(correct_answer).strip().lower()
        is_correct = user_clean == correct_clean

        return {
            'score': 100 if is_correct else 0,
            'is_correct': is_correct,
            'remark': 'Correct option selected.' if is_correct else 'Incorrect option.',
            'reference_answer': correct_answer,
            'reference_points': ref_points,
            'evaluation': {
                'remark': 'MCQ checked against exact correct answer.',
                'strengths': [],
                'improvements': [] if is_correct else ['Review the explanation and reasoning behind the correct option.']
            }
        }

    # Behavioral / open-ended
    word_count = len(text.split())
    if word_count > 120:
        score = 80
        remark = "Good depth in your answer."
    elif word_count > 60:
        score = 65
        remark = "Decent answer, but can add more detail."
    else:
        score = 40
        remark = "Too short; expand with more concrete details."

    strengths = []
    improvements = []
    lower = text.lower()
    # Example STAR check
    for key in ["situation", "task", "action", "result", "reflection"]:
        if key in lower:
            strengths.append(f"Mentions {key} explicitly.")
        else:
            improvements.append(f"Consider explicitly stating the {key}.")

    return {
        'score': score,
        'is_correct': False,  # behavioral is not strictly correct/incorrect
        'remark': remark,
        'reference_answer': reference_answer,
        'reference_points': ref_points,
        'evaluation': {
            'remark': remark,
            'strengths': strengths[:3],
            'improvements': improvements[:3]
        }
    }
