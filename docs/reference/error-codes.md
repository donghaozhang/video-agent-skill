# Error Codes Reference

Complete reference for error codes and troubleshooting in the AI Content Pipeline.

## Error Code Format

Error codes follow the pattern: `[CATEGORY][NUMBER]`

| Category | Prefix | Description |
|----------|--------|-------------|
| Authentication | AUTH | API key and credential errors |
| Configuration | CFG | YAML and config file errors |
| Model | MDL | Model-related errors |
| Pipeline | PIP | Pipeline execution errors |
| Network | NET | Network and connectivity errors |
| File | FILE | File I/O errors |
| Rate Limit | RATE | API rate limiting errors |
| Cost | COST | Budget and cost errors |
| Validation | VAL | Input validation errors |

---

## Authentication Errors (AUTH)

### AUTH001: Missing API Key

**Message:** `API key not found for provider: {provider}`

**Cause:** The required API key is not set in environment variables.

**Solution:**
```bash
# Add to .env file
FAL_KEY=your_fal_api_key
GEMINI_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key
```

### AUTH002: Invalid API Key

**Message:** `Invalid API key for provider: {provider}`

**Cause:** The API key is malformed or has been revoked.

**Solution:**
1. Verify the key is copied correctly (no extra spaces)
2. Check if the key is still active in your provider dashboard
3. Generate a new key if needed

### AUTH003: API Key Expired

**Message:** `API key expired for provider: {provider}`

**Cause:** The API key has reached its expiration date.

**Solution:**
1. Log into your provider dashboard
2. Generate a new API key
3. Update your `.env` file

### AUTH004: Insufficient Permissions

**Message:** `API key lacks required permissions: {permissions}`

**Cause:** The API key doesn't have access to the requested model or feature.

**Solution:**
1. Check your subscription tier with the provider
2. Upgrade your plan if needed
3. Request additional permissions

### AUTH005: Google Cloud Authentication Failed

**Message:** `Google Cloud authentication failed`

**Cause:** Google Cloud credentials are not configured properly.

**Solution:**
```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project your-project-id
```

---

## Configuration Errors (CFG)

### CFG001: Invalid YAML Syntax

**Message:** `YAML parsing error at line {line}: {detail}`

**Cause:** The YAML file contains syntax errors.

**Solution:**
```yaml
# Check for common issues:

# Wrong: Tabs instead of spaces
steps:
	- name: "step1"  # Tab character

# Correct: Use spaces
steps:
  - name: "step1"  # Two spaces

# Wrong: Missing quotes
params:
  prompt: text with: colon

# Correct: Quote strings with special characters
params:
  prompt: "text with: colon"
```

### CFG002: Missing Required Field

**Message:** `Missing required field: {field} in {location}`

**Cause:** A required configuration field is not provided.

**Solution:**
```yaml
# Required fields for pipeline:
name: "Pipeline Name"  # Required
steps:                 # Required
  - name: "step1"      # Optional but recommended
    type: "text_to_image"  # Required
    model: "flux_dev"      # Required
    params:                # Required for most steps
      prompt: "..."
```

### CFG003: Invalid Step Type

**Message:** `Unknown step type: {type}`

**Cause:** The step type is not recognized.

**Valid Step Types:**
```yaml
# Image generation
type: "text_to_image"
type: "image_to_image"

# Video generation
type: "image_to_video"
type: "text_to_video"

# Audio generation
type: "text_to_speech"
type: "audio_generation"

# Utilities
type: "video_upscale"
type: "image_upscale"
type: "parallel_group"
```

### CFG004: Invalid Model Name

**Message:** `Unknown model: {model} for step type: {type}`

**Cause:** The specified model doesn't exist or isn't compatible with the step type.

**Solution:**
```bash
# List available models
ai-content-pipeline list-models

# Check model compatibility
ai-content-pipeline list-models --type text_to_image
```

### CFG005: Invalid Parameter

**Message:** `Invalid parameter: {param} for model: {model}`

**Cause:** The parameter is not supported by the specified model.

**Solution:**
Check model documentation for supported parameters:
```yaml
# FLUX models support:
params:
  prompt: "..."
  aspect_ratio: "16:9"
  num_images: 1
  guidance_scale: 3.5

# Kling models support:
params:
  prompt: "..."
  duration: 5
  aspect_ratio: "16:9"
```

### CFG006: Circular Dependency

**Message:** `Circular dependency detected: {step_a} <-> {step_b}`

**Cause:** Steps reference each other creating an infinite loop.

**Solution:**
```yaml
# Wrong: Circular reference
steps:
  - name: "step_a"
    input_from: "step_b"
  - name: "step_b"
    input_from: "step_a"

# Correct: Linear dependency
steps:
  - name: "step_a"
    params: { prompt: "..." }
  - name: "step_b"
    input_from: "step_a"
```

### CFG007: Missing Input Reference

**Message:** `Referenced step not found: {step_name}`

**Cause:** `input_from` references a step that doesn't exist.

**Solution:**
```yaml
steps:
  - name: "image"  # This name must match
    type: "text_to_image"

  - name: "video"
    input_from: "image"  # Must match step name above
```

---

## Model Errors (MDL)

### MDL001: Model Not Available

**Message:** `Model {model} is currently unavailable`

**Cause:** The model is temporarily unavailable or deprecated.

**Solution:**
1. Check provider status page
2. Use an alternative model
3. Wait and retry later

### MDL002: Model Timeout

**Message:** `Model {model} timed out after {seconds}s`

**Cause:** Generation took longer than allowed timeout.

**Solution:**
```yaml
# Increase timeout in config
settings:
  timeout: 600  # 10 minutes

# Or use a faster model
model: "flux_schnell"  # Instead of flux_dev
```

### MDL003: Model Capacity Exceeded

**Message:** `Model {model} at maximum capacity`

**Cause:** Too many concurrent requests to the model.

**Solution:**
1. Wait and retry with exponential backoff
2. Reduce parallel workers
3. Use a different model

### MDL004: Invalid Input Format

**Message:** `Invalid input format for model {model}: {detail}`

**Cause:** Input data format doesn't match model requirements.

**Solution:**
```python
# Image input requirements
# - Format: PNG, JPEG, WebP
# - Max size: Usually 10MB
# - Resolution: Model-specific

# Video input requirements
# - Format: MP4, WebM
# - Duration: Model-specific limits
```

### MDL005: Content Policy Violation

**Message:** `Content rejected by model safety filters`

**Cause:** The prompt or output was flagged by content filters.

**Solution:**
1. Review prompt for policy violations
2. Rephrase request in neutral terms
3. Avoid sensitive topics

---

## Pipeline Errors (PIP)

### PIP001: Pipeline Execution Failed

**Message:** `Pipeline failed at step: {step_name}`

**Cause:** A step in the pipeline encountered an error.

**Solution:**
```bash
# Run with verbose logging
ai-content-pipeline run-chain --config config.yaml --verbose

# Run individual step for debugging
ai-content-pipeline generate-image --text "test" --model flux_schnell
```

### PIP002: Step Dependency Failed

**Message:** `Step {step} failed because dependency {dependency} failed`

**Cause:** A required previous step didn't complete successfully.

**Solution:**
1. Check the error from the dependency step
2. Fix the dependency step first
3. Re-run the pipeline

### PIP003: Parallel Execution Error

**Message:** `Parallel execution failed: {detail}`

**Cause:** Error during parallel step execution.

**Solution:**
```bash
# Disable parallel execution for debugging
PIPELINE_PARALLEL_ENABLED=false ai-content-pipeline run-chain --config config.yaml
```

### PIP004: Output Path Conflict

**Message:** `Output path already exists: {path}`

**Cause:** Output file would overwrite existing file.

**Solution:**
```yaml
# Use unique output names
settings:
  output_naming: "timestamp"  # Adds timestamp to filenames

# Or specify unique output
output:
  path: "output/unique_name_{{timestamp}}.png"
```

### PIP005: Maximum Retries Exceeded

**Message:** `Step {step} failed after {n} retries`

**Cause:** Step failed repeatedly despite retry attempts.

**Solution:**
```yaml
# Configure retry behavior
settings:
  max_retries: 5
  retry_delay: 10  # seconds

# Or disable retries for debugging
settings:
  max_retries: 0
```

---

## Network Errors (NET)

### NET001: Connection Failed

**Message:** `Failed to connect to {endpoint}`

**Cause:** Cannot establish connection to API endpoint.

**Solution:**
1. Check internet connectivity
2. Check if provider service is up
3. Check firewall settings

### NET002: Connection Timeout

**Message:** `Connection timed out to {endpoint}`

**Cause:** Connection took too long to establish.

**Solution:**
```yaml
settings:
  connection_timeout: 30  # Increase timeout
```

### NET003: SSL Certificate Error

**Message:** `SSL certificate verification failed`

**Cause:** SSL/TLS certificate issue.

**Solution:**
1. Update your system's CA certificates
2. Check system date/time is correct
3. Contact IT if behind corporate proxy

### NET004: DNS Resolution Failed

**Message:** `Could not resolve host: {hostname}`

**Cause:** DNS lookup failed for API endpoint.

**Solution:**
1. Check DNS settings
2. Try alternative DNS (8.8.8.8)
3. Check if domain is blocked

### NET005: Proxy Error

**Message:** `Proxy connection failed`

**Cause:** Configured proxy is not working.

**Solution:**
```bash
# Check proxy settings
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Unset if not needed
unset HTTP_PROXY
unset HTTPS_PROXY
```

---

## File Errors (FILE)

### FILE001: File Not Found

**Message:** `File not found: {path}`

**Cause:** The specified file doesn't exist.

**Solution:**
```bash
# Check file exists
ls -la /path/to/file

# Use absolute paths
ai-content-pipeline image-to-video --image /full/path/to/image.png
```

### FILE002: Permission Denied

**Message:** `Permission denied: {path}`

**Cause:** Insufficient permissions to read/write file.

**Solution:**
```bash
# Check permissions
ls -la /path/to/file

# Fix permissions
chmod 644 /path/to/file  # Read/write for owner, read for others
```

### FILE003: Invalid File Format

**Message:** `Invalid file format: expected {expected}, got {actual}`

**Cause:** File format doesn't match expected type.

**Supported Formats:**
```
Images: PNG, JPEG, WebP, GIF
Videos: MP4, WebM, MOV
Audio: MP3, WAV, OGG
Config: YAML, JSON
```

### FILE004: File Too Large

**Message:** `File exceeds maximum size: {size}MB > {max}MB`

**Cause:** Input file exceeds size limits.

**Solution:**
1. Compress or resize the file
2. Use a different input file
3. Check model-specific limits

### FILE005: Disk Space Full

**Message:** `Insufficient disk space for output`

**Cause:** Not enough disk space to save output.

**Solution:**
```bash
# Check disk space
df -h

# Clean up old outputs
rm -rf output/old_runs/

# Change output directory
ai-content-pipeline run-chain --output /path/with/space/
```

### FILE006: Output Directory Error

**Message:** `Cannot create output directory: {path}`

**Cause:** Cannot create the output directory.

**Solution:**
```bash
# Create directory manually
mkdir -p output/my_project

# Check parent directory permissions
ls -la output/
```

---

## Rate Limit Errors (RATE)

### RATE001: API Rate Limited

**Message:** `Rate limit exceeded for {provider}. Retry after {seconds}s`

**Cause:** Too many API requests in a short period.

**Solution:**
```yaml
# Reduce parallel workers
settings:
  max_workers: 2  # Default is 4

# Add delay between requests
settings:
  request_delay: 1.0  # seconds
```

### RATE002: Concurrent Request Limit

**Message:** `Maximum concurrent requests exceeded: {limit}`

**Cause:** Too many simultaneous requests.

**Solution:**
1. Reduce `max_workers` setting
2. Process items sequentially
3. Add delays between batches

### RATE003: Daily Quota Exceeded

**Message:** `Daily API quota exceeded for {provider}`

**Cause:** Reached daily usage limit.

**Solution:**
1. Wait until quota resets (usually midnight UTC)
2. Upgrade your API plan
3. Use a different provider

### RATE004: Monthly Quota Exceeded

**Message:** `Monthly API quota exceeded`

**Cause:** Reached monthly usage limit.

**Solution:**
1. Upgrade your subscription
2. Wait until next billing cycle
3. Contact provider for increase

---

## Cost Errors (COST)

### COST001: Budget Exceeded

**Message:** `Estimated cost ${cost} exceeds budget ${budget}`

**Cause:** Pipeline cost would exceed configured budget.

**Solution:**
```yaml
# Increase budget limit
settings:
  max_budget: 10.00

# Or use cheaper models
model: "flux_schnell"  # Instead of flux_dev
```

### COST002: Insufficient Credits

**Message:** `Insufficient credits: have ${have}, need ${need}`

**Cause:** Not enough prepaid credits for the operation.

**Solution:**
1. Add credits to your account
2. Reduce pipeline scope
3. Use cheaper models

### COST003: Cost Estimation Failed

**Message:** `Could not estimate cost for model: {model}`

**Cause:** Pricing information unavailable.

**Solution:**
```bash
# Skip cost estimation
ai-content-pipeline run-chain --config config.yaml --skip-cost-check
```

---

## Validation Errors (VAL)

### VAL001: Empty Prompt

**Message:** `Prompt cannot be empty`

**Cause:** No prompt text provided.

**Solution:**
```yaml
params:
  prompt: "A beautiful sunset over the ocean"  # Must have content
```

### VAL002: Prompt Too Long

**Message:** `Prompt exceeds maximum length: {length} > {max}`

**Cause:** Prompt text is too long for the model.

**Solution:**
```python
# Most models: 1000-2000 characters
# Summarize or split long prompts
```

### VAL003: Invalid Aspect Ratio

**Message:** `Invalid aspect ratio: {ratio}`

**Cause:** Unsupported aspect ratio format.

**Valid Aspect Ratios:**
```yaml
aspect_ratio: "1:1"     # Square
aspect_ratio: "16:9"    # Landscape
aspect_ratio: "9:16"    # Portrait
aspect_ratio: "4:3"     # Standard
aspect_ratio: "3:4"     # Portrait standard
aspect_ratio: "2.39:1"  # Cinemascope
```

### VAL004: Invalid Duration

**Message:** `Invalid duration: {duration}. Must be between {min} and {max}`

**Cause:** Video duration out of allowed range.

**Solution:**
```yaml
# Check model limits
params:
  duration: 5  # Most models: 3-10 seconds
```

### VAL005: Invalid Image Dimensions

**Message:** `Image dimensions {width}x{height} not supported`

**Cause:** Image size doesn't meet model requirements.

**Solution:**
```bash
# Resize image to supported dimensions
# Common requirements: 512x512, 1024x1024, etc.
```

---

## Troubleshooting Steps

### General Debugging

1. **Enable verbose logging:**
   ```bash
   ai-content-pipeline run-chain --config config.yaml --verbose
   ```

2. **Check configuration:**
   ```bash
   ai-content-pipeline validate-config --config config.yaml
   ```

3. **Test API connectivity:**
   ```bash
   ai-content-pipeline test-connection --provider fal
   ```

4. **Use dry run mode:**
   ```bash
   ai-content-pipeline run-chain --config config.yaml --dry-run
   ```

### Getting Help

If errors persist:

1. Check the [Troubleshooting Guide](../guides/troubleshooting.md)
2. Search existing [GitHub Issues](https://github.com/donghaozhang/video-agent-skill/issues)
3. Create a new issue with:
   - Error code and message
   - Configuration file (redact API keys)
   - Python version and OS
   - Steps to reproduce
