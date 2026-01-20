# Troubleshooting Guide

Solutions for common issues with the AI Content Generation Suite.

## Quick Diagnostics

Run these commands to diagnose issues:

```bash
# Check installation
ai-content-pipeline --version
ai-content-pipeline --help

# Verify environment
python -c "from packages.core.ai_content_pipeline import AIPipelineManager; print('OK')"

# List available models
ai-content-pipeline list-models

# Test with mock mode
ai-content-pipeline generate-image --text "test" --mock
```

---

## Installation Issues

### "Command not found: ai-content-pipeline"

**Cause:** Package not installed or not in PATH.

**Solutions:**
```bash
# Reinstall package
pip install video-ai-studio

# Or use Python module directly
python -m ai_content_pipeline --help

# Check if pip bin is in PATH
echo $PATH
pip show video-ai-studio
```

### "ModuleNotFoundError: No module named 'packages'"

**Cause:** Package not properly installed.

**Solutions:**
```bash
# Reinstall in development mode
pip install -e .

# Or reinstall from PyPI
pip uninstall video-ai-studio
pip install video-ai-studio
```

### Dependency Conflicts

**Cause:** Conflicting package versions.

**Solutions:**
```bash
# Create fresh virtual environment
python -m venv fresh_env
source fresh_env/bin/activate  # Linux/macOS
fresh_env\Scripts\activate     # Windows

# Install package
pip install video-ai-studio
```

### Python Version Issues

**Cause:** Python version too old.

**Solutions:**
```bash
# Check Python version
python --version

# Use Python 3.10+
python3.11 -m pip install video-ai-studio
```

---

## API Key Issues

### "API key not found" or "Authentication failed"

**Cause:** Missing or invalid API key.

**Solutions:**

1. **Check .env file exists:**
   ```bash
   ls -la .env
   cat .env
   ```

2. **Verify key format:**
   ```env
   # Correct format (no quotes needed)
   FAL_KEY=your_actual_key_here

   # Wrong formats
   FAL_KEY="your_key"  # Don't use quotes
   FAL_KEY=            # Empty value
   ```

3. **Check environment variable:**
   ```bash
   echo $FAL_KEY
   python -c "import os; print(os.getenv('FAL_KEY', 'NOT SET'))"
   ```

4. **Verify API key is valid:**
   - FAL AI: https://fal.ai/dashboard
   - Check key hasn't expired
   - Check usage limits

### "Rate limit exceeded"

**Cause:** Too many requests.

**Solutions:**
- Wait and retry later
- Implement rate limiting in your code
- Contact provider for higher limits

### "Insufficient credits"

**Cause:** API account has insufficient balance.

**Solutions:**
- Add credits to your account
- Use mock mode for testing: `--mock`
- Use cheaper models for development

---

## Generation Issues

### "Model not found"

**Cause:** Invalid model name.

**Solutions:**
```bash
# List all available models
ai-content-pipeline list-models

# Check exact model name
ai-content-pipeline list-models --format json | grep -i "model_name"
```

### "Invalid prompt"

**Cause:** Prompt contains invalid characters or is empty.

**Solutions:**
- Ensure prompt is not empty
- Remove special characters
- Keep prompt under model's character limit

### "Generation timeout"

**Cause:** Operation took too long.

**Solutions:**
```bash
# Increase timeout (if supported)
ai-content-pipeline generate-image --text "test" --timeout 120

# Use faster model
ai-content-pipeline generate-image --text "test" --model flux_schnell
```

### Empty or Corrupted Output

**Cause:** API returned invalid data.

**Solutions:**
- Check output directory permissions
- Verify disk space available
- Retry the operation
- Check API status page

---

## Pipeline Issues

### "Configuration validation failed"

**Cause:** Invalid YAML configuration.

**Solutions:**

1. **Validate YAML syntax:**
   ```bash
   python -c "import yaml; yaml.safe_load(open('config.yaml'))"
   ```

2. **Common YAML errors:**
   ```yaml
   # Wrong: Improper indentation
   steps:
   - name: "step1"
     type: "text_to_image"

   # Correct: Consistent indentation
   steps:
     - name: "step1"
       type: "text_to_image"
   ```

3. **Dry run to check configuration:**
   ```bash
   ai-content-pipeline run-chain --config config.yaml --dry-run
   ```

### "Step reference not found"

**Cause:** Invalid `input_from` reference.

**Solutions:**
```yaml
# Wrong: Reference doesn't exist
- name: "video"
  input_from: "nonexistent_step"

# Correct: Reference existing step name
- name: "image"
  type: "text_to_image"

- name: "video"
  input_from: "image"  # Matches step above
```

### "Circular dependency detected"

**Cause:** Steps reference each other in a loop.

**Solutions:**
```yaml
# Wrong: Circular reference
- name: "step_a"
  input_from: "step_b"

- name: "step_b"
  input_from: "step_a"

# Correct: Linear dependency chain
- name: "step_a"

- name: "step_b"
  input_from: "step_a"
```

### Parallel Execution Fails

**Cause:** Parallel processing configuration issues.

**Solutions:**
```bash
# Disable parallel to isolate issue
ai-content-pipeline run-chain --config config.yaml

# Enable with explicit flag
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain --config config.yaml

# Check for thread-safety issues in custom code
```

---

## Network Issues

### "Connection refused" or "Network unreachable"

**Cause:** Network connectivity problems.

**Solutions:**
```bash
# Test network connectivity
curl https://api.fal.ai
ping api.fal.ai

# Check firewall settings
# Check proxy settings
export HTTPS_PROXY=http://proxy:port
```

### "SSL certificate verify failed"

**Cause:** SSL certificate issues.

**Solutions:**
```bash
# Update certifi
pip install --upgrade certifi

# For development only (not recommended for production):
export SSL_CERT_FILE=""
```

### "Timeout waiting for response"

**Cause:** Slow API response.

**Solutions:**
- Check API status page
- Retry later
- Use faster models
- Increase timeout in code

---

## File Issues

### "Permission denied"

**Cause:** Insufficient file permissions.

**Solutions:**
```bash
# Check directory permissions
ls -la output/

# Create with correct permissions
mkdir -p output
chmod 755 output

# Run with correct user
```

### "Disk space full"

**Cause:** No disk space for output files.

**Solutions:**
```bash
# Check disk space
df -h

# Clean up old files
rm -rf output/old_files/

# Use different output directory
ai-content-pipeline generate-image --text "test" --output /path/with/space/
```

### "File not found"

**Cause:** Input file doesn't exist.

**Solutions:**
```bash
# Verify file exists
ls -la path/to/file.png

# Use absolute path
ai-content-pipeline image-to-video --image /full/path/to/image.png
```

---

## Performance Issues

### Slow Generation

**Solutions:**
1. Use faster models (e.g., `flux_schnell`)
2. Enable parallel processing
3. Reduce image/video resolution
4. Check network latency

### High Memory Usage

**Solutions:**
```bash
# Limit parallel workers
PIPELINE_MAX_WORKERS=2 ai-content-pipeline run-chain --config config.yaml

# Process in smaller batches
```

### Slow Pipeline Execution

**Solutions:**
```yaml
# Enable parallel processing
settings:
  parallel: true

# Use parallel groups for independent steps
steps:
  - type: "parallel_group"
    steps:
      - type: "text_to_image"
        params: { prompt: "image 1" }
      - type: "text_to_image"
        params: { prompt: "image 2" }
```

---

## Getting Help

### Enable Debug Logging

```bash
# Verbose output
ai-content-pipeline --verbose generate-image --text "test"

# Set log level
PIPELINE_LOG_LEVEL=DEBUG ai-content-pipeline run-chain --config config.yaml
```

### Collect Diagnostic Information

```bash
# System info
python --version
pip list | grep video-ai-studio
echo $FAL_KEY | head -c 10

# Test basic functionality
ai-content-pipeline list-models
ai-content-pipeline generate-image --text "test" --mock
```

### Report Issues

When reporting issues, include:
1. Python version
2. Package version
3. Operating system
4. Full error message
5. Steps to reproduce
6. Relevant configuration (without API keys)

**GitHub Issues:** https://github.com/donghaozhang/video-agent-skill/issues

---

## Error Code Reference

| Code | Meaning | Solution |
|------|---------|----------|
| 1 | General error | Check error message |
| 2 | Invalid arguments | Check command syntax |
| 3 | API error | Check API key and credits |
| 4 | File not found | Verify file path |
| 5 | Configuration error | Validate YAML/JSON |
| 10 | Network error | Check connectivity |
| 20 | Authentication error | Check API key |
| 30 | Rate limit | Wait and retry |
| 40 | Quota exceeded | Add credits |

---

[Back to Documentation Index](../index.md)
