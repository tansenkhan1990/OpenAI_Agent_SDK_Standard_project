"""
Main entry point for the Agentic AI application.
Implements industry-standard patterns for application startup and execution.
"""

import asyncio
import sys
from typing import Optional
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_tracing_disabled

# Import from reorganized project structure
from src.config.settings import get_config
from src.utils.logger import setup_logging
from src.agents.workforce import setup_workforce
from src.services.agent_service import AgentService, AgentExecutionError, TimeoutError

logger = setup_logging(__name__)


def initialize_app() -> tuple[AsyncOpenAI, OpenAIChatCompletionsModel, AgentService]:
    """
    Initialize the application with configuration and clients.
    
    Returns:
        Tuple of (openai_client, model, agent_service)
        
    Raises:
        ValueError: If configuration is invalid
    """
    try:
        logger.info("Starting application initialization")
        
        # Load configuration
        config = get_config()
        logger.info(f"Configuration loaded: debug={config.debug}, log_level={config.log_level}")
        
        # Disable tracing if not enabled
        if not config.enable_tracing:
            set_tracing_disabled(True)
            logger.debug("Cloud tracing disabled")
        
        # Initialize Ollama client
        logger.debug(f"Connecting to Ollama at: {config.ollama.base_url}")
        client = AsyncOpenAI(
            base_url=config.ollama.base_url,
            api_key=config.ollama.api_key
        )
        
        # Initialize model
        logger.debug(f"Initializing model: {config.ollama.model_name}")
        model = OpenAIChatCompletionsModel(
            model=config.ollama.model_name,
            openai_client=client
        )
        
        # Initialize service
        agent_service = AgentService()
        
        logger.info("Application initialization completed successfully")
        return client, model, agent_service
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise


async def run_test_queries(manager, agent_service: AgentService) -> None:
    """
    Execute predefined test queries.
    
    Args:
        manager: The manager agent
        agent_service: Service for executing agents
    """
    logger.info("Starting test query execution")
    
    test_queries = [
        "Find the refund policy and update ticket #101 to 'Resolved'.",
        "What's our shipping policy?",
        "Check the warranty policy for electronics."
    ]
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"Executing test query {i}/{len(test_queries)}")
        print(f"\n📝 TEST {i}: {query}")
        print("-" * 60)
        
        try:
            result = await agent_service.execute_agent(manager, query)
            
            print("\n✅ AGENT RESPONSE:")
            print(f"   Ticket ID: {result.ticket_id}")
            print(f"   Status: {result.status}")
            print(f"   Summary: {result.summary}")
            if result.next_steps:
                print(f"   Next Steps: {', '.join(result.next_steps)}")
            print()
            
            logger.info(f"Test query {i} completed successfully")
            
        except TimeoutError as e:
            error_msg = f"❌ TIMEOUT: Agent execution timed out"
            print(f"\n{error_msg}")
            logger.error(f"Timeout on test query {i}: {e}")
            
        except AgentExecutionError as e:
            error_msg = f"❌ AGENT ERROR: {str(e)}"
            print(f"\n{error_msg}")
            logger.error(f"Agent error on test query {i}: {e}")
            
        except Exception as e:
            error_msg = f"❌ UNEXPECTED ERROR: {str(e)}"
            print(f"\n{error_msg}")
            logger.error(f"Unexpected error on test query {i}: {e}")
            print("\nTroubleshooting tips:")
            print("1. Ensure Ollama is running: `ollama serve`")
            print("2. Verify model is available: `ollama list`")
            print("3. Check network connectivity")


async def run_custom_query(manager, agent_service: AgentService, query: str) -> None:
    """
    Execute a single custom query.
    
    Args:
        manager: The manager agent
        agent_service: Service for executing agents
        query: The query to execute
    """
    logger.info(f"Executing custom query: {query[:100]}")
    print(f"\n📝 CUSTOM QUERY: {query}")
    print("-" * 60)
    
    try:
        result = await agent_service.execute_agent(manager, query)
        
        print("\n✅ RESPONSE:")
        print(f"   Ticket ID: {result.ticket_id}")
        print(f"   Status: {result.status}")
        print(f"   Summary: {result.summary}")
        if result.next_steps:
            print(f"   Next Steps: {', '.join(result.next_steps)}")
        
        logger.info("Custom query executed successfully")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Failed to execute custom query: {e}")


async def interactive_mode(manager, agent_service: AgentService) -> None:
    """
    Run the agent in interactive mode for continuous conversation.
    
    Args:
        manager: The manager agent
        agent_service: Service for executing agents
    """
    logger.info("Starting interactive mode")
    
    print("\n" + "=" * 60)
    print("🤖 INTERACTIVE MODE [Type 'quit' to exit]")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                logger.info("User exited interactive mode")
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            result = await agent_service.execute_agent(manager, user_input)
            
            print(f"\n🤖 Agent: {result.summary}")
            print(f"   Status: {result.status}")
            if result.next_steps:
                print(f"   Next Steps: {', '.join(result.next_steps)}")
            
            logger.info(f"Interactive query processed: {user_input[:50]}")
                    
        except KeyboardInterrupt:
            logger.info("Interactive mode interrupted by user")
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Error in interactive mode: {e}")


async def main() -> int:
    """
    Main application entry point.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        logger.info("="*60)
        logger.info("🏠 LOCAL AGENT SDK RUNNER [Ollama - llama3.2:3b]")
        logger.info("="*60)
        
        # Initialize application
        client, model, agent_service = initialize_app()
        
        # Setup agents
        logger.info("Setting up agent workforce")
        manager = setup_workforce(model)
        
        # Determine execution mode from command line arguments
        if len(sys.argv) > 1:
            mode = sys.argv[1]
            
            if mode == "interactive":
                await interactive_mode(manager, agent_service)
                
            elif mode == "custom" and len(sys.argv) > 2:
                query = " ".join(sys.argv[2:])
                await run_custom_query(manager, agent_service, query)
                
            else:
                print("Usage:")
                print("  python -m src.main              # Run test queries")
                print("  python -m src.main interactive  # Interactive mode")
                print("  python -m src.main custom 'query' # Single custom query")
                return 1
        else:
            # Default: run test queries
            await run_test_queries(manager, agent_service)
        
        logger.info("Application completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\n\nApplication interrupted. Goodbye!")
        return 0
    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
        print(f"\n❌ Critical Error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
