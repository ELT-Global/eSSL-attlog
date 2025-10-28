"""
Data router for viewing saved attendance and operation data
"""
from fastapi import APIRouter, HTTPException
from app.utils.data_manager import data_manager
from typing import List, Dict, Any

router = APIRouter()

@router.get("/attendance")
async def get_attendance_data() -> List[Dict[Any, Any]]:
    """Get all attendance records from attendance.json"""
    try:
        return data_manager.get_all_data("attendance")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving attendance data: {str(e)}")

@router.get("/operations")
async def get_operations_data() -> List[Dict[Any, Any]]:
    """Get all operation records from operations.json"""
    try:
        return data_manager.get_all_data("operations")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving operations data: {str(e)}")

@router.get("/users")
async def get_users_data() -> List[Dict[Any, Any]]:
    """Get all user records from users.json"""
    try:
        return data_manager.get_all_data("users")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving users data: {str(e)}")

@router.get("/fingerprints")
async def get_fingerprints_data() -> List[Dict[Any, Any]]:
    """Get all fingerprint records from fingerprints.json"""
    try:
        return data_manager.get_all_data("fingerprints")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving fingerprints data: {str(e)}")

@router.get("/faces")
async def get_faces_data() -> List[Dict[Any, Any]]:
    """Get all face records from faces.json"""
    try:
        return data_manager.get_all_data("faces")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving faces data: {str(e)}")

@router.get("/summary")
async def get_data_summary():
    """Get a summary of all data counts"""
    try:
        return {
            "attendance_count": len(data_manager.get_all_data("attendance")),
            "operations_count": len(data_manager.get_all_data("operations")),
            "users_count": len(data_manager.get_all_data("users")),
            "fingerprints_count": len(data_manager.get_all_data("fingerprints")),
            "faces_count": len(data_manager.get_all_data("faces"))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data summary: {str(e)}")

@router.delete("/attendance")
async def clear_attendance_data():
    """Clear all attendance records"""
    try:
        data_manager.clear_data("attendance")
        return {"message": "Attendance data cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing attendance data: {str(e)}")

@router.delete("/operations")
async def clear_operations_data():
    """Clear all operation records"""
    try:
        data_manager.clear_data("operations")
        return {"message": "Operations data cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing operations data: {str(e)}")

@router.delete("/users")
async def clear_users_data():
    """Clear all user records"""
    try:
        data_manager.clear_data("users")
        return {"message": "Users data cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing users data: {str(e)}")

@router.delete("/fingerprints")
async def clear_fingerprints_data():
    """Clear all fingerprint records"""
    try:
        data_manager.clear_data("fingerprints")
        return {"message": "Fingerprints data cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing fingerprints data: {str(e)}")

@router.delete("/faces")
async def clear_faces_data():
    """Clear all face records"""
    try:
        data_manager.clear_data("faces")
        return {"message": "Faces data cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing faces data: {str(e)}")