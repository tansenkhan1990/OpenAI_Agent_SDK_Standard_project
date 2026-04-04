from agents import Agent, ModelSettings, input_guardrail, GuardrailFunctionOutput, RunContextWrapper
from tools import query_knowledge_base, update_record
from models import AgentResponse

@input_guardrail
async def safety_check(
    context: RunContextWrapper,
    agent: Agent,
    user_input: str
) -> GuardrailFunctionOutput:
    """Prevent prompt injection and malicious instructions."""
    dangerous_patterns = [
        "ignore previous instructions",
        "ignore your instructions", 
        "system prompt",
        "you are now",
        "forget your",
        "disregard",
        "ignore all"
    ]
    
    for pattern in dangerous_patterns:
        if pattern in user_input.lower():
            return GuardrailFunctionOutput(
                tripwire_triggered=True,
                output_info={"reason": f"Blocked pattern: {pattern}"}
            )
    
    return GuardrailFunctionOutput(
        tripwire_triggered=False,
        output_info={"reason": "Input passed safety check"}
    )

def setup_workforce(model):
    """Create and configure the agent workforce."""
    
    # Model settings optimized for llama3.2:3b
    local_settings = ModelSettings(
        max_tokens=1000,
        temperature=0.1,  # Low temperature for consistent outputs
        top_p=0.9
    )
    
    # Specialist Agent 1: Researcher
    researcher = Agent(
        name="Researcher",
        instructions="""You are a Research Specialist. Your job is to:
        1. Query the knowledge base for relevant information
        2. Provide accurate, factual answers about company policies
        3. If you don't know something, say so clearly
        
        Always use the query_knowledge_base tool to find information.""",
        tools=[query_knowledge_base],
        model=model,
        model_settings=local_settings
    )
    
    # Specialist Agent 2: Executor
    executor = Agent(
        name="Executor",
        instructions="""You are an Execution Specialist. Your job is to:
        1. Update system records based on decisions made
        2. Confirm updates were successful
        3. Track ticket status changes
        
        Always use the update_record tool to make system changes.""",
        tools=[update_record],
        model=model,
        model_settings=local_settings
    )
    
    # Manager Agent (Coordinates everything)
    manager = Agent(
        name="Manager",
        instructions="""You are a Manager Agent coordinating customer support requests.

YOUR WORKFLOW:
1. Analyze the user's request
2. If policy information is needed → handoff to Researcher
3. If system updates are needed → handoff to Executor
4. After getting information from specialists, produce a final AgentResponse

FINAL RESPONSE REQUIREMENTS:
- status: Choose "Resolved" if complete, "In-Progress" if partial, "Escalated" if complex
- summary: Concise summary of what was done
- next_steps: List any remaining actions needed

Always complete with a structured AgentResponse after gathering all information.""",
        model=model,
        handoffs=[researcher, executor],
        input_guardrails=[safety_check],
        output_type=AgentResponse,
        model_settings=local_settings
    )
    
    return manager