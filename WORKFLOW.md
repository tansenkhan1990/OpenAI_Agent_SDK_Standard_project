# Project Workflow Guide

## 🔄 Complete System Workflow

This document describes how the Agentic AI system processes requests from user input to final response.

---

## 📊 High-Level Architecture

```
User Input
    ↓
Configuration Loading
    ↓
Agent Initialization
    ↓
AgentService (Execution Layer)
    ├─ Timeout Protection
    ├─ Error Handling
    └─ Retry Logic
    ↓
Manager Agent (Orchestrator)
    ├─ Analyze Request
    ├─ Route to Specialists
    └─ Produce Final Response
    ↓
Specialist Agents (as needed)
    ├─ Researcher Agent → query_knowledge_base
    └─ Executor Agent → update_record
    ↓
Structured Response
    ↓
Return to User
```

---

## 📝 Step-by-Step Request Flow

### Step 1: Application Startup

**File**: `src/main.py`

```
main()
  ├─ Load Configuration
  │   └─ Read from .env file
  ├─ Initialize Logger
  │   └─ Setup logging system
  ├─ Connect to Ollama
  │   └─ Create AsyncOpenAI client
  ├─ Initialize Model
  │   └─ Setup OpenAIChatCompletionsModel
  └─ Setup Agents
      └─ Create workforce with setup_workforce()
```

### Step 2: Configuration Loading

**File**: `src/config/settings.py`

```python
# From .env file
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY = "ollama"
OLLAMA_MODEL_NAME = "llama3.2:3b"
LOG_LEVEL = "INFO"
```

Configuration options:
- Ollama connection details
- Logging configuration
- Debug mode
- Tracing settings

### Step 3: Agent Initialization

**File**: `src/agents/workforce.py`

```
setup_workforce(model)
  ├─ Create Researcher Agent
  │   ├─ Tools: query_knowledge_base
  │   └─ Instructions: Query knowledge base for info
  ├─ Create Executor Agent
  │   ├─ Tools: update_record
  │   └─ Instructions: Update system records
  └─ Create Manager Agent
      ├─ Handoffs: [Researcher, Executor]
      ├─ Guardrails: [safety_check]
      ├─ Output Type: AgentResponse
      └─ Instructions: Coordinate workflow
```

### Step 4: User Input Processing

**File**: `src/main.py` (main function routes to different modes)

#### Mode 1: Test Queries
```
Pre-defined queries:
  1. "Find the refund policy and update ticket #101 to 'Resolved'."
  2. "What's our shipping policy?"
  3. "Check the warranty policy for electronics."
```

#### Mode 2: Interactive
```
Loop:
  ├─ Prompt: "💬 You: "
  ├─ Read user input
  ├─ If "quit" → exit
  └─ Process query
```

#### Mode 3: Custom Query
```
Single query from command line:
  python -m src.main custom "Your question here"
```

### Step 5: Input Validation & Safety

**File**: `src/agents/workforce.py` (safety_check function)

```
safety_check(user_input)
  ├─ Check against dangerous patterns
  │   ├─ "ignore previous instructions"
  │   ├─ "system prompt"
  │   ├─ "forget your"
  │   └─ ... etc
  ├─ Check input length (max 10000 chars)
  └─ Return GuardrailFunctionOutput
      ├─ tripwire_triggered: True/False
      └─ output_info: Reason if blocked
```

If blocked → Request rejected with reason  
If passes → Proceed to agent execution

### Step 6: Agent Service Execution

**File**: `src/services/agent_service.py`

```
AgentService.execute_agent(agent, query)
  ├─ Log request
  ├─ Set timeout (default: 30 seconds)
  ├─ Execute with asyncio.wait_for()
  │   ├─ Calls Runner.run(agent, query)
  │   └─ Returns result.final_output
  ├─ Validate response has AgentResponse type
  ├─ Handle exceptions:
  │   ├─ TimeoutError
  │   │   └─ Retry logic (max 3 retries)
  │   ├─ AgentExecutionError
  │   │   └─ Log and propagate
  │   └─ Other exceptions
  │       └─ Retry with exponential backoff
  └─ Return structured AgentResponse
```

### Step 7: Manager Agent Orchestration

**File**: `src/agents/workforce.py` (Manager Agent)

```
Manager Agent processes query:

1. ANALYZE REQUEST
   └─ Understand what user is asking

2. DETERMINE WORKFLOW
   ├─ Does it need info? 
   │   └─ YES → Handoff to Researcher
   └─ Does it need action?
       └─ YES → Handoff to Executor

3. COORDINATE WITH SPECIALISTS
   ├─ Researcher Agent
   │   ├─ Calls: query_knowledge_base(topic)
   │   └─ Returns: Policy information
   └─ Executor Agent
       ├─ Calls: update_record(record_id, status)
       └─ Returns: Confirmation of update

4. PRODUCE FINAL RESPONSE
   └─ Construct AgentResponse with:
       ├─ ticket_id: UUID
       ├─ status: "Resolved" | "In-Progress" | "Escalated"
       ├─ summary: What was done
       └─ next_steps: Remaining actions
```

### Step 8: Tool Execution

**File**: `src/tools/knowledge_base.py`

#### Tool 1: query_knowledge_base

```python
@function_tool
def query_knowledge_base(topic: str) -> str:
  1. Validate input
     └─ QueryKnowledgeBaseInput(topic=topic)
  2. Look up topic in knowledge base
     └─ KNOWLEDGE_BASE.get(topic)
  3. Return result or "not found"
  4. Log operation
  5. Handle errors gracefully
```

**Knowledge Base Contents**:
```python
{
  "refund": "Refunds require an original receipt and are processed within 5-7 business days.",
  "shipping": "Standard shipping takes 3-5 business days. Express shipping takes 1-2 days.",
  "return": "Returns are accepted within 30 days of purchase with original packaging.",
  "warranty": "All products come with a 1-year limited warranty.",
  "cancellation": "Orders can be cancelled within 1 hour of placement."
}
```

#### Tool 2: update_record

```python
@function_tool
def update_record(record_id: str, status: str) -> str:
  1. Validate inputs
     └─ UpdateRecordInput(record_id, status)
  2. Update mock database
     └─ _mock_records[record_id] = status
  3. Return success message
  4. Log operation
  5. Handle errors gracefully
```

**Mock Database**: In-memory dictionary  
```python
_mock_records = {
  "ticket-001": "Resolved",
  "ticket-002": "In-Progress"
}
```

### Step 9: Response Generation

**File**: `src/models/responses.py`

```
AgentResponse (Pydantic Model)
  ├─ ticket_id: str (auto-generated UUID)
  ├─ status: Literal["Resolved", "In-Progress", "Escalated"]
  ├─ summary: str (validated, non-empty)
  ├─ next_steps: List[str] (optional)
  └─ created_at: datetime (auto-generated)

Validation Rules:
  ├─ status must be one of 3 values
  ├─ summary cannot be empty
  ├─ next_steps can be empty list
  └─ created_at auto-set to UTC now
```

### Step 10: Response Output

**File**: `src/main.py`

```
Display Response:
  ├─ Print formatted output
  │   ├─ Ticket ID
  │   ├─ Status
  │   ├─ Summary
  │   └─ Next Steps
  ├─ Log the response
  └─ Return control to user (interactive) or exit
```

---

## 🔄 Workflow Diagram: Request Processing

```
User Input
    ↓
[Safety Check]
  • Check for prompt injection
  • Validate input length
    ↓ (if blocked)
    └→ [Reject Request]
    ↓ (if passes)
[Manager Agent Analyzes]
  • Understand intent
  • Determine workflow
    ├─ Need Info?
    │  └→ [Researcher Agent] ← query_knowledge_base
    │       • Searches knowledge base
    │       • Returns policy info
    │       ↓
    │     [Manager Receives Info]
    │
    ├─ Need Action?
    │  └→ [Executor Agent] ← update_record
    │       • Updates database
    │       • Confirms changes
    │       ↓
    │     [Manager Receives Confirmation]
    │
    └─ Both or Neither?
       └→ [Proceed with Available Info]
          ↓
[Manager Constructs Response]
  • Create AgentResponse
  • Set status (Resolved/In-Progress/Escalated)
  • Summarize actions taken
  • List next steps
    ↓
[Validate Response]
  • Type validation
  • Field validation
    ↓
[Return to User]
  • Display in console
  • Log to file
  • Exit or wait for next query
```

---

## 💾 Data Flow Example

### Example: "Find refund policy and update ticket #101 to 'Resolved'"

```
INPUT:
  "Find the refund policy and update ticket #101 to 'Resolved'."

SAFETY CHECK:
  ✅ Passes - no dangerous patterns detected

MANAGER ANALYSIS:
  • Intent: Get refund info AND update ticket
  • Action: Needs both Researcher and Executor

WORKFLOW EXECUTION:

  1. Call Researcher:
     → query_knowledge_base("refund")
     ← Returns: "Refunds require an original receipt and are 
               processed within 5-7 business days."

  2. Call Executor:
     → update_record("ticket-101", "Resolved")
     ← Returns: "SUCCESS: Record ticket-101 updated to status: Resolved"

  3. Manager Constructs Response:
     {
       "ticket_id": "550e8400-e29b-41d4-a716-446655440000",
       "status": "Resolved",
       "summary": "Refunds require an original receipt and are 
                   processed within 5-7 business days. Record 
                   ticket-101 has been updated to status: Resolved.",
       "next_steps": ["Send confirmation email"],
       "created_at": "2025-04-04T10:30:00"
     }

OUTPUT:
  ✅ AGENT RESPONSE:
     Ticket ID: 550e8400-e29b-41d4-a716-446655440000
     Status: Resolved
     Summary: Refunds require an original receipt and are processed 
              within 5-7 business days. Record ticket-101 has been 
              updated to status: Resolved.
     Next Steps: Send confirmation email
```

---

## 🛠️ Error Handling Flow

```
Exception Occurs
    ↓
[AgentService.execute_agent]
  ├─ TimeoutError?
  │   ├─ Retry < 3 times?
  │   │   └─ YES: Wait 1s, retry
  │   │   └─ NO: Raise TimeoutError
  │   └─ Return ErrorResponse
  │
  ├─ AgentExecutionError?
  │   ├─ Retry < 3 times?
  │   │   └─ YES: Wait 1s, retry
  │   │   └─ NO: Raise AgentExecutionError
  │   └─ Return ErrorResponse
  │
  └─ Other Exception?
      ├─ Retry < 3 times?
      │   └─ YES: Wait 1s, retry
      │   └─ NO: Raise AgentExecutionError
      └─ Return ErrorResponse

[Log Error]
  └─ Log with full context and stack trace

[Display Error to User]
  └─ Show user-friendly error message
```

---

## 📋 Component Interactions

### 1. Configuration System
```
.env File
    ↓
get_config() (settings.py)
    ↓
ApplicationConfig (dataclass)
    ├─ OllamaConfig
    ├─ log_level
    ├─ debug mode
    └─ tracing enabled/disabled
    ↓
Used by: main.py, logger.py
```

### 2. Logging System
```
setup_logging(__name__)
    ↓
Logger Instance
    ├─ Console Handler (stdout)
    ├─ File Handler (logs/app.log)
    └─ Rotating File Handler
    ↓
Used by: All modules log important operations
```

### 3. Model System
```
Pydantic Models (responses.py)
    ├─ AgentResponse ← Main output
    ├─ QueryKnowledgeBaseInput ← Tool input validation
    ├─ UpdateRecordInput ← Tool input validation
    ├─ ToolInput ← Base class
    └─ ErrorResponse ← Error output
    ↓
Used by: Tools, Services, Models
```

### 4. Tool System
```
Tools (knowledge_base.py)
    ├─ query_knowledge_base
    │   └─ Validates: QueryKnowledgeBaseInput
    │   └─ Uses Constants: KNOWLEDGE_BASE
    │   └─ Logs: operation, errors
    │
    └─ update_record
        └─ Validates: UpdateRecordInput
        └─ Uses: _mock_records (in-memory DB)
        └─ Logs: operation, errors
```

### 5. Agent System
```
setup_workforce(model)
    ├─ Create Researcher Agent
    │   └─ Tools: [query_knowledge_base]
    │
    ├─ Create Executor Agent
    │   └─ Tools: [update_record]
    │
    └─ Create Manager Agent
        ├─ Handoffs: [Researcher, Executor]
        ├─ Guardrails: [safety_check]
        ├─ Output Type: AgentResponse
        └─ Returns: Manager instance
```

### 6. Service System
```
AgentService
    ├─ execute_agent(agent, query)
    │   ├─ Validates input
    │   ├─ Sets timeout (30s default)
    │   ├─ Runs with retries (max 3)
    │   ├─ Converts exceptions
    │   └─ Returns AgentResponse
    │
    └─ get_error_response(exception)
        └─ Converts exceptions to ErrorResponse
```

---

## 🔗 File Dependency Graph

```
src/main.py (entry point)
    ├─ src/config/settings.py (load config)
    ├─ src/utils/logger.py (setup logging)
    ├─ src/agents/workforce.py (create agents)
    │   ├─ src/tools/knowledge_base.py (agent tools)
    │   ├─ src/models/responses.py (output schema)
    │   ├─ src/utils/constants.py (guardrail patterns)
    │   └─ src/utils/logger.py (logging)
    │
    └─ src/services/agent_service.py (execute agents)
        ├─ src/models/responses.py (error/response models)
        └─ src/utils/logger.py (logging)

Tests:
    ├─ tests/test_models.py
    │   └─ src/models/responses.py
    │
    └─ tests/test_tools.py
        └─ src/tools/knowledge_base.py
```

---

## ⚙️ Execution Flow Summary

| Step | Component | Input | Output | Purpose |
|------|-----------|-------|--------|---------|
| 1 | Config | .env | ApplicationConfig | Load settings |
| 2 | Logger | Config | Logger | Setup logging |
| 3 | Ollama Client | Config | AsyncOpenAI | Connect to model |
| 4 | Model | Config | OpenAIChatCompletionsModel | Initialize model |
| 5 | Workforce | Model | Manager Agent | Create agents |
| 6 | Safety Check | Query | GuardrailFunctionOutput | Validate input |
| 7 | Service | Agent + Query | AgentResponse | Execute with safety |
| 8 | Manager | Query | Handoff Decision | Route to specialists |
| 9 | Specialists | Tools | Results | Execute operations |
| 10 | Response | Results | AgentResponse | Format output |

---

## 🎯 Key Design Patterns

### 1. **Dependency Injection**
- Components receive dependencies as parameters
- Makes testing easier, reduces coupling

### 2. **Service Layer Pattern**
- AgentService abstracts Agent execution
- Handles timeouts, retries, errors consistently

### 3. **Configuration Management**
- 12-factor app principles
- Configuration from environment, not code

### 4. **Validation with Pydantic**
- All data validated at boundaries
- Type safety throughout

### 5. **Logging Throughout**
- Important operations logged at INFO level
- Debug info logged at DEBUG level
- Errors logged with context

### 6. **Graceful Error Handling**
- Custom exceptions for different error types
- Retry logic with exponential backoff
- Structured error responses

---

## 📊 Performance Considerations

```
Execution Timeline (typical):

Input Received
    ↓ (< 1ms)
Safety Check
    ↓ (< 10ms)
Agent Analysis
    ↓ (0.5-2s) ← Model inference
Tool Calls (if needed)
    ↓ (< 100ms) ← DB lookup or knowledge base
Response Generation
    ↓ (< 50ms)
Output Display
    ↓
Total: ~1-3 seconds
```

**Timeout Protection**: 30 seconds (configurable)  
**Retry Attempts**: Up to 3 total attempts  
**Retry Delay**: 1 second between retries

---

This workflow ensures your Agentic AI system is:
- ✅ **Secure** - Input validation, safety guardrails
- ✅ **Reliable** - Error handling, retries, timeouts
- ✅ **Observable** - Comprehensive logging
- ✅ **Maintainable** - Clear separation of concerns
- ✅ **Scalable** - Service layer abstraction
