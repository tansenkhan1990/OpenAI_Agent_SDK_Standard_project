from agents import function_tool

@function_tool
def query_knowledge_base(topic: str) -> str:
    """Search internal documentation for policies and procedures."""
    kb = {
        "refund": "Refunds require an original receipt and are processed within 5-7 business days.",
        "shipping": "Standard shipping takes 3-5 business days. Express shipping takes 1-2 days.",
        "return": "Returns are accepted within 30 days of purchase with original packaging.",
        "warranty": "All products come with a 1-year limited warranty.",
        "cancellation": "Orders can be cancelled within 1 hour of placement."
    }
    return kb.get(topic.lower(), f"Policy for '{topic}' not found in knowledge base.")

@function_tool
def update_record(record_id: str, status: str) -> str:
    """Update system records with new status."""
    return f"SUCCESS: Record {record_id} has been updated to status: {status}."