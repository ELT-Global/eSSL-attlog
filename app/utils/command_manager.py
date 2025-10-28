"""
Command management utilities for device command queuing and delivery.
"""
from typing import Dict, List, Optional, TypedDict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DeviceCommand(TypedDict):
    """Type definition for a device command"""
    id: int
    command: str
    status: str  # 'pending' | 'sent' | 'done'
    queuedAt: str
    sentAt: Optional[str]
    doneAt: Optional[str]
    deviceAck: Optional[str]


class CommandManager:
    """Manages device command queuing and delivery"""
    
    def __init__(self):
        # deviceCommands: Map<SN, Array<DeviceCommand>>
        self._device_commands: Dict[str, List[DeviceCommand]] = {}
        # deviceSeq: Map<SN, lastId> to generate incremental IDs per device
        self._device_seq: Dict[str, int] = {}
    
    def _next_command_id_for(self, sn: str) -> int:
        """Generate next incremental command ID for a device"""
        last_id = self._device_seq.get(sn, 0)
        next_id = last_id + 1
        self._device_seq[sn] = next_id
        return next_id
    
    def queue_command(self, sn: str, command_text: str) -> DeviceCommand:
        """
        Create a new command for a device and return the created command object
        
        Args:
            sn: Device serial number
            command_text: Command to be executed by the device
            
        Returns:
            DeviceCommand: The created command object
        """
        command_id = self._next_command_id_for(sn)
        now = datetime.now().isoformat()
        
        cmd: DeviceCommand = {
            'id': command_id,
            'command': command_text,
            'status': 'pending',
            'queuedAt': now,
            'sentAt': None,
            'doneAt': None,
            'deviceAck': None
        }
        
        # Get existing commands for device or create new list
        device_commands = self._device_commands.get(sn, [])
        device_commands.append(cmd)
        self._device_commands[sn] = device_commands
        
        logger.info(f"📋 Queued command for {sn}: C:{command_id}:{command_text}")
        return cmd
    
    def get_pending_commands(self, sn: str) -> List[DeviceCommand]:
        """
        Get all pending commands for a device and mark them as sent
        
        Args:
            sn: Device serial number
            
        Returns:
            List[DeviceCommand]: List of pending commands (now marked as sent)
        """
        device_commands = self._device_commands.get(sn, [])
        
        # Find all pending commands
        pending_commands = []
        now = datetime.now().isoformat()
        
        for cmd in device_commands:
            if cmd['status'] == 'pending':
                # Mark as sent
                cmd['status'] = 'sent'
                cmd['sentAt'] = now
                pending_commands.append(cmd)
        
        if pending_commands:
            logger.info(f"📤 Sending {len(pending_commands)} commands to {sn}")
            for cmd in pending_commands:
                logger.info(f"  C:{cmd['id']}:{cmd['command']}")
        
        return pending_commands
    
    def get_pending_command(self, sn: str) -> Optional[DeviceCommand]:
        """
        Get the next pending command for a device and mark it as sent
        (Legacy method - use get_pending_commands for multiple commands)
        
        Args:
            sn: Device serial number
            
        Returns:
            Optional[DeviceCommand]: The next pending command, or None if no pending commands
        """
        pending_commands = self.get_pending_commands(sn)
        return pending_commands[0] if pending_commands else None
    
    def acknowledge_command(self, sn: str, command_id: int, device_ack: str) -> bool:
        """
        Acknowledge a command completion and remove it from queue
        
        Args:
            sn: Device serial number
            command_id: Command ID to acknowledge
            device_ack: Device acknowledgment status (e.g., 'OK', 'ERR')
            
        Returns:
            bool: True if command was found and acknowledged, False otherwise
        """
        device_commands = self._device_commands.get(sn, [])
        
        # Find and remove the command
        for i, cmd in enumerate(device_commands):
            if cmd['id'] == command_id and cmd['status'] == 'sent':
                cmd['status'] = 'done'
                cmd['doneAt'] = datetime.now().isoformat()
                cmd['deviceAck'] = device_ack
                
                # Log the acknowledgment
                logger.info(f"✅ Command C:{command_id}:{cmd['command']} acknowledged by {sn} -> {device_ack}")
                
                # Remove from queue
                device_commands.pop(i)
                
                # Update or delete the device entry
                if len(device_commands) == 0:
                    del self._device_commands[sn]
                else:
                    self._device_commands[sn] = device_commands
                
                return True
        
        logger.warning(f"⚠️ Ack for unknown command id {command_id} (SN={sn})")
        return False
    
    def acknowledge_multiple_commands(self, sn: str, acknowledgments: List[tuple[int, str]]) -> int:
        """
        Acknowledge multiple commands at once
        
        Args:
            sn: Device serial number
            acknowledgments: List of (command_id, device_ack) tuples
            
        Returns:
            int: Number of commands successfully acknowledged
        """
        acknowledged_count = 0
        for command_id, device_ack in acknowledgments:
            if self.acknowledge_command(sn, command_id, device_ack):
                acknowledged_count += 1
        return acknowledged_count
    
    def mark_command_done(self, sn: str, command_id: int) -> bool:
        """
        Mark a command as done (legacy method - use acknowledge_command instead)
        
        Args:
            sn: Device serial number
            command_id: Command ID to mark as done
            
        Returns:
            bool: True if command was found and marked as done, False otherwise
        """
        return self.acknowledge_command(sn, command_id, 'OK')
    
    def get_device_commands(self, sn: str) -> List[DeviceCommand]:
        """
        Get all commands for a device
        
        Args:
            sn: Device serial number
            
        Returns:
            List[DeviceCommand]: List of all commands for the device
        """
        return self._device_commands.get(sn, [])
    
    def get_all_commands(self) -> Dict[str, List[DeviceCommand]]:
        """
        Get all commands for all devices
        
        Returns:
            Dict[str, List[DeviceCommand]]: Dictionary mapping device SN to command lists
        """
        return self._device_commands.copy()
    
    def cleanup_completed_commands(self, sn: Optional[str] = None, keep_last_n: int = 100) -> int:
        """
        Clean up completed commands to prevent memory bloat
        
        Args:
            sn: Device serial number (if None, cleanup all devices)
            keep_last_n: Number of completed commands to keep per device
            
        Returns:
            int: Number of commands cleaned up
        """
        cleaned_count = 0
        devices_to_clean = [sn] if sn else list(self._device_commands.keys())
        
        for device_sn in devices_to_clean:
            device_commands = self._device_commands.get(device_sn, [])
            
            # Separate pending/sent commands from done commands
            active_commands = [cmd for cmd in device_commands if cmd['status'] in ['pending', 'sent']]
            done_commands = [cmd for cmd in device_commands if cmd['status'] == 'done']
            
            # Keep only the last N done commands
            if len(done_commands) > keep_last_n:
                kept_done = done_commands[-keep_last_n:]
                cleaned_count += len(done_commands) - keep_last_n
                self._device_commands[device_sn] = active_commands + kept_done
            
        if cleaned_count > 0:
            logger.info(f"🧹 Cleaned up {cleaned_count} completed commands")
        
        return cleaned_count


# Global command manager instance
command_manager = CommandManager()