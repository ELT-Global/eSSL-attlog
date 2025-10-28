"""
Data manager utility for handling JSON file operations
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DataManager:
    """Manages JSON data files for attendance and operation logs"""
    
    def __init__(self, base_path: str = "data"):
        """Initialize data manager with base data directory path"""
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # Define file paths for different data types
        self.files = {
            "attendance": self.base_path / "attendance.json",
            "operations": self.base_path / "operations.json", 
            "users": self.base_path / "users.json",
            "fingerprints": self.base_path / "fingerprints.json",
            "faces": self.base_path / "faces.json"
        }
        
        # Initialize empty files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize empty JSON files if they don't exist"""
        for data_type, file_path in self.files.items():
            if not file_path.exists():
                self._save_data(data_type, [])
                logger.info(f"Initialized empty {data_type}.json file")
    
    def _load_data(self, data_type: str) -> List[Dict[Any, Any]]:
        """Load data from JSON file"""
        file_path = self.files.get(data_type)
        if not file_path or not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading {data_type} data: {e}")
            return []
    
    def _save_data(self, data_type: str, data: List[Dict[Any, Any]]):
        """Save data to JSON file"""
        file_path = self.files.get(data_type)
        if not file_path:
            raise ValueError(f"Unknown data type: {data_type}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except IOError as e:
            logger.error(f"Error saving {data_type} data: {e}")
            raise
    
    def sync_attendance_records(self, records: List[Dict[Any, Any]], machine_id: Optional[str] = None):
        """Sync attendance records - add new ones and update existing ones based on PIN + Timestamp + machine_id"""
        if not records:
            return
        
        # Add metadata to each record
        timestamp = datetime.now().isoformat()
        for record in records:
            record['machine_id'] = machine_id
            record['received_at'] = timestamp
        
        # Load existing data
        existing_data = self._load_data("attendance")
        
        # Create a lookup for existing records based on unique key
        existing_lookup = {}
        for i, existing_record in enumerate(existing_data):
            unique_key = (
                existing_record.get('PIN', ''),
                existing_record.get('Timestamp', ''),
                existing_record.get('machine_id', '')
            )
            existing_lookup[unique_key] = i
        
        # Process new records
        new_count = 0
        updated_count = 0
        for record in records:
            unique_key = (
                record.get('PIN', ''),
                record.get('Timestamp', ''),
                record.get('machine_id', '')
            )
            
            if unique_key in existing_lookup:
                # Update existing record
                existing_data[existing_lookup[unique_key]] = record
                updated_count += 1
            else:
                # Add new record
                existing_data.append(record)
                new_count += 1
        
        # Save updated data
        self._save_data("attendance", existing_data)
        logger.info(f"Synced attendance records: {new_count} new, {updated_count} updated")
    
    def sync_operations(self, operations: List[Dict[Any, Any]], machine_id: Optional[str] = None):
        """Sync operation records - add new ones and update existing ones based on userPin + codeNumber + machine_id"""
        if not operations:
            return
        
        # Add metadata to each record
        timestamp = datetime.now().isoformat()
        for operation in operations:
            operation['machine_id'] = machine_id
            operation['received_at'] = timestamp
        
        # Load existing data
        existing_data = self._load_data("operations")
        
        # Create a lookup for existing records based on unique key
        existing_lookup = {}
        for i, existing_record in enumerate(existing_data):
            unique_key = (
                existing_record.get('userPin', ''),
                existing_record.get('codeNumber', ''),
                existing_record.get('machine_id', '')
            )
            existing_lookup[unique_key] = i
        
        # Process new records
        new_count = 0
        updated_count = 0
        for record in operations:
            unique_key = (
                record.get('userPin', ''),
                record.get('codeNumber', ''),
                record.get('machine_id', '')
            )
            
            if unique_key in existing_lookup:
                # Update existing record
                existing_data[existing_lookup[unique_key]] = record
                updated_count += 1
            else:
                # Add new record
                existing_data.append(record)
                new_count += 1
        
        # Save updated data
        self._save_data("operations", existing_data)
        logger.info(f"Synced operation records: {new_count} new, {updated_count} updated")
    
    def sync_users(self, users: List[Dict[Any, Any]], machine_id: Optional[str] = None):
        """Sync user records - add new ones and update existing ones based on PIN"""
        if not users:
            return
        
        # Add metadata to each record
        timestamp = datetime.now().isoformat()
        for user in users:
            user['machine_id'] = machine_id
            user['received_at'] = timestamp
        
        # Load existing data
        existing_data = self._load_data("users")
        
        # Create a lookup for existing records based on unique key (PIN)
        existing_lookup = {}
        for i, existing_record in enumerate(existing_data):
            unique_key = existing_record.get('PIN', '')
            existing_lookup[unique_key] = i
        
        # Process new records
        new_count = 0
        updated_count = 0
        for record in users:
            unique_key = record.get('PIN', '')
            
            if unique_key in existing_lookup:
                # Update existing record
                existing_data[existing_lookup[unique_key]] = record
                updated_count += 1
            else:
                # Add new record
                existing_data.append(record)
                new_count += 1
        
        # Save updated data
        self._save_data("users", existing_data)
        logger.info(f"Synced user records: {new_count} new, {updated_count} updated")
    
    def sync_fingerprints(self, fingerprints: List[Dict[Any, Any]], machine_id: Optional[str] = None):
        """Sync fingerprint records - add new ones and update existing ones based on pin + fingerId"""
        if not fingerprints:
            return
        
        # Add metadata to each record
        timestamp = datetime.now().isoformat()
        for fingerprint in fingerprints:
            fingerprint['machine_id'] = machine_id
            fingerprint['received_at'] = timestamp
        
        # Load existing data
        existing_data = self._load_data("fingerprints")
        
        # Create a lookup for existing records based on unique key
        existing_lookup = {}
        for i, existing_record in enumerate(existing_data):
            unique_key = (
                existing_record.get('pin', ''),
                existing_record.get('fingerId', '')
            )
            existing_lookup[unique_key] = i
        
        # Process new records
        new_count = 0
        updated_count = 0
        for record in fingerprints:
            unique_key = (
                record.get('pin', ''),
                record.get('fingerId', '')
            )
            
            if unique_key in existing_lookup:
                # Update existing record
                existing_data[existing_lookup[unique_key]] = record
                updated_count += 1
            else:
                # Add new record
                existing_data.append(record)
                new_count += 1
        
        # Save updated data
        self._save_data("fingerprints", existing_data)
        logger.info(f"Synced fingerprint records: {new_count} new, {updated_count} updated")
    
    def sync_faces(self, faces: List[Dict[Any, Any]], machine_id: Optional[str] = None):
        """Sync face records - add new ones and update existing ones based on pin + faceId"""
        if not faces:
            return
        
        # Add metadata to each record
        timestamp = datetime.now().isoformat()
        for face in faces:
            face['machine_id'] = machine_id
            face['received_at'] = timestamp
        
        # Load existing data
        existing_data = self._load_data("faces")
        
        # Create a lookup for existing records based on unique key
        existing_lookup = {}
        for i, existing_record in enumerate(existing_data):
            unique_key = (
                existing_record.get('pin', ''),
                existing_record.get('faceId', '')
            )
            existing_lookup[unique_key] = i
        
        # Process new records
        new_count = 0
        updated_count = 0
        for record in faces:
            unique_key = (
                record.get('pin', ''),
                record.get('faceId', '')
            )
            
            if unique_key in existing_lookup:
                # Update existing record
                existing_data[existing_lookup[unique_key]] = record
                updated_count += 1
            else:
                # Add new record
                existing_data.append(record)
                new_count += 1
        
        # Save updated data
        self._save_data("faces", existing_data)
        logger.info(f"Synced face records: {new_count} new, {updated_count} updated")
    
    def get_all_data(self, data_type: str) -> List[Dict[Any, Any]]:
        """Get all data for a specific data type"""
        return self._load_data(data_type)
    
    def clear_data(self, data_type: str):
        """Clear all data for a specific data type"""
        self._save_data(data_type, [])
        logger.info(f"Cleared all data from {data_type}.json")

    # Backward compatibility methods (deprecated - use sync_ methods instead)
    def append_attendance_records(self, records: List[Dict[Any, Any]], machine_id: Optional[str] = None):
        """Deprecated: Use sync_attendance_records instead"""
        return self.sync_attendance_records(records, machine_id)
    
    def append_operations(self, operations: List[Dict[Any, Any]], machine_id: Optional[str] = None):
        """Deprecated: Use sync_operations instead"""
        return self.sync_operations(operations, machine_id)
    
    def append_users(self, users: List[Dict[Any, Any]], machine_id: Optional[str] = None):
        """Deprecated: Use sync_users instead"""
        return self.sync_users(users, machine_id)
    
    def append_fingerprints(self, fingerprints: List[Dict[Any, Any]], machine_id: Optional[str] = None):
        """Deprecated: Use sync_fingerprints instead"""
        return self.sync_fingerprints(fingerprints, machine_id)
    
    def append_faces(self, faces: List[Dict[Any, Any]], machine_id: Optional[str] = None):
        """Deprecated: Use sync_faces instead"""
        return self.sync_faces(faces, machine_id)


# Global instance
data_manager = DataManager()