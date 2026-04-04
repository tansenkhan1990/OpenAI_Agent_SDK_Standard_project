# Examples Directory

Example code and configurations for using the Agentic AI system.

## Example Files

### basic_usage.py
Basic example of running the agent

```python
from src.config.settings import get_config
from src.agents.workforce import setup_workforce
from src.services.agent_service import AgentService
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

# Setup
config = get_config()
client = AsyncOpenAI(base_url=config.ollama.base_url, api_key=config.ollama.api_key)
model = OpenAIChatCompletionsModel(model=config.ollama.model_name, openai_client=client)

# Create agent and service
manager = setup_workforce(model)
service = AgentService()

# Execute
result = await service.execute_agent(manager, "What is your refund policy?")
print(result.summary)
```

### custom_agent.py
Example of creating a custom agent

```python
from agents import Agent, OpenAIChatCompletionsModel

custom_agent = Agent(
    name="CustomAgent",
    instructions="Your custom instructions here",
    model=model,
    tools=[your_tool_here]
)
```

### adding_tools.py
Example of adding custom tools

```python
from agents import function_tool
from src.models.responses import ToolInput

@function_tool
def my_custom_tool(param: str) -> str:
    \"\"\"Tool description\"\"\"
    return f"Result for {param}"
```

## Running Examples

```bash
# Run basic example
python examples/basic_usage.py

# Run custom agent example
python examples/custom_agent.py
```

## Creating New Examples

1. Create new file in `examples/`
2. Prefix with example name: `example_*.py`
3. Add comments explaining the code
4. List in this README
