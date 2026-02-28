from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId

bp = Blueprint('profile', __name__, url_prefix='/api/profile')

@bp.route('', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get user's profile
    """
    current_user_email = get_jwt_identity()
    user = current_app.db.users.find_one(
        {'email': current_user_email},
        {'password': 0}  # Exclude password hash
    )
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # Convert ObjectId to string for JSON serialization
    user['_id'] = str(user['_id'])
    
    # Get user's interview statistics
    # Include answers so that we can compute average score correctly
    interviews = list(current_app.db.interviews.find(
        {'user_id': user['_id']}
    ))
    
    # Convert ObjectId to string for each interview
    for interview in interviews:
        interview['_id'] = str(interview['_id'])
    
    return jsonify({
        'status': 'success',
        'profile': user,
        'stats': {
            'total_interviews': len(interviews),
            'completed_interviews': len([i for i in interviews if i.get('status') == 'completed']),
            'average_score': calculate_average_score(interviews),
            'recent_interviews': interviews[:5]  # Return only 5 most recent interviews
        }
    })

def calculate_average_score(interviews):
    """Helper function to calculate average score from interviews"""
    if not interviews:
        return 0
    
    total_score = 0
    valid_interviews = 0
    
    for interview in interviews:
        if interview.get('status') == 'completed' and 'answers' in interview:
            correct_answers = sum(1 for a in interview['answers'] if a.get('is_correct', False))
            total_questions = len(interview.get('questions', []))
            if total_questions > 0:
                total_score += (correct_answers / total_questions) * 100
                valid_interviews += 1
    
    return round(total_score / valid_interviews, 2) if valid_interviews > 0 else 0

@bp.route('', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update user's profile
    """
    current_user_email = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    
    # Only allow certain fields to be updated (aligned with frontend profile form)
    allowed_fields = [
        'name', 'bio', 'skills', 'experience', 'education', 'resume_url',
        'phone', 'location', 'role', 'primary_languages', 'target_roles',
        'github', 'linkedin', 'timezone'
    ]
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    if not update_data:
        return jsonify({'status': 'error', 'message': 'No valid fields to update'}), 400
    
    # Update the user's profile
    result = current_app.db.users.update_one(
        {'email': current_user_email},
        {'$set': update_data}
    )
    
    if result.modified_count == 0:
        return jsonify({'status': 'error', 'message': 'No changes made'}), 400
    
    return jsonify({
        'status': 'success',
        'message': 'Profile updated successfully'
    })

@bp.route('/interviews', methods=['GET'])
@jwt_required()
def get_user_interviews():
    """
    Get all interviews for the current user
    """
    current_user_email = get_jwt_identity()
    user = current_app.db.users.find_one(
        {'email': current_user_email},
        {'_id': 1}
    )
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    skip = (page - 1) * per_page
    
    # Query interviews with pagination
    interviews = list(current_app.db.interviews.find(
        {'user_id': str(user['_id'])},
        {'answers': 0}  # Exclude answers to reduce payload size
    ).sort('started_at', -1).skip(skip).limit(per_page))
    
    # Convert ObjectId to string for each interview
    for interview in interviews:
        interview['_id'] = str(interview['_id'])
    
    # Get total count for pagination
    total = current_app.db.interviews.count_documents({'user_id': str(user['_id'])})
    
    return jsonify({
        'status': 'success',
        'interviews': interviews,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page
        }
    })
