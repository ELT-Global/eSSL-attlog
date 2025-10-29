from pydantic import BaseModel

class DeviceStats(BaseModel):
    users: int
    fingers: int
    faces: int
    cards: int
    records: int
    users_cap: int
    fingers_cap: int