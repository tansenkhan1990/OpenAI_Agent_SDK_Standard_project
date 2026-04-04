"""
Agent configuration and setup with comprehensive error handling.
Follows industry standards for multi-agent orchestration.
"""

from typing import Optional
from agents import Agent, ModelSettings, input_guardrail, GuardrailFunctionOutput, RunContextWrapper
import logging
from src.utils.logger import setup_logging
from src.tools.knowledge_base import query_knowledge_base, update_record
from src.models.responses import AgentResponse
from src.utils.constants import (
    MAX_TOKENS,
    TEMPERATURE,
    TOP_P,
    AGENT_NAME_MANAGER,
    AGENT_NAME_RESEARCHER,
    AGENT_NAME_EXECUTOR,
    DANGEROUS_PATTERNS,
)

logger = setup_logging(__name__)


@input_guardrail
async def safety_check(
    context: RunContextWrapper,
    agent: Agent,
    user_input: str
) -> GuardrailFunctionOutput:
    """
    Security guardrail to prevent prompt injection and malicious instructions.
    
    Args:
        context: Run context from the agent framework
        agent: Current agent processing the input
        user_input: User input to validate
        
    Returns:
        GuardrailFunctionOutput indicating if input is safe
    """
    try:
        logger.debug(f"Evaluating input safety for agent: {agent.name if hasattr(agent, 'name') else 'Unknown'}")
        
        # Check for dangerous patterns
        for pattern in DANGEROUS_PATTERNS:
            if pattern in user_input.lower():
                logger.warning(f"Dangerous pattern detected: '{pattern}' in user input")
                return GuardrailFunctionOutput(
                    tripwire_triggered=True,
                    output_info={"reason": f"Blocked dangerous pattern: {pattern}"}
                )
        
        # Check for extremely long inputs (potential DoS)
        if len(user_input) > 10000:
            logger.warning(f"Input exceeds maximum length: {len(user_input)} characters")
            return GuardrailFunctionOutput(
                tripwire_triggered=True,
                output_info={"reason": "Input exceeds maximum allowed length"}
            )
        
        logger.debug("Input passed safety check")
        return GuardrailFunctionOutput(
            tripwire_triggered=False,
            output_info={"reason": "Input passed safety check"}
        )
        
    except Exception as e:
        logger.error(f"Error during safety check: {e}")
        # Fail safe - block input if check fails
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={"reason": f"Safety check error: {e}"}
        )


def setup_workforce(model) -> Agent:
    """
    Create and configure the agent workforce with proper error handling.
    
    Args:
        model: The language model to use for all agents
        
    Returns:
        Manager agent that orchestrates the workflow
        
    Raises:
        ValueError: If model is not provided
        
    Example:
        >>> from agents import OpenAIChatCompletionsModel
        >>> model = OpenAIChatCompletionsModel(model="llama3.2:3b", openai_client=client)
        >>> manager = setup_workforce(model)
    """
    try:
        if not model:
            raise ValueError("Model parameter is required for agent setup")
        
        logger.info("Setting up agent workforce")
        
        # Model settings optimized for local execution
        local_settings = ModelSettings(
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P
        )
        
        logger.debug(f"Model settings: max_tokens={MAX_TOKENS}, temperature={TEMPERATURE}")
        
        # Specialist Agent 1: Researcher
        researcher = Agent(
            name=AGENT_NAME_RESEARCHER,
            instructions="""You are a Research Specialist. Your job is to:
1. Query the knowledge base for relevant information
2. Provide accurate, factual answers about company policies
3. If you don't know something, say so clearly

Always use the query_knowledge_base tool to find information.
Return information in a structured, easy-to-understand format.""",
            tools=[query_knowledge_base],
            model=model,
            model_settings=local_settings
        )
        logger.debug(f"Created agent: {AGENT_NAME_RESEARCHER}")
        
        # Specialist Agent 2: Executor
        executor = Agent(
            name=AGENT_NAME_EXECUTOR,
            instructions="""You are an Execution Specialist. Your job is to:
1. Update system records based on decisions made
2. Confirm updates were successful
3. Track ticket status changes
4. Provide clear confirmation of all actions taken

Always use the update_record tool to make system changes.
Report back with the result of each operation.""",
            tools=[update_record],
            model=model,
            model_settings=local_settings
        )
        logger.debug(f"Created agent: {AGENT_NAME_EXECUTOR}")
        
        # Manager Agent (Coordinates everything)
        manager = Agent(
            name=AGENT_NAME_MANAGER,
            instructions="""You are a Manager Agent coordinating customer support requests.

YOUR WORKFLOW:
1. Analyze the user's request carefully
2. If policy information is needed → handoff to Researcher
3. If system updates are needed → handoff to Executor
4. After gathering all information, produce a final structured response

FINAL RESPONSE REQUIREMENTS:
The response MUST include:
- status: "Resolved" if complete, "In-Progress" if partial, "Escalated" if complex
- summary: Clear, concise summary of what was done or decided
- next_steps: List of any remaining actions needed (can be empty if resolved)

Always be thorough and ensure all information is accurate before responding.""",
            model=model,
            handoffs=[researcher, executor],
            input_guardrails=[safety_check],
            output_type=AgentResponse,
            model_settings=local_settings
        )
        logger.debug(f"Created agent: {AGENT_NAME_MANAGER}")
        logger.info("Agent workforce setup completed successfully")
        
        return manager
        
    except ValueError as e:
        logger.error(f"Configuration error during workforce setup: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during workforce setup: {e}")
        raise RuntimeError(f"Failed to setup agent workforce: {e}")
