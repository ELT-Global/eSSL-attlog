import os
import sys
from dotenv import load_dotenv
load_dotenv()
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import attendance, users, actions, stats, push_api, data, commands, devices
from app.utils.network_scan import scanner

# ---------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.flush = sys.stdout.flush
logging.basicConfig(level=logging.INFO, handlers=[handler])

# ---------------------------------------------------------------------
# Lifespan handler
# ---------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("DISCOVER_DEVICES_ON_STARTUP", "true").lower() == "true":
        logger.info("📡 Scanning for ZKTeco devices on startup...")
        await scanner.discover_devices()
        logger.info(f"✅ Discovered {len(scanner.list_devices())} device(s): {scanner.list_ips()}")
    yield
    logger.info("🛑 Shutting down eSSL Attendance Logger...")


# ---------------------------------------------------------------------
# FastAPI app setup
# ---------------------------------------------------------------------
app = FastAPI(title="eSSL Attendance Logger", version="1.0.0", lifespan=lifespan)

# Register routers
app.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(data.router, prefix="/data", tags=["Data"])
app.include_router(devices.router, prefix="/devices", tags=["Devices"])
app.include_router(actions.router, prefix="/devices/{device_sn}/actions:", tags=["Device/Actions"])
app.include_router(stats.router, prefix="/devices/{device_sn}/stats", tags=["Device/Stats"])
app.include_router(commands.router, prefix="/devices/{device_sn}/commands", tags=["Device/Commands"])
app.include_router(push_api.router, prefix="/{token}/iclock", tags=["ADMS/Push API"])

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "data_dir": os.path.exists("data"),
        "port": os.getenv("PORT", "8000"),
        "devices_detected": len(scanner.list_devices())
    }
