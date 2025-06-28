# in app/services/calendar_service.py

import base64
import json
from functools import lru_cache

from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource

from app.core.config import settings

class CalendarService:
    """A service to manage interactions with the Google Calendar API."""

    @lru_cache(maxsize=1)
    def get_client(self) -> Resource:
        """
        Initializes and returns a singleton instance of the Google Calendar service client.
        The client is cached to avoid re-creating it multiple times.

        Returns:
            Resource: The Google Calendar service client.

        Raises:
            ConnectionError: If the service client cannot be initialized.
        """
        try:
            creds_info = json.loads(base64.b64decode(settings.GOOGLE_CREDENTIALS_BASE64))
            creds = service_account.Credentials.from_service_account_info(
                creds_info, scopes=settings.GOOGLE_CALENDAR_SCOPES
            )
            return build('calendar', 'v3', credentials=creds)
        except Exception as e:
            raise ConnectionError(f"Failed to build Google Calendar service: {e}")

# We can keep a singleton instance available for easy use if needed,
# but the primary access should be through the ServiceProvider.
calendar_service_instance = CalendarService()