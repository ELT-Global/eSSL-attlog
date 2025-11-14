"""
ZKTeco/ESSL Device Command Definitions
--------------------------------------
This file contains formatted command strings for communicating with biometric
attendance devices using the ADMS-style protocol.

References:
- DATA QUERY / DATA UPDATE / DATA DELETE / CONTROL / CLEAR
- Based on multiple observed device implementations.
"""

# --- Core/Control Commands ---
REBOOT = "REBOOT"  # Restart the device
SHUTDOWN = "SHUTDOWN"  # Shutdown the device
UNLOCK = "AC_UNLOCK"  # Unlock the door
UNALARM = "AC_UNALARM"  # Disable alarm
INFO = "INFO"  # Request device info/status
CHECK = "CHECK"  # Simple device health check
LOCK_DEVICE = "CHECK Lock"  # Lock the device (disable input)
UNLOCK_DEVICE = "CHECK Unlock"  # Unlock the device (enable input)
ACK = "OK"  # Generic acknowledgment
ACK_COUNT = lambda count: f"OK:{count}"  # Acknowledge with count of records

# --- User Management ---
# Add or update a user record
UPDATE_USERINFO = (
    "DATA UPDATE USERINFO PIN={pin}\tName={name}\tPri={pri}\tPasswd={password}\tCard={card}\tGrp={group}\tTZ={tz}"
)

# Simplified alias (lambda version)
UPDATE_USERINFO_SIMPLE = (
    lambda pin, name, privilege=0, card=0: f"DATA UPDATE USERINFO PIN={pin}\tName={name}\tPrivilege={privilege}\tCard={card}"
)

# Delete a user record
DELETE_USER = lambda pin: f"DATA DELETE USERINFO PIN={pin}"

# --- Fingerprint, Face, and Biometric Updates ---
UPDATE_FINGER = (
    lambda pin, fid, size, valid, tmp: f"DATA UPDATE FINGERTMP PIN={pin}\tFID={fid}\tSize={size}\tValid={valid}\tTMP={tmp}"
)
UPDATE_FACE = (
    lambda pin, fid, valid, size, tmp: f"DATA UPDATE FACE PIN={pin}\tFID={fid}\tValid={valid}\tSize={size}\tTMP={tmp}"
)
UPDATE_FVEIN = (
    lambda pin, fid, index, valid, size, tmp: f"DATA$ UPDATE FVEIN Pin={pin}\tFID={fid}\tIndex={index}\tValid={valid}\tSize={size}\tTmp={tmp}"
)
DELETE_FINGER = lambda pin, fid=None: (
    f"DATA DELETE FINGERTMP PIN={pin}" if fid is None else f"DATA DELETE FINGERTMP PIN={pin}\tFID={fid}"
)
DELETE_FACE = lambda pin: f"DATA DELETE FACE PIN={pin}"

# --- Attendance Queries ---
# Get all logs
QUERY_ATTLOG = "DATA QUERY ATTLOG"

# Get attendance logs for a date range
QUERY_ATTLOG_RANGE = (
    lambda start, end: f"DATA QUERY ATTLOG StartTime={start}\tEndTime={end}"
)

# Get all logs via legacy ATTLOG command (some models)
ATTLOG = "ATTLOG"
GET_ATTLOG = (
    lambda start, end: f"GET ATTLOG StartTime={start}\tEndTime={end}"
)

# --- User Queries ---
QUERY_USERINFO = "DATA QUERY USERINFO"
QUERY_USERINFO_BY_PIN = lambda pin: f"DATA QUERY USERINFO PIN={pin}"
QUERY_ALL_USERS = "DATA QUERY USERINFO *"

# --- Operation and System Logs ---
QUERY_OPLOG = "DATA QUERY OPERLOG"

# --- Deletions and Clears ---
CLEAR_ATTLOG = "DATA DELETE ATTLOG"  # Delete all attendance logs
CLEAR_LOG = "CLEAR LOG"  # Clear logs (shortcut command)
CLEAR_DATA = "CLEAR DATA"  # Clear all stored data
CLEAR_BIODATA = "CLEAR BIODATA"  # Clear biometric data

# --- Access Control Related ---
UPDATE_ACC_GROUP = (
    lambda id, verify, valid_holiday, tz: f"DATA UPDATE AccGroup ID={id}\tVerify={verify}\tValidHoliday={valid_holiday}\tTZ={tz}"
)
UPDATE_ACC_TIMEZONE = (
    lambda uid, sun_s, sun_e, mon_s, mon_e: f"DATA UPDATE AccTimeZone UID={uid}\tSunStart={sun_s}\tSunEnd={sun_e}\tMonStart={mon_s}\tMonEnd={mon_e}"
)
UPDATE_ACC_HOLIDAY = (
    lambda uid, name, start, end, tz: f"DATA UPDATE AccHoliday UID={uid}\tHolidayName={name}\tStartDate={start}\tEndDate={end}\tTimeZone={tz}"
)

# --- Device Configuration ---
SET_OPTION = lambda key, val: f"SET OPTION {key}={val}"
RELOAD_OPTIONS = "RELOAD OPTIONS"

# --- File Transfer ---
PUT_FILE = lambda name, path: f"PutFile {name}\t{path}"

# --- Enrollment Commands ---
ENROLL_FP = (
    lambda pin, fid, retry=3, overwrite=1: f"ENROLL_FP PIN={pin}\tFID={fid}\tRETRY={retry}\tOVERWRITE={overwrite}"
)

# --- Miscellaneous / Unknown ---
UNKNOWN = "UNKNOWN"

# --- Command Builders (helpers) ---
def build_attlog_query(start, end, iso=False):
    """
    Build a properly formatted attendance log query.

    :param start: Start time string (e.g. '2025-01-01 00:00:00')
    :param end: End time string (e.g. '2025-01-02 23:59:59')
    :param iso: If True, use ISO 8601 (T separator)
    """
    if iso:
        return f"DATA QUERY ATTLOG StartTime={start.replace(' ', 'T')}\tEndTime={end.replace(' ', 'T')}"
    return f"DATA QUERY ATTLOG StartTime={start}\tEndTime={end}"