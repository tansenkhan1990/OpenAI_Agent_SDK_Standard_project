import asyncio
import os
from openai import AsyncOpenAI
from agents import Runner, OpenAIChatCompletionsModel, set_tracing_disabled
from dotenv import load_dotenv
from agents_config import setup_workforce

load_dotenv()
set_tracing_disabled(True)

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# ✅ SWITCHED: Qwen 3.6 is currently more stable than Llama for Free Tier
shared_model = OpenAIChatCompletionsModel(
    model="qwen/qwen3.6-plus-preview:free", 
    openai_client=client
)

async def run_project():
    manager = setup_workforce(shared_model)
    
    print("\n--- 🤖 OpenAI Agent SDK [Qwen 3.6 Build] ---")
    query = "Find the refund policy and update ticket #101 to 'Resolved'."

    try:
        # Settings are inherited from Agent.model_settings
        result = await Runner.run(manager, query)
        
        res = result.final_output
        print(f"\n[REPORT SUCCESS]")
        print(f"Status: {res.status}\nSummary: {res.summary}")

    except Exception as e:
        # Check if the error is still a 429
        if "429" in str(e):
            print("\n🚨 STILL RATE LIMITED: The Free Tier is very busy. Wait 60 seconds and try again.")
        else:
            print(f"\n❌ FATAL ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_project())