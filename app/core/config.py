from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    DATABASE_NAME: str

    CALENDAR_ID: str
    GOOGLE_CALENDAR_SCOPES: List[str] = ["https://www.googleapis.com/auth/calendar"]
    GOOGLE_CREDENTIALS_BASE64: str
    GOOGLE_API_KEY: str

    SERPER_API_KEY: str

    JWT_SECRET_KEY: str 
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    COMPANY_TIMEZONE: str = "Asia/Kolkata"
    COMPANY_WORKING_HOURS: str = "10:00 AM to 6:00 PM"
    MEETING_BUFFER_MINUTES: int = 15

    COMPANY_WORKING_START_HOUR: int = 10
    COMPANY_WORKING_END_HOUR: int = 18
    SLOT_CHECK_DURATION_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = 'ignore'

settings = Settings()