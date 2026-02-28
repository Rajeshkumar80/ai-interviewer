from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')

    # Allow frontend origins
    CORS(app, resources={r"/*": {"origins": [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]}}, supports_credentials=True)

    jwt = JWTManager(app)

    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ai_interviewer')
    mongo = MongoClient(mongo_uri)
    app.db = mongo.get_database()

    from .routes import auth, interview, profile, analytics, settings
    app.register_blueprint(auth.bp)
    app.register_blueprint(interview.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(analytics.bp)
    app.register_blueprint(settings.bp)

    return app
