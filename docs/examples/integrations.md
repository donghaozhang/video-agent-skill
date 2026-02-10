# Integration Examples

Examples of integrating AI Content Generation Suite with various frameworks and services.

## Web Frameworks

### Flask Integration

```python
from flask import Flask, request, jsonify, send_file
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager
import os

app = Flask(__name__)
manager = AIPipelineManager()

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """Generate an image from text prompt."""
    data = request.json

    if not data or not data.get('prompt'):
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        result = manager.generate_image(
            prompt=data['prompt'],
            model=data.get('model', 'flux_dev')
        )

        return jsonify({
            'success': True,
            'path': result.output_path,
            'cost': result.cost
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-video', methods=['POST'])
def generate_video():
    """Generate video from text prompt."""
    data = request.json

    if not data or not data.get('prompt'):
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        result = manager.create_video(
            prompt=data['prompt'],
            image_model=data.get('image_model', 'flux_dev'),
            video_model=data.get('video_model', 'kling_2_6_pro')
        )

        return jsonify({
            'success': True,
            'path': result.output_path,
            'cost': result.cost
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<path:filename>')
def download_file(filename):
    """Download generated file."""
    file_path = os.path.join('output', filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**Usage:**
```bash
curl -X POST http://localhost:5000/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a beautiful sunset", "model": "flux_dev"}'
```

---

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager
import uuid

app = FastAPI(title="AI Content API")
manager = AIPipelineManager()

# Store for async jobs
jobs = {}


class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = "flux_dev"


class VideoRequest(BaseModel):
    prompt: str
    image_model: Optional[str] = "flux_dev"
    video_model: Optional[str] = "kling_2_6_pro"
    duration: Optional[int] = 5


class JobResponse(BaseModel):
    job_id: str
    status: str


@app.post("/generate-image")
async def generate_image(request: GenerateRequest):
    """Generate image synchronously."""
    try:
        result = manager.generate_image(
            prompt=request.prompt,
            model=request.model
        )
        return {
            "success": True,
            "output_path": result.output_path,
            "cost": result.cost
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def process_video_job(job_id: str, request: VideoRequest):
    """Background video generation."""
    jobs[job_id]["status"] = "processing"
    try:
        result = manager.create_video(
            prompt=request.prompt,
            image_model=request.image_model,
            video_model=request.video_model
        )
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = {
            "output_path": result.output_path,
            "cost": result.cost
        }
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@app.post("/generate-video", response_model=JobResponse)
async def generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """Generate video asynchronously."""
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "pending"}

    background_tasks.add_task(process_video_job, job_id, request)

    return {"job_id": job_id, "status": "pending"}


@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Check job status."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@app.get("/models")
async def list_models():
    """List available models."""
    return manager.list_models()
```

**Usage:**
```bash
# Start server
uvicorn main:app --reload

# Generate image
curl -X POST "http://localhost:8000/generate-image" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "space station"}'

# Generate video (async)
curl -X POST "http://localhost:8000/generate-video" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "ocean waves"}'

# Check job status
curl "http://localhost:8000/job/{job_id}"
```

---

## Task Queues

### Celery Integration

```python
# tasks.py
from celery import Celery
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

app = Celery('tasks', broker='redis://localhost:6379/0')
manager = AIPipelineManager()


@app.task
def generate_image_task(prompt: str, model: str = "flux_dev"):
    """Async image generation task."""
    result = manager.generate_image(prompt=prompt, model=model)
    return {
        "output_path": result.output_path,
        "cost": result.cost
    }


@app.task
def generate_video_task(prompt: str, image_model: str = "flux_dev",
                        video_model: str = "kling_2_6_pro"):
    """Async video generation task."""
    result = manager.create_video(
        prompt=prompt,
        image_model=image_model,
        video_model=video_model
    )
    return {
        "output_path": result.output_path,
        "cost": result.cost
    }


@app.task
def run_pipeline_task(config_path: str, input_text: str):
    """Async pipeline execution task."""
    results = manager.run_pipeline(config_path, input_text=input_text)
    return [
        {"step": r.step_name, "output": str(r.output), "cost": r.cost}
        for r in results
    ]
```

**Usage:**
```python
from tasks import generate_image_task, generate_video_task

# Queue image generation
result = generate_image_task.delay("a beautiful sunset")

# Check status
if result.ready():
    print(result.get())

# Queue video generation
video_result = generate_video_task.delay("ocean waves at sunset")
```

---

### Redis Queue (RQ)

```python
# worker.py
from redis import Redis
from rq import Queue, Worker
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

redis_conn = Redis()
queue = Queue(connection=redis_conn)
manager = AIPipelineManager()


def generate_image(prompt: str, model: str = "flux_dev"):
    result = manager.generate_image(prompt=prompt, model=model)
    return {"output_path": result.output_path, "cost": result.cost}


def generate_video(prompt: str):
    result = manager.create_video(prompt=prompt)
    return {"output_path": result.output_path, "cost": result.cost}


if __name__ == '__main__':
    worker = Worker([queue], connection=redis_conn)
    worker.work()
```

```python
# client.py
from redis import Redis
from rq import Queue
from worker import generate_image, generate_video

redis_conn = Redis()
queue = Queue(connection=redis_conn)

# Queue jobs
job1 = queue.enqueue(generate_image, "sunset over mountains")
job2 = queue.enqueue(generate_video, "flowing river")

# Check results
print(job1.get_status())
print(job1.result)
```

---

## Cloud Functions

### AWS Lambda

```python
# lambda_function.py
import json
import boto3
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

s3 = boto3.client('s3')
manager = AIPipelineManager()


def lambda_handler(event, context):
    body = json.loads(event['body'])
    prompt = body.get('prompt')
    model = body.get('model', 'flux_schnell')  # Use fast model for Lambda

    if not prompt:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Prompt required'})
        }

    try:
        result = manager.generate_image(prompt=prompt, model=model)

        # Upload to S3
        bucket = 'your-output-bucket'
        key = f"generated/{result.output_path.split('/')[-1]}"

        s3.upload_file(result.output_path, bucket, key)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                's3_url': f"s3://{bucket}/{key}",
                'cost': result.cost
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

### Google Cloud Function

```python
# main.py
import functions_framework
from google.cloud import storage
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()
storage_client = storage.Client()


@functions_framework.http
def generate_content(request):
    request_json = request.get_json()

    prompt = request_json.get('prompt')
    if not prompt:
        return {'error': 'Prompt required'}, 400

    try:
        result = manager.generate_image(
            prompt=prompt,
            model=request_json.get('model', 'flux_schnell')
        )

        # Upload to GCS
        bucket = storage_client.bucket('your-bucket')
        blob = bucket.blob(f"generated/{result.output_path.split('/')[-1]}")
        blob.upload_from_filename(result.output_path)

        return {
            'success': True,
            'gcs_url': f"gs://your-bucket/generated/{blob.name}",
            'cost': result.cost
        }
    except Exception as e:
        return {'error': str(e)}, 500
```

---

## Webhooks

### Incoming Webhook Handler

```python
import os
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)
manager = AIPipelineManager()

# Load secret from environment variable (never hardcode secrets)
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")
if not WEBHOOK_SECRET:
    raise ValueError("WEBHOOK_SECRET environment variable must be set")


def verify_signature(payload: bytes, signature: str) -> bool:
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


@app.route('/webhook/generate', methods=['POST'])
def webhook_generate():
    # Verify signature
    signature = request.headers.get('X-Signature')
    if not verify_signature(request.data, signature):
        return {'error': 'Invalid signature'}, 401

    data = request.json

    # Process webhook
    result = manager.generate_image(
        prompt=data['prompt'],
        model=data.get('model', 'flux_dev')
    )

    # Send callback if provided
    if data.get('callback_url'):
        import requests
        requests.post(data['callback_url'], json={
            'status': 'completed',
            'output_path': result.output_path
        })

    return {'status': 'processed'}
```

### Outgoing Webhook

```python
import requests
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()


def generate_with_callback(prompt: str, callback_url: str):
    """Generate content and notify via webhook."""
    try:
        result = manager.generate_image(prompt=prompt)

        # Send success callback
        requests.post(callback_url, json={
            'status': 'success',
            'output_path': result.output_path,
            'cost': result.cost
        })
    except Exception as e:
        # Send failure callback
        requests.post(callback_url, json={
            'status': 'failed',
            'error': str(e)
        })
```

---

## Scheduled Jobs

### APScheduler

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager
from datetime import datetime

scheduler = BlockingScheduler()
manager = AIPipelineManager()


@scheduler.scheduled_job('cron', hour=6)
def daily_content_generation():
    """Generate daily content at 6 AM."""
    topics = ["sunrise", "motivation", "nature"]

    for topic in topics:
        prompt = f"{topic} of the day, inspiring, beautiful"
        result = manager.generate_image(prompt=prompt, model="flux_schnell")
        print(f"Generated: {result.output_path}")


@scheduler.scheduled_job('interval', hours=1)
def hourly_batch():
    """Run batch processing every hour."""
    # Check for pending jobs in database/queue
    pending_jobs = get_pending_jobs()  # Your implementation

    for job in pending_jobs:
        result = manager.generate_image(prompt=job['prompt'])
        mark_job_complete(job['id'], result.output_path)


if __name__ == '__main__':
    scheduler.start()
```

---

## Database Integration

### SQLAlchemy

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///generations.db')
Session = sessionmaker(bind=engine)


class Generation(Base):
    __tablename__ = 'generations'

    id = Column(Integer, primary_key=True)
    prompt = Column(String)
    model = Column(String)
    output_path = Column(String)
    cost = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)


def generate_and_store(prompt: str, model: str = "flux_dev"):
    """Generate image and store in database."""
    result = manager.generate_image(prompt=prompt, model=model)

    session = Session()
    generation = Generation(
        prompt=prompt,
        model=model,
        output_path=result.output_path,
        cost=result.cost
    )
    session.add(generation)
    session.commit()

    return generation


def get_recent_generations(limit: int = 10):
    """Get recent generations from database."""
    session = Session()
    return session.query(Generation)\
        .order_by(Generation.created_at.desc())\
        .limit(limit)\
        .all()
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Install package
RUN pip install -e .

# Create output directory
RUN mkdir -p output

# Run application
CMD ["python", "app.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FAL_KEY=${FAL_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./output:/app/output
    restart: unless-stopped

  worker:
    build: .
    command: celery -A tasks worker --loglevel=info
    environment:
      - FAL_KEY=${FAL_KEY}
    depends_on:
      - redis

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```
