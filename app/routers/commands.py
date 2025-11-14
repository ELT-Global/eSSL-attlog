"""
Device Command Management Router

This router handles command operations for ZKTeco devices using the new ADMS queue system.
Each device maintains its own ADMSQueue instance for better isolation and management.

Endpoints:
- GET /devices/{device_sn}/commands - List all commands for a device
- POST /devices/{device_sn}/commands:queue - Queue a new command for a device  
- POST /devices/{device_sn}/commands:cleanup - Clean up old acknowledged commands

Note: This replaces the legacy command_manager with individual device ADMS queues.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.actions import QueueCommandRequest
from app.utils.device_manager import device_manager
from app.utils.device import Device
import logging
from app.schemas.common import CleanupRequest
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("")
async def get_device_commands(device_sn: str):
    """
    Get all commands for a specific device from its ADMS queue
    
    Args:
        device_sn: Device serial number
        
    Returns:
        dict: Response containing all commands for the device
    """
    try:
        # Get device from device manager
        device = device_manager.get_device(device_sn)
        if device is None:
            raise HTTPException(status_code=404, detail=f"Device with SN {device_sn} not found")
        
        # Get all commands from the device's ADMS queue
        commands = device.adms_queue.commands
        
        # Convert commands to the expected format for response
        command_list = []
        for cmd in commands:
            command_list.append({
                "id": cmd["id"],
                "command": cmd["command"],
                "status": cmd["status"],
                "queued_at": cmd["queued_at"].isoformat(),
                "sent_at": cmd["sent_at"].isoformat() if cmd["sent_at"] else None,
                "ack_at": cmd["ack_at"].isoformat() if cmd["ack_at"] else None,
                "return_code": cmd["return_code"]
            })
        
        return {
            "message": f"Commands for device {device_sn}",
            "data": {
                "device_sn": device_sn,
                "commands": command_list,
                "total_commands": len(command_list),
                "pending_commands": len([cmd for cmd in commands if cmd['status'] == 'pending']),
                "sent_commands": len([cmd for cmd in commands if cmd['status'] == 'sent']),
                "completed_commands": len([cmd for cmd in commands if cmd['status'] == 'acked'])
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting commands for device {device_sn}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving commands")

@router.post(":queue")
async def queue_command(device_sn: str, request: QueueCommandRequest):
    """
    Queue a command for a device using its ADMS queue
    
    Args:
        device_sn: Device serial number
        request: QueueCommandRequest containing command
        
    Returns:
        dict: Response containing the queued command details
    """
    try:
        # Get device from device manager
        device = device_manager.get_device(device_sn)
        if device is None:
            raise HTTPException(status_code=404, detail=f"Device with SN {device_sn} not found")
        
        # Add command to the device's ADMS queue
        queued_command = device.adms_queue.add_command(request.command)
        
        logger.info(f"📋 Command queued successfully for device {device_sn}: {request.command}")
        
        return {
            "message": "Command queued successfully",
            "data": {
                "device_sn": device_sn,
                "command_id": queued_command['id'],
                "command": queued_command['command'],
                "status": queued_command['status'],
                "queued_at": queued_command['queued_at'].isoformat()
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
    Clean up completed (acknowledged) commands to prevent memory bloat
    
    Args:
        request: CleanupRequest containing optional device_sn and keep_last_n parameters
        
    Returns:
        dict: Response containing cleanup results
    """
    try:
        cleaned_count = 0
        
        if request.device_sn:
            # Clean up commands for a specific device
            device = device_manager.get_device(request.device_sn)
            if device is None:
                raise HTTPException(status_code=404, detail=f"Device with SN {request.device_sn} not found")
            
            cleaned_count = _cleanup_device_commands(device, request.keep_last_n)
            
        else:
            # Clean up commands for all devices
            devices = device_manager.list_devices()
            for device in devices:
                cleaned_count += _cleanup_device_commands(device, request.keep_last_n)
        
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


def _cleanup_device_commands(device: Device, keep_last_n: int = 10) -> int:
    """
    Helper function to clean up commands for a specific device
    
    Args:
        device: Device object containing ADMS queue
        keep_last_n: Number of completed commands to keep
        
    Returns:
        int: Number of commands cleaned up
    """
    # Get acknowledged commands sorted by ack_at time (newest first)
    acked_commands = [
        cmd for cmd in device.adms_queue.commands 
        if cmd['status'] == 'acked' and cmd['ack_at'] is not None
    ]
    # Sort by ack_at time, newest first (we know ack_at is not None due to filter above)
    acked_commands.sort(key=lambda x: x['ack_at'] or datetime.min, reverse=True)
    
    # Determine which commands to remove (keep the most recent keep_last_n)
    commands_to_remove = acked_commands[keep_last_n:] if len(acked_commands) > keep_last_n else []
    
    # Remove old acknowledged commands
    for cmd_to_remove in commands_to_remove:
        if cmd_to_remove in device.adms_queue.commands:
            device.adms_queue.commands.remove(cmd_to_remove)
    
    return len(commands_to_remove)
