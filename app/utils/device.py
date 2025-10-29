from datetime import datetime
from typing import Optional
from zk import ZK, const 
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
        self.zk = zk or ZK(device_ip, port=device_port, timeout=5, password=password, force_udp=False, ommit_ping=False)
    
        
    def connect_device(self, force = False) -> None:
        """Attempt to establish socket connection with a device."""
        
        try:
            if self.zk.is_connect and not force:
                logger.info(f"ℹ️ Device SN: {self.sn} is already connected.")
                return
            # if self.device_ip != self.zk.__address[0]:
            #     self.zk.__address = (self.device_ip, self.device_port)
            self.zk.connect()
            logger.info(f"✅ Connected to device SN: {self.sn} at IP: {self.device_ip}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to device SN: {self.sn} at IP: {self.device_ip} - Error: {e}")
    
    def play_voice(self, voice_id: int) -> None:
        """Play a voice prompt on the device."""
        try:
            if not self.zk.is_connect:
                self.connect_device()
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