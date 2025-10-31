import asyncio
import ipaddress
import socket
from contextlib import suppress
from typing import Dict, List, Optional, Union, Any, TypedDict, Literal
from zk import ZK

class DeviceInfo(TypedDict):
    """Type definition for device information dictionary."""
    ip: str
    serial: Optional[str]
    status: Literal["success", "error"]
    error: Optional[str]

class ZKDeviceScanner:
    """
    Scans the local network for ZKTeco devices (or any device) with TCP port 4370 open,
    then retrieves their serial numbers asynchronously.

    Usage:
        scanner = ZKDeviceScanner(prefix=24)
        await scanner.discover_devices()
        print(scanner.devices)
    """

    def __init__(self, prefix: int = 24, port: int = 4370, concurrency: int = 200, timeout: int = 5) -> None:
        self.prefix: int = prefix
        self.port: int = port
        self.concurrency: int = concurrency
        self.timeout: int = timeout
        self.local_ip: str = self._get_local_ip()
        self.devices: List[DeviceInfo] = []

    # --- Core Network Utilities -----------------------------------------------------

    @staticmethod
    def _get_local_ip() -> str:
        """Determine the local IP used for outbound connections."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"
        finally:
            s.close()

    def _hosts_from_local_ip(self) -> List[str]:
        """Generate all possible hosts in the subnet (defaults to /24)."""
        network = ipaddress.ip_network(f"{self.local_ip}/{self.prefix}", strict=False)
        return [str(h) for h in network.hosts()]

    # --- Async Port Probing ---------------------------------------------------------

    async def _probe_port(self, host: str) -> bool:
        """Return True if the host's port is open."""
        try:
            conn = asyncio.open_connection(host, self.port)
            _, writer = await asyncio.wait_for(conn, timeout=self.timeout)
            writer.close()
            with suppress(Exception):
                await writer.wait_closed()
            return True
        except Exception:
            return False

    async def _scan_hosts(self, hosts: List[str]) -> List[str]:
        """Run concurrent port probes across the subnet."""
        sem = asyncio.Semaphore(self.concurrency)
        results: List[str] = []

        async def worker(h: str) -> None:
            async with sem:
                if await self._probe_port(h):
                    results.append(h)

        await asyncio.gather(*(worker(h) for h in hosts))
        return results

    # --- ZK Serial Number Retrieval -------------------------------------------------

    async def _get_serial_number_async(self, ip: str) -> DeviceInfo:
        """Retrieve the serial number from a ZK device asynchronously."""
        loop = asyncio.get_event_loop()

        def _get_serial() -> Optional[str]:
            zk = ZK(ip, port=self.port, timeout=self.timeout)
            zk.connect()
            try:
                return zk.get_serialnumber()
            finally:
                zk.disconnect()

        try:
            serial = await loop.run_in_executor(None, _get_serial)
            return DeviceInfo(ip=ip, serial=serial, status="success", error=None)
        except Exception as e:
            return DeviceInfo(ip=ip, serial=None, status="error", error=str(e))

    # --- Public API -----------------------------------------------------------------

    async def discover_devices(self) -> List[DeviceInfo]:
        """Scan subnet and retrieve serials for all detected devices."""
        hosts = self._hosts_from_local_ip()
        print(f"📡 Scanning {len(hosts)} hosts in {self.local_ip}/{self.prefix} for port {self.port}...")

        found = await self._scan_hosts(hosts)
        print(f"✅ Found {len(found)} open hosts: {found}")

        if not found:
            self.devices = []
            return []

        print(f"🔍 Fetching serial numbers from {len(found)} devices...")
        results = await asyncio.gather(*(self._get_serial_number_async(ip) for ip in found))
        self.devices = results
        return results

    def list_devices(self) -> List[DeviceInfo]:
        """Return list of successfully identified devices."""
        return [d for d in self.devices if d["status"] == "success"]

    def list_ips(self) -> List[str]:
        """Return list of all detected device IPs."""
        return [d["ip"] for d in self.devices]
    
    def get_device_by_ip(self, ip: str) -> Optional[DeviceInfo]:
        """Return device info by IP address."""
        for d in self.devices:
            if d["ip"] == ip:
                return d
        return None

    def get_device_by_serial(self, serial: str) -> Optional[DeviceInfo]:
        """Return device info by serial number."""
        for d in self.devices:
            if d["serial"] == serial:
                return d
        return None



# Example Usage (if run directly)
if __name__ == "__main__":
    async def _run():
        scanner = ZKDeviceScanner()
        await scanner.discover_devices()
        print("\nDiscovered devices:")
        for d in scanner.list_devices():
            print(f" - {d['ip']} : {d['serial']}")
    asyncio.run(_run())
scanner = ZKDeviceScanner()