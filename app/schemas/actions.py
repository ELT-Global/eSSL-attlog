"""
Action-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from datetime import datetime


class QueueCommandRequest(BaseModel):
    """Request model for queueing commands to devices"""
    model_config = {"str_strip_whitespace": True}
    
    command: Annotated[str, Field(
        min_length=1,
        description="Command to queue for the device"
    )]


class PlayVoiceRequest(BaseModel):
    """Request model for playing voice prompts on devices"""
    model_config = {"str_strip_whitespace": True}
    
    voice_id: Annotated[int, Field(
        ge=1,
        description="Voice prompt ID (must be positive)"
    )]


class CommandResponse(BaseModel):
    """Response model for command operations"""
    device_sn: str
    command_id: str
    command: str
    status: str
    queued_at: str


class VoiceResponse(BaseModel):
    """Response model for voice operations"""
    device_sn: str
    voice_id: int


class SetTimeRequest(BaseModel):
    """Request model for setting device time"""
    model_config = {"str_strip_whitespace": True}
    
    new_time: Optional[datetime] = Field(
        default=None,
        description="New time to set on device (ISO format). If not provided, current time will be used."
    )


class DeviceStatsResponse(BaseModel):
    """Response model for device statistics"""
    device_sn: str
    stats: dict


class SocketModeRequest(BaseModel):
    """Request model for setting socket mode"""
    model_config = {"str_strip_whitespace": True}
    
    is_on: bool = Field(
        default=True,
        description="Whether to enable or disable socket mode"
    )
    force: bool = Field(
        default=False,
        description="Force reconnection even if already in desired state"
    )


class APIResponse(BaseModel):
    """Generic API response wrapper"""
    message: str
    data: dict