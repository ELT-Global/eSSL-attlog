from fastapi import APIRouter, Request, Response
from fastapi.responses import PlainTextResponse
import logging
from app.utils.parsers import parse_attendance_line, parse_operation_line, parse_user_line, parse_face_line, parse_fingerprint_line
from app.utils.command_manager import command_manager
from app.utils.data_manager import data_manager
from datetime import datetime, timedelta
import app.commands as COMMAND
from urllib.parse import parse_qs

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CURRENT_TIMESTAMP = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
last_attlog = datetime.now() - timedelta(minutes=10)
ATTLOG_FREQUENCY_MINUTES = 5  # in minutes

router = APIRouter()

def log_request(request: Request):
    """Helper function to log incoming requests"""
    logger.info(f"Incoming request: {request.method} {request.url.path} - Query params: {dict(request.query_params)}")
    logger.info(f"Headers: {dict(request.headers)}")

@router.get("/getrequest.aspx")
async def get_request(request: Request):
    global last_attlog, stamp
    """The device polls this endpoint for commands."""
    query_params = dict(request.query_params)
    SN = query_params.get("SN")
    logger.info(f"[Heartbeat 💓] Machine ID: '{SN}' polled for commands.")
    
    # Log device info if provided
    INFO = query_params.get("INFO")
    if INFO is not None:
        logger.info(f"\tℹ️ INFO parameter received: {INFO}")
        info_tokens = INFO.split(',')
        firmware_version = info_tokens[0] if len(info_tokens) > 0 else "Unknown"
        device_type = info_tokens[1] if len(info_tokens) > 1 else "Unknown"
        device_ip = info_tokens[4] if len(info_tokens) > 4 else "Unknown"
        logger.info(f"\t\tDevice Info - Firmware: {firmware_version}, Type: {device_type}, IP: {device_ip}")
    
    if datetime.now() - last_attlog > timedelta(minutes=ATTLOG_FREQUENCY_MINUTES) and SN is not None:
        logger.info(f"\t⏰ It's time to send attendance logs (every {ATTLOG_FREQUENCY_MINUTES} minutes).")
        last_attlog = datetime.now()
        command_manager.queue_command(SN, COMMAND.QUERY_ATTLOG)
    
    # Check if there are any pending commands for this device
    if SN:
        pending_commands = command_manager.get_pending_commands(SN)
        if pending_commands:
            # Build response: one command per line as "C:<id>:<command>"
            lines = [f"C:{cmd['id']}:{cmd['command']}" for cmd in pending_commands]
            response_text = '\n'.join(lines) + '\n'  # trailing newline is important
            
            logger.info(f"📤 Delivering {len(pending_commands)} commands to device {SN}")
            return PlainTextResponse(response_text)
    
    # No commands or no device SN - return OK
    return PlainTextResponse(COMMAND.ACK)

@router.get("/cdata.aspx")
async def get_cdata(request: Request):
    """Handle GET /cdata.aspx"""
    query_params = dict(request.query_params)
    SN = query_params.get("SN")
    table = query_params.get("table")
    op_stamp = query_params.get("OpStamp")
    logger.info(f"🔄️ Machine ID: '{SN}' requested data for Table: '{table}' [{op_stamp}].")

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
    log_request(request)
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
