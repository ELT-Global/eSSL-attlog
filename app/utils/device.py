from datetime import datetime
from typing import Optional, Literal, List
from zk import ZK, const
from zk.user import User
from app.utils.command_manager import command_manager
from app.utils.device_stats import DeviceStats
import app.commands as ADMS_CMD
import logging
logger = logging.getLogger(__name__)

class Device:
    def __init__(
        self, 
        sn: str,
        firmware_version: str,
        device_type: str,
        device_ip: str,
        device_port: int = 4370,
        connected_at: Optional[datetime] = None,
        password: int = 0,
        zk: Optional[ZK] = None 
    ):
        self.firmware_version = firmware_version
        self.device_type = device_type
        self.device_ip = device_ip
        self.device_port = device_port
        self.sn = sn
        self.connected_at = connected_at or datetime.now()
        self.socket_mode = False
        self.zk = zk or ZK(device_ip, port=device_port, timeout=5, password=password, force_udp=False, ommit_ping=False)
    
    def is_socket_mode(self) -> bool:
        """Check if the device is in socket mode (connected via TCP)."""
        self.socket_mode = self.zk.is_connect
        return self.socket_mode
            
    def set_socket_mode(self, is_on: bool = True, force = False) -> None:
        """Attempt to establish socket connection with a device."""
        
        if is_on == self.is_socket_mode() and not force:
            return

        # Disconnect if already connected because we're forcing a change.
        try:
            if self.zk.is_connect:
                self.zk.disconnect()
                logger.info(f"🔌 Disconnected from device SN: {self.sn} at IP: {self.device_ip}")
                self.socket_mode = False
        except Exception as e:
            logger.error(f"❌ Error disconnecting from device SN: {self.sn} at IP: {self.device_ip} - Error: {e}")

        if is_on:    
            # Recreate ZK instance to ensure fresh connection, variables may have changed.
            self.zk = ZK(self.device_ip, port=self.device_port, timeout=5, password=0, force_udp=False, ommit_ping=False)
            try:
                self.zk.connect()
                logger.info(f"✅ Connected to device SN: {self.sn} at IP: {self.device_ip}")
                self.socket_mode = True
            except Exception as e:
                self.socket_mode = False
                logger.error(f"❌ Failed to connect to device SN: {self.sn} at IP: {self.device_ip} - Error: {e}")
            
    def restart(self) -> None:
        """Restart the device remotely."""
        if not self.is_socket_mode():
            command_manager.queue_command(self.sn, ADMS_CMD.REBOOT)
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
            command_manager.queue_command(self.sn, ADMS_CMD.SHUTDOWN)
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
        self.set_socket_mode()
        if not self.is_socket_mode():
            # DATA QUERY USERINFO oughta work here
            raise ConnectionError(f"Device SN: {self.sn} is not connected via Socket.")
        
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
        return f"Device(SN={self.sn}, IP={self.device_ip}, Type={self.device_type})"
    
    def __repr__(self) -> str:
        return (f"Device(firmware_version='{self.firmware_version}', "
                f"device_type='{self.device_type}', device_ip='{self.device_ip}', "
                f"sn='{self.sn}', connected_at={self.connected_at})")