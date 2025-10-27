from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_users():
    """Get all users"""
    return {
        "message": "Get all users",
        "data": [
            {
                "id": "101",
                "name": "John Doe",
                "department": "Engineering"
            },
            {
                "id": "102",
                "name": "Jane Smith",
                "department": "Marketing"
            }
        ]
    }


@router.post("/")
async def create_user():
    """Create a new user"""
    return {
        "message": "User created successfully",
        "data": {
            "id": "103",
            "name": "Bob Johnson",
            "department": "Sales"
        }
    }
