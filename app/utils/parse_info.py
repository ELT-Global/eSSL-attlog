from pydantic import BaseModel
from enum import IntEnum
from typing import Optional

class DeviceFunction(IntEnum):
    """Device function identifiers based on position in function support string.
    
    Each digit in the function support string represents whether a specific
    function is supported (1) or not supported (0).
    """
    FINGERPRINT = 1         # Position 1: Fingerprint function
    FACE = 2               # Position 2: Face function  
    USER_PHOTO = 3         # Position 3: User photo function
    COMPARISON_PHOTO = 4   # Position 4: Comparison photo function (requires BioPhotoFun=1)
    VISIBLE_LIGHT_FACE = 5 # Position 5: Visible light face template function (requires BioDataFun=1)

class DeviceFunctionSupport(BaseModel):
    """Structured representation of device function support capabilities."""
    fingerprint_supported: bool
    face_supported: bool  
    user_photo_supported: bool
    comparison_photo_supported: Optional[bool] = None
    visible_light_face_supported: Optional[bool] = None
    raw_value: str

def parse_device_functions(function_str: str) -> DeviceFunctionSupport:
    """Parse device function support string into structured format.
    
    Args:
        function_str: String of digits (e.g., "101", "10110") where each digit
                     represents function support (0=not supported, 1=supported)
                     
    Returns:
        DeviceFunctionSupport object with parsed capabilities
        
    Raises:
        ValueError: If function_str is invalid or too short
    """
    if not function_str or len(function_str) < 3:
        raise ValueError("Function support string must be at least 3 digits long")
    
    # Validate that all characters are 0 or 1
    if not all(c in '01' for c in function_str):
        raise ValueError("Function support string must contain only 0 and 1 digits")
    
    # Parse required functions (first 3 digits)
    fingerprint_supported = function_str[0] == '1'
    face_supported = function_str[1] == '1'
    user_photo_supported = function_str[2] == '1'
    
    # Parse optional functions (digits 4-5 if present)
    comparison_photo_supported = None
    visible_light_face_supported = None
    
    if len(function_str) >= 4:
        comparison_photo_supported = function_str[3] == '1'
    
    if len(function_str) >= 5:
        visible_light_face_supported = function_str[4] == '1'
    
    return DeviceFunctionSupport(
        fingerprint_supported=fingerprint_supported,
        face_supported=face_supported,
        user_photo_supported=user_photo_supported,
        comparison_photo_supported=comparison_photo_supported,
        visible_light_face_supported=visible_light_face_supported,
        raw_value=function_str
    )

class GetRequestInfo(BaseModel):
    firmware_version: str
    user_count: int
    fingerprint_count: int
    attendance_count: int
    ip_address: str
    fingerprint_algorithm_version: str
    face_algorithm_version: str
    face_enrollment_count: int
    enrolled_face_count: int
    function_support: DeviceFunctionSupport
 
def parse_info(info_str: str) -> GetRequestInfo:
    """Parse the INFO string from the device and return a structured GetRequestInfo object."""
    parts = info_str.split(',')
    if len(parts) < 10:
        raise ValueError("INFO string does not contain enough parts")
    
    # Parse function support string (default to "000" if not present)
    function_str = parts[9] if len(parts) > 9 and parts[9] else "000"
    function_support = parse_device_functions(function_str)
    
    return GetRequestInfo(
        firmware_version=parts[0],
        user_count=int(parts[1]),
        fingerprint_count=int(parts[2]),
        attendance_count=int(parts[3]),
        ip_address=parts[4],
        fingerprint_algorithm_version=parts[5],
        face_algorithm_version=parts[6],
        face_enrollment_count=int(parts[7]),
        enrolled_face_count=int(parts[8]),
        function_support=function_support
    )