from typing import List, Literal, Optional, TypedDict
from datetime import datetime

class DeviceCommand(TypedDict):
    """Type definition for a device command"""
    id: int
    command: str
    status: Literal['pending', 'sent', 'failed', 'acked']
    queued_at: datetime
    sent_at: Optional[datetime]
    ack_at: Optional[datetime]
    return_code: Optional[str]

class ADMSQueue:
    commands: List[DeviceCommand]
    command_sequence: int
    
    def __init__(self, commands: Optional[List[DeviceCommand]] = None, command_sequence: int = 0):
        self.commands = commands if commands is not None else []
        self.command_sequence = command_sequence

    def next_sequence(self) -> int:
        self.command_sequence += 1
        return self.command_sequence
    
    def add_command(self, command: str) -> DeviceCommand:
        command_id = self.next_sequence()
        device_command: DeviceCommand = {
            "id": command_id,
            "command": command,
            "status": "pending",
            "queued_at": datetime.now(),
            "sent_at": None,
            "ack_at": None,
            "return_code": None
        }
        self.commands.append(device_command)
        return device_command

    def get_pending_commands(self) -> List[DeviceCommand]:
        return [cmd for cmd in self.commands if cmd['status'] == 'pending']

    def mark_command_sent(self, command_id: int) -> None:
        for cmd in self.commands:
            if cmd['id'] == command_id:
                cmd['status'] = "sent"
                cmd['sent_at'] = datetime.now()
                break
    
    def mark_command_acked(self, command_id: int, return_code: str) -> None:
        for cmd in self.commands:
            if cmd['id'] == command_id:
                cmd['status'] = "acked"
                cmd['ack_at'] = datetime.now()
                cmd['return_code'] = return_code
                break