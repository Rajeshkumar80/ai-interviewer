from datetime import datetime
from typing import Optional, Dict, Any
from ..models.user import UserProfile, UserProfileUpdate

class ProfileService:
    def __init__(self, db):
        self.db = db
        self.profiles = db.profiles
    
    async def get_profile(self, user_id: str) -> Optional[Dict]:
        profile = await self.profiles.find_one({"user_id": user_id})
        if profile and "_id" in profile:
            profile["_id"] = str(profile["_id"])
        return profile
    
    async def create_profile(self, user_data: Dict) -> Dict:
        profile_data = {
            **user_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "stats": {
                "total_interviews": 0,
                "avg_interview_score": 0,
                "aptitude_tests_taken": 0,
                "avg_aptitude_score": 0
            }
        }
        result = await self.profiles.insert_one(profile_data)
        return await self.get_profile(str(result.inserted_id))
    
    async def update_profile(self, user_id: str, update_data: Dict) -> Optional[Dict]:
        update_data["updated_at"] = datetime.utcnow()
        result = await self.profiles.update_one(
            {"user_id": user_id},
            {"$set": update_data},
            upsert=True
        )
        if result.modified_count > 0 or result.upserted_id:
            return await self.get_profile(user_id)
        return None
    
    async def update_stats(self, user_id: str, stats_update: Dict[str, Any]) -> bool:
        result = await self.profiles.update_one(
            {"user_id": user_id},
            {"$set": {"stats": stats_update, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    async def add_badge(self, user_id: str, badge_name: str) -> bool:
        result = await self.profiles.update_one(
            {"user_id": user_id},
            {
                "$addToSet": {"badges": badge_name},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
