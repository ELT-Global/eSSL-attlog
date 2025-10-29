from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.command_manager import command_manager
import logging
from app.utils.device_manager import device_manager


logger = logging.getLogger(__name__)

router = APIRouter()


class QueueCommandRequest(BaseModel):
    SN: str
    command: str

class PlayVoiceRequest(BaseModel):
    SN: str
    voice_id: int

@router.post("/play-voice")
async def play_voice(request: PlayVoiceRequest):
    """
    Play a voice prompt on the device
    
    Args:
        request: PlayVoiceRequest containing SN (device serial number) and voice_id
        
    Returns:
        dict: Response indicating success or failure
    """
    try:
        # Validate input
        if not request.SN or not request.SN.strip():
            raise HTTPException(status_code=400, detail="SN (device serial number) is required")
        
        if request.voice_id < 1:
            raise HTTPException(status_code=400, detail="voice_id must be a positive integer")
        
        # Retrieve the device
        device = device_manager.get_device(request.SN.strip())
        if device is None:
            raise HTTPException(status_code=404, detail=f"Device with SN {request.SN} not found")
        
        # Play the voice prompt
        device.play_voice(request.voice_id)
        
        logger.info(f"🔊 Voice ID {request.voice_id} played on device {request.SN}")
        
        return {
            "message": "Voice played successfully",
            "data": {
                "device_sn": request.SN,
                "voice_id": request.voice_id
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error playing voice on device {request.SN}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while playing voice")


@router.post("/queue-command")
async def queue_command(request: QueueCommandRequest):
    """
    Queue a command for a device
    
    Args:
        request: QueueCommandRequest containing SN (device serial number) and command
        
    Returns:
        dict: Response containing the queued command details
    """
    try:
        # Validate input
        if not request.SN or not request.SN.strip():
            raise HTTPException(status_code=400, detail="SN (device serial number) is required")
        
        if not request.command or not request.command.strip():
            raise HTTPException(status_code=400, detail="command is required")
        
        # Queue the command
        queued_command = command_manager.queue_command(request.SN.strip(), request.command.strip())
        
        logger.info(f"📋 Command queued successfully for device {request.SN}: {request.command}")
        
        return {
            "message": "Command queued successfully",
            "data": {
                "device_sn": request.SN,
                "command_id": queued_command['id'],
                "command": queued_command['command'],
                "status": queued_command['status'],
                "queued_at": queued_command['queuedAt']
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error queuing command for device {request.SN}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while queuing command")


@router.get("/commands/{device_sn}")
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


@router.get("/commands")
async def get_all_commands():
    """
    Get all commands for all devices
    
    Returns:
        dict: Response containing all commands for all devices
    """
    try:
        all_commands = command_manager.get_all_commands()
        
        # Calculate summary statistics
        total_devices = len(all_commands)
        total_commands = sum(len(commands) for commands in all_commands.values())
        
        device_summaries = {}
        for sn, commands in all_commands.items():
            device_summaries[sn] = {
                "total": len(commands),
                "pending": len([cmd for cmd in commands if cmd['status'] == 'pending']),
                "sent": len([cmd for cmd in commands if cmd['status'] == 'sent']),
                "completed": len([cmd for cmd in commands if cmd['status'] == 'done'])
            }
        
        return {
            "message": "All device commands",
            "data": {
                "commands": all_commands,
                "summary": {
                    "total_devices": total_devices,
                    "total_commands": total_commands,
                    "device_summaries": device_summaries
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting all commands: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving commands")


@router.post("/cleanup-commands")
async def cleanup_commands(device_sn: str | None = None, keep_last_n: int = 100):
    """
    Clean up completed commands to prevent memory bloat
    
    Args:
        device_sn: Optional device serial number (if not provided, cleanup all devices)
        keep_last_n: Number of completed commands to keep per device (default: 100)
        
    Returns:
        dict: Response containing cleanup results
    """
    try:
        if keep_last_n < 1:
            raise HTTPException(status_code=400, detail="keep_last_n must be at least 1")
        
        cleaned_count = command_manager.cleanup_completed_commands(device_sn, keep_last_n)
        
        return {
            "message": "Command cleanup completed",
            "data": {
                "device_sn": device_sn or "all",
                "commands_cleaned": cleaned_count,
                "commands_kept_per_device": keep_last_n
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during command cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during command cleanup")
