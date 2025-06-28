import base64
import json
from datetime import datetime, timedelta
from typing import List, Dict

from bson import ObjectId
from fastapi.concurrency import run_in_threadpool
from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from langchain_core.tools import tool
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
import pytz
import requests

from app.core.config import settings
from app.database.mongodb import get_db

def _get_calendar_service() -> Resource:
    """(Internal) Initializes the Google Calendar service client."""
    try:
        creds_info = json.loads(base64.b64decode(settings.GOOGLE_CREDENTIALS_BASE64))
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=settings.GOOGLE_CALENDAR_SCOPES
        )
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        raise ConnectionError(f"Failed to build Google Calendar service: {e}")

async def _internal_create_event(summary: str, start_time: str, end_time: str, current_user: Dict) -> str:
    """(Internal) Creates the event after all checks and locks have passed."""
    db: AsyncIOMotorDatabase = get_db()
    events_collection = db.get_collection("events")
    user_tz = pytz.timezone(current_user.get('timezone', 'UTC'))
    start_dt = datetime.fromisoformat(start_time.replace('Z', ''))
    end_dt = datetime.fromisoformat(end_time.replace('Z', ''))

    if start_dt.tzinfo is None: start_dt = user_tz.localize(start_dt)
    if end_dt.tzinfo is None: end_dt = user_tz.localize(end_dt)

    start_utc = start_dt.astimezone(pytz.UTC)
    end_utc = end_dt.astimezone(pytz.UTC)
    
    event_to_db = {
        "google_event_id": None, "owner_user_id": ObjectId(current_user['id']), "title": summary,
        "start_time_utc": start_utc, "end_time_utc": end_utc, "original_timezone": current_user.get('timezone'),
        "attendees": [], "created_at": datetime.utcnow(), "status": "pending"
    }

    try:
        result = await events_collection.insert_one(event_to_db)
        temp_event_id_for_db = result.inserted_id
    except DuplicateKeyError:
        return "Error: Apologies, but that exact time slot was booked while we were finalizing. Please try another time."

    try:
        service = _get_calendar_service()
        event_body = {
            'summary': summary, 'description': f"Call booked by {current_user.get('email')}",
            'start': {'dateTime': start_time, 'timeZone': current_user.get('timezone')},
            'end': {'dateTime': end_time, 'timeZone': current_user.get('timezone')},
        }
        created_event = service.events().insert(calendarId=settings.CALENDAR_ID, body=event_body).execute()
        
        await events_collection.update_one(
            {"_id": temp_event_id_for_db},
            {"$set": {"google_event_id": created_event['id'], "status": "confirmed"}}
        )
        return f"Event created successfully! Link: {created_event.get('htmlLink')}"
    except Exception as e:
        await events_collection.delete_one({"_id": temp_event_id_for_db})
        return f"Error: Could not create event on Google Calendar after reserving the slot. Reason: {e}"

@tool
async def confirm_and_book_event(summary: str, start_time: str, end_time: str, current_user: Dict) -> str:
    """
    Performs a final availability check and books the event if the slot is still free. This is the ONLY tool that should be used to create an event and should only be called AFTER the user has explicitly confirmed the proposed time.
    """
    try:
        db: AsyncIOMotorDatabase = get_db()
        events_collection = db.get_collection("events")
        user_tz = pytz.timezone(current_user.get('timezone', 'UTC'))
        start_dt = datetime.fromisoformat(start_time.replace('Z', ''))
        end_dt = datetime.fromisoformat(end_time.replace('Z', ''))
        
        if start_dt.tzinfo is None: start_dt = user_tz.localize(start_dt)
        if end_dt.tzinfo is None: end_dt = user_tz.localize(end_dt)
        
        start_utc, end_utc = start_dt.astimezone(pytz.UTC), end_dt.astimezone(pytz.UTC)
        
        conflicting_event = await events_collection.find_one({
            "start_time_utc": {"$lt": end_utc}, "end_time_utc": {"$gt": start_utc}
        })

        if conflicting_event:
            return "Error: Apologies, that time slot was just taken. Please find another available slot."
        
        return await _internal_create_event(summary, start_time, end_time, current_user)
    except Exception as e:
        return f"An unexpected error occurred during the final booking step: {e}"

@tool
async def list_events(current_user: Dict, start_time: str = None, end_time: str = None) -> List[Dict]:
    """
    Retrieves the user's own calendar events as a list of structured data, automatically converted to their local timezone. Can be filtered by a time range. If no time range is given, it lists upcoming events.
    """
    db: AsyncIOMotorDatabase = get_db()
    events_collection = db.get_collection("events")
    try:
        user_id = ObjectId(current_user['id'])
        user_tz = pytz.timezone(current_user.get('timezone', 'UTC'))
    except pytz.UnknownTimeZoneError:
        return [{"error": "User has an invalid timezone set in their profile."}]
    except Exception:
        return [{"error": "Invalid user ID format."}]

    query = {"owner_user_id": user_id}
    time_filter = {}

    if start_time:
        try:
            dt_aware = user_tz.localize(datetime.fromisoformat(start_time.replace('Z', '')))
            time_filter["$gte"] = dt_aware.astimezone(pytz.UTC)
        except ValueError: return [{"error": "Invalid start_time format. Please use ISO format."}]
    if end_time:
        try:
            dt_aware = user_tz.localize(datetime.fromisoformat(end_time.replace('Z', '')))
            time_filter["$lte"] = dt_aware.astimezone(pytz.UTC)
        except ValueError: return [{"error": "Invalid end_time format. Please use ISO format."}]

    if time_filter: query["start_time_utc"] = time_filter
    else: query["start_time_utc"] = {"$gte": datetime.utcnow()}
    
    serializable_events = []
    cursor = events_collection.find(query).sort("start_time_utc", 1)
    async for event in cursor:
        start_utc_aware = event['start_time_utc'].replace(tzinfo=pytz.UTC)
        end_utc_aware = event['end_time_utc'].replace(tzinfo=pytz.UTC)
        start_local = start_utc_aware.astimezone(user_tz)
        end_local = end_utc_aware.astimezone(user_tz)

        event_data = {
            "google_event_id": event.get("google_event_id"), "title": event.get("title"),
            "start_time": start_local.isoformat(), "end_time": end_local.isoformat(),
            "attendees": event.get("attendees", [])
        }
        serializable_events.append(event_data)

    return serializable_events

@tool
async def delete_event(event_id: str, current_user: Dict) -> str:
    """Deletes a specific event using its unique google_event_id. The user must be the owner."""
    db: AsyncIOMotorDatabase = get_db()
    events_collection = db.get_collection("events")
    
    event_doc = await events_collection.find_one({"google_event_id": event_id})
    if not event_doc:
        return f"Error: Event with ID '{event_id}' not found in our records."
    
    if str(event_doc['owner_user_id']) != current_user['id']:
        return "Error: Permission Denied. You are not the owner of this event."

    try:
        service = await run_in_threadpool(_get_calendar_service)
        await run_in_threadpool(service.events().delete(calendarId=settings.CALENDAR_ID, eventId=event_id).execute)
        await events_collection.delete_one({"google_event_id": event_id})
        return f"Event '{event_doc['title']}' deleted successfully."
    except HttpError as e:
        return f"An error occurred with Google Calendar API: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@tool
async def update_user_timezone(current_user: Dict, timezone: str) -> str:
    """Updates the current user's preferred timezone in their profile. Use this when a user specifies their timezone."""
    db: AsyncIOMotorDatabase = get_db()
    users_collection = db.get_collection("users")
    try:
        pytz.timezone(timezone)
        await users_collection.update_one(
            {"_id": ObjectId(current_user['id'])}, {"$set": {"timezone": timezone}}
        )
        return f"Timezone updated successfully to {timezone}."
    except pytz.UnknownTimeZoneError:
        return "Error: Invalid timezone name. Please provide a valid IANA timezone, like 'America/New_York' or 'Asia/Kolkata'."
    except Exception as e:
        return f"An error occurred while updating timezone: {e}"

@tool
async def update_event(event_id: str, current_user: Dict, new_start_time: str = None, new_summary: str = None) -> str:
    """
    Updates an existing event's time or title using its google_event_id. The user must be the owner. To reschedule, provide the `new_start_time`. The original duration will be preserved. This tool performs a final check to ensure the new time slot is available before committing.
    """
    db: AsyncIOMotorDatabase = get_db()
    events_collection = db.get_collection("events")

    event_doc = await events_collection.find_one({"google_event_id": event_id})
    if not event_doc:
        return f"Error: Event with ID '{event_id}' not found."
    if str(event_doc['owner_user_id']) != current_user['id']:
        return "Error: Permission Denied. You do not own this event."

    if not new_start_time and not new_summary:
        return "Error: You must provide a new start time or a new summary to update the event."

    original_start_utc = event_doc['start_time_utc']
    original_end_utc = event_doc['end_time_utc']
    db_update_payload = {}
    new_start_dt, new_end_dt = None, None

    if new_summary: db_update_payload['title'] = new_summary
    if new_start_time:
        user_tz = pytz.timezone(current_user.get('timezone', 'UTC'))
        duration = original_end_utc - original_start_utc
        new_start_dt = datetime.fromisoformat(new_start_time.replace('Z', ''))
        if new_start_dt.tzinfo is None: new_start_dt = user_tz.localize(new_start_dt)
        new_end_dt = new_start_dt + duration
        
        db_update_payload['start_time_utc'] = new_start_dt.astimezone(pytz.UTC)
        db_update_payload['end_time_utc'] = new_end_dt.astimezone(pytz.UTC)
    
    try:
        await events_collection.update_one({"google_event_id": event_id}, {"$set": db_update_payload})
    except DuplicateKeyError:
        return "Error: The requested new time slot is already booked. Please try another time."
    except Exception as e:
        return f"Error updating database: {e}"

    try:
        service = await run_in_threadpool(_get_calendar_service)
        event_on_google = await run_in_threadpool(service.events().get(calendarId=settings.CALENDAR_ID, eventId=event_id).execute)
        
        if new_summary: event_on_google['summary'] = new_summary
        if new_start_time:
            event_on_google['start']['dateTime'] = new_start_dt.isoformat()
            event_on_google['end']['dateTime'] = new_end_dt.isoformat()
        
        updated_event = await run_in_threadpool(
            service.events().update(calendarId=settings.CALENDAR_ID, eventId=event_id, body=event_on_google).execute
        )
        start = updated_event['start'].get('dateTime', updated_event['start'].get('date'))
        return f"Event '{updated_event['summary']}' updated successfully. It is now scheduled for {start}."
    except Exception as e:
        await events_collection.update_one(
            {"google_event_id": event_id},
            {"$set": {"start_time_utc": original_start_utc, "end_time_utc": original_end_utc}}
        )
        return f"Error: Failed to update Google Calendar after reserving slot. Reverted. Reason: {e}"

@tool
async def find_available_slots(date: str, user_timezone: str, duration_minutes: float = 30.0, current_user: Dict = None) -> List[str]:
    """
    Finds available meeting slots on a given date. Understands "today" or "tomorrow". Converts company's available slots into the user's local timezone.
    """
    db: AsyncIOMotorDatabase = get_db()
    events_collection = db.get_collection("events")
    try:
        duration, buffer = timedelta(minutes=int(duration_minutes)), timedelta(minutes=15)
        company_tz, user_tz = pytz.timezone(settings.COMPANY_TIMEZONE), pytz.timezone(user_timezone)
        now_in_user_tz = datetime.now(user_tz)
        
        target_date_obj = None
        if date.lower() == 'today': target_date_obj = now_in_user_tz.date()
        elif date.lower() == 'tomorrow': target_date_obj = (now_in_user_tz + timedelta(days=1)).date()
        else: target_date_obj = datetime.strptime(date, '%Y-%m-%d').date()

        user_req_date_aware = user_tz.localize(datetime.combine(target_date_obj, datetime.min.time()))

        if user_req_date_aware.date() < now_in_user_tz.date(): return ["The date you selected is in the past."]
        
        search_start_utc = (user_req_date_aware - timedelta(days=1)).astimezone(pytz.UTC)
        search_end_utc = (user_req_date_aware + timedelta(days=2)).astimezone(pytz.UTC)
        
        cursor = events_collection.find({"start_time_utc": {"$gte": search_start_utc, "$lt": search_end_utc}})
        busy_blocks_utc = [{"start": e['start_time_utc'].replace(tzinfo=pytz.UTC), "end": e['end_time_utc'].replace(tzinfo=pytz.UTC) + buffer} async for e in cursor]
        
        available_slots_in_user_tz = []
        for day_offset in range(2):
            day_to_check = (user_req_date_aware + timedelta(days=day_offset)).astimezone(company_tz)
            slot_runner = day_to_check.replace(hour=10, minute=0, second=0, microsecond=0)
            day_end = slot_runner.replace(hour=18)
            
            while slot_runner < day_end:
                slot_start_utc, slot_end_utc = slot_runner.astimezone(pytz.UTC), (slot_runner + duration).astimezone(pytz.UTC)
                if not any(slot_start_utc < block['end'] and slot_end_utc > block['start'] for block in busy_blocks_utc):
                    slot_in_user_tz = slot_start_utc.astimezone(user_tz)
                    if slot_in_user_tz > now_in_user_tz and slot_in_user_tz.date() == user_req_date_aware.date():
                        available_slots_in_user_tz.append(slot_in_user_tz.isoformat())
                slot_runner += timedelta(minutes=30)
        return sorted(list(set(available_slots_in_user_tz)))
    except Exception as e:
        return [f"An unexpected error occurred in find_available_slots: {e}"]

@tool
def propose_event(summary: str, start_time: str, end_time: str) -> Dict:
    """Use this tool to structure event details before creating it to allow the user to confirm."""
    return {"summary": summary, "start_time": start_time, "end_time": end_time}