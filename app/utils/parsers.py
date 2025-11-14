from pydantic import BaseModel


def parse_attendance_line(line: str) -> dict:
    """Parse a single attendance log line and return structured data"""
    parts = line.strip().split()
    return {
        "PIN": parts[0] if len(parts) > 0 else "",
        "Timestamp": parts[1] + (" " + parts[2] if len(parts) > 2 else "") if len(parts) > 1 else "",
        "VerifyMode": parts[3] if len(parts) > 3 else "",
        "InOutMode": parts[4] if len(parts) > 4 else "",
        "WorkCode": parts[5] if len(parts) > 5 else "",
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