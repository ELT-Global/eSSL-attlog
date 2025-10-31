from typing import Dict, List
from app.utils.device import Device

import logging

logger = logging.getLogger(__name__)


class DeviceManager:
        
    def __init__(self):
        # deviceRegistry: Map<SN, Array<Device>>
        self.device_registry: Dict[str, Device] = {}

    def add_device(self, device: Device, attempt_socket_connection: bool = False) -> None:
        """Add a device to the manager"""
        if device.sn not in self.device_registry:
            self.device_registry[device.sn] = device
            logger.info(f"📋 Added device: {device}")
            if attempt_socket_connection:
                device.set_socket_mode()
    
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
        if device is not None and not device.is_socket_mode():
            # Attempt to reconnect if not connected
            device.set_socket_mode()
        return device

# Singleton instance
device_manager = DeviceManager()