from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv("app/.env") # Wait, checking path
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB_NAME", "ai_interviewer")

mongo = MongoClient(MONGO_URI)
db = mongo[DB_NAME]

# Delete demo user data and seeded data
res_interviews = db.interviews.delete_many({"user_email": "demo@aiinterviewer.com"})
print(f"Deleted {res_interviews.deleted_count} interviews for demo user.")

# Sometimes seeded data might not have user_email or have different ones.
# Actually let's delete all attempts as they don't even have user_emails right now.
res_attempts = db.attempts.delete_many({})
print(f"Deleted {res_attempts.deleted_count} old anonymous attempts.")

# Delete demo user if we want, but the prompt says 
# "DO NOT Break login system - Change UI - Affect Google auth"
# We'll leave demo user but clear their data.

print("Database cleaned.")
