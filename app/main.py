import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.error_handler import custom_exception_handler
from app.core.exceptions import BaseAPIException
from app.core.log_config import logger

from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.middleware.timing_middleware import TimingMiddleware

from app.api import auth as auth_router
from app.api import user as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    - Connects to MongoDB on startup.
    - Closes MongoDB connection on shutdown.
    """
    logger.info("Application startup...") 
    await connect_to_mongo()
    yield
    logger.info("Application shutdown...")
    await close_mongo_connection()

app = FastAPI(
    title="AI Booking Agent API",
    description="API for an AI-powered event booking agent.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(TimingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

app.add_exception_handler(BaseAPIException, custom_exception_handler)

# --- API Router Setup ---
logger.info("Attaching API routers...")
app.include_router(auth_router.router, prefix="/api")
app.include_router(user_router.router, prefix="/api")

@app.get("/", tags=["Health Check"])
async def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "Welcome to the AI Booking Agent API"} 