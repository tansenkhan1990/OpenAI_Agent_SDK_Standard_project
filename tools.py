from openai_agents import function_tool

@function_tool
def verify_account_balance(account_id: str) -> str:
    """
    Retrieves the balance for a specific account. 
    Agentic Design: Keep tools atomic and read-only where possible.
    """
    # Mock Database lookup
    db = {"ACC-77": 5000.0, "ACC-88": 1200.0}
    balance = db.get(account_id)
    if balance is not None:
        return f"Account {account_id} has a balance of ${balance}."
    return "Error: Account ID not found."

@function_tool
def execute_refund(account_id: str, amount: float) -> str:
    """Triggers a refund to a customer account after validation."""
    return f"REFUND_SUCCESS: ${amount} credited to {account_id}."