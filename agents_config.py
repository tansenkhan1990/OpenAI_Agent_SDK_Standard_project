from agents import Agent, ModelSettings, input_guardrail, GuardrailFunctionOutput
from tools import query_knowledge_base, update_record
from models import AgentResponse

# ✅ Define guardrail FIRST
@input_guardrail
async def safety_check(context, agent, user_input):
    if "ignore previous instructions" in user_input.lower():
        return GuardrailFunctionOutput(
            tripwire_triggered=True, 
            output_info="Security: Blocked prompt injection."
        )
    return GuardrailFunctionOutput(
        tripwire_triggered=False, 
        output_info="Security: Safe."
    )

def setup_workforce(model):
    # Standard settings for Free Tier
    free_settings = ModelSettings(max_tokens=500, temperature=0.1)

    researcher = Agent(
        name="Research Specialist",
        instructions="Find facts in the KB.",
        tools=[query_knowledge_base],
        model=model,
        model_settings=free_settings
    )

    executor = Agent(
        name="Action Specialist",
        instructions="Update records via tool.",
        tools=[update_record],
        model=model,
        model_settings=free_settings
    )

    manager = Agent(
        name="Support Manager",
        instructions="Triage to specialists. You MUST return an AgentResponse.",
        model=model,
        handoffs=[researcher, executor],
        input_guardrails=[safety_check], 
        output_type=AgentResponse,
        model_settings=free_settings
    )
    return manager