import asyncio
import os
from dotenv import load_dotenv
from openai_agents import Runner
from agents_config import triage_agent, safety_guard

# Load environment variables (API Keys)
load_dotenv()

async def run_professional_agent():
    """
    Production-ready execution loop using the Agent SDK Runner.
    This handles the complexity of 'Thought -> Action -> Observation' loops.
    """
    print("--- Financial Agent System Online [v2026.3.31] ---")
    
    # Example Industry Scenario: Complex multi-step request
    user_query = "I need a refund of $50 for my account ACC-77 because I was overcharged."

    try:
        # The Runner is the heart of the SDK
        result = await Runner.run(
            agent=triage_agent,
            input=user_query,
            guardrails=[safety_guard], # Apply safety policies
            max_steps=5 # Prevent infinite loops in complex logic
        )

        # Handle Guardrail Violations
        if result.interrupted_by_guardrail:
            print(f"BLOCK: {result.interruption_message}")
            return

        # Output the validated, structured result
        # Because we used 'response_format', result.final_output is a Pydantic object
        output = result.final_output
        print(f"\n[FINAL RESPONSE]")
        print(f"Status: {output.status.upper()}")
        print(f"ID: {output.transaction_id}")
        print(f"Summary: {output.summary}")

    except Exception as e:
        print(f"Critical System Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_professional_agent())