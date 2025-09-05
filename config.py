import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_PATH = f"/bot/{BOT_TOKEN}"
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your_webhook_secret")
    
    # AI Services
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GROK_API_KEY = os.getenv("GROK_API_KEY", "")
    
    # Voice Services
    GOOGLE_TTS_KEY = os.getenv("GOOGLE_TTS_KEY", "")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
    WHISPER_API_KEY = os.getenv("WHISPER_API_KEY", "")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/vetsupport")
    FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "firebase_credentials.json")
    
    # Telemedicine APIs
    HELSI_API_KEY = os.getenv("HELSI_API_KEY", "")
    DOCTOR_ONLINE_API_KEY = os.getenv("DOCTOR_ONLINE_API_KEY", "")
    
    # Social Media APIs
    FACEBOOK_TOKEN = os.getenv("FACEBOOK_TOKEN", "")
    INSTAGRAM_TOKEN = os.getenv("INSTAGRAM_TOKEN", "")
    LINKEDIN_TOKEN = os.getenv("LINKEDIN_TOKEN", "")
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 10000))
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "your_encryption_key_here")
    
    # Admin Settings
    ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")
    SUPPORT_CHAT_ID = os.getenv("SUPPORT_CHAT_ID", "")
    
    # Premium Features
    PREMIUM_PRICE = int(os.getenv("PREMIUM_PRICE", 99))  # UAH
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    
    # Marketing
    REFERRAL_BONUS_DAYS = int(os.getenv("REFERRAL_BONUS_DAYS", 30))
    AUTO_POST_CHANNELS = os.getenv("AUTO_POST_CHANNELS", "").split(",")
    
    # Legal Updates
    LEGAL_API_URL = os.getenv("LEGAL_API_URL", "")
    GOVERNMENT_API_KEY = os.getenv("GOVERNMENT_API_KEY", "")
    
    # Render-specific settings
    RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "")
    
    @classmethod
    def get_webhook_url(cls):
        """Get webhook URL with fallback to Render external URL"""
        if cls.WEBHOOK_URL:
            return cls.WEBHOOK_URL
        elif cls.RENDER_EXTERNAL_URL:
            return cls.RENDER_EXTERNAL_URL
        else:
            return ""

# Initialize configuration
config = Config()