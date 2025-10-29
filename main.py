import os
from fastapi import FastAPI
from app.routers import attendance, users, actions, stats, push_api, data

app = FastAPI(title="eSSL Attendance Logger", version="1.0.0")

# Include routers
app.include_router(push_api.router, prefix="/iclock", tags=["Push API"])
app.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(actions.router, prefix="/actions", tags=["Actions"])
app.include_router(stats.router, prefix="/stats", tags=["Stats"])
app.include_router(data.router, prefix="/data", tags=["Data"])


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "data_dir": os.path.exists("data"),
        "port": os.getenv("PORT", "8000")
    }
