from pydantic import BaseModel

def parse_attendance_line(line: str) -> dict:
    """
    Parse a single attendance log line and return structured data.
    
    Format: `${Pin}${HT}${Time}${HT}${Status}${HT}${Verify}${HT}${Workcode}${HT}${Reserved}${HT}${Reserved}`
    
    Where:
    - `${Pin}`: User PIN/ID
    - `${Time}`: Verification time in format YYYY-MM-DD HH:MM:SS (e.g., 2015-07-29 11:11:11)
    - `${Status}`: Status code (typically 0 or 1 for In/Out)
    - `${Verify}`: Verification method (fingerprint, card, password, etc.)
    - `${Workcode}`: Work code (optional)
    - `${Reserved}`: Reserved fields (typically empty)
    - `${HT}`: Horizontal tab character as field separator
    
    Args:
        line: Raw attendance log line from device
        
    Returns:
        dict: Parsed attendance data with standardized field names
    """
    parts = line.strip().split('\t')  # Use tab separator as per ADMS protocol
    
    return {
        "PIN": parts[0] if len(parts) > 0 else "",
        "Time": parts[1] if len(parts) > 1 else "",  # Full timestamp as single field
        "Status": parts[2] if len(parts) > 2 else "",  # In/Out status
        "Verify": parts[3] if len(parts) > 3 else "",  # Verification method
        "Workcode": parts[4] if len(parts) > 4 else "",  # Work code
        "Reserved1": parts[5] if len(parts) > 5 else "",  # First reserved field
        "Reserved2": parts[6] if len(parts) > 6 else "",  # Second reserved field
    }

class AckLine(BaseModel):
    ID: str
    Return: str
    CMD: str

def parse_ack_line(line: str) -> AckLine:
    """Parse acknowledgment line into parameters dictionary."""
    ack_params = {}
    for param in line.split('&'):
        if '=' in param:
            key, value = param.split('=', 1)
            ack_params[key] = value
    return AckLine(**ack_params)

def parse_user_line(line: str) -> dict:
    """Parse a user line and return structured data"""
    fields = {}
    pairs = line.split()
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            fields[key] = value if value else ""
    
    return {
        "PIN": fields.get("PIN", ""),
        "Name": fields.get("Name", ""),
        "Privilege": int(fields.get("Pri", "0")) if fields.get("Pri", "").isdigit() else 0,
        "Password": fields.get("Passwd", ""),
        "Card": fields.get("Card", ""),
    }

def parse_operation_line(line: str) -> dict:
    """Parse an operation line and return structured data"""
    # Remove "OPLOG " prefix if present
    clean_line = line.replace("OPLOG ", "", 1) if line.startswith("OPLOG ") else line
    parts = clean_line.split("\t")
    
    return {
        "userPin": parts[1] if len(parts) > 1 else None,
        "codeNumber": parts[0] if len(parts) > 0 else None,
    }

def parse_face_line(line: str) -> dict:
    """Parse a face line and return structured data"""
    fields = {}
    pairs = line.split()
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            fields[key] = value if value else ""
    
    return {
        "pin": fields.get("PIN", ""),
        "faceId": fields.get("FID", ""),
        "size": int(fields.get("SIZE", "0")) if fields.get("SIZE", "").isdigit() else 0,
        "valid": int(fields.get("VALID", "0")) if fields.get("VALID", "").isdigit() else 0,
        "template": fields.get("TMP", ""),
    }

def parse_fingerprint_line(line: str) -> dict:
    """Parse a fingerprint line and return structured data"""
    fields = {}
    pairs = line.split()
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            fields[key] = value if value else ""
    
    return {
        "pin": fields.get("PIN", ""),
        "fingerId": fields.get("FID", ""),
        "size": int(fields.get("Size", "0")) if fields.get("Size", "").isdigit() else 0,
        "valid": int(fields.get("Valid", "0")) if fields.get("Valid", "").isdigit() else 0,
        "template": fields.get("TMP", ""),
    }