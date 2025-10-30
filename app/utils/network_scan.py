import asyncio
import ipaddress
import socket
from contextlib import suppress
from zk import ZK, const

# 1) find local IP (best-effort)
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't actually connect; just picks a local IP
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()

# 2) create a host list (assume /24 by default)
def hosts_from_local_ip(local_ip, prefix=24):
    network = ipaddress.ip_network(f"{local_ip}/{prefix}", strict=False)
    return [str(h) for h in network.hosts()]

# 3) async probe for TCP port (4370)
async def probe_port(host, port=4370, timeout=1.0):
    try:
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout)
        writer.close()
        with suppress(Exception):
            await writer.wait_closed()
        return True
    except Exception:
        return False

async def scan_hosts(hosts, port=4370, concurrency=200):
    sem = asyncio.Semaphore(concurrency)
    results = []

    async def worker(h):
        async with sem:
            if await probe_port(h, port):
                results.append(h)

    await asyncio.gather(*(worker(h) for h in hosts))
    return results

# 4) get serial number from ZK device (async version)
async def get_serial_number_async(ip, port=4370, timeout=10):
    """Async wrapper for ZK serial number retrieval"""
    loop = asyncio.get_event_loop()
    try:
        # Run blocking ZK operations in thread pool to avoid blocking event loop
        def _get_serial():
            zk = ZK(ip, port=port, timeout=timeout)
            zk.connect()
            try:
                return zk.get_serialnumber()
            finally:
                zk.disconnect()
        
        serial = await loop.run_in_executor(None, _get_serial)
        return {"ip": ip, "serial": serial, "status": "success"}
    except Exception as e:
        return {"ip": ip, "serial": None, "status": "error", "error": str(e)}

async def main():
    local_ip = get_local_ip()
    print("Local IP:", local_ip)
    hosts = hosts_from_local_ip(local_ip, prefix=24)  # change prefix if needed
    print(f"Scanning {len(hosts)} hosts for port 4370...")
    
    found = await scan_hosts(hosts, port=4370)
    print(f"✓ Found {len(found)} device(s) with port 4370 open: {found}")
    
    # Get serial numbers from found devices (NOW IN PARALLEL!)
    if found:
        print(f"\nRetrieving serial numbers from {len(found)} device(s) concurrently...")
        # Query all devices at once instead of one-by-one
        results = await asyncio.gather(*(get_serial_number_async(ip) for ip in found))
        
        print("\n" + "="*60)
        for result in results:
            if result["status"] == "success":
                print(f"  ✓ {result['ip']}: Serial = {result['serial']}")
            else:
                print(f"  ✗ {result['ip']}: {result['error']}")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())