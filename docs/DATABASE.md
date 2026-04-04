# Database Documentation

## Overview

The project uses a **JSON-based persistent database** stored in `data/database.json`. This provides a simple, file-based storage solution that persists between application runs.

## Database Structure

### Top-Level Schema

```json
{
  "metadata": {
    "version": "1.0",
    "created": "2025-04-04T10:00:00",
    "last_updated": "2025-04-04T10:30:00",
    "description": "Mock database storing tickets and records"
  },
  "tickets": { ... },
  "records": { ... },
  "audit_log": [ ... ]
}
```

### Sections

#### 1. Metadata
Database metadata and versioning information.

```json
{
  "metadata": {
    "version": "1.0",
    "created": "ISO timestamp",
    "last_updated": "ISO timestamp",
    "description": "Database description"
  }
}
```

#### 2. Tickets
Customer support tickets.

```json
{
  "tickets": {
    "ticket-001": {
      "id": "ticket-001",
      "customer": "John Smith",
      "status": "Open|In-Progress|Resolved|Escalated",
      "issue": "Description of issue",
      "created": "ISO timestamp",
      "updated": "ISO timestamp"
    }
  }
}
```

**Ticket Fields**:
- `id`: Unique ticket identifier
- `customer`: Customer name
- `status`: Current ticket status
- `issue`: Description of the issue
- `created`: Creation timestamp
- `updated`: Last update timestamp

#### 3. Records
General records (orders, returns, etc.).

```json
{
  "records": {
    "order-001": {
      "id": "order-001",
      "type": "order|return|payment",
      "status": "Pending|Shipped|Delivered|Approved|Rejected",
      "amount": 99.99,
      "created": "ISO timestamp",
      "updated": "ISO timestamp"
    }
  }
}
```

**Record Fields**:
- `id`: Unique record identifier
- `type`: Type of record (order, return, payment, etc.)
- `status`: Current status
- `amount`: Monetary amount (if applicable)
- `created`: Creation timestamp
- `updated`: Last update timestamp

#### 4. Audit Log
Log of all database changes for auditing.

```json
{
  "audit_log": [
    {
      "timestamp": "ISO timestamp",
      "action": "ticket_created|ticket_updated|record_updated",
      "record_id": "ID of affected record",
      "details": "Description of change"
    }
  ]
}
```

## Database Service API

### Location
`src/services/database.py`

### Key Methods

#### Getting Database Instance
```python
from src.services.database import get_database

db = get_database()  # Singleton pattern
```

#### Ticket Operations

```python
# Get ticket by ID
ticket = db.get_ticket("ticket-001")

# Get all tickets
all_tickets = db.get_all_tickets()

# Create new ticket
ticket_id = db.create_ticket({
    "customer": "Jane Doe",
    "status": "Open",
    "issue": "Product inquiry"
})

# Update ticket
success = db.update_ticket("ticket-001", {
    "status": "Resolved",
    "notes": "Issue resolved"
})
```

#### Record Operations

```python
# Get record by ID
record = db.get_record("order-001")

# Get all records
all_records = db.get_all_records()

# Update record
success = db.update_record("order-001", {
    "status": "Shipped"
})
```

#### Audit Log

```python
# Get audit log
audit_log = db.get_audit_log()
```

#### Utility Functions

```python
# Clear database (testing only)
db.clear_database()

# Reset database instance
from src.services.database import reset_database
reset_database()
```

## Tools Integration

### update_record Tool

The `update_record()` tool in `src/tools/knowledge_base.py` uses the database:

```python
@function_tool
def update_record(record_id: str, status: str) -> str:
    """Update system records with new status."""
    db = get_database()
    
    # Try ticket first
    ticket_updated = db.update_ticket(record_id, {"status": status})
    
    if not ticket_updated:
        # Try as record
        record_updated = db.update_record(record_id, {"status": status})
    
    return success_message
```

## Sample Data

### Included Tickets

```json
{
  "ticket-001": {
    "id": "ticket-001",
    "customer": "John Smith",
    "status": "Open",
    "issue": "Refund request",
    "created": "2025-04-01",
    "updated": "2025-04-02"
  },
  "ticket-002": {
    "id": "ticket-002",
    "customer": "Jane Doe",
    "status": "In-Progress",
    "issue": "Shipping inquiry",
    "created": "2025-04-02",
    "updated": "2025-04-03"
  },
  "ticket-101": {
    "id": "ticket-101",
    "customer": "Alice Williams",
    "status": "Open",
    "issue": "General inquiry",
    "created": "2025-04-04",
    "updated": "2025-04-04"
  }
}
```

### Included Records

```json
{
  "order-001": {
    "id": "order-001",
    "type": "order",
    "status": "Shipped",
    "amount": 99.99,
    "created": "2025-03-25"
  },
  "order-002": {
    "id": "order-002",
    "type": "order",
    "status": "Pending",
    "amount": 149.99,
    "created": "2025-04-03"
  }
}
```

## Example Workflows

### Workflow 1: Query and Update

```python
from src.services.database import get_database

db = get_database()

# Get ticket info
ticket = db.get_ticket("ticket-001")
print(f"Current status: {ticket['status']}")

# Update ticket
db.update_ticket("ticket-001", {"status": "Resolved"})

# Verify update
updated_ticket = db.get_ticket("ticket-001")
print(f"New status: {updated_ticket['status']}")
```

### Workflow 2: Create Record and Log

```python
# Create new ticket
ticket_id = db.create_ticket({
    "customer": "Bob Johnson",
    "status": "Open",
    "issue": "Warranty question"
})

# Get audit log
audit = db.get_audit_log()
for entry in audit:
    if entry["record_id"] == ticket_id:
        print(f"Action: {entry['action']}, Details: {entry['details']}")
```

### Workflow 3: Batch Operations

```python
# Get all tickets
all_tickets = db.get_all_tickets()
open_tickets = [t for t in all_tickets.values() if t["status"] == "Open"]

# Update all open tickets
for ticket in open_tickets:
    db.update_ticket(ticket["id"], {"status": "In-Progress"})

print(f"Updated {len(open_tickets)} tickets")
```

## Error Handling

```python
from src.services.database import get_database, DatabaseError

try:
    db = get_database()
    ticket = db.get_ticket("nonexistent")
    
    if not ticket:
        print("Ticket not found")
    
except DatabaseError as e:
    print(f"Database error: {e}")
```

## Logging

All database operations are logged:

```
INFO - Retrieved ticket: ticket-001
INFO - Updated ticket: ticket-001 with ['status']
INFO - Created ticket: ticket-102
DEBUG - Database written successfully
DEBUG - Audit log entry added: ticket_created for ticket-102
```

## Testing

### Clear Database
```python
from src.services.database import get_database

db = get_database()
db.clear_database()
```

This resets the database to default state with no data.

### Run Database Tests
```bash
pytest tests/test_tools.py -v
```

## Performance Considerations

- **File I/O**: Each operation reads/writes entire JSON file
- **Scalability**: Suitable for small-medium datasets
- **Persistence**: Data survives application restarts
- **Concurrent Access**: Not recommended for concurrent modifications

## Migration to Real Database

To replace JSON with a real database:

1. Create new database driver (e.g., `src/services/sql_database.py`)
2. Implement same interface as `JSONDatabase`
3. Update `get_database()` to use new driver
4. No changes needed to tools or agents

## Backup

The database file is stored in `data/database.json`:

```bash
# Backup database
cp data/database.json data/database.backup.json

# Restore from backup
cp data/database.backup.json data/database.json
```

## Future Enhancements

- [ ] Add search/query functionality
- [ ] Add filtering and sorting
- [ ] Add transactions/rollback
- [ ] Add encryption for sensitive data
- [ ] Add migration tools
- [ ] Add schema validation
- [ ] Replace with SQL database
- [ ] Add caching layer

---

**Database Path**: `data/database.json`  
**Service Version**: 1.0  
**Last Updated**: April 2025
