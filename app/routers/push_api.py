from fastapi import HTTPException, Depends
import os
from fastapi import APIRouter, Request, Response
from fastapi.responses import PlainTextResponse
import logging
from app.utils.parsers import parse_attendance_line, parse_operation_line, parse_user_line, parse_face_line, parse_fingerprint_line
from app.utils.command_manager import command_manager
from app.utils.data_manager import data_manager
from app.services.polling_service import polling_service
from app.utils.device_manager import device_manager
from app.utils.parse_info import parse_info
from app.utils.device import Device
from datetime import datetime, timedelta
import app.commands as COMMAND
from urllib.parse import parse_qs
from app.utils.network_scan import scanner

# Set up logging
logger = logging.getLogger(__name__)

# Constants
CURRENT_TIMESTAMP = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
last_attlog = datetime.now() - timedelta(minutes=10)
ATTLOG_FREQUENCY_MINUTES = 5  # in minutes

def validate_token(request: Request):
    token = request.path_params.get("token")
    expected = os.getenv("DEVICE_API_TOKEN")
    if token != expected:
        raise HTTPException(status_code=403, detail="Invalid token")
    
router = APIRouter(dependencies=[Depends(validate_token)])

@router.get("/getrequest.aspx")
async def get_request(request: Request):
    """The device polls this endpoint for commands."""
    query_params = dict(request.query_params)
    SN = query_params.get("SN")
    if not SN:
        logger.warning("⚠️ getrequest.aspx called without SN parameter.")
        raise HTTPException(status_code=400, detail="Missing SN parameter")

    # Log device info if provided
    INFO = query_params.get("INFO")
    
    device_command_response = polling_service.get_commands(SN, INFO)
    return PlainTextResponse(device_command_response)

@router.get("/cdata.aspx")
async def get_cdata(request: Request):
    """Handle GET /cdata.aspx"""
    query_params = dict(request.query_params)
    SN = query_params.get("SN")
    if not SN:
        logger.warning("⚠️ cdata.aspx called without SN parameter.")
        raise HTTPException(status_code=400, detail="Missing SN parameter")
    
    table = query_params.get("table")
    options = query_params.get("options")
    
    if options:
        logger.info(f"🔄️ Machine ID: '{SN}' initialized with options: {options}")
    else:
        logger.info(f"🔄️ Machine ID: '{SN}' requested data for Table: '{table}'.")

    return PlainTextResponse(COMMAND.ACK)

@router.post("/cdata.aspx")
async def post_cdata(request: Request):
    """Handles attendance and operation log data sent by the device."""
    query_params = dict(request.query_params)
    
    SN = query_params.get("SN")
    table = query_params.get("table")
    stamp = query_params.get("Stamp")
    
    logger.info(f"🔄️ Machine ID: '{SN}' sent data for Table: '{table}' [{stamp}].")
    body = await request.body()
    body_str = body.decode('utf-8') if body else ""
    
    if table == "ATTLOG":
        lines = body_str.splitlines()
        attendance_records = [parse_attendance_line(line) for line in lines if line.strip()]
        logger.info(f"📥 Received {len(attendance_records)} attendance records from Machine ID: '{SN}'.")
        
        # Save attendance records to /data/attendance.json
        data_manager.sync_attendance_records(attendance_records, SN)
        
        return PlainTextResponse(COMMAND.ACK_ATTLOG)
    elif table == "OPERLOG":
        lines = body_str.splitlines()
        operation_records = [line.strip() for line in lines if line.strip()]
        
        operations = [parse_operation_line(l) for l in lines if l.strip() and l.startswith("OPLOG")]
        users = [parse_user_line(l) for l in lines if l.strip() and l.startswith("USER")]
        fingerprints = [parse_fingerprint_line(l) for l in lines if l.strip() and l.startswith("FP")]
        faces = [parse_face_line(l) for l in lines if l.strip() and l.startswith("Face")]
        
        logger.info(f"📥 Received {len(operation_records)} operation logs from Machine ID: '{SN}'.")
        logger.info(f"\tIncludes: {len(operations)} OPLOG entries, {len(users)} USER entries, {len(fingerprints)} FP entries, {len(faces)} Face entries.")
        
        # Save each type of data to their respective JSON files
        data_manager.sync_operations(operations, SN)
        data_manager.sync_users(users, SN)
        data_manager.sync_fingerprints(fingerprints, SN)
        data_manager.sync_faces(faces, SN)
        
        return PlainTextResponse(COMMAND.ACK_OPERLOG)
    else:
        logger.warning(f"Received data for unsupported table '{table}' from Machine ID: '{SN}'.")
        return PlainTextResponse(COMMAND.ACK)


def _process_command_acknowledgment_post(sn: str, body_data: dict) -> None:
    """Process command acknowledgment from POST body"""
    cmd_id = body_data.get('ID')
    return_code = body_data.get('Return')
    cmd_text = body_data.get('CMD')
    
    if not (sn and cmd_id and cmd_text):
        return
    
    try:
        command_id = int(cmd_id)
        device_ack = 'OK' if return_code == '0' else 'ERR'
        
        success = command_manager.acknowledge_command(sn, command_id, device_ack)
        if success:
            logger.info(f"✅ Command C:{cmd_id}:{cmd_text} acknowledged by device {sn} -> Return={return_code}")
        else:
            logger.warning(f"⚠️ Unknown command ack C:{cmd_id}:{cmd_text} from device {sn}")
            
    except (ValueError, TypeError) as e:
        logger.warning(f"⚠️ Could not parse POST command ack from device {sn}: {e}")


@router.post("/devicecmd.aspx")
async def device_command_post(request: Request):
    """Handle POST /devicecmd.aspx - process command acknowledgments and return plain text 'OK'"""
    query_params = dict(request.query_params)
    SN = query_params.get("SN", "")
    
    try:
        body = await request.body()
        body_str = body.decode('utf-8') if body else ""
        logger.info(f"POST /devicecmd.aspx called with params: {query_params}, body: {body_str[:200]}")
        
        # Try to parse as form data for the new format
        if body_str and "=" in body_str:
            parsed_body = parse_qs(body_str)
            body_data = {k: v[0] if v else "" for k, v in parsed_body.items()}
            
            # Also check SN from body
            if not SN and 'SN' in body_data:
                SN = body_data['SN']
            
            _process_command_acknowledgment_post(SN, body_data)
        
    except Exception as e:
        logger.warning(f"Could not process POST /devicecmd.aspx: {e}")
    
    return PlainTextResponse(COMMAND.ACK)


# Catch-all route to log unknown requests
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def catch_all_unknown_requests(request: Request, path: str):
    """Catch and log all unknown requests to this router"""
    logger.info(f"Incoming request: {request.method} {request.url.path} - Query params: {dict(request.query_params)}")
    logger.info(f"Headers: {dict(request.headers)}")

    method = request.method
    query_params = dict(request.query_params)
    
    logger.warning(f"UNKNOWN REQUEST: {method} /{path} - Query params: {query_params}")
    
    try:
        if method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            if body:
                body_str = body.decode('utf-8')
                logger.info(f"Unknown request body (first 500 chars): {body_str[:500]}")
    except Exception as e:
        logger.warning(f"Could not read body for unknown request: {e}")
    
    return {
        "status": "NOT_IMPLEMENTED",
        "message": f"Unknown endpoint: {method} /{path}",
        "method": method,
        "path": path,
        "params": query_params,
        "timestamp": CURRENT_TIMESTAMP,
        "note": "This request has been logged for analysis"
    }
