# OpenAI Agent SDK Standard Project - Financial Scenario

This project is a demonstration of the [OpenAI Agent SDK](https://github.com/openai/openai-python), showcasing a professional financial/billing agent system. It highlights several core capabilities of the new SDK, such as autonomous agent interaction, multi-agent handoffs, strict guardrails, and structured outputs using Pydantic.

## 🚀 Features

*   **Multi-Agent Handoffs**: Utilizes a `Front Desk Manager` (Triage Agent) that identifies the user's intent and seamlessly routes the request to specialized agents like a `Billing Specialist`.
*   **Safety Guardrails**: Implements a `Guardrail` ("FinancialSafety") to intercept and block the agent from disclosing sensitive internal banking algorithms, competitor names, or non-financial topics.
*   **Structured Outputs**: Guarantees the final output matches a precise schema defined with Pydantic (e.g., extracting `transaction_id`, `status`, `amount_processed`, and a `summary`), ensuring predictability for downstream systems.
*   **Custom Tools**: Integrates atomic Python functions (`@function_tool`) allowing the agents to interact with a mock database to verify balances and execute simulated refunds.
*   **Managed Execution Loop**: Uses the SDK's `Runner` to handle the complex underlying "Thought -> Action -> Observation" loops autonomously.

## 📁 Project Structure

*   `main.py`: The main entry point. Initializes the asynchronous SDK `Runner` and executes the scenario.
*   `agents_config.py`: Configuration file where the agents (`triage_agent`, `billing_agent`) and their instructions, tools, and handoffs are defined, along with the system `Guardrail`.
*   `tools.py`: Contains the actual functions the agents can invoke, registered with the `@function_tool` decorator (e.g., `verify_account_balance`, `execute_refund`).
*   `models.py`: Defines the Pydantic data model (`TransactionResult`) used to enforce Structured Outputs from the agent.
*   `database_mock.py`: A simple, mock in-memory database used by the tools to look up user account balances.

## 🛠 Prerequisites

*   Python 3.9+
*   The `openai-agents` package
*   The `pydantic`, `python-dotenv` packages
*   An active OpenAI API Key

## ⚙️ Setup and Installation

1.  **Install dependencies:**
    Ensure you have the required packages installed in your environment.
    ```bash
    pip install openai-agents pydantic python-dotenv
    ```

2.  **Environment Variables:**
    Create a `.env` file in the root of the project to store your OpenAI API key:
    ```env
    OPENAI_API_KEY=your_api_key_here
    ```

## ▶️ Usage

To execute the financial agent scenario, run the `main.py` file:

```bash
python main.py
```

**What to expect:**
The script simulates a user asking for a refund. The `triage_agent` will receive the request, hand it off to the `billing_agent` which will use the mock database tools to process the refund. Finally, the system will output a structured JSON-like response containing the summary and transaction status. If any guardrails are tripped during execution, the system will actively block the completion.
