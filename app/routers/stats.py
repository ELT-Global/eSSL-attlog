from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_stats():
    """Get statistics"""
    return {
        "message": "Get statistics",
        "data": {
            "total_users": 150,
            "total_attendance_records": 1250,
            "today_check_ins": 85,
            "today_check_outs": 42,
            "active_devices": 3
        }
    }


@router.post("/")
async def update_stats():
    """Update or recalculate statistics"""
    return {
        "message": "Statistics updated successfully",
        "data": {
            "last_updated": "2025-10-27T10:35:00",
            "status": "success"
        }
    }
