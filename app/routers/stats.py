from fastapi import APIRouter, HTTPException
from app.utils.command_manager import command_manager
import logging
from app.utils.device_manager import device_manager

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("")
async def get_device_stats(device_sn: str):
    """
    Get device statistics (users, fingers, faces, etc.)
    
    Args:
        device_sn: Device serial number
        
    Returns:
        dict: Response containing device statistics
    """
    try:
        device = device_manager.get_device(device_sn)
        if device is None:
            raise HTTPException(status_code=404, detail=f"Device with SN {device_sn} not found")
        
        stats = device.get_stats()
        
        return {
            "message": f"Device statistics for {device_sn}",
            "data": {
                "device_sn": device_sn,
                "stats": {
                    "users": stats.users,
                    "fingers": stats.fingers,
                    "faces": stats.faces,
                    "cards": stats.cards,
                    "records": stats.records,
                    "users_capacity": stats.users_cap,
                    "fingers_capacity": stats.fingers_cap
                }
            }
        }
    
    except HTTPException:
        raise
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Device connection error: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting stats for device {device_sn}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving device stats")