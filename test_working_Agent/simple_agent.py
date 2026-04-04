# this is a simple Agent perfectly working 
# It run with Open Router key where model is loading from cloud
import asyncio
import os
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel
from agents import set_tracing_disabled
from dotenv import load_dotenv

load_dotenv()

# CRITICAL: Disable tracing (it tries to call OpenAI's platform)
set_tracing_disabled(True)

# Create client pointing to OpenRouter's cloud endpoint
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),  # Your existing key
)

# Use a model via OpenRouter
model = OpenAIChatCompletionsModel(
    model="openai/gpt-3.5-turbo",  # Commonly available model
    openai_client=client
)

async def main():
    agent = Agent(
        name="Gemini Assistant",
        instructions="You are a helpful assistant. Respond concisely.",
        model=model
    )
    
    result = await Runner.run(agent, "What are three benefits of cloud computing?")
    print(result.final_output)

if asyncio.run(main()):
    print("Done!")