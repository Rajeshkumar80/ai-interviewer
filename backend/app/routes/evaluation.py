from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.evaluation import EvaluationEngine
from datetime import datetime

bp = Blueprint('evaluation', __name__, url_prefix='/api/evaluate')
evaluator = EvaluationEngine()

@bp.route('/answer', methods=['POST'])
@jwt_required()
def evaluate_answer():
    data = request.get_json()
    
    if not data or 'user_answer' not in data or 'ideal_answer' not in data:
        return jsonify({
            'status': 'error',
            'message': 'user_answer and ideal_answer are required'
        }), 400
    
    evaluation_results = {
        'question_type': data.get('question_type', 'text'),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    try:
        semantic_similarity = evaluator.calculate_semantic_similarity(
            data['user_answer'],
            data['ideal_answer']
        )
        evaluation_results['semantic_similarity'] = semantic_similarity
        
        if 'audio_duration' in data:
            evaluation_results['speech_metrics'] = evaluator.analyze_speech_metrics(
                data['user_answer'],
                data['audio_duration']
            )
        
        if data.get('question_type') == 'code' and 'code_test_cases' in data:
            evaluation_results['code_evaluation'] = evaluator.evaluate_code(
                data['user_answer'],
                data['code_test_cases']
            )
        
        feedback = evaluator.generate_feedback(evaluation_results)
        
        return jsonify({
            'status': 'success',
            'evaluation': feedback
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Evaluation failed: {str(e)}'
        }), 500
