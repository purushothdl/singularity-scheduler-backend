from fastapi import FastAPI
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.api.auth import router as auth_router
from app.api.user import router as user_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()