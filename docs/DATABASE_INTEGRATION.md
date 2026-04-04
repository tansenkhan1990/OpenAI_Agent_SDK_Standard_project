# Database Integration Guide

## 📊 Database Architecture

### System Overview

```
User Query
    ↓
Agent Tools
    ↓
Database Service (src/services/database.py)
    ↓
JSON Database File (data/database.json)
    ↓
Persistent Storage
```

## 🗄️ Database Structure

### Complete Schema

```
data/database.json
│
├── metadata (Database info)
│   ├── version: "1.0"
│   ├── created: "2025-04-04T..."
│   ├── last_updated: "2025-04-04T..."
│   └── description: "Mock database..."
│
├── tickets (Customer support tickets)
│   ├── ticket-001
│   │   ├── id: "ticket-001"
│   │   ├── customer: "John Smith"
│   │   ├── status: "Open"
│   │   ├── issue: "Refund request"
│   │   ├── created: "2025-04-01"
│   │   └── updated: "2025-04-02"
│   ├── ticket-002
│   ├── ticket-101
│   └── ...
│
├── records (Orders, returns, etc.)
│   ├── order-001
│   │   ├── id: "order-001"
│   │   ├── type: "order"
│   │   ├── status: "Shipped"
│   │   ├── amount: 99.99
│   │   └── created: "2025-03-25"
│   ├── order-002
│   ├── return-001
│   └── ...
│
└── audit_log (Change tracking)
    ├── [0]
    │   ├── timestamp: "2025-04-04T10:00:00"
    │   ├── action: "ticket_created"
    │   ├── record_id: "ticket-101"
    │   └── details: "New ticket created"
    ├── [1]
    └── ...
```

## 🔌 Integration Points

### 1. Tools Use Database

```
update_record(ticket_id, status)
    ↓
get_database()
    ↓
db.update_ticket() OR db.update_record()
    ↓
Read database.json
    ↓
Update record
    ↓
Write database.json
    ↓
Return success message
```

### 2. Query Operations

```
query_knowledge_base(topic)
    ↓
Search CONSTANTS.KNOWLEDGE_BASE
    ↓
Return policy information
```

### 3. Status Queries

```
get_record_status(record_id)
    ↓
get_database()
    ↓
db.get_ticket() or db.get_record()
    ↓
Return current status
```

## 📝 Data Flow Examples

### Example 1: Updating a Ticket

```
User Command: "Update ticket-001 to Resolved"
    ↓
Manager Agent calls: update_record("ticket-001", "Resolved")
    ↓
Tool validates input using UpdateRecordInput
    ↓
Tool gets database: db = get_database()
    ↓
Tool updates: db.update_ticket("ticket-001", {"status": "Resolved"})
    ↓
Database reads: data/database.json
    ↓
Database modifies: tickets["ticket-001"]["status"] = "Resolved"
    ↓
Database logs: audit_log entry created
    ↓
Database writes: data/database.json
    ↓
Returns: "SUCCESS: Record ticket-001 updated to status: Resolved"
    ↓
Agent Response returned to user
```

### Example 2: Creating a Ticket

```
db.create_ticket({
    "customer": "New Customer",
    "status": "Open",
    "issue": "Product inquiry"
})
    ↓
Generates unique ID: "ticket-105"
    ↓
Adds timestamps
    ↓
Reads database.json
    ↓
Adds to tickets section
    ↓
Adds audit log entry
    ↓
Writes back to database.json
    ↓
Returns: "ticket-105"
```

### Example 3: Querying Status

```
get_record_status("order-001")
    ↓
Gets database instance
    ↓
Tries: db.get_ticket("order-001") → Not found
    ↓
Tries: db.get_record("order-001") → Found!
    ↓
Returns: "Shipped"
```

## 💾 Persistence Mechanism

### How Data Survives Restarts

```
Application Start
    ↓
initialize_app() in src/main.py
    ↓
get_database() creates JSONDatabase
    ↓
JSONDatabase.__init__()
    ↓
_ensure_database_exists()
    ↓
Check: Does database.json exist?
    ├─ YES: Load it into memory
    └─ NO: Create default database
    ↓
Database ready for queries
```

### File-Based Storage

```
Runtime Changes:
    ticket-001.status = "Open" → "Resolved"
    ↓
Immediately written to file:
    data/database.json (persistent)
    ↓
Next application run:
    Load from: data/database.json
    ↓
Restored state:
    ticket-001.status = "Resolved" (from previous session)
```

## 🔄 CRUD Operations

### Create

```python
db.create_ticket({
    "customer": "Name",
    "status": "Open",
    "issue": "Description"
})
# Returns: "ticket-105"
```

### Read

```python
# Get single ticket
ticket = db.get_ticket("ticket-001")

# Get all tickets
all_tickets = db.get_all_tickets()

# Get all records
all_records = db.get_all_records()
```

### Update

```python
db.update_ticket("ticket-001", {
    "status": "Resolved",
    "notes": "Issue fixed"
})

db.update_record("order-001", {
    "status": "Shipped"
})
```

### Delete

Not implemented (soft delete - change status)

## 📊 Data Statistics

### Sample Database

```
Tickets:     4 items     (ticket-001, 002, 101, etc.)
Records:     3 items     (order-001, 002, return-001)
Audit Log:   8+ entries  (all changes tracked)
Total Size:  ~2KB        (typical JSON file)
```

### Growth Estimates

```
Per Ticket:     ~200 bytes
Per Record:     ~150 bytes
Per Audit Log:  ~100 bytes

For 1000 tickets:   ~300 KB
For 10000 tickets:  ~3 MB
For 100000 tickets: ~30 MB (consider SQL)
```

## 🛡️ Data Integrity

### Validation

```
Input → UpdateRecordInput Pydantic Model
           ↓
           Validates: record_id (non-empty, < 100 chars)
           Validates: status (non-empty, < 50 chars)
           ↓
           Database Operation
           ↓
           Write to File
           ↓
           Audit Log Entry
```

### Audit Trail

```
Every change logged:
├── ticket_created
├── ticket_updated
├── record_updated
└── ...

Each entry includes:
├── timestamp: When it happened
├── action: What happened
├── record_id: Which record
└── details: Specific changes
```

## 🔐 Git Ignore

Database is protected:

```
# .gitignore
data/*.json
data/cache/
data/backup/
```

This prevents:
- Committing sensitive customer data
- Overwriting production databases
- Sharing private information

## 🧪 Testing

### Reset Database

```python
from src.services.database import get_database

db = get_database()
db.clear_database()  # Reset to defaults
```

### Backup Before Testing

```bash
cp data/database.json data/backup/database_before_test.json
```

## 🚀 Performance

### Read Performance
```
Operation: db.get_ticket("ticket-001")
Time:      ~1ms (file I/O + JSON parsing)
```

### Write Performance
```
Operation: db.update_ticket("ticket-001", {...})
Time:      ~5ms (read + modify + write)
```

### Typical Query
```
User request → Tool execution → DB operation → Response
Total time:   1-3 seconds (mostly model inference)
DB portion:   ~5-10ms (negligible)
```

## 🔄 Update Workflow

```
1. Tool receives request
   ├─ Validate input (Pydantic)
   ├─ Log operation (DEBUG level)
   └─ Get database instance

2. Database operation
   ├─ Read JSON file
   ├─ Locate record section
   ├─ Find specific record by ID
   └─ Update field(s)

3. Metadata update
   ├─ Update "last_updated" timestamp
   ├─ Create audit log entry with timestamp
   └─ Prepare response

4. Write and return
   ├─ Write JSON back to file
   ├─ Log success (INFO level)
   └─ Return result to agent
```

## 📋 Sample Queries

### Query: Get all open tickets
```python
db = get_database()
all_tickets = db.get_all_tickets()
open_tickets = {k: v for k, v in all_tickets.items() 
                if v['status'] == 'Open'}
```

### Query: Find ticket by customer
```python
all_tickets = db.get_all_tickets()
customer_tickets = {k: v for k, v in all_tickets.items() 
                    if v['customer'] == 'John Smith'}
```

### Query: Get recent changes
```python
audit_log = db.get_audit_log()
recent = audit_log[-10:]  # Last 10 changes
```

### Query: Update multiple records
```python
for ticket_id in ['ticket-001', 'ticket-002']:
    db.update_ticket(ticket_id, {'status': 'Resolved'})
```

## 🔗 Related Files

```
Database Implementation:   src/services/database.py
Database Usage (Tools):    src/tools/knowledge_base.py
Database Tests:            tests/test_tools.py
Database Documentation:    docs/DATABASE.md
Database File:             data/database.json
Data Directory:            data/README.md
```

## 🎯 Quick Reference

| Task | Code |
|------|------|
| Get DB | `db = get_database()` |
| Get Ticket | `db.get_ticket("id")` |
| Update Ticket | `db.update_ticket("id", {...})` |
| Create Ticket | `db.create_ticket({...})` |
| Get All Tickets | `db.get_all_tickets()` |
| Get Record | `db.get_record("id")` |
| Get Audit Log | `db.get_audit_log()` |
| Clear DB | `db.clear_database()` |

## ✅ Verification

```bash
# Check database exists
ls -la data/database.json

# Validate JSON structure
python -m json.tool data/database.json

# Check file size
du -h data/database.json

# View contents
cat data/database.json | python -m json.tool
```

---

**Database Location**: `data/database.json`  
**Service Module**: `src/services/database.py`  
**Last Updated**: April 2025
