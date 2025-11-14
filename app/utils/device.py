from datetime import datetime
from typing import Optional, Literal, List
from zk import ZK, const
from zk.user import User
from app.utils.adms_queue import ADMSQueue, DeviceCommand
from app.utils.device_stats import DeviceStats
from app.utils.parse_info import GetRequestInfo
import app.commands as ADMS_CMD
import logging
logger = logging.getLogger(__name__)

class Device:
    _connection_mode: Literal['adms', 'socket+adms']
    def __init__(
        self, 
        sn: str,
        
        ip: Optional[str] = None,
        port: Optional[int] = 4370,
        password: Optional[int] = 0,
        info: Optional[GetRequestInfo] = None,
        connected_at: Optional[datetime] = None,
        connection_mode: Literal['adms', 'socket+adms'] = 'adms',
        
        adms_queue: Optional[ADMSQueue] = None
    ):
        self.sn = sn
        
        self.ip = ip
        self.port = port or 4370
        self.password = password or 0
        self.info = info
        
        self._connection_mode = connection_mode
        self.connected_at = connected_at or datetime.now()
        
        self.socket_mode = False
        
        self.zk = ZK(self.ip, port=self.port, timeout=5, password=self.password, force_udp=False, ommit_ping=False)
        
        self.adms_queue = adms_queue or ADMSQueue([], 1)
    
    @property
    def connection_mode(self) -> Literal['adms', 'socket+adms']:
        """Get the current connection mode of the device."""
        return self._connection_mode
    
    @connection_mode.setter
    def connection_mode(self, mode: Literal['adms', 'socket+adms']) -> None:
        """Set the connection mode of the device."""
        self._connection_mode = mode
    
    def add_command(self, command_text: str) -> None:
        """Add a command to the device's ADMS queue."""
        self.adms_queue.add_command(command_text)

    def get_pending_commands(self) -> List[DeviceCommand]:
        """Retrieve pending commands for the device."""
        return self.adms_queue.get_pending_commands()

    def mark_commands_sent(self, command_ids: List[str]) -> None:
        """Mark specified commands as sent."""
        for cmd_id in command_ids:
            self.adms_queue.mark_command_sent(cmd_id)
        
    def mark_command_acked(self, command_id: str, return_code: str) -> None:
        """Acknowledge a command completion."""
        self.adms_queue.mark_command_acked(command_id, return_code)
    
    def is_socket_mode(self) -> bool:
        """Check if the device is in socket mode (connected via TCP)."""
        self.socket_mode = self.zk.is_connect and self._connection_mode == 'socket+adms'
        return self.socket_mode
            
    def set_socket_mode(self, is_on: bool = True, force = False) -> None:
        """Attempt to establish socket connection with a device."""
        if self._connection_mode == "adms":
            return
        
        if is_on == self.is_socket_mode() and not force:
            return

        if not self._connection_mode and not force:
            logger.warning(f"⚠️ Socket mode not possible for device SN: {self.sn} at IP: {self.ip}")
            return
        
        # Disconnect if already connected because we're forcing a change.
        try:
            if self.zk.is_connect:
                self.zk.disconnect()
                logger.info(f"🔌 Disconnected from device SN: {self.sn} at IP: {self.ip}")
                self.socket_mode = False
                self._connection_mode = "adms"
        except Exception as e:
            logger.error(f"❌ Error disconnecting from device SN: {self.sn} at IP: {self.ip} - Error: {e}")

        if is_on:    
            # Recreate ZK instance to ensure fresh connection, variables may have changed.
            self.zk = ZK(self.ip, port=self.port, timeout=5, password=0, force_udp=False, ommit_ping=False)
            try:
                logger.info(f"⌛ Attempting to establishing connection: {self.sn} at IP: {self.ip}")
                self.zk.connect()
                logger.info(f"\t✅ Connected to device SN: {self.sn}")
                self.socket_mode = True
                self._connection_mode = "socket+adms"
            except Exception as e:
                self.socket_mode = False
                self._connection_mode = "adms"
                logger.error(f"❌ Failed to connect to device SN: {self.sn} at IP: {self.ip} - Error: {e}")
            
    def restart(self) -> None:
        """Restart the device remotely."""
        if not self.is_socket_mode():
            self.adms_queue.add_command(ADMS_CMD.REBOOT)
            logger.info(f"🔄 Queued REBOOT command for device SN: {self.sn}")
            return
        
        try:
            self.zk.restart()
            logger.info(f"🔄 Restarted device SN: {self.sn}")
        except Exception as e:
            logger.error(f"❌ Failed to restart device SN: {self.sn} - Error: {e}")
    
    def poweroff(self) -> None:
        """Shutdown the device remotely."""
        if not self.is_socket_mode():
            self.adms_queue.add_command(ADMS_CMD.SHUTDOWN)
            logger.info(f"🛑 Queued SHUTDOWN command for device SN: {self.sn}")
            return
        
        try:
            self.zk.poweroff()
            logger.info(f"🛑 Shutdown device SN: {self.sn}")
        except Exception as e:
            logger.error(f"❌ Failed to shutdown device SN: {self.sn} - Error: {e}")
     
    def get_stats(self) -> DeviceStats:
        """Retrieve device statistics."""
        self.set_socket_mode()
        if not self.is_socket_mode():
            raise ConnectionError(f"Device SN: {self.sn} is not connected via Socket.")
        
        try:
            return DeviceStats(
                users=self.zk.users,
                fingers=self.zk.fingers,
                faces=self.zk.faces,
                records=self.zk.records,
                cards=self.zk.cards,
                users_cap=self.zk.users_cap,
                fingers_cap=self.zk.fingers_cap
            )
        except Exception as e:
            logger.error(f"❌ Failed to retrieve stats from device SN: {self.sn} - Error: {e}")
            return DeviceStats(
                users=0,
                fingers=0,
                faces=0,
                cards=0,
                records=0,
                users_cap=0,
                fingers_cap=0
            )
        
    def sync_users(self) -> None:
        """Sync user data from the device."""
        if not self.is_socket_mode():
            self.adms_queue.add_command(ADMS_CMD.QUERY_ALL_USERS)
            logger.info(f"👥 Queued QUERY_ALL_USERS command for device SN: {self.sn}")
            return
        
        try:
            self.zk.disable_device()
            users: List[User] = self.zk.get_users()
            self.zk.enable_device()
            logger.info(f"👥 Synced {len(users)} users from device SN: {self.sn}")
            logger.info(f"👥 Users: {users}")
        except Exception as e:
            logger.error(f"❌ Failed to sync users from device SN: {self.sn} - Error: {e}")
               
    def set_time(self, new_time: Optional[datetime] = None) -> None:
        """Set the device's internal clock to the specified time or current time."""
        self.set_socket_mode()
        if not self.is_socket_mode():
            raise ConnectionError(f"Device SN: {self.sn} is not connected via Socket.")
        
        try:
            current_time = self.zk.get_time()
            target_time = new_time or datetime.now()
            self.zk.set_time(target_time)
            logger.info(f"⏰ Set time on device SN: {self.sn} from '{current_time}' to '{target_time}'")
        except Exception as e:
            logger.error(f"❌ Failed to set time on device SN: {self.sn} - Error: {e}")
            
    def play_voice(self, voice_id: int) -> None:
        """Play a voice prompt on the device."""
        self.set_socket_mode()
        if not self.is_socket_mode():
            raise ConnectionError(f"Device SN: {self.sn} is not connected via Socket.")
        
        try:
            self.zk.test_voice(voice_id)
            logger.info(f"🔊 Played voice ID {voice_id} on device SN: {self.sn}")
        except Exception as e:
            logger.error(f"❌ Failed to play voice on device SN: {self.sn} - Error: {e}")

    def __str__(self) -> str:
        return f"Device(SN={self.sn}, IP={self.ip})"
    
    def __repr__(self) -> str:
        return (f"Device(info='{self.info}', "
                f"sn='{self.sn}', connected_at={self.connected_at})")