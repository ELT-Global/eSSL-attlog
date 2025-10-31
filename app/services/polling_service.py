from typing import Dict, List, Optional
from datetime import datetime
from app.utils.device_manager import device_manager
from app.utils.parse_info import parse_info
from app.utils.network_scan import scanner
from app.utils.device import Device
import logging
logger = logging.getLogger(__name__)

import app.commands as ADMS_CMD

class PollingService:
    def __init__(self):
        # Map<SN, datetime> of polls for a particular device
        self.last_polled: Dict[str, datetime] = {}
    
    def no_op(self) -> str:
        return ADMS_CMD.ACK
    
    def get_commands(self, sn: str, info: Optional[str] = None) -> str:
        """Handle heartbeat from device with given SN and INFO string."""
        
        existing_machine = device_manager.get_device(sn)
        if not existing_machine:
            existing_machine = Device(sn=sn)
            device_manager.add_device(existing_machine)
        
        logger.info(f"[Heartbeat 💓] Machine ID: '{sn}' polled for commands.")

        if info:
            device_info = parse_info(info)
            known_device = scanner.get_device_by_ip(device_info.ip_address)
            can_connect = bool(known_device and known_device["status"] == "success")
            existing_machine.ip = device_info.ip_address # should we set IP here?
            existing_machine.info = device_info
            if can_connect and existing_machine.connection_mode != "adms":
                existing_machine.connection_mode = "socket+adms"
                existing_machine.set_socket_mode()
        
        # Flush pending commands for this device, if any
        pending_commands = existing_machine.get_pending_commands()
        if pending_commands:
            lines = [f"C:{cmd['id']}:{cmd['command']}" for cmd in pending_commands]
            command_text = "\n".join(lines) + '\n'
            logger.info(f"📤 Delivering {len(pending_commands)} commands to device {sn}")
            return command_text
        
        return ADMS_CMD.ACK
    
    def record_poll(self, sn: str, firmware_version: str, device_type: str, device_ip: str) -> None:
        """Record the current time as the last poll time for the given device SN."""
        self.last_polled[sn] = datetime.now()

polling_service = PollingService()