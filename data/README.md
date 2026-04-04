# Data Directory

This directory stores application data files and database.

## Structure

```
data/
├── database.json                # JSON-based persistent database
├── README.md                    # This file
├── cache/                       # Cached responses
└── backup/                      # Backup files
```

## Database

### Location
`data/database.json`

### Purpose
- Persistent storage for tickets and records
- Survives application restarts
- Stores customer support tickets
- Stores general records (orders, returns, etc.)
- Maintains audit log of changes

### Schema

```json
{
  "metadata": { ... },           // Database metadata
  "tickets": { ... },            // Customer support tickets
  "records": { ... },            // Orders, returns, etc.
  "audit_log": [ ... ]           // Change tracking
}
```

### Sample Data

**Tickets**:
- `ticket-001`: John Smith - Refund request (Open)
- `ticket-002`: Jane Doe - Shipping inquiry (In-Progress)
- `ticket-101`: Alice Williams - General inquiry (Open)

**Records**:
- `order-001`: $99.99 - Shipped
- `order-002`: $149.99 - Pending
- `return-001`: $79.99 - Approved

### Usage

```python
from src.services.database import get_database

# Get database
db = get_database()

# Get ticket
ticket = db.get_ticket("ticket-001")

# Update ticket
db.update_ticket("ticket-001", {"status": "Resolved"})

# Get all records
records = db.get_all_records()

# Get audit log
audit = db.get_audit_log()
```

## Documentation

Full database documentation available in:
- [docs/DATABASE.md](../docs/DATABASE.md)

## Example Operations

### 1. Query Ticket
```python
db = get_database()
ticket = db.get_ticket("ticket-001")
print(f"Status: {ticket['status']}")
```

### 2. Update Status
```python
db.update_ticket("ticket-001", {"status": "Resolved"})
```

### 3. View Changes
```python
audit_log = db.get_audit_log()
for entry in audit_log:
    print(f"{entry['action']}: {entry['details']}")
```

### 4. Create New Ticket
```python
ticket_id = db.create_ticket({
    "customer": "New Customer",
    "status": "Open",
    "issue": "Product question"
})
```

## File Format

**Format**: JSON  
**Encoding**: UTF-8  
**Pretty Print**: Yes (indented)  
**Location**: `data/database.json`

## Git Ignore

This directory is in `.gitignore` to protect:
- Sensitive customer data
- Private information
- Database backups

## Backup

Backup database regularly:

```bash
# Manual backup
cp data/database.json data/backup/database_$(date +%Y%m%d).json

# List backups
ls -la data/backup/

# Restore from backup
cp data/backup/database_20250401.json data/database.json
```

## Reset Database

Reset to initial state:

```python
from src.services.database import get_database

db = get_database()
db.clear_database()  # Resets to default
```

## Performance Notes

- Database loads entire file into memory
- Suitable for small-medium datasets
- Consider migration to SQL for large datasets
- File I/O on each operation (no caching)

## Maintenance

### Monitor Database Size
```bash
du -h data/database.json
```

### Validate JSON
```bash
python -m json.tool data/database.json > /dev/null && echo "Valid"
```

### Pretty Print
```bash
python -m json.tool data/database.json
```

## Future

Planned enhancements:
- [ ] SQL database integration
- [ ] Automatic backups
- [ ] Data encryption
- [ ] Query optimization
- [ ] Schema versioning

---

**Database Service**: `src/services/database.py`  
**Database Documentation**: [docs/DATABASE.md](../docs/DATABASE.md)  
**Last Updated**: April 2025

