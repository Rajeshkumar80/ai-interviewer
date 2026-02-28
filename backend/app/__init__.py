from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configuration 
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour

    # FIXED: FULL CORS SUPPORT
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5500",
                "http://127.0.0.1:5500",
                "http://localhost:8000",
                "http://127.0.0.1:8000"
            ],
            "allow_headers": [
                "Content-Type",
                "Authorization"
            ],
            "methods": [
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "OPTIONS"
            ],
            "supports_credentials": True
        }
    })

    # JWT
    jwt = JWTManager(app)

    # MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/ai_interviewer")
    mongo = MongoClient(mongo_uri)
    app.db = mongo.get_database()

    # Register routes
    from .routes import auth, interview, profile, analytics, settings
    app.register_blueprint(auth.bp)
    app.register_blueprint(interview.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(analytics.bp)
    app.register_blueprint(settings.bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {"status": "error", "message": "Resource not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"status": "error", "message": "Internal server error"}, 500

    return app
