# Data Directory

This directory stores application data files.

## Structure

```
data/
├── knowledge_base.json      # Knowledge base entries
├── policies/                # Company policies
├── cache/                   # Cached responses
└── backup/                  # Backup files
```

## Usage

- **knowledge_base.json**: Stores policies and procedures for agents to query
- **policies/**: Individual policy files
- **cache/**: Speed up repeated queries
- **backup/**: Backup of important data

## Example: Adding Policies

Create a JSON file with policies:

```json
{
  "refund": "Refunds require an original receipt and are processed within 5-7 business days.",
  "shipping": "Standard shipping takes 3-5 business days. Express shipping takes 1-2 days.",
  "warranty": "All products come with a 1-year limited warranty."
}
```

**Note:** Data directory is added to `.gitignore` for privacy.
