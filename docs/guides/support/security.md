# Security Best Practices

Guidelines for securely using the AI Content Generation Suite.

## API Key Security

### Never Commit API Keys

API keys should never be committed to version control.

**Add to `.gitignore`:**
```gitignore
# Environment files
.env
.env.local
.env.*.local

# API keys
*.key
secrets/
```

### Use Environment Variables

Store API keys in environment variables or `.env` files:

```env
# .env file (never commit this)
FAL_KEY=your_fal_api_key
GEMINI_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

### Rotate Keys Regularly

- Rotate API keys periodically (every 90 days recommended)
- Immediately rotate if a key may have been exposed
- Use separate keys for development and production

### Use Least Privilege

- Only request permissions you need
- Use read-only keys where possible
- Create separate keys for different applications

---

## Secure Configuration

### Validate Input

Always validate user input before using in prompts:

```python
def sanitize_prompt(user_input: str) -> str:
    """Sanitize user input for use in prompts."""
    # Remove potentially dangerous characters
    sanitized = user_input.strip()
    # Limit length
    sanitized = sanitized[:1000]
    return sanitized

prompt = sanitize_prompt(user_input)
manager.generate_image(prompt=prompt)
```

### Avoid Prompt Injection

Be cautious with user-provided prompts:

```python
# Risky: Direct user input
prompt = user_input  # Could contain malicious instructions

# Safer: Structured prompts with user input in specific places
prompt = f"Generate an image of: {sanitize_prompt(user_input)}, in a safe style"
```

### Secure File Handling

Validate file paths and types:

```python
import os
from pathlib import Path

def safe_output_path(user_path: str, base_dir: str = "output") -> Path:
    """Ensure output path is within allowed directory."""
    # Resolve to absolute path
    base = Path(base_dir).resolve()
    requested = (base / user_path).resolve()

    # Ensure path is within base directory
    if not str(requested).startswith(str(base)):
        raise ValueError("Output path must be within output directory")

    return requested
```

---

## Network Security

### Use HTTPS

All API calls should use HTTPS (default behavior):

```python
# The package uses HTTPS by default
# Don't override this unless absolutely necessary
```

### Verify SSL Certificates

Don't disable SSL verification:

```python
# Bad: Disabling SSL verification
# httpx.get(url, verify=False)  # Never do this

# Good: Use default SSL verification
# The package handles this correctly by default
```

### Rate Limiting

Implement rate limiting to prevent abuse:

```python
import time
from functools import wraps

def rate_limit(calls_per_minute: int):
    """Rate limit decorator."""
    min_interval = 60.0 / calls_per_minute
    last_call = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            last_call[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(calls_per_minute=30)
def generate_content(prompt):
    return manager.generate_image(prompt=prompt)
```

---

## Output Security

### Validate Generated Content

Be aware that AI-generated content may be unexpected:

```python
import os

def safe_save(content: bytes, filename: str, output_dir: str = "output"):
    """Safely save generated content."""
    # Validate filename
    safe_name = "".join(c for c in filename if c.isalnum() or c in "._-")

    # Ensure proper extension
    if not safe_name.endswith(('.png', '.jpg', '.mp4', '.mp3')):
        raise ValueError("Invalid file extension")

    # Save to controlled directory
    path = os.path.join(output_dir, safe_name)
    with open(path, 'wb') as f:
        f.write(content)

    return path
```

### Set Proper File Permissions

```python
import os
import stat

def secure_file(path: str):
    """Set secure permissions on generated files."""
    # Remove world-readable permissions
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)  # 600
```

### Content Moderation

Consider content moderation for user-facing applications:

```python
def moderate_prompt(prompt: str) -> bool:
    """Check if prompt is appropriate."""
    # Implement content moderation logic
    # Could use external moderation APIs
    blocked_terms = ["explicit", "violent", ...]
    return not any(term in prompt.lower() for term in blocked_terms)

if not moderate_prompt(user_prompt):
    raise ValueError("Content policy violation")
```

---

## Production Security

### Environment Isolation

Use separate environments for development and production:

```bash
# Development
cp .env.development .env

# Production
cp .env.production .env
```

### Logging Security

Don't log sensitive information:

```python
import logging

# Bad: Logging API keys
# logger.info(f"Using key: {api_key}")

# Good: Log without sensitive data
logger.info("API call initiated")
logger.info(f"Model: {model}, Prompt length: {len(prompt)}")
```

### Error Handling

Don't expose internal details in errors:

```python
try:
    result = manager.generate_image(prompt=prompt)
except APIError as e:
    # Log full error internally
    logger.error(f"API error: {e}")

    # Return sanitized error to user
    raise UserFacingError("Image generation failed. Please try again.")
```

### Audit Logging

Track operations for security auditing:

```python
import datetime

def log_operation(user_id: str, operation: str, model: str):
    """Log operation for audit trail."""
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "user_id": user_id,
        "operation": operation,
        "model": model,
    }
    # Write to secure audit log
    audit_logger.info(json.dumps(entry))
```

---

## Cost Security

### Set Spending Limits

Configure cost limits to prevent runaway spending:

```yaml
settings:
  cost_management:
    max_cost_per_run: 10.00
    daily_limit: 100.00
    require_confirmation: true
```

### Monitor Usage

Regularly check usage dashboards:
- FAL AI: https://fal.ai/dashboard
- Google Cloud: https://console.cloud.google.com/billing
- ElevenLabs: https://elevenlabs.io/app/usage

### Alert on Anomalies

Set up alerts for unusual spending patterns in provider dashboards.

---

## Deployment Security

### Container Security

If using Docker:

```dockerfile
# Use non-root user
RUN useradd -m appuser
USER appuser

# Don't copy .env file
COPY --chown=appuser:appuser . .
# Use secrets mounting instead
```

### Secret Management

Use proper secret management in production:

```python
# AWS Secrets Manager
import boto3

def get_api_key(secret_name: str) -> str:
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

# Azure Key Vault
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_azure_secret(vault_url: str, secret_name: str) -> str:
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    return client.get_secret(secret_name).value
```

---

## Security Checklist

### Before Deployment

- [ ] API keys not in code or version control
- [ ] `.env` files in `.gitignore`
- [ ] Input validation implemented
- [ ] File paths validated
- [ ] Error messages don't expose internals
- [ ] Logging doesn't include sensitive data
- [ ] Cost limits configured
- [ ] SSL verification enabled

### Ongoing

- [ ] API keys rotated regularly
- [ ] Usage monitored
- [ ] Audit logs reviewed
- [ ] Dependencies updated
- [ ] Security patches applied

---

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do not** open a public GitHub issue
2. Email security concerns to the maintainers
3. Provide detailed description of the vulnerability
4. Allow time for a fix before public disclosure
