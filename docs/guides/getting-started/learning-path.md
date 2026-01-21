# Learning Path Guide

A structured learning journey to master the AI Content Generation Suite.

## Choose Your Path

### 🚀 Quick Start Track (30 minutes)
For users who want to generate content immediately.

### 📚 Comprehensive Track (2-3 hours)
For users who want to understand the full system.

### 🔧 Developer Track (4-6 hours)
For developers building integrations or extending the system.

---

## 🚀 Quick Start Track

### Level 1: First Generation (10 minutes)

**Goal:** Generate your first AI image.

> Need help with installation? See **[Setup Guide](setup.md)** for detailed setup and configuration options.

1. **Install the package:**
   ```bash
   pip install video-ai-studio
   ```

2. **Set up API key:**
   ```bash
   echo "FAL_KEY=your_api_key" > .env
   ```

3. **Generate an image:**
   ```bash
   ai-content-pipeline generate-image --text "sunset over mountains" --model flux_schnell
   ```

**Checkpoint:** You should have an image in your `output/` folder.

---

### Level 2: First Video (10 minutes)

**Goal:** Create a video from text.

1. **Generate video directly:**
   ```bash
   ai-content-pipeline text-to-video --text "ocean waves on beach" --model hailuo_pro
   ```

2. **Or use image-to-video:**
   ```bash
   ai-content-pipeline create-video --text "peaceful forest stream"
   ```

**Checkpoint:** You should have a video file.

---

### Level 3: First Pipeline (10 minutes)

**Goal:** Run a multi-step workflow.

1. **Create `my-pipeline.yaml`:**
   ```yaml
   name: "My First Pipeline"
   steps:
     - name: "image"
       type: "text_to_image"
       model: "flux_schnell"
       params:
         prompt: "{{input}}"
         aspect_ratio: "16:9"

     - name: "video"
       type: "image_to_video"
       model: "hailuo"
       input_from: "image"
       params:
         duration: 6
   ```

2. **Run the pipeline:**
   ```bash
   ai-content-pipeline run-chain --config my-pipeline.yaml --input "beautiful sunset"
   ```

**Checkpoint:** You've completed the Quick Start Track!

---

## 📚 Comprehensive Track

### Module 1: Understanding the System (30 minutes)

**Learning objectives:**
- Understand the architecture
- Know available models and their purposes
- Understand pricing

**Study materials:**
1. Read [Architecture Overview](../../reference/architecture.md)
2. Review [Models Reference](../../reference/models.md)
3. Study [Cost Management](../optimization/cost-management.md)

**Practice:**
```bash
# Explore available models
ai-content-pipeline list-models

# Estimate costs before running
ai-content-pipeline estimate-cost --config sample-pipeline.yaml
```

**Quiz yourself:**
- What's the difference between flux_schnell and flux_dev?
- Which model is best for budget video generation?
- How does image-to-video differ from text-to-video?

---

### Module 2: Mastering YAML Pipelines (45 minutes)

**Learning objectives:**
- Write pipeline configurations
- Use variables and references
- Understand step dependencies

**Study materials:**
1. Read [YAML Pipeline Configuration](../pipelines/yaml-pipelines.md)
2. Review [Basic Examples](../../examples/basic-examples.md)

**Practice exercises:**

**Exercise 1:** Create a pipeline with custom output naming
```yaml
name: "Custom Output"
output:
  directory: "my_project"
  naming: "timestamp"
steps:
  - type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "test image"
```

**Exercise 2:** Create a two-step pipeline with dependencies
```yaml
name: "Two Step"
steps:
  - name: "base_image"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "mountain landscape"

  - name: "animated"
    type: "image_to_video"
    input_from: "base_image"
    model: "kling_2_1"
    params:
      duration: 5
```

**Checkpoint:** Can you create a pipeline from scratch?

---

### Module 3: Optimization Techniques (30 minutes)

**Learning objectives:**
- Enable parallel execution
- Choose optimal models
- Minimize costs while maintaining quality

**Study materials:**
1. Read [Parallel Execution](../pipelines/parallel-execution.md)
2. Read [Performance Optimization](../optimization/performance.md)
3. Read [Best Practices](../optimization/best-practices.md)

**Practice:**
```bash
# Run with parallel execution
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain --config batch.yaml

# Compare execution times
time ai-content-pipeline run-chain --config config.yaml  # Sequential
time PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain --config config.yaml  # Parallel
```

---

### Module 4: Effective Prompting (30 minutes)

**Learning objectives:**
- Write effective image prompts
- Write effective video motion prompts
- Avoid common mistakes

**Study materials:**
1. Read [Prompting Guide](../content-creation/prompting.md)
2. Read [Video Generation Tips](../content-creation/video-tips.md)

**Practice exercises:**

**Exercise 1:** Improve these prompts
```
Original: "a cat"
Improved: "Orange tabby cat sitting on windowsill, warm afternoon sunlight,
          cozy home interior, shallow depth of field, lifestyle photography"

Original: "person walking"
Improved: "Young professional walking through modern office corridor,
          confident stride, natural movement, soft ambient lighting"
```

**Exercise 2:** Write video motion prompts
```yaml
# For a landscape image
prompt: "slow cinematic pan from left to right, clouds drifting, peaceful atmosphere"

# For a portrait
prompt: "subtle movement, gentle breathing, eyes blinking naturally, soft wind"
```

---

### Module 5: Troubleshooting (15 minutes)

**Learning objectives:**
- Diagnose common errors
- Use debugging tools
- Know where to find help

**Study materials:**
1. Read [Troubleshooting Guide](../support/troubleshooting.md)
2. Read [Error Codes Reference](../../reference/error-codes.md)
3. Read [FAQ](../support/faq.md)

**Practice:**
```bash
# Validate configuration
ai-content-pipeline validate-config --config config.yaml

# Test with mock mode
ai-content-pipeline generate-image --text "test" --mock

# Run with verbose output
ai-content-pipeline run-chain --config config.yaml --verbose
```

**Checkpoint:** You've completed the Comprehensive Track!

---

## 🔧 Developer Track

### Module D1: Python API (1 hour)

**Learning objectives:**
- Use the Python API directly
- Build custom applications
- Handle results programmatically

**Study materials:**
1. Read [Python API Reference](../../api/python-api.md)
2. Review [Integration Examples](../../examples/integrations.md)

**Practice:**
```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()

# Generate image
result = manager.generate_image(
    prompt="beautiful sunset",
    model="flux_dev"
)
print(f"Image saved: {result.output_path}")
print(f"Cost: ${result.cost:.4f}")

# Run pipeline
results = manager.run_pipeline(
    "config.yaml",
    input_text="mountain landscape"
)
for step_result in results:
    print(f"{step_result.step_name}: {step_result.output_path}")
```

---

### Module D2: Web Integrations (1 hour)

**Learning objectives:**
- Integrate with Flask/FastAPI
- Handle async processing
- Build REST APIs

**Study materials:**
1. Read [Integration Examples](../../examples/integrations.md)
2. Review [Advanced Pipelines](../../examples/advanced-pipelines.md)

**Practice: Build a Flask API**
```python
from flask import Flask, request, jsonify
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

app = Flask(__name__)
manager = AIPipelineManager()

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.json.get('prompt')
    model = request.json.get('model', 'flux_schnell')

    result = manager.generate_image(prompt=prompt, model=model)

    return jsonify({
        'success': result.success,
        'output_path': result.output_path,
        'cost': result.cost
    })

if __name__ == '__main__':
    app.run(debug=True)
```

---

### Module D3: Background Processing (1 hour)

**Learning objectives:**
- Use Celery for async tasks
- Build job queues
- Handle long-running operations

**Study materials:**
1. Read async patterns in [Integration Examples](../../examples/integrations.md)
2. Read [Performance Optimization](../optimization/performance.md)

**Practice: Celery Task**
```python
from celery import Celery
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

app = Celery('tasks', broker='redis://localhost:6379/0')
manager = AIPipelineManager()

@app.task
def generate_video_task(config_path, input_text):
    results = manager.run_pipeline(config_path, input_text=input_text)
    return {
        'outputs': [r.output_path for r in results],
        'total_cost': sum(r.cost for r in results)
    }
```

---

### Module D4: Testing & CI/CD (1 hour)

**Learning objectives:**
- Write unit tests
- Set up CI/CD pipelines
- Use mock mode for testing

**Study materials:**
1. Read [Testing Guide](../support/testing.md)
2. Read [Contributing Guide](../contributing/contributing.md)

**Practice: Write Tests**
```python
import pytest
from unittest.mock import Mock, patch

class TestMyIntegration:
    @patch('packages.core.ai_content_pipeline.pipeline.manager.AIPipelineManager')
    def test_image_generation(self, mock_manager):
        mock_manager.return_value.generate_image.return_value = Mock(
            success=True,
            output_path="/tmp/test.png",
            cost=0.003
        )

        # Your integration code here
        result = my_function_that_uses_manager()

        assert result['success'] is True
```

---

### Module D5: Contributing (30 minutes)

**Learning objectives:**
- Understand the codebase structure
- Follow contribution guidelines
- Submit pull requests

**Study materials:**
1. Read [Contributing Guide](../contributing/contributing.md)
2. Read [Package Structure](../../reference/package-structure.md)
3. Review [Architecture Overview](../../reference/architecture.md)

**Practice:**
1. Fork the repository
2. Create a feature branch
3. Make a small improvement
4. Submit a pull request

**Checkpoint:** You've completed the Developer Track!

---

## Progress Checklist

### Quick Start Track
- [ ] Installed the package
- [ ] Generated first image
- [ ] Generated first video
- [ ] Ran first pipeline

### Comprehensive Track
- [ ] Understand system architecture
- [ ] Know available models and pricing
- [ ] Can write YAML pipelines
- [ ] Can use parallel execution
- [ ] Write effective prompts
- [ ] Can troubleshoot common issues

### Developer Track
- [ ] Use Python API fluently
- [ ] Built a web integration
- [ ] Implemented async processing
- [ ] Write tests with mocks
- [ ] Contributed to the project

---

## Recommended Learning Order

### Beginners
1. Quick Start Track (all levels)
2. Comprehensive Track Modules 1-2
3. Practice with example pipelines
4. Comprehensive Track Modules 3-5

### Experienced Developers
1. Quick Start Track Level 3 (to understand the system)
2. Comprehensive Track Modules 1-2
3. Developer Track Modules D1-D2
4. Continue with remaining modules as needed

### Content Creators
1. Quick Start Track (all levels)
2. Comprehensive Track Module 4 (Prompting)
3. Comprehensive Track Module 2 (Pipelines)
4. Practice, practice, practice!

---

## Additional Resources

### Documentation
- [Complete Documentation Index](../../index.md)
- [CLI Commands Reference](../../reference/cli-commands.md)
- [Models Reference](../../reference/models.md)

### Examples
- [Basic Examples](../../examples/basic-examples.md)
- [Advanced Pipelines](../../examples/advanced-pipelines.md)
- [Real-World Use Cases](../../examples/use-cases.md)

### Community
- [GitHub Repository](https://github.com/donghaozhang/video-agent-skill)
- [Issue Tracker](https://github.com/donghaozhang/video-agent-skill/issues)

---

## Next Steps

After completing your chosen track:

1. **Build a real project** - Apply what you learned
2. **Explore advanced features** - Try parallel groups, video analysis
3. **Optimize for production** - Cost management, error handling
4. **Contribute** - Help improve the project

---

[Back to Documentation Index](../../index.md)
