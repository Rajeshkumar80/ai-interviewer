from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    CANDIDATE = "candidate"
    INTERVIEWER = "interviewer"
    ADMIN = "admin"

class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"

class SocialLinks(BaseModel):
    github: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    twitter: Optional[str] = None

class UserProfile(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    role: UserRole = UserRole.CANDIDATE
    experience_level: Optional[ExperienceLevel] = None
    bio: Optional[str] = None
    skills: List[str] = []
    languages: List[str] = ["English"]
    social_links: SocialLinks = SocialLinks()
    resume_url: Optional[str] = None
    timezone: str = "UTC"
    target_roles: List[str] = []
    avatar_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    badges: List[str] = []
    stats: Dict[str, Any] = {
        "total_interviews": 0,
        "avg_interview_score": 0,
        "aptitude_tests_taken": 0,
        "avg_aptitude_score": 0
    }

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    experience_level: Optional[ExperienceLevel] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    social_links: Optional[SocialLinks] = None
    timezone: Optional[str] = None
    target_roles: Optional[List[str]] = None
