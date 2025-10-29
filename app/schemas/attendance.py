"""
Attendance-related Pydantic schemas
Example for future implementation
"""
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from datetime import datetime
from enum import Enum


class AttendanceStatus(str, Enum):
    """Attendance status enumeration"""
    CHECK_IN = "check-in"
    CHECK_OUT = "check-out"
    BREAK_START = "break-start"
    BREAK_END = "break-end"


class CreateAttendanceRequest(BaseModel):
    """Request model for creating attendance records"""
    model_config = {"str_strip_whitespace": True}
    
    user_id: Annotated[str, Field(
        min_length=1,
        description="User ID"
    )]
    device_sn: Annotated[str, Field(
        min_length=1,
        description="Device serial number"
    )]
    status: AttendanceStatus = Field(
        description="Attendance status"
    )
    timestamp: Optional[datetime] = Field(
        default=None,
        description="Timestamp (auto-generated if not provided)"
    )


class AttendanceRecord(BaseModel):
    """Attendance record model"""
    id: int
    user_id: str
    device_sn: str
    status: AttendanceStatus
    timestamp: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None


class GetAttendanceQuery(BaseModel):
    """Query parameters for getting attendance records"""
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    device_sn: Optional[str] = Field(None, description="Filter by device serial number")
    status: Optional[AttendanceStatus] = Field(None, description="Filter by status")
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Page size")