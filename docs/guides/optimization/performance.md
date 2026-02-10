# Performance Optimization Guide

Maximize speed and efficiency when using AI Content Generation Suite.

## Overview

Performance depends on:
1. **Model selection** - Different models have different speeds
2. **Parallel execution** - Run independent operations concurrently
3. **Network optimization** - Minimize latency
4. **Resource management** - Efficient use of system resources

---

## Model Speed Comparison

> For complete model details and capabilities, see **[Models Reference](../../reference/models.md)**.

### Text-to-Image Speed

| Model | Typical Time | Speed Rating |
|-------|--------------|--------------|
| `flux_schnell` | 2-4s | ★★★★★ Fastest |
| `nano_banana_pro` | 3-5s | ★★★★☆ |
| `flux_dev` | 5-10s | ★★★☆☆ |
| `imagen4` | 8-15s | ★★☆☆☆ |
| `gen4` | 15-30s | ★☆☆☆☆ Slowest |

### Image-to-Video Speed

| Model | Typical Time | Speed Rating |
|-------|--------------|--------------|
| `hailuo` | 30-60s | ★★★★☆ Fast |
| `kling_2_1` | 45-90s | ★★★☆☆ |
| `kling_2_6_pro` | 60-120s | ★★☆☆☆ |
| `sora_2` | 90-180s | ★★☆☆☆ |
| `sora_2_pro` | 120-300s | ★☆☆☆☆ Slowest |

### Speed vs Quality Trade-off

```text
Speed ←──────────────────────────────→ Quality

flux_schnell ──── nano_banana ──── flux_dev ──── imagen4
   Fastest           Fast           Medium        Best
   $0.001           $0.002          $0.003       $0.004
```

---

## Parallel Execution

### Enable Parallel Processing

```bash
# Environment variable
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain --config config.yaml
```

```yaml
# YAML setting
settings:
  parallel: true
```

### Parallel Groups

Group independent operations:

```yaml
steps:
  # These run in parallel (2-3x faster)
  - type: "parallel_group"
    name: "batch_images"
    steps:
      - name: "image_1"
        type: "text_to_image"
        params: { prompt: "sunset" }
      - name: "image_2"
        type: "text_to_image"
        params: { prompt: "mountains" }
      - name: "image_3"
        type: "text_to_image"
        params: { prompt: "ocean" }
```

**Without parallel:** 3 images × 5s = 15s
**With parallel:** 3 images running together ≈ 6s

### Optimal Worker Count

| Scenario | Workers | Why |
|----------|---------|-----|
| Light usage | 2-4 | Avoid rate limits |
| Standard usage | 4-6 | Good balance |
| Heavy usage | 6-8 | Maximum throughput |
| Rate-limited API | 2 | Prevent blocks |

```yaml
settings:
  parallel: true
  max_workers: 4  # Adjust based on your usage
```

### Dependency-Aware Parallelization

The system automatically handles dependencies:

```yaml
steps:
  # Step 1: Runs first (no dependencies)
  - name: "base_image"
    type: "text_to_image"

  # Steps 2-3: Run in parallel (both depend only on step 1)
  - type: "parallel_group"
    steps:
      - name: "video"
        type: "image_to_video"
        input_from: "base_image"

      - name: "thumbnail"
        type: "image_to_image"
        input_from: "base_image"

  # Step 4: Runs after parallel group completes
  - name: "analysis"
    type: "analyze_image"
    input_from: "thumbnail"
```

---

## Batching Strategies

### Batch Size Guidelines

| Operation | Recommended Batch | Max Batch |
|-----------|-------------------|-----------|
| Text-to-image | 10-20 | 50 |
| Image-to-video | 3-5 | 10 |
| Image analysis | 20-50 | 100 |

### Chunked Processing

For large batches, process in chunks:

```python
def process_in_chunks(prompts: list, chunk_size: int = 10):
    results = []

    for i in range(0, len(prompts), chunk_size):
        chunk = prompts[i:i + chunk_size]

        # Process chunk in parallel
        chunk_results = manager.run_pipeline(
            config={
                "settings": {"parallel": True},
                "steps": [
                    {"type": "parallel_group", "steps": [
                        {"type": "text_to_image", "params": {"prompt": p}}
                        for p in chunk
                    ]}
                ]
            }
        )
        results.extend(chunk_results)

        # Optional: Rate limit between chunks
        time.sleep(1)

    return results
```

---

## Network Optimization

### Connection Reuse

The SDK reuses HTTP connections automatically. For custom implementations:

```python
import httpx

# Create persistent client
client = httpx.Client(
    timeout=60,
    limits=httpx.Limits(
        max_connections=10,
        max_keepalive_connections=5
    )
)

# Reuse for multiple requests
for prompt in prompts:
    response = client.post(api_url, json={"prompt": prompt})
```

### Timeout Configuration

Set appropriate timeouts:

```python
# Short timeout for fast models
manager.generate_image(prompt="test", model="flux_schnell", timeout=30)

# Longer timeout for slow models
manager.generate_image(prompt="test", model="sora_2_pro", timeout=600)
```

### Regional Endpoints

Use endpoints closest to your location when available (check provider documentation).

---

## Resource Management

### Memory Optimization

For large batch operations:

```python
import gc

def batch_generate_with_cleanup(prompts: list):
    results = []

    for i, prompt in enumerate(prompts):
        result = manager.generate_image(prompt=prompt)
        results.append(result.output_path)  # Store only path, not full result

        # Periodic cleanup
        if i % 50 == 0:
            gc.collect()

    return results
```

### Disk Space Management

Monitor output directory size:

```python
import os
from pathlib import Path

def check_disk_space(output_dir: str, min_gb: float = 1.0) -> bool:
    """Check if there's enough disk space."""
    import shutil
    total, used, free = shutil.disk_usage(output_dir)
    free_gb = free / (1024 ** 3)
    return free_gb >= min_gb

def cleanup_old_outputs(output_dir: str, max_age_days: int = 7):
    """Remove outputs older than specified days."""
    import time
    cutoff = time.time() - (max_age_days * 86400)

    for path in Path(output_dir).rglob("*"):
        if path.is_file() and path.stat().st_mtime < cutoff:
            path.unlink()
```

---

## Caching Strategies

### Result Caching

Cache generated content to avoid regeneration:

```python
import hashlib
import json
from pathlib import Path

class GenerationCache:
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_key(self, prompt: str, model: str, **kwargs) -> str:
        data = json.dumps({"prompt": prompt, "model": model, **kwargs}, sort_keys=True)
        return hashlib.md5(data.encode()).hexdigest()

    def get(self, prompt: str, model: str, **kwargs) -> str | None:
        key = self._get_key(prompt, model, **kwargs)
        cache_file = self.cache_dir / f"{key}.json"

        if cache_file.exists():
            data = json.loads(cache_file.read_text())
            if Path(data["output_path"]).exists():
                return data["output_path"]
        return None

    def set(self, prompt: str, model: str, output_path: str, **kwargs):
        key = self._get_key(prompt, model, **kwargs)
        cache_file = self.cache_dir / f"{key}.json"
        cache_file.write_text(json.dumps({"output_path": output_path}))

# Usage
cache = GenerationCache()

def generate_cached(prompt: str, model: str = "flux_dev"):
    cached = cache.get(prompt, model)
    if cached:
        return cached

    result = manager.generate_image(prompt=prompt, model=model)
    cache.set(prompt, model, result.output_path)
    return result.output_path
```

### Prompt Similarity Caching

For similar prompts, reuse results:

```python
from difflib import SequenceMatcher

def find_similar_cached(prompt: str, threshold: float = 0.9) -> str | None:
    """Find cached result for similar prompt."""
    for cached_prompt, output_path in cache.items():
        similarity = SequenceMatcher(None, prompt, cached_prompt).ratio()
        if similarity >= threshold:
            return output_path
    return None
```

---

## Benchmarking

### Measure Pipeline Performance

```python
import time

def benchmark_pipeline(config_path: str, iterations: int = 5):
    times = []

    for i in range(iterations):
        start = time.time()
        manager.run_pipeline(config_path, input_text="benchmark test")
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"Iteration {i+1}: {elapsed:.2f}s")

    avg = sum(times) / len(times)
    print(f"\nAverage: {avg:.2f}s")
    print(f"Min: {min(times):.2f}s")
    print(f"Max: {max(times):.2f}s")

benchmark_pipeline("pipeline.yaml")
```

### Compare Models

```python
def compare_models(prompt: str, models: list):
    results = {}

    for model in models:
        start = time.time()
        result = manager.generate_image(prompt=prompt, model=model)
        elapsed = time.time() - start

        results[model] = {
            "time": elapsed,
            "cost": result.cost,
            "path": result.output_path
        }

    # Print comparison
    print(f"\n{'Model':<20} {'Time':<10} {'Cost':<10}")
    print("-" * 40)
    for model, data in sorted(results.items(), key=lambda x: x[1]["time"]):
        print(f"{model:<20} {data['time']:.2f}s    ${data['cost']:.4f}")

compare_models("a beautiful sunset", ["flux_schnell", "flux_dev", "imagen4"])
```

---

## Performance Checklist

### Quick Wins

- [ ] Enable parallel execution
- [ ] Use fast models for prototyping
- [ ] Batch similar operations
- [ ] Cache results

### Advanced Optimization

- [ ] Tune worker count for your rate limits
- [ ] Implement result caching
- [ ] Use chunked processing for large batches
- [ ] Monitor and cleanup disk space

### Monitoring

- [ ] Track generation times
- [ ] Monitor API response times
- [ ] Set up alerts for slow operations
- [ ] Review costs regularly
