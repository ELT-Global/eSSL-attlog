"""
Pydantic schemas for request/response models
"""

# Import commonly used schemas for easier access
from .actions import QueueCommandRequest, PlayVoiceRequest
from .common import APIResponse, ErrorResponse, PaginatedResponse, CleanupRequest
from .responses import (
    VoicePlayResponse, 
    CommandQueueResponse, 
    DeviceCommandsResponse, 
    AllCommandsResponse,
    CleanupResponse
)

__all__ = [
    # Action schemas
    'QueueCommandRequest',
    'PlayVoiceRequest',
    
    # Common schemas
    'APIResponse',
    'ErrorResponse', 
    'PaginatedResponse',
    'CleanupRequest',
    
    # Response schemas
    'VoicePlayResponse',
    'CommandQueueResponse',
    'DeviceCommandsResponse',
    'AllCommandsResponse',
    'CleanupResponse',
]