"""
Central constants for the Agentic AI application.
Follows DRY principle - single source of truth for all constants.
"""

# Model Configuration
MAX_TOKENS = 1000
TEMPERATURE = 0.1
TOP_P = 0.9

# Ollama Configuration
OLLAMA_DEFAULT_BASE_URL = "http://localhost:11434/v1"
OLLAMA_DEFAULT_API_KEY = "ollama"
OLLAMA_MODEL_NAME = "llama3.2:3b"

# Agent Names
AGENT_NAME_MANAGER = "Manager"
AGENT_NAME_RESEARCHER = "Researcher"
AGENT_NAME_EXECUTOR = "Executor"

# Status Values
STATUS_RESOLVED = "Resolved"
STATUS_IN_PROGRESS = "In-Progress"
STATUS_ESCALATED = "Escalated"

# Knowledge Base Policies
KNOWLEDGE_BASE = {
    "refund": "Refunds require an original receipt and are processed within 5-7 business days.",
    "shipping": "Standard shipping takes 3-5 business days. Express shipping takes 1-2 days.",
    "return": "Returns are accepted within 30 days of purchase with original packaging.",
    "warranty": "All products come with a 1-year limited warranty.",
    "cancellation": "Orders can be cancelled within 1 hour of placement."
}

# Security Patterns
DANGEROUS_PATTERNS = [
    "ignore previous instructions",
    "ignore your instructions",
    "system prompt",
    "you are now",
    "forget your",
    "disregard",
    "ignore all"
]

# Logging Levels
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Timeout Values (seconds)
AGENT_EXECUTION_TIMEOUT = 30
TOOL_EXECUTION_TIMEOUT = 10

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds
