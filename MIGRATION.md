# Migration Guide: Legacy to Best Practices

This guide helps you understand the changes made to your project and how to use the new structure.

## 🎯 What Changed?

### File Organization

**Before:**
```
main.py (entry point)
simple_agent.py (old code)
agents_config.py
tools.py
models.py
```

**After:**
```
src/
├── main.py (new entry point)
├── config/settings.py (configuration)
├── services/agent_service.py (execution layer)
├── agents/workforce.py (agent setup)
├── tools/knowledge_base.py (tools)
├── models/responses.py (data models)
└── utils/ (logging, constants, etc.)
```

### Running Your Code

**Old Way:**
```bash
python main.py
```

**New Way:**
```bash
python -m src.main
# or
uv run -m src.main
```

## 🔄 Key Improvements

### 1. Configuration Management

**Before:**
```python
# Hardcoded in main.py
client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)
```

**After:**
```python
# From .env file
from src.config.settings import get_config
config = get_config()
client = AsyncOpenAI(
    base_url=config.ollama.base_url,
    api_key=config.ollama.api_key
)
```

### 2. Error Handling

**Before:**
```python
try:
    result = await Runner.run(manager, query)
    print(result.final_output)
except Exception as e:
    print(f"Error: {e}")
```

**After:**
```python
from src.services.agent_service import AgentService, TimeoutError
service = AgentService()

try:
    result = await service.execute_agent(manager, query)
except TimeoutError as e:
    logger.error(f"Timeout: {e}")
except AgentExecutionError as e:
    logger.error(f"Agent error: {e}")
```

### 3. Type Safety

**Before:**
```python
def query_knowledge_base(topic: str) -> str:
    kb = {...}
    return kb.get(topic, "Not found")  # No validation
```

**After:**
```python
from src.models.responses import QueryKnowledgeBaseInput

@function_tool
def query_knowledge_base(topic: str) -> str:
    validated_input = QueryKnowledgeBaseInput(topic=topic)
    kb = {...}
    return kb.get(validated_input.topic, "Not found")
```

### 4. Logging

**Before:**
```python
print("Starting agent...")  # No control over log level
```

**After:**
```python
from src.utils.logger import setup_logging
logger = setup_logging(__name__)
logger.info("Starting agent...")  # Can control via environment
```

## 📦 Migration Checklist

- [x] Project reorganized into modular structure
- [x] Configuration moved to `config/settings.py`
- [x] Service layer created for agent execution
- [x] All error handling improved
- [x] Type hints added throughout
- [x] Logging system implemented
- [x] Models with validation created
- [x] Tests written
- [x] Documentation created

## 🚀 Next Steps

1. **Review the new structure**
   - Check `src/` directory organization
   - Read [README_BEST_PRACTICES.md](README_BEST_PRACTICES.md)

2. **Test the application**
   ```bash
   python -m src.main
   ```

3. **Run the tests**
   ```bash
   pytest tests/ -v
   ```

4. **Try different modes**
   ```bash
   # Interactive
   python -m src.main interactive
   
   # Custom query
   python -m src.main custom "your query here"
   ```

5. **Customize for your needs**
   - Modify tools in `src/tools/knowledge_base.py`
   - Add new agents in `src/agents/workforce.py`
   - Add tests in `tests/`

## 🔗 Old Files Reference

The original files (`main.py`, `agents_config.py`, `tools.py`, `models.py`) are still in the root for reference but are **deprecated**. Use the new `src/` structure for all future development.

### Deprecated Files
- `main.py` → Use `src/main.py`
- `agents_config.py` → Use `src/agents/workforce.py`
- `tools.py` → Use `src/tools/knowledge_base.py`
- `models.py` → Use `src/models/responses.py`

## ❓ FAQ

**Q: Can I still use the old `main.py`?**  
A: Yes, but it's not recommended. The new structure is more maintainable and follows best practices.

**Q: Do I need to update my `.env` file?**  
A: No, but verify it has:
```env
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_API_KEY=ollama
OLLAMA_MODEL_NAME=llama3.2:3b
```

**Q: How do I add a new tool?**  
A: Add it to `src/tools/knowledge_base.py` following the existing pattern, then add tests in `tests/test_tools.py`.

**Q: How do I add a new agent?**  
A: Update `src/agents/workforce.py` and add the agent to `setup_workforce()`.

**Q: How do I enable/disable logging?**  
A: Set `LOG_LEVEL` in `.env`:
```env
LOG_LEVEL=DEBUG    # Verbose
LOG_LEVEL=INFO     # Normal
LOG_LEVEL=WARNING  # Quiet
```

## 📞 Questions?

Refer to:
- [README_BEST_PRACTICES.md](README_BEST_PRACTICES.md) - Comprehensive guide
- [README.md](README.md) - Original project documentation
- Code comments and docstrings in `src/`

---

**Congratulations!** Your project now follows industry-standard best practices for Agentic AI development! 🎉
