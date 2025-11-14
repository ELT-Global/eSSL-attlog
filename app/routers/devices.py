from fastapi import APIRouter, HTTPException
from app.utils.device_manager import device_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
async def get_connected_devices():
    """
    Get all currently connected devices managed by the device manager.
    
    Returns:
        dict: Response containing list of connected devices with their details
    """
    try:
        devices = device_manager.list_devices()
        
        device_list = []
        for device in devices:
            device_info = {
                "sn": device.sn,
                "ip": device.ip,
                "port": device.port,
                "connection_mode": device.connection_mode,
                "is_socket_connected": device.is_socket_mode(),
                "connected_at": device.connected_at.isoformat() if device.connected_at else None,
                "pending_commands_count": len(device.get_pending_commands())
            }
            
            # Add device info if available
            if device.info:
                device_info.update({
                    "device_info": {
                        "model": getattr(device.info, 'model', None),
                        "firmware_version": getattr(device.info, 'firmware_version', None),
                        "platform": getattr(device.info, 'platform', None),
                        "device_name": getattr(device.info, 'device_name', None)
                    }
                })
            
            device_list.append(device_info)
        
        return {
            "message": f"Found {len(device_list)} connected device(s)",
            "data": {
                "devices": device_list,
                "total_count": len(device_list)
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving connected devices: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving connected devices")


@router.get("/{device_sn}")
async def get_device_details(device_sn: str):
    """
    Get detailed information about a specific device by its serial number.
    
    Args:
        device_sn: Device serial number
        
    Returns:
        dict: Response containing detailed device information
    """
    try:
        device = device_manager.get_device(device_sn)
        if device is None:
            raise HTTPException(status_code=404, detail=f"Device with SN {device_sn} not found")
        
        device_details = {
            "sn": device.sn,
            "ip": device.ip,
            "port": device.port,
            "password": "***" if device.password else None,  # Mask password for security
            "connection_mode": device.connection_mode,
            "is_socket_connected": device.is_socket_mode(),
            "connected_at": device.connected_at.isoformat() if device.connected_at else None,
            "pending_commands": [
                {
                    "id": cmd["id"],
                    "command": cmd["command"],
                    "status": cmd["status"],
                    "queued_at": cmd["queued_at"].isoformat(),
                    "sent_at": cmd["sent_at"].isoformat() if cmd["sent_at"] else None,
                    "ack_at": cmd["ack_at"].isoformat() if cmd["ack_at"] else None,
                    "return_code": cmd["return_code"]
                }
                for cmd in device.get_pending_commands()
            ]
        }
        
        # Add device info if available
        if device.info:
            device_details["device_info"] = {
                "model": getattr(device.info, 'model', None),
                "firmware_version": getattr(device.info, 'firmware_version', None),
                "platform": getattr(device.info, 'platform', None),
                "device_name": getattr(device.info, 'device_name', None),
                "mac_address": getattr(device.info, 'mac_address', None),
                "serial_number": getattr(device.info, 'serial_number', None)
            }
        
        return {
            "message": f"Device details for {device_sn}",
            "data": device_details
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving device details for {device_sn}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving device details")


@router.get("/{device_sn}/status")
async def get_device_status(device_sn: str):
    """
    Get the current status of a specific device (connection, socket mode, etc.).
    
    Args:
        device_sn: Device serial number
        
    Returns:
        dict: Response containing device status information
    """
    try:
        device = device_manager.get_device(device_sn)
        if device is None:
            raise HTTPException(status_code=404, detail=f"Device with SN {device_sn} not found")
        
        status_info = {
            "sn": device.sn,
            "ip": device.ip,
            "connection_mode": device.connection_mode,
            "is_socket_connected": device.is_socket_mode(),
            "is_online": device.zk.is_connect if hasattr(device.zk, 'is_connect') else False,
            "pending_commands_count": len(device.get_pending_commands()),
            "last_check": device.connected_at.isoformat() if device.connected_at else None
        }
        
        return {
            "message": f"Status for device {device_sn}",
            "data": status_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving device status for {device_sn}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving device status")