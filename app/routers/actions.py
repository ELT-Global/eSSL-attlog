from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_actions():
    """Get all actions"""
    return {
        "message": "Get all actions",
        "data": [
            {
                "id": 1,
                "action_type": "sync",
                "timestamp": "2025-10-27T09:00:00",
                "status": "completed"
            },
            {
                "id": 2,
                "action_type": "backup",
                "timestamp": "2025-10-27T09:30:00",
                "status": "in_progress"
            }
        ]
    }


@router.post("/")
async def create_action():
    """Create a new action"""
    return {
        "message": "Action created successfully",
        "data": {
            "id": 3,
            "action_type": "restore",
            "timestamp": "2025-10-27T10:00:00",
            "status": "pending"
        }
    }
