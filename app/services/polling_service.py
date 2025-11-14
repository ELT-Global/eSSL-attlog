from typing import Dict, List, Optional
from datetime import datetime
from app.utils.device_manager import device_manager
from app.utils.parse_info import parse_info
from app.utils.network_scan import scanner
from app.utils.device import Device
from app.utils.parsers import parse_ack_line
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

    def ack_command(self, sn: str, command_ack_data: str) -> str:
        """
        Process command acknowledgments from device.
        
        Based on the ADMS protocol documentation, devices send acknowledgments
        in the format: ID=cmd_id&Return=return_code&CMD=command_text
        Multiple commands can be acknowledged in a single request separated by newlines.
        
        Command IDs are alphanumeric strings (max 16 characters) as per ADMS protocol.
        
        Args:
            sn: Device serial number sending the acknowledgment
            command_ack_data: Raw acknowledgment data from device
            
        Returns:
            str: Response to send back to device (typically "OK")
        """
        
        # Get the device from device manager
        existing_machine = device_manager.get_device(sn)
        if not existing_machine:
            logger.warning(f"⚠️ Received acknowledgment from unknown device {sn}")
            return ADMS_CMD.ACK
        
        # Process acknowledgment lines
        ack_lines = command_ack_data.strip().split('\n')
        successful_acks = 0
        for line in ack_lines:
            line = line.strip()
            if line and self._process_single_ack_line(sn, line, existing_machine):
                successful_acks += 1
        
        # Log summary if any acknowledgments were processed
        if successful_acks > 0:
            logger.info(f"📨 Processed {successful_acks} command acknowledgment(s) from device {sn}")
        
        return ADMS_CMD.ACK

    def _process_single_ack_line(self, sn: str, line: str, device: Device) -> bool:
        """Process a single acknowledgment line. Returns True if successful."""
        try:
            # Parse acknowledgment parameters
            ack_params = parse_ack_line(line)
            cmd_id = ack_params.ID
            return_code = ack_params.Return
            cmd_text = ack_params.CMD
            
            # Mark command as acknowledged
            device.mark_command_acked(cmd_id, return_code)
            
            # Process the acknowledgment
            is_success = return_code == ADMS_CMD.RETURN_CODE_SUCCESS
            # Log the result
            if is_success:
                logger.info(f"✅ Command C:{cmd_id}:{cmd_text} acknowledged successfully by device {sn}")
            else:
                logger.warning(f"❌ Command C:{cmd_id}:{cmd_text} failed on device {sn} ({ADMS_CMD.RETURN_CODE.get(return_code, 'Return=' + return_code)})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing acknowledgment line from device {sn}: {line} - Error: {e}")
            return False

    def record_attlog(self) -> None:
        """TODO: Implement attendance log recording functionality."""
        pass
    
    def record_operlog(self) -> None:
        """TODO: Implement operation log recording functionality."""
        pass
    
    def record_options(self) -> None:
        """TODO: Implement device options recording functionality."""
        pass
    
    def record_poll(self, sn: str, _firmware_version: str, _device_type: str, _device_ip: str) -> None:
        """Record the current time as the last poll time for the given device SN."""
        self.last_polled[sn] = datetime.now()

polling_service = PollingService()