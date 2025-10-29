from typing import Dict, List
from app.utils.device import Device

import logging

logger = logging.getLogger(__name__)


class DeviceManager:
        
    def __init__(self):
        # deviceRegistry: Map<SN, Array<Device>>
        self.device_registry: Dict[str, Device] = {}

    def add_device(self, device: Device) -> None:
        """Add a device to the manager"""
        if device.sn not in self.device_registry:
            self.device_registry[device.sn] = device
            logger.info(f"📋 Added device: {device}")
            device.connect_device()
    
    def remove_device(self, sn: str) -> None:
        """Remove a device from the manager by its serial number"""
        if sn in self.device_registry:
            device = self.device_registry.get(sn)
            if device is not None:
                device.zk.disconnect()
            del self.device_registry[sn]
            logger.info(f"🗑️ Removed device with SN: {sn}")
    
    def get_device(self, sn: str) -> Device | None:
        """Retrieve a device by its serial number"""
        device = self.device_registry.get(sn)
        if device is not None and not device.zk.is_connect:
            # Attempt to reconnect if not connected
            device.connect_device()
        return device

# Singleton instance
device_manager = DeviceManager()