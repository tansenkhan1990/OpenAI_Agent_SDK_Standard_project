import asyncio
from typing import List
from pydantic import BaseModel
from openai import AsyncOpenAI
from agents import (
    Agent, Runner, function_tool, trace, 
    set_tracing_disabled, InputGuardrail,
    OpenAIChatCompletionsModel, SQLiteSession,
    GuardrailFunctionOutput, RunContextWrapper
)
from agents.exceptions import InputGuardrailTripwireTriggered

# ==========================================
# 1. CONNECTION SETUP (The Foundation)
# ==========================================
# IMPORTANT: Disable OpenAI's cloud tracing to keep everything local
set_tracing_disabled(True)

# Create a client that points to your local Ollama server
local_client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",  # Ollama's default API endpoint
    api_key="ollama",                      # Ollama ignores this, but a value is required
)

# Create the model instance that the SDK will use
model = OpenAIChatCompletionsModel(
    model="llama3.2:3b",                  # The model you pulled
    openai_client=local_client
)

# ==========================================
# 2. TOOLS (Functions the agent can call)
# ==========================================
@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # In a real scenario, this would call a weather API
    return f"The weather in {city} is 22°C and sunny."

@function_tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)
        return f"The result of '{expression}' is {result}."
    except Exception as e:
        return f"Error: {str(e)}"

# ==========================================
# 3. HANDOFFS (Delegate to another agent)
# ==========================================
# Create a specialized agent for Spanish responses
spanish_agent = Agent(
    name="Spanish Assistant",
    instructions="You only respond in Spanish. Be helpful and concise.",
    model=model,
)

# Create the main agent that can hand off to the Spanish agent
main_agent = Agent(
    name="Main Assistant",
    instructions="You are a helpful assistant. If someone asks you to speak Spanish, hand off to the Spanish Assistant.",
    model=model,
    handoffs=[spanish_agent],
    tools=[get_weather, calculate],
)

# ==========================================
# 4. GUARDRAILS (Validate inputs) - FIXED SIGNATURE
# ==========================================
# Guardrail function MUST accept 3 arguments: context, agent, input_text
def check_input_appropriateness(
    context: RunContextWrapper,  # Context wrapper (required but may not be used)
    agent: Agent,                 # The agent instance (required but may not be used)
    input_text: str              # The user input text
) -> GuardrailFunctionOutput:
    """Check if the user input is appropriate."""
    inappropriate_keywords = ["badword", "spam", "offensive"]
    is_ok = not any(keyword in input_text.lower() for keyword in inappropriate_keywords)
    
    # Return GuardrailFunctionOutput with tripwire_triggered flag
    return GuardrailFunctionOutput(
        output_info={
            "is_appropriate": is_ok,
            "reasoning": "Input contains no inappropriate content." if is_ok else "Input flagged for inappropriate content."
        },
        tripwire_triggered=not is_ok  # True = block, False = allow
    )

input_guardrail = InputGuardrail(guardrail_function=check_input_appropriateness)

guarded_agent = Agent(
    name="Safe Assistant",
    instructions="You are a helpful assistant.",
    model=model,
    input_guardrails=[input_guardrail],
)

# ==========================================
# 5. SESSIONS (Multi-turn memory)
# ==========================================
async def session_example():
    # Create a SQLite session (in-memory by default)
    session = SQLiteSession("alice_user")
    
    agent = Agent(
        name="Assistant with Memory",
        instructions="You are a helpful assistant. Remember what the user tells you.",
        model=model,
    )
    
    print("Turn 1 - Teaching the agent...")
    result1 = await Runner.run(
        agent,
        "My name is Alice and I love pizza.",
        session=session
    )
    print(f"Agent: {result1.final_output}\n")
    
    print("Turn 2 - Testing memory...")
    result2 = await Runner.run(
        agent,
        "What's my name and what food do I like?",
        session=session
    )
    print(f"Agent: {result2.final_output}")

# ==========================================
# 6. TRACING (Debug + visualize)
# ==========================================
async def tracing_example():
    # Create a trace to group multiple agent runs together
    with trace(workflow_name="My Agent Workflow"):
        agent = Agent(
            name="Traced Assistant",
            instructions="You are a helpful assistant.",
            model=model,
            tools=[get_weather],
        )
        
        result = await Runner.run(
            agent,
            "What's the weather in Paris?"
        )
        print(f"Response: {result.final_output}")

# ==========================================
# 7. RUNNER (Executes an agent turn)
# ==========================================
async def runner_example():
    agent = Agent(
        name="Simple Assistant",
        instructions="You are a helpful assistant. Answer concisely.",
        model=model,
    )
    
    result = await Runner.run(
        agent,
        "Explain what a large language model is in one sentence."
    )
    
    print(f"Final output: {result.final_output}")
    print(f"Number of steps: {len(result.steps)}")
    print(f"Input tokens used: {result.input_tokens}")
    print(f"Output tokens used: {result.output_tokens}")

# ==========================================
# 8. COMPLETE EXAMPLE: Multi-Agent System
# ==========================================
async def main():
    print("=== Testing Local Agent with llama3.2:3b ===\n")
    
    # Test basic agent with tools
    print("--- Test 1: Agent with Tools ---")
    agent_with_tools = Agent(
        name="Math & Weather Assistant",
        instructions="You can do calculations and check weather. Use the tools provided.",
        model=model,
        tools=[calculate, get_weather],
    )
    result = await Runner.run(agent_with_tools, "What is 25 * 4? Also, what's the weather in London?")
    print(f"Response: {result.final_output}\n")
    
    # Test handoffs
    print("--- Test 2: Agent Handoffs ---")
    result = await Runner.run(main_agent, "Can you say 'Hello, how are you?' in Spanish?")
    print(f"Response: {result.final_output}\n")
    
    # Test session/memory
    print("--- Test 3: Session Memory ---")
    await session_example()
    print()
    
    # Test guardrails - with safe input
    print("--- Test 4: Guardrails (Safe Input) ---")
    result = await Runner.run(guarded_agent, "What is the capital of France?")
    print(f"Response: {result.final_output}\n")
    
    # Test guardrails - with unsafe input (should be blocked)
    print("--- Test 4b: Guardrails (Unsafe Input - Should be blocked) ---")
    try:
        result = await Runner.run(guarded_agent, "This is an offensive message with badword")
        print(f"Response: {result.final_output}\n")
    except InputGuardrailTripwireTriggered as e:
        print(f"Blocked: Input contained inappropriate content!\n")
    
    # Test runner with tracing
    print("--- Test 5: Runner with Tracing ---")
    await tracing_example()

if __name__ == "__main__":
    asyncio.run(main())