from fastapi import HTTPException, status

class BaseAPIException(HTTPException):
    """Base class for all custom API exceptions in this application."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


# --- Authentication & Authorization Exceptions (4xx) ---

class InvalidCredentialsException(BaseAPIException):
    """Raised for invalid username or password during login."""
    def __init__(self, detail="Invalid email or password"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )

class UserAlreadyExistsException(BaseAPIException):
    """Raised when trying to register a user that already exists."""
    def __init__(self, detail="User with this email already exists"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class InvalidTokenException(BaseAPIException):
    """Raised when a JWT token is invalid, malformed, or expired."""
    def __init__(self, detail="Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )
        self.headers = {"WWW-Authenticate": "Bearer"}


# --- User & Profile Exceptions (4xx) ---

class UserNotFoundException(BaseAPIException):
    """Raised when an operation targets a user that does not exist."""
    def __init__(self, detail="User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


# --- Calendar & Agent Exceptions (4xx / 5xx) ---

class CalendarConflictException(BaseAPIException):
    """Raised when a booking/update conflicts with an existing event."""
    def __init__(self, detail="The requested time slot is already booked"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

class InvalidDateException(BaseAPIException):
    """Raised when a provided date string is invalid or in the past."""
    def __init__(self, detail="The provided date is invalid or in the past"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class GoogleCalendarAPIError(BaseAPIException):
    """Raised for errors communicating with the Google Calendar API."""
    def __init__(self, detail="An error occurred with the Google Calendar service"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)