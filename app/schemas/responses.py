"""
Response Pydantic schemas
"""
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime


class VoicePlayResponse(BaseModel):
    """Response model for voice play operations"""
    message: str
    data: Dict[str, Any]


class CommandQueueResponse(BaseModel):
    """Response model for command queue operations"""
    message: str
    data: Dict[str, Any]


class DeviceCommandsResponse(BaseModel):
    """Response model for device commands retrieval"""
    message: str
    data: Dict[str, Any]


class AllCommandsResponse(BaseModel):
    """Response model for all commands retrieval"""
    message: str
    data: Dict[str, Any]


class CleanupResponse(BaseModel):
    """Response model for cleanup operations"""
    message: str
    data: Dict[str, Any]