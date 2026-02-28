from flask import Blueprint, request, jsonify, redirect, url_for, session, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os
from datetime import timedelta, datetime
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__)

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

DEMO_EMAIL = os.getenv('DEMO_USER_EMAIL', 'demo@aiinterviewer.com')
DEMO_PASSWORD = os.getenv('DEMO_USER_PASSWORD', 'Demo1234!')

@bp.route('/auth/google', methods=['POST'])
def google_auth():
    """
    Authenticate user with Google OAuth
    """
    try:
        token = request.json.get('token')
        if not token:
            return jsonify({'status': 'error', 'message': 'Token is required'}), 400
        
        # Verify the Google token
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
        
        # Check if the user is already registered
        user = current_app.db.users.find_one({'email': idinfo['email']})
        
        if not user:
            # Create a new user
            user_data = {
                'name': idinfo.get('name', ''),
                'email': idinfo['email'],
                'picture': idinfo.get('picture', ''),
                'created_at': datetime.utcnow(),
                'last_login': datetime.utcnow(),
                'roles': ['user']
            }
            result = current_app.db.users.insert_one(user_data)
            user_data['_id'] = str(result.inserted_id)
        else:
            # Update last login time
            current_app.db.users.update_one(
                {'_id': user['_id']},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            user_data = user
            user_data['_id'] = str(user['_id'])
        
        # Create JWT token
        access_token = create_access_token(
            identity=user_data['email'],
            expires_delta=timedelta(minutes=60)
        )
        
        return jsonify({
            'status': 'success',
            'access_token': access_token,
            'user': {
                'id': user_data['_id'],
                'name': user_data['name'],
                'email': user_data['email'],
                'picture': user_data.get('picture', '')
            }
        })
        
    except ValueError as e:
        return jsonify({'status': 'error', 'message': 'Invalid token'}), 401

@bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current user's profile
    """
    current_user_email = get_jwt_identity()
    user = current_app.db.users.find_one({'email': current_user_email})
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    return jsonify({
        'status': 'success',
        'user': {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'picture': user.get('picture', '')
        }
    })

@bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user (client should remove the token)
    """
    return jsonify({'status': 'success', 'message': 'Successfully logged out'})


def ensure_demo_user():
    users = current_app.db.users
    existing = users.find_one({'email': DEMO_EMAIL})
    if existing:
        return existing
    password_hash = generate_password_hash(DEMO_PASSWORD)
    now = datetime.utcnow()
    demo_user = {
        'name': 'Demo Candidate',
        'email': DEMO_EMAIL,
        'password': password_hash,
        'roles': ['demo', 'user'],
        'created_at': now,
        'last_login': now
    }
    result = users.insert_one(demo_user)
    demo_user['_id'] = str(result.inserted_id)
    return demo_user


@bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip() or 'User'
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email and password are required'}), 400

    users = current_app.db.users
    existing = users.find_one({'email': email})
    if existing:
        return jsonify({'status': 'error', 'message': 'Email already registered'}), 400

    password_hash = generate_password_hash(password)
    now = datetime.utcnow()
    user_data = {
        'name': name,
        'email': email,
        'password': password_hash,
        'roles': ['user'],
        'created_at': now,
        'last_login': now
    }
    result = users.insert_one(user_data)
    user_data['_id'] = str(result.inserted_id)

    access_token = create_access_token(
        identity=user_data['email'],
        expires_delta=timedelta(minutes=60)
    )

    return jsonify({
        'status': 'success',
        'access_token': access_token,
        'user': {
            'id': user_data['_id'],
            'name': user_data['name'],
            'email': user_data['email'],
            'picture': user_data.get('picture', '')
        }
    }), 201


@bp.route('/auth/login', methods=['POST'])
def login_email():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email and password are required'}), 400

    if email == DEMO_EMAIL and password == DEMO_PASSWORD:
        ensure_demo_user()

    users = current_app.db.users
    user = users.find_one({'email': email})
    if not user or not user.get('password'):
        return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401

    if not check_password_hash(user['password'], password):
        return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401

    now = datetime.utcnow()
    users.update_one({'_id': user['_id']}, {'$set': {'last_login': now}})

    access_token = create_access_token(
        identity=user['email'],
        expires_delta=timedelta(minutes=60)
    )

    user_payload = {
        'id': str(user['_id']),
        'name': user.get('name', ''),
        'email': user['email'],
        'picture': user.get('picture', '')
    }

    return jsonify({
        'status': 'success',
        'access_token': access_token,
        'user': user_payload
    })
