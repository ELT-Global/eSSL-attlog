"""
Common Pydantic schemas used across multiple modules
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from datetime import datetime


class APIResponse(BaseModel):
    """Generic API response wrapper"""
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    message: str
    data: Dict[str, Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class CleanupRequest(BaseModel):
    """Request model for cleanup operations"""
    model_config = {"str_strip_whitespace": True}
    
    device_sn: Optional[str] = Field(None, description="Device serial number (optional)")
    keep_last_n: int = Field(
        default=100, 
        ge=1, 
        description="Number of items to keep (minimum 1)"
    )