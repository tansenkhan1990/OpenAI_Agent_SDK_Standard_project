# This file contains a comprehensive test suite for the Agent system, demonstrating various features such as tools, handoffs, guardrails, structured output, sessions (memory), and tracing. It uses a local Ollama instance with the llama3.2:3b model for testing.
# To run this test, ensure you have Ollama installed and running with the llama3.2:3b model pulled. You can start Ollama with `ollama serve` and pull the model with `ollama pull llama3.2:3b`.
# it run locally and test the agent system with various scenarios, showcasing the capabilities of the Agent SDK in a controlled environment.
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
# 1. CONNECTION SETUP
# ==========================================
set_tracing_disabled(True)

local_client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

model = OpenAIChatCompletionsModel(
    model="llama3.2:3b",
    openai_client=local_client
)

# ==========================================
# 2. TOOLS
# ==========================================
@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is 22°C and sunny."

@function_tool
def calculate(expression: str) -> str:
    try:
        result = eval(expression)
        return f"The result of '{expression}' is {result}."
    except Exception as e:
        return f"Error: {str(e)}"

# ==========================================
# 3. HANDOFFS
# ==========================================
spanish_agent = Agent(
    name="Spanish Assistant",
    instructions="You only respond in Spanish. Be helpful and concise.",
    model=model,
)

main_agent = Agent(
    name="Main Assistant",
    instructions="If the user asks for Spanish, hand off to the Spanish Assistant.",
    model=model,
    handoffs=[spanish_agent],
    tools=[get_weather, calculate],
)

# ==========================================
# 4. GUARDRAILS
# ==========================================
def check_input_appropriateness(
    context: RunContextWrapper,
    agent: Agent,
    input_text: str
) -> GuardrailFunctionOutput:

    inappropriate_keywords = ["badword", "spam", "offensive"]
    is_ok = not any(k in input_text.lower() for k in inappropriate_keywords)

    return GuardrailFunctionOutput(
        output_info={
            "is_appropriate": is_ok,
            "reasoning": (
                "Input contains no inappropriate content."
                if is_ok else
                "Input flagged for inappropriate content."
            )
        },
        tripwire_triggered=not is_ok
    )

input_guardrail = InputGuardrail(guardrail_function=check_input_appropriateness)

guarded_agent = Agent(
    name="Safe Assistant",
    instructions="You are a helpful assistant.",
    model=model,
    input_guardrails=[input_guardrail],
)

# ==========================================
# 5. STRUCTURED OUTPUT
# ==========================================
class QAOutput(BaseModel):
    question: str
    answer: str

structured_agent = Agent(
    name="Structured QA Assistant",
    instructions="Return JSON with fields 'question' and 'answer'.",
    model=model,
    output_type=QAOutput,
)

async def structured_output_example():
    print("--- Structured Output Example ---")
    result = await Runner.run(
        structured_agent,
        "What is the capital of Germany?"
    )
    print("Final output:")
    print(result.final_output)
    print()

# ==========================================
# 6. SESSIONS (MEMORY)
# ==========================================
async def session_example():
    session = SQLiteSession("alice_user")

    agent = Agent(
        name="Assistant with Memory",
        instructions="Remember what the user tells you.",
        model=model,
    )

    print("Turn 1:")
    r1 = await Runner.run(agent, "My name is Alice and I love pizza.", session=session)
    print(r1.final_output, "\n")

    print("Turn 2:")
    r2 = await Runner.run(agent, "What is my name and what food do I like?", session=session)
    print(r2.final_output)

# ==========================================
# 7. TRACING
# ==========================================
async def tracing_example():
    with trace(workflow_name="My Agent Workflow"):
        agent = Agent(
            name="Traced Assistant",
            instructions="You are a helpful assistant.",
            model=model,
            tools=[get_weather],
        )

        result = await Runner.run(agent, "What's the weather in Paris?")
        print(f"Response: {result.final_output}")

# ==========================================
# 8. RUNNER EXAMPLE (FIXED)
# ==========================================
async def runner_example():
    agent = Agent(
        name="Simple Assistant",
        instructions="Answer concisely.",
        model=model,
    )

    result = await Runner.run(
        agent,
        "Explain what a large language model is in one sentence."
    )

    print(f"Final output: {result.final_output}")
# ==========================================
# 9. MAIN
# ==========================================
async def main():
    print("=== Testing Local Agent with llama3.2:3b ===\n")

    print("--- Test 1: Tools ---")
    agent_with_tools = Agent(
        name="Math & Weather Assistant",
        instructions="Use tools when needed.",
        model=model,
        tools=[calculate, get_weather],
    )
    r = await Runner.run(agent_with_tools, "What is 25 * 4? And weather in London?")
    print(r.final_output, "\n")

    print("--- Test 2: Handoffs ---")
    r = await Runner.run(main_agent, "Say hello in Spanish.")
    print(r.final_output, "\n")

    print("--- Test 3: Memory ---")
    await session_example()
    print()

    print("--- Test 4: Guardrails (Safe) ---")
    r = await Runner.run(guarded_agent, "What is the capital of France?")
    print(r.final_output, "\n")

    print("--- Test 4b: Guardrails (Unsafe) ---")
    try:
        await Runner.run(guarded_agent, "This is an offensive badword message")
    except InputGuardrailTripwireTriggered:
        print("Blocked: inappropriate content!\n")

    print("--- Test 5: Runner Example ---")
    await runner_example()
    print()

    print("--- Test 6: Tracing ---")
    await tracing_example()
    print()

    print("--- Test 7: Structured Output ---")
    await structured_output_example()
    print()

if __name__ == "__main__":
    asyncio.run(main())
