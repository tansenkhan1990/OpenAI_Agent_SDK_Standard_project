# Logs Directory

Application logs will be stored here when file logging is enabled.

## Usage

Logs are automatically created when the application runs with `LOG_LEVEL` configured.

### Configuration

In `.env`:
```env
LOG_LEVEL=INFO
```

### Log Files

- Application logs are rotating files (10MB max, keeps 5 backups)
- Logs are written to: `logs/app.log`

### Viewing Logs

```bash
# View recent logs
tail -f logs/app.log

# Search for errors
grep ERROR logs/app.log

# View with timestamps
tail -n 50 logs/app.log
```

**Note:** Logs directory is added to `.gitignore` for security.
