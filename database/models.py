from datetime import datetime
from enum import Enum
from typing import Optional, List
import uuid

class UserRole(Enum):
    USER = "user"
    PREMIUM = "premium"
    PSYCHOLOGIST = "psychologist"
    ADMIN = "admin"

class SubscriptionStatus(Enum):
    FREE = "free"
    PREMIUM = "premium"
    TRIAL = "trial"

class MoodLevel(Enum):
    VERY_LOW = 1
    LOW = 2
    BELOW_AVERAGE = 3
    AVERAGE = 4
    SLIGHTLY_ABOVE = 5
    GOOD = 6
    VERY_GOOD = 7
    GREAT = 8
    EXCELLENT = 9
    OUTSTANDING = 10

class ConsultationStatus(Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User:
    def __init__(self, user_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None, language: str = "uk", role: UserRole = UserRole.USER):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.language = language
        self.role = role
        self.subscription_status = SubscriptionStatus.FREE
        self.subscription_expires = None
        self.referral_code = str(uuid.uuid4())[:8]
        self.referred_by = None
        self.is_veteran = False
        self.registration_date = datetime.now()
        self.last_activity = datetime.now()
        self.privacy_accepted = False
        self.terms_accepted = False
        self.phone_number = None
        self.email = None
        self.emergency_contact = None

class MoodCheckIn:
    def __init__(self, user_id: int, mood_level: int, note: str = None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.mood_level = mood_level
        self.note = note
        self.timestamp = datetime.now()
        self.ai_analysis = None
        self.recommended_actions = []

class AIChat:
    def __init__(self, user_id: int, message: str, response: str, 
                 model_used: str = "gemini", is_voice: bool = False):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.message = message
        self.response = response
        self.model_used = model_used
        self.is_voice = is_voice
        self.timestamp = datetime.now()
        self.sentiment_score = None
        self.crisis_flag = False

class Recommendation:
    def __init__(self, title: str, content: str, category: str, 
                 language: str = "uk", target_mood: List[int] = None):
        self.id = str(uuid.uuid4())
        self.title = title
        self.content = content
        self.category = category  # breathing, exercise, meditation, reading
        self.language = language
        self.target_mood = target_mood or []
        self.difficulty_level = 1  # 1-5
        self.duration_minutes = 0
        self.media_url = None
        self.created_date = datetime.now()

class Consultation:
    def __init__(self, user_id: int, psychologist_id: int, 
                 consultation_type: str = "text"):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.psychologist_id = psychologist_id
        self.consultation_type = consultation_type  # text, audio, video
        self.status = ConsultationStatus.SCHEDULED
        self.scheduled_time = None
        self.start_time = None
        self.end_time = None
        self.notes = ""
        self.rating = None
        self.feedback = ""
        self.cost = 0

class LegalDocument:
    def __init__(self, title: str, content: str, category: str, language: str = "uk"):
        self.id = str(uuid.uuid4())
        self.title = title
        self.content = content
        self.category = category  # benefits, compensation, procedures, rights
        self.language = language
        self.last_updated = datetime.now()
        self.source_url = None
        self.is_template = False
        self.tags = []

class TelemedicineAppointment:
    def __init__(self, user_id: int, doctor_name: str, specialization: str):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.doctor_name = doctor_name
        self.specialization = specialization
        self.appointment_date = None
        self.appointment_time = None
        self.status = "pending"
        self.appointment_url = None
        self.notes = ""
        self.cost = 0

class UserStats:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.total_check_ins = 0
        self.average_mood = 0.0
        self.streak_days = 0
        self.ai_chats_count = 0
        self.consultations_count = 0
        self.recommendations_completed = 0
        self.last_check_in = None
        self.mood_trend = "stable"  # improving, stable, declining

class ReferralSystem:
    def __init__(self, referrer_id: int, referee_id: int):
        self.id = str(uuid.uuid4())
        self.referrer_id = referrer_id
        self.referee_id = referee_id
        self.referral_date = datetime.now()
        self.bonus_awarded = False
        self.bonus_days = 0

class MarketingCampaign:
    def __init__(self, title: str, content: str, campaign_type: str = "tip"):
        self.id = str(uuid.uuid4())
        self.title = title
        self.content = content
        self.campaign_type = campaign_type  # tip, news, promotion
        self.target_channels = []
        self.scheduled_time = None
        self.sent_time = None
        self.engagement_stats = {}
        self.is_active = True