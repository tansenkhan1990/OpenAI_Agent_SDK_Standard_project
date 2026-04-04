"""
JSON Database service for persistent data storage.
Provides a simple interface to read/write to database.json file.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Path to database file
DB_PATH = Path(__file__).parent.parent.parent / "data" / "database.json"


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


class JSONDatabase:
    """Simple JSON-based database for persistent storage."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database.
        
        Args:
            db_path: Path to database.json file
        """
        self.db_path = db_path or DB_PATH
        self._ensure_database_exists()
    
    def _ensure_database_exists(self) -> None:
        """Ensure database file exists and is valid."""
        try:
            if not self.db_path.exists():
                logger.warning(f"Database file not found at {self.db_path}, creating default")
                self._create_default_database()
            
            # Validate by loading
            with open(self.db_path, 'r') as f:
                json.load(f)
            
            logger.info(f"Database loaded from {self.db_path}")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise DatabaseError(f"Failed to initialize database: {e}")
    
    def _create_default_database(self) -> None:
        """Create default database structure."""
        default_db = {
            "metadata": {
                "version": "1.0",
                "created": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "description": "Mock database storing tickets and records"
            },
            "tickets": {},
            "records": {},
            "audit_log": []
        }
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump(default_db, f, indent=2)
        
        logger.info(f"Created default database at {self.db_path}")
    
    def _read_database(self) -> Dict[str, Any]:
        """Read entire database from file."""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read database: {e}")
            raise DatabaseError(f"Failed to read database: {e}")
    
    def _write_database(self, data: Dict[str, Any]) -> None:
        """Write database to file."""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug("Database written successfully")
        except Exception as e:
            logger.error(f"Failed to write database: {e}")
            raise DatabaseError(f"Failed to write database: {e}")
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """
        Get ticket by ID.
        
        Args:
            ticket_id: Ticket ID to retrieve
            
        Returns:
            Ticket data or None if not found
        """
        try:
            db = self._read_database()
            ticket = db.get("tickets", {}).get(ticket_id)
            
            if ticket:
                logger.info(f"Retrieved ticket: {ticket_id}")
            else:
                logger.warning(f"Ticket not found: {ticket_id}")
            
            return ticket
            
        except Exception as e:
            logger.error(f"Error getting ticket {ticket_id}: {e}")
            raise
    
    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update ticket by ID.
        
        Args:
            ticket_id: Ticket ID to update
            updates: Fields to update
            
        Returns:
            True if successful, False if not found
        """
        try:
            db = self._read_database()
            
            if ticket_id not in db.get("tickets", {}):
                logger.warning(f"Ticket not found for update: {ticket_id}")
                return False
            
            # Update ticket
            db["tickets"][ticket_id].update(updates)
            db["tickets"][ticket_id]["updated"] = datetime.utcnow().isoformat()
            
            # Update metadata
            db["metadata"]["last_updated"] = datetime.utcnow().isoformat()
            
            # Add to audit log
            self._add_audit_log(db, "ticket_updated", ticket_id, f"Updated: {list(updates.keys())}")
            
            self._write_database(db)
            logger.info(f"Updated ticket: {ticket_id} with {list(updates.keys())}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating ticket {ticket_id}: {e}")
            raise
    
    def create_ticket(self, ticket_data: Dict[str, Any]) -> str:
        """
        Create new ticket.
        
        Args:
            ticket_data: Ticket information
            
        Returns:
            Created ticket ID
        """
        try:
            db = self._read_database()
            
            # Generate ID if not provided
            if "id" not in ticket_data:
                ticket_id = f"ticket-{len(db['tickets']) + 1:03d}"
            else:
                ticket_id = ticket_data["id"]
            
            # Add metadata
            ticket_data["id"] = ticket_id
            ticket_data["created"] = datetime.utcnow().isoformat()
            ticket_data["updated"] = datetime.utcnow().isoformat()
            
            db["tickets"][ticket_id] = ticket_data
            
            # Update metadata
            db["metadata"]["last_updated"] = datetime.utcnow().isoformat()
            
            # Add to audit log
            self._add_audit_log(db, "ticket_created", ticket_id, f"New ticket created")
            
            self._write_database(db)
            logger.info(f"Created ticket: {ticket_id}")
            
            return ticket_id
            
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            raise
    
    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID."""
        try:
            db = self._read_database()
            record = db.get("records", {}).get(record_id)
            
            if record:
                logger.info(f"Retrieved record: {record_id}")
            else:
                logger.warning(f"Record not found: {record_id}")
            
            return record
            
        except Exception as e:
            logger.error(f"Error getting record {record_id}: {e}")
            raise
    
    def update_record(self, record_id: str, updates: Dict[str, Any]) -> bool:
        """Update record by ID."""
        try:
            db = self._read_database()
            
            if record_id not in db.get("records", {}):
                logger.warning(f"Record not found for update: {record_id}")
                return False
            
            db["records"][record_id].update(updates)
            db["records"][record_id]["updated"] = datetime.utcnow().isoformat()
            
            db["metadata"]["last_updated"] = datetime.utcnow().isoformat()
            self._add_audit_log(db, "record_updated", record_id, f"Updated: {list(updates.keys())}")
            
            self._write_database(db)
            logger.info(f"Updated record: {record_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating record {record_id}: {e}")
            raise
    
    def get_all_tickets(self) -> Dict[str, Dict[str, Any]]:
        """Get all tickets."""
        try:
            db = self._read_database()
            tickets = db.get("tickets", {})
            logger.info(f"Retrieved {len(tickets)} tickets")
            return tickets
        except Exception as e:
            logger.error(f"Error getting all tickets: {e}")
            raise
    
    def get_all_records(self) -> Dict[str, Dict[str, Any]]:
        """Get all records."""
        try:
            db = self._read_database()
            records = db.get("records", {})
            logger.info(f"Retrieved {len(records)} records")
            return records
        except Exception as e:
            logger.error(f"Error getting all records: {e}")
            raise
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log."""
        try:
            db = self._read_database()
            audit_log = db.get("audit_log", [])
            logger.info(f"Retrieved {len(audit_log)} audit log entries")
            return audit_log
        except Exception as e:
            logger.error(f"Error getting audit log: {e}")
            raise
    
    def _add_audit_log(self, db: Dict[str, Any], action: str, record_id: str, details: str) -> None:
        """Add entry to audit log."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "record_id": record_id,
            "details": details
        }
        db["audit_log"].append(entry)
        logger.debug(f"Audit log entry added: {action} for {record_id}")
    
    def clear_database(self) -> None:
        """Clear all data from database (for testing)."""
        try:
            self._create_default_database()
            logger.info("Database cleared and reset to default")
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            raise


# Global database instance
_db_instance: Optional[JSONDatabase] = None


def get_database() -> JSONDatabase:
    """Get or create database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = JSONDatabase()
    return _db_instance


def reset_database() -> None:
    """Reset database instance (useful for testing)."""
    global _db_instance
    if _db_instance:
        _db_instance.clear_database()
