# Project Directory Structure Guide

## Complete Project Layout

```
Agentic AI/OpenAI_Agent_SDK_Standard_project/
│
├── 📂 src/                           # Main source code (modular)
│   ├── __init__.py
│   ├── main.py                       # ⭐ Entry point
│   │
│   ├── 📂 config/                    # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py               # Environment-based config
│   │
│   ├── 📂 services/                  # Business logic layer
│   │   ├── __init__.py
│   │   └── agent_service.py          # Agent execution with error handling
│   │
│   ├── 📂 agents/                    # Agent definitions
│   │   ├── __init__.py
│   │   └── workforce.py              # Multi-agent orchestration
│   │
│   ├── 📂 tools/                     # Tool implementations
│   │   ├── __init__.py
│   │   └── knowledge_base.py         # Knowledge base tools
│   │
│   ├── 📂 models/                    # Data models (Pydantic)
│   │   ├── __init__.py
│   │   └── responses.py              # Structured output schemas
│   │
│   └── 📂 utils/                     # Utilities
│       ├── __init__.py
│       ├── constants.py              # Centralized constants
│       └── logger.py                 # Logging configuration
│
├── 📂 tests/                         # Unit and integration tests
│   ├── test_models.py                # Model validation tests
│   └── test_tools.py                 # Tool functionality tests
│
├── 📂 logs/                          # Application logs (git-ignored)
│   ├── README.md                     # Logging guide
│   └── app.log                       # Generated at runtime
│
├── 📂 data/                          # Application data (git-ignored)
│   ├── README.md                     # Data directory guide
│   ├── knowledge_base.json           # Policy database
│   ├── cache/                        # Cached responses
│   └── backup/                       # Backups
│
├── 📂 docs/                          # Documentation
│   ├── README.md                     # Documentation index
│   ├── ARCHITECTURE.md               # System design
│   ├── API_REFERENCE.md              # API documentation
│   ├── TROUBLESHOOTING.md            # FAQs and fixes
│   └── DEPLOYMENT.md                 # Deployment guide
│
├── 📂 scripts/                       # Utility scripts
│   ├── README.md                     # Scripts guide
│   ├── setup.sh                      # Project setup
│   ├── test.sh                       # Run tests
│   ├── format.sh                     # Code formatting
│   ├── lint.sh                       # Code linting
│   └── run-local.sh                  # Local execution
│
├── 📂 examples/                      # Example code
│   ├── README.md                     # Examples guide
│   ├── basic_usage.py                # Basic usage example
│   ├── custom_agent.py               # Custom agent example
│   └── adding_tools.py               # Adding tools example
│
├── 📂 test_working_Agent/            # Legacy test files
│
├── 📂 .git/                          # Git repository
│
├── 📂 .venv/                         # Virtual environment (git-ignored)
│
├── 📄 .env                           # Environment config (git-ignored)
│   └── Contains: OLLAMA_BASE_URL, OLLAMA_API_KEY, LOG_LEVEL, etc.
│
├── 📄 .gitignore                     # Git ignore rules
│
├── 📄 .python-version                # Python version (3.12)
│
├── 📄 pyproject.toml                 # Project metadata & dependencies
│
├── 📄 uv.lock                        # Dependency lock file
│
├── 📄 README.md                      # Project overview
│
├── 📄 README_BEST_PRACTICES.md       # Best practices guide ⭐
│
├── 📄 MIGRATION.md                   # Migration from legacy code
│
├── 📄 IMPROVEMENTS_SUMMARY.md        # Summary of improvements
│
└── 📄 UV_documentation.txt           # UV package manager docs
```

## Directory Organization Guide

### 1. **src/** - Main Application Code
**Purpose**: All production code organized by responsibility  
**Key Folders**:
- `config/` - Load configuration from environment
- `services/` - Business logic and service layers
- `agents/` - Agent definitions and orchestration
- `tools/` - Tool implementations (functions agents can call)
- `models/` - Data structures with validation
- `utils/` - Helper utilities (logging, constants)

### 2. **tests/** - Test Suite
**Purpose**: Unit and integration tests  
**Files**:
- `test_models.py` - Pydantic model validation tests
- `test_tools.py` - Tool functionality tests

### 3. **logs/** - Application Logs
**Purpose**: Store application runtime logs  
**Note**: Git-ignored for privacy/security  
**Usage**: Check for debugging information

### 4. **data/** - Application Data
**Purpose**: Store knowledge base, policies, cache, backups  
**Note**: Git-ignored to protect sensitive data  
**Subdirectories**:
- `cache/` - Cached query results
- `backup/` - Data backups

### 5. **docs/** - Additional Documentation
**Purpose**: Extended documentation beyond README  
**Key Files**:
- `ARCHITECTURE.md` - System design
- `API_REFERENCE.md` - Function reference
- `TROUBLESHOOTING.md` - Common issues
- `DEPLOYMENT.md` - Production deployment

### 6. **scripts/** - Utility Scripts
**Purpose**: Shell scripts for common tasks  
**Key Scripts**:
- `setup.sh` - Initial project setup
- `test.sh` - Run test suite
- `format.sh` - Code formatting
- `lint.sh` - Code quality checks
- `run-local.sh` - Local development

### 7. **examples/** - Example Code
**Purpose**: Demonstrate how to use the system  
**Files**:
- `basic_usage.py` - Minimal working example
- `custom_agent.py` - Creating custom agents
- `adding_tools.py` - Adding custom tools

## Git-Ignored Directories

These directories are in `.gitignore` for security/privacy:
- `.venv/` - Virtual environment (large, local-specific)
- `logs/` - Contains runtime logs with sensitive info
- `data/` - Contains user data, cache, backups
- `__pycache__/` - Python compiled files

## Important Files

### Configuration
- `.env` - Environment variables (API keys, settings) - **NEVER commit**
- `pyproject.toml` - Project metadata and dependencies

### Documentation
- `README.md` - Quick start and overview
- `README_BEST_PRACTICES.md` - Comprehensive architecture guide
- `MIGRATION.md` - How to upgrade from legacy code
- `IMPROVEMENTS_SUMMARY.md` - What changed and why

### Entry Points
- `src/main.py` - Main application entry point
- Use: `python -m src.main`

## How to Navigate

### For Development
```bash
# Source code
ls -la src/

# Tests
ls -la tests/

# Add new feature
Create file in src/{module}/
Add tests in tests/
```

### For Running
```bash
# Main application
python -m src.main

# Use scripts
./scripts/test.sh
./scripts/format.sh
```

### For Documentation
```bash
# Quick start
cat README.md

# Detailed guide
cat README_BEST_PRACTICES.md

# Migration help
cat MIGRATION.md

# Additional docs
ls -la docs/
```

## Best Practices

1. **Add code to src/** not root
2. **Add tests to tests/** for new features
3. **Update .env for local config** (never commit)
4. **Use utils/constants.py** for magic strings
5. **Add logging** to important operations
6. **Document with docstrings** in code
7. **Use type hints** throughout

---

**Total Directories**: 13  
**Total Files Tracked**: 30+  
**Structure Type**: Modular, scalable, production-ready  
**Status**: ✅ Ready for development and deployment
