from fastapi import APIRouter, HTTPException
from app.utils.command_manager import command_manager
import logging
from datetime import datetime
from app.utils.device_manager import device_manager
from app.schemas.actions import (
    PlayVoiceRequest, 
    SetTimeRequest, 
    SocketModeRequest
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("play-voice")
async def play_voice(device_sn: str, request: PlayVoiceRequest):
    """
    Play a voice prompt on the device
    
    Args:
        device_sn: Device serial number
        request: PlayVoiceRequest containing voice_id
        
    Returns:
        dict: Response indicating success or failure
    """
    try:
        # Retrieve the device (Pydantic handles validation automatically)
        device = device_manager.get_device(device_sn)
        if device is None:
            raise HTTPException(status_code=404, detail=f"Device with SN {device_sn} not found")
        
        # Play the voice prompt
        device.play_voice(request.voice_id)
        
        logger.info(f"🔊 Voice ID {request.voice_id} played on device {device_sn}")
        
        return {
            "message": "Voice played successfully",
            "data": {
                "device_sn": device_sn,
                "voice_id": request.voice_id
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error playing voice on device {device_sn}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while playing voice")

@router.post("restart")
async def restart_device(device_sn: str):
    """
    Restart a device remotely
    
    Args:
        device_sn: Device serial number
        
    Returns:
        dict: Response indicating success or failure
    """
    try:
        device = device_manager.get_device(device_sn)
        if device is None:
            raise HTTPException(status_code=404, detail=f"Device with SN {device_sn} not found")
        
        device.restart()
        
        logger.info(f"🔄 Device {device_sn} restart initiated")
        
        return {
            "message": "Device restart initiated",
            "data": {
                "device_sn": device_sn,
                "action": "restart"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restarting device {device_sn}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while restarting device")


@router.post("poweroff")
async def poweroff_device(device_sn: str):
    """
    Shutdown a device remotely
    
    Args:
        device_sn: Device serial number
        
    Returns:
        dict: Response indicating success or failure
    """
    try:
        device = device_manager.get_device(device_sn)
        if device is None:
            raise HTTPException(status_code=404, detail=f"Device with SN {device_sn} not found")
        
        device.poweroff()
        
        logger.info(f"🛑 Device {device_sn} shutdown initiated")
        
        return {
            "message": "Device shutdown initiated",
            "data": {
                "device_sn": device_sn,
                "action": "poweroff"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error shutting down device {device_sn}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while shutting down device")

@router.post("sync-users")
async def sync_users(device_sn: str):
    """
    Sync user data from the device
    
    Args:
        device_sn: Device serial number
        
    Returns:
        dict: Response indicating sync completion
    """
    try:
        device = device_manager.get_device(device_sn)
        if device is None:
            raise HTTPException(status_code=404, detail=f"Device with SN {device_sn} not found")
        
        device.sync_users()
        
        logger.info(f"👥 User sync completed for device {device_sn}")
        
        return {
            "message": "User sync completed",
            "data": {
                "device_sn": device_sn,
                "action": "sync_users"
            }
        }
    
    except HTTPException:
        raise
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Device connection error: {str(e)}")
    except Exception as e:
        logger.error(f"Error syncing users for device {device_sn}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while syncing users")

@router.post("set-time")
async def set_device_time(device_sn: str, request: SetTimeRequest):
    """
    Set the device's internal clock
    
    Args:
        device_sn: Device serial number
        request: SetTimeRequest containing optional new time
        
    Returns:
        dict: Response indicating time set completion
    """
    try:
        device = device_manager.get_device(device_sn)
        if device is None:
            raise HTTPException(status_code=404, detail=f"Device with SN {device_sn} not found")
        
        device.set_time(request.new_time)
        
        target_time = request.new_time or datetime.now()
        logger.info(f"⏰ Time set for device {device_sn} to {target_time}")
        
        return {
            "message": "Device time set successfully",
            "data": {
                "device_sn": device_sn,
                "time_set": target_time.isoformat()
            }
        }
    
    except HTTPException:
        raise
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Device connection error: {str(e)}")
    except Exception as e:
        logger.error(f"Error setting time for device {device_sn}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while setting device time")

@router.get("get-socket-mode")
async def get_socket_status(device_sn: str):
    """
    Get socket connection status for a device
    
    Args:
        device_sn: Device serial number
        
    Returns:
        dict: Response containing socket connection status
    """
    try:
        device = device_manager.get_device(device_sn)
        if device is None:
            raise HTTPException(status_code=404, detail=f"Device with SN {device_sn} not found")
        
        is_connected = device.is_socket_mode()
        
        return {
            "message": f"Socket status for device {device_sn}",
            "data": {
                "device_sn": device_sn,
                "socket_mode": is_connected,
                "connection_status": "connected" if is_connected else "disconnected"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting socket status for device {device_sn}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while getting socket status")

@router.post("set-socket-mode")
async def set_socket_mode(device_sn: str, request: SocketModeRequest):
    """
    Set socket mode (TCP connection) for a device
    
    Args:
        device_sn: Device serial number
        request: SocketModeRequest containing socket mode settings
        
    Returns:
        dict: Response indicating socket mode status
    """
    try:
        device = device_manager.get_device(device_sn)
        if device is None:
            raise HTTPException(status_code=404, detail=f"Device with SN {device_sn} not found")
        
        device.set_socket_mode(request.is_on, request.force)
        
        status = "enabled" if request.is_on else "disabled"
        logger.info(f"🔌 Socket mode {status} for device {device_sn}")
        
        return {
            "message": f"Socket mode {status}",
            "data": {
                "device_sn": device_sn,
                "socket_mode": request.is_on,
                "is_connected": device.is_socket_mode()
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting socket mode for device {device_sn}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while setting socket mode")
