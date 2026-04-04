import asyncio
import os
from openai import AsyncOpenAI
from agents import Runner, OpenAIChatCompletionsModel, set_tracing_disabled
from agents_config import setup_workforce
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Disable cloud tracing for local development
set_tracing_disabled(True)

# Connect to local Ollama server with env variables
client = AsyncOpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.getenv("OLLAMA_API_KEY", "ollama"),  # Dummy key for Ollama
)

# ✅ Using your perfectly working model: llama3.2:3b
shared_model = OpenAIChatCompletionsModel(
    model="llama3.2:3b",  # Your working model from the previous tests
    openai_client=client
)

async def run_project():
    """Main entry point for the agent system."""
    
    print("\n" + "="*60)
    print("🏠 LOCAL AGENT SDK RUNNER [Ollama - llama3.2:3b]")
    print("="*60)
    
    # Setup the agent workforce
    manager = setup_workforce(shared_model)
    
    # Test queries
    test_queries = [
        "Find the refund policy and update ticket #101 to 'Resolved'.",
        "What's our shipping policy?",
        "Check the warranty policy for electronics."
    ]
    
    # Run all test queries
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 TEST {i}: {query}")
        print("-"*40)
        
        try:
            result = await Runner.run(manager, query)
            response = result.final_output
            
            print("\n✅ AGENT RESPONSE:")
            print(f"   Ticket ID: {response.ticket_id}")
            print(f"   Status: {response.status}")
            print(f"   Summary: {response.summary}")
            if response.next_steps:
                print(f"   Next Steps: {', '.join(response.next_steps)}")
            print()
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            print("\nTroubleshooting tips:")
            print("1. Make sure Ollama is running: `ollama serve`")
            print("2. Verify model is pulled: `ollama list`")
            print("3. Check Ollama is responding: `ollama ps`")

async def run_custom_query(query: str):
    """Run a custom query through the agent system."""
    
    manager = setup_workforce(shared_model)
    
    print(f"\n📝 CUSTOM QUERY: {query}")
    print("-"*40)
    
    try:
        result = await Runner.run(manager, query)
        response = result.final_output
        
        print("\n✅ RESPONSE:")
        print(f"   Status: {response.status}")
        print(f"   Summary: {response.summary}")
        if response.next_steps:
            print(f"   Next Steps: {response.next_steps}")
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

async def interactive_mode():
    """Run the agent in interactive mode for continuous conversation."""
    
    manager = setup_workforce(shared_model)
    
    print("\n" + "="*60)
    print("🤖 INTERACTIVE MODE [Type 'quit' to exit]")
    print("="*60)
    
    while True:
        user_input = input("\n💬 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            result = await Runner.run(manager, user_input)
            response = result.final_output
            
            print(f"\n🤖 Agent: {response.summary}")
            print(f"   Status: {response.status}")
            if response.next_steps:
                print(f"   Next Steps: {', '.join(response.next_steps)}")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    # Choose mode based on command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            asyncio.run(interactive_mode())
        elif sys.argv[1] == "custom" and len(sys.argv) > 2:
            query = " ".join(sys.argv[2:])
            asyncio.run(run_custom_query(query))
        else:
            print("Usage:")
            print("  python main.py              # Run test queries")
            print("  python main.py interactive  # Interactive mode")
            print("  python main.py custom 'query' # Custom single query")
    else:
        asyncio.run(run_project())