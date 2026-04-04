from agents import function_tool

@function_tool
def query_knowledge_base(topic: str) -> str:
    """Search internal docs."""
    kb = {"refund": "Refunds require a receipt.", "shipping": "Takes 3-5 days."}
    return kb.get(topic.lower(), "Policy not found.")

@function_tool
def update_record(record_id: str, status: str) -> str:
    """Update system records."""
    return f"SUCCESS: Record {record_id} set to {status}."