from fastapi import APIRouter, HTTPException
from app.schemas.actions import QueueCommandRequest
from app.utils.command_manager import command_manager
import logging
from app.schemas.common import CleanupRequest

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("")
async def get_device_commands(device_sn: str):
    """
    Get all commands for a specific device
    
    Args:
        device_sn: Device serial number
        
    Returns:
        dict: Response containing all commands for the device
    """
    try:
        commands = command_manager.get_device_commands(device_sn)
        
        return {
            "message": f"Commands for device {device_sn}",
            "data": {
                "device_sn": device_sn,
                "commands": commands,
                "total_commands": len(commands),
                "pending_commands": len([cmd for cmd in commands if cmd['status'] == 'pending']),
                "sent_commands": len([cmd for cmd in commands if cmd['status'] == 'sent']),
                "completed_commands": len([cmd for cmd in commands if cmd['status'] == 'done'])
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting commands for device {device_sn}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving commands")

@router.post(":queue")
async def queue_command(device_sn: str, request: QueueCommandRequest):
    """
    Queue a command for a device
    
    Args:
        device_sn: Device serial number
        request: QueueCommandRequest containing command
        
    Returns:
        dict: Response containing the queued command details
    """
    try:
        # Queue the command (Pydantic handles validation automatically)
        queued_command = command_manager.queue_command(device_sn, request.command)
        
        logger.info(f"📋 Command queued successfully for device {device_sn}: {request.command}")
        
        return {
            "message": "Command queued successfully",
            "data": {
                "device_sn": device_sn,
                "command_id": queued_command['id'],
                "command": queued_command['command'],
                "status": queued_command['status'],
                "queued_at": queued_command['queuedAt']
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error queuing command for device {device_sn}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while queuing command")

@router.post(":cleanup")
async def cleanup_commands(request: CleanupRequest):
    """
    Clean up completed commands to prevent memory bloat
    
    Args:
        request: CleanupRequest containing optional device_sn and keep_last_n parameters
        
    Returns:
        dict: Response containing cleanup results
    """
    try:
        cleaned_count = command_manager.cleanup_completed_commands(
            request.device_sn, 
            request.keep_last_n
        )
        
        return {
            "message": "Command cleanup completed",
            "data": {
                "device_sn": request.device_sn or "all",
                "commands_cleaned": cleaned_count,
                "commands_kept_per_device": request.keep_last_n
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during command cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during command cleanup")
