from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_attendance():
    """Get attendance records"""
    return {
        "message": "Get attendance records",
        "data": [
            {
                "id": 1,
                "user_id": "101",
                "timestamp": "2025-10-27T10:00:00",
                "status": "check-in"
            },
            {
                "id": 2,
                "user_id": "102",
                "timestamp": "2025-10-27T10:15:00",
                "status": "check-in"
            }
        ]
    }


@router.post("/")
async def create_attendance():
    """Create a new attendance record"""
    return {
        "message": "Attendance record created successfully",
        "data": {
            "id": 3,
            "user_id": "103",
            "timestamp": "2025-10-27T10:30:00",
            "status": "check-in"
        }
    }
