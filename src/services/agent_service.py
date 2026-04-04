"""
Service layer for agent execution - abstraction of SDK Runner.
Implements error handling, timeouts, and retry logic.
Follows industry standard patterns for production services.
"""

import asyncio
from typing import Optional, Any
from agents import Runner
import logging
from src.utils.logger import setup_logging, LoggerMixin
from src.models.responses import AgentResponse, ErrorResponse
from src.utils.constants import AGENT_EXECUTION_TIMEOUT, MAX_RETRIES, RETRY_DELAY

logger = setup_logging(__name__)


class AgentExecutionError(Exception):
    """Custom exception for agent execution errors."""
    pass


class TimeoutError(AgentExecutionError):
    """Agent execution exceeded timeout."""
    pass


class AgentService(LoggerMixin):
    """
    Service for executing agents with proper error handling and resource management.
    Provides clean API for agent execution.
    """
    
    def __init__(self, timeout_seconds: int = AGENT_EXECUTION_TIMEOUT):
        """
        Initialize AgentService.
        
        Args:
            timeout_seconds: Maximum time allowed for agent execution
        """
        self.timeout_seconds = timeout_seconds
        self.logger.info(f"AgentService initialized with timeout: {timeout_seconds}s")
    
    async def execute_agent(
        self,
        agent: Any,
        query: str,
        retry_count: int = 0
    ) -> AgentResponse:
        """
        Execute an agent with the given query, including timeout and error handling.
        
        Args:
            agent: The agent to execute
            query: User query/input for the agent
            retry_count: Current retry attempt (internal use)
            
        Returns:
            AgentResponse with structured output
            
        Raises:
            AgentExecutionError: If execution fails after retries
            TimeoutError: If execution exceeds timeout
            
        Example:
            >>> service = AgentService()
            >>> response = await service.execute_agent(manager, "What's your refund policy?")
            >>> print(response.summary)
        """
        try:
            self.logger.info(f"Executing agent with query: {query[:100]}...")
            
            # Execute with timeout
            result = await asyncio.wait_for(
                self._run_agent(agent, query),
                timeout=self.timeout_seconds
            )
            
            self.logger.info(f"Agent execution completed successfully")
            return result
            
        except asyncio.TimeoutError as e:
            error_msg = f"Agent execution exceeded {self.timeout_seconds} second timeout"
            self.logger.error(error_msg)
            
            # Retry logic
            if retry_count < MAX_RETRIES:
                self.logger.info(f"Retrying execution (attempt {retry_count + 1}/{MAX_RETRIES})")
                await asyncio.sleep(RETRY_DELAY)
                return await self.execute_agent(agent, query, retry_count + 1)
            
            raise TimeoutError(error_msg)
            
        except AgentExecutionError as e:
            self.logger.error(f"Agent execution error: {e}")
            raise
            
        except Exception as e:
            error_msg = f"Unexpected error during agent execution: {e}"
            self.logger.error(error_msg)
            
            # Retry on unexpected errors
            if retry_count < MAX_RETRIES:
                self.logger.info(f"Retrying after error (attempt {retry_count + 1}/{MAX_RETRIES})")
                await asyncio.sleep(RETRY_DELAY)
                return await self.execute_agent(agent, query, retry_count + 1)
            
            raise AgentExecutionError(error_msg)
    
    async def _run_agent(self, agent: Any, query: str) -> AgentResponse:
        """
        Internal method to run the agent with the SDK Runner.
        
        Args:
            agent: Agent to run
            query: User input query
            
        Returns:
            Agent response
        """
        try:
            result = await Runner.run(agent, query)
            
            # Validate result has final_output
            if not hasattr(result, 'final_output'):
                raise AgentExecutionError("Agent returned result without final_output")
            
            final_output = result.final_output
            
            # Ensure response is AgentResponse type
            if isinstance(final_output, AgentResponse):
                return final_output
            elif isinstance(final_output, dict):
                return AgentResponse(**final_output)
            else:
                # Try to construct from result
                return AgentResponse(
                    status="In-Progress",
                    summary=str(final_output)
                )
                
        except Exception as e:
            self.logger.error(f"Error in _run_agent: {e}")
            raise
    
    def get_error_response(self, error: Exception) -> ErrorResponse:
        """
        Convert an exception to a structured ErrorResponse.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Structured ErrorResponse
        """
        if isinstance(error, TimeoutError):
            return ErrorResponse(
                error_code="AGENT_TIMEOUT",
                message=str(error),
                details={"timeout_seconds": self.timeout_seconds}
            )
        elif isinstance(error, AgentExecutionError):
            return ErrorResponse(
                error_code="AGENT_EXECUTION_ERROR",
                message=str(error)
            )
        else:
            return ErrorResponse(
                error_code="UNKNOWN_ERROR",
                message=str(error)
            )
