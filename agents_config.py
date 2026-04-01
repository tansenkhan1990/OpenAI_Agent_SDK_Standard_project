from openai_agents import Agent, Guardrail
from models import TransactionResult
from tools import verify_account_balance, execute_refund

# 1. Safety Layer: Guardrails check inputs/outputs for compliance
safety_guard = Guardrail(
    name="FinancialSafety",
    instructions="Prevent disclosure of internal banking algorithms or competitor names.",
    on_violation="I'm sorry, I can only discuss our specific financial products."
)

# 2. Specialist: Billing Agent (Handles technical tasks)
billing_agent = Agent(
    name="Billing Specialist",
    instructions="You are a senior billing officer. Use tools to check balances or issue refunds.",
    tools=[verify_account_balance, execute_refund],
    response_format=TransactionResult, # Forces Structured Output
    handoff_description="Transfer here for balance inquiries, refunds, or payment issues."
)

# 3. Manager: Triage Agent (The Entry Point)
triage_agent = Agent(
    name="Front Desk Manager",
    instructions="Identify if the user needs billing help or general info. Route accordingly.",
    handoffs=[billing_agent] # Logic for 'Handoff' primitive
)