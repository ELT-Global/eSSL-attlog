from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_push_status():
    """Get push API status"""
    return {
        "message": "Push API is active",
        "data": {
            "version": "1.0.0",
            "status": "operational",
            "last_push": "2025-10-27T10:00:00",
            "pending_events": 5
        }
    }


@router.post("/")
async def receive_push():
    """Receive push data from eSSL devices"""
    return {
        "message": "Push data received successfully",
        "data": {
            "processed": True,
            "timestamp": "2025-10-27T10:40:00",
            "events_received": 1
        }
    }
