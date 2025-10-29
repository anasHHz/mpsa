# Performance Tuning Guide

This guide provides recommendations for optimizing the performance of the MPSA application for different scenarios.

## Table of Contents

- [Hardware Requirements](#hardware-requirements)
- [Model Optimization](#model-optimization)
- [Batch Processing](#batch-processing)
- [Caching Strategies](#caching-strategies)
- [Scaling Approaches](#scaling-approaches)
- [Monitoring and Profiling](#monitoring-and-profiling)
- [Benchmarks](#benchmarks)

## Hardware Requirements

### Minimum Requirements

- **CPU**: Dual-core processor (2.0 GHz+)
- **RAM**: 8 GB
- **Storage**: 10 GB (5 GB for models + 5 GB for data)
- **OS**: Linux, macOS, or Windows

### Recommended Requirements

- **CPU**: Quad-core processor (2.5 GHz+)
- **RAM**: 16 GB
- **Storage**: 20 GB SSD
- **GPU**: NVIDIA GPU with 4 GB+ VRAM (CUDA 11.8+)

### High-Performance Requirements

- **CPU**: 8+ cores (3.5 GHz+)
- **RAM**: 32 GB+
- **Storage**: 50 GB SSD
- **GPU**: NVIDIA GPU with 8 GB+ VRAM
- **Network**: 1 Gbps+ connection

## Model Optimization

### 1. GPU Acceleration

**Enable CUDA for faster processing:**

```python
import torch
from src.nlp_analysis.sentiment_analyzer import FinBertSentimentAnalyzer

# Check GPU availability
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))

# Analyzer automatically uses GPU if available
analyzer = FinBertSentimentAnalyzer()
```

**Performance Improvement:**
- Single sentiment: ~5-10x faster
- Batch processing: ~10-20x faster

### 2. Model Quantization

Reduce model size while maintaining accuracy:

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

# Quantize to INT8 (50% size reduction)
from torch.quantization import quantize_dynamic
quantized_model = quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)

# Quantized model: ~175MB instead of ~400MB
# Performance impact: -5-10% accuracy for +30-50% speed
```

### 3. Model Distillation

Create smaller, faster models from larger ones:

```python
# Using distilbert (faster, smaller)
from transformers import AutoModelForSequenceClassification

# This would require custom training
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased"
)
# ~40% smaller, ~50% faster, ~2-3% accuracy loss
```

## Batch Processing

### 1. Optimal Batch Sizes

Adjust batch sizes based on available hardware:

```python
from src.nlp_analysis.sentiment_analyzer import FinBertSentimentAnalyzer

analyzer = FinBertSentimentAnalyzer()

texts = [...]  # Your texts

# Small GPU (4GB): batch_size = 16
# Medium GPU (8GB): batch_size = 32
# Large GPU (12GB+): batch_size = 64
# CPU: batch_size = 8

# Process in batches
batch_size = 32
for i in range(0, len(texts), batch_size):
    batch = texts[i:i + batch_size]
    results = analyzer.analyze_batch(batch)
```

### 2. Streaming Processing

Process large datasets without loading everything in memory:

```python
import pandas as pd
from src.nlp_analysis.sentiment_analyzer import FinBertSentimentAnalyzer

analyzer = FinBertSentimentAnalyzer()

# Read in chunks
chunk_size = 1000
for chunk in pd.read_csv('large_reviews.csv', chunksize=chunk_size):
    texts = chunk['review_text'].tolist()
    results = analyzer.analyze_batch(texts)
    # Process/save results
```

### 3. Parallel Processing

Use multiple processes for data preprocessing:

```python
from multiprocessing import Pool
import numpy as np

def preprocess_text(text):
    # Your preprocessing logic
    return cleaned_text

# Use all available cores
with Pool() as pool:
    cleaned_texts = pool.map(preprocess_text, texts)
```

## Caching Strategies

### 1. Streamlit Cache

Already implemented in main.py:

```python
import streamlit as st
from src.nlp_analysis.sentiment_analyzer import FinBertSentimentAnalyzer

@st.cache_resource
def load_models():
    return FinBertSentimentAnalyzer()

analyzer = load_models()  # Loaded once, reused across runs
```

**Benefits:**
- Model loaded once per session
- Significant reduction in startup time
- Memory usage reduced

### 2. Redis Caching

For API server distributed caching:

```python
import redis
from src.nlp_analysis.sentiment_analyzer import FinBertSentimentAnalyzer

# Connect to Redis
cache = redis.Redis(host='localhost', port=6379, db=0)

def get_sentiment_cached(text):
    # Check cache
    cached_result = cache.get(text)
    if cached_result:
        return json.loads(cached_result)
    
    # Analyze if not cached
    analyzer = FinBertSentimentAnalyzer()
    result = analyzer.analyze_single(text)
    
    # Store in cache (expire after 7 days)
    cache.setex(text, 7*24*3600, json.dumps(result))
    return result
```

**Configuration in docker-compose:**
- Redis service already included
- Accessible at `redis:6379`

### 3. Result Caching

Cache analysis results for repeat requests:

```python
import hashlib
from functools import lru_cache

@lru_cache(maxsize=10000)
def analyze_cached(text_hash):
    # Implementation
    pass

# Usage
text_hash = hashlib.md5(text.encode()).hexdigest()
result = analyze_cached(text_hash)
```

## Scaling Approaches

### 1. Horizontal Scaling (Multiple Instances)

**Docker Compose with load balancing:**

```yaml
version: '3.8'
services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf

  api-1:
    build: .
    environment:
      - PORT=8001

  api-2:
    build: .
    environment:
      - PORT=8002

  api-3:
    build: .
    environment:
      - PORT=8003
```

### 2. Kubernetes Deployment

**Horizontal Pod Autoscaling:**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mpsa-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mpsa-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 3. Async Processing

**Background job processing for long operations:**

```python
from celery import Celery

app = Celery('mpsa')

@app.task
def analyze_reviews_async(review_ids):
    from src.nlp_analysis.sentiment_analyzer import FinBertSentimentAnalyzer
    
    analyzer = FinBertSentimentAnalyzer()
    # Perform analysis
    # Store results in database
    return results
```

## Monitoring and Profiling

### 1. Performance Profiling

**Using cProfile:**

```python
import cProfile
import pstats
from src.nlp_analysis.sentiment_analyzer import FinBertSentimentAnalyzer

def profile_sentiment_analysis():
    analyzer = FinBertSentimentAnalyzer()
    texts = ["Sample review"] * 100
    analyzer.analyze_batch(texts)

profiler = cProfile.Profile()
profiler.enable()
profile_sentiment_analysis()
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

### 2. Memory Profiling

**Using memory_profiler:**

```bash
pip install memory-profiler
python -m memory_profiler main.py
```

**Code decorators:**

```python
from memory_profiler import profile

@profile
def analyze_large_batch(texts):
    analyzer = FinBertSentimentAnalyzer()
    return analyzer.analyze_batch(texts)
```

### 3. Metrics Collection

**With Prometheus:**

```python
from prometheus_client import Counter, Histogram, start_http_server
import time

# Define metrics
sentiment_requests = Counter(
    'sentiment_requests_total',
    'Total sentiment analysis requests'
)
sentiment_duration = Histogram(
    'sentiment_duration_seconds',
    'Sentiment analysis duration'
)

# Use metrics
@sentiment_duration.time()
def analyze_with_metrics(text):
    sentiment_requests.inc()
    analyzer = FinBertSentimentAnalyzer()
    return analyzer.analyze_single(text)

# Start metrics server
start_http_server(8000)
```

## Benchmarks

### Single Review Analysis

| Hardware | Model | Time (ms) | GPU |
|----------|-------|-----------|-----|
| CPU (i7-8700K) | FinBERT | 450-550 | ❌ |
| GPU (RTX 2080) | FinBERT | 50-70 | ✅ |
| GPU (RTX 3090) | FinBERT | 20-30 | ✅ |

### Batch Analysis (100 reviews)

| Hardware | Batch Size | Time (sec) | TPS |
|----------|-----------|-----------|-----|
| CPU | 8 | 45-55 | 1.8-2.2 |
| GPU (RTX 2080) | 32 | 3-4 | 25-33 |
| GPU (RTX 3090) | 64 | 1-1.5 | 67-100 |

### Topic Modeling (1000 documents)

| n_topics | CPU Time (sec) | GPU Time (sec) | Speedup |
|----------|---|---|---------|
| 2 | 2-3 | 1.5-2 | 1.2-2x |
| 5 | 4-5 | 2-3 | 1.5-2.5x |
| 10 | 8-10 | 3-5 | 2-3x |

## Optimization Checklist

- [ ] Enable GPU acceleration if available
- [ ] Use batch processing for multiple reviews
- [ ] Implement caching for repeated requests
- [ ] Profile code to identify bottlenecks
- [ ] Optimize database queries
- [ ] Use connection pooling for databases
- [ ] Implement request rate limiting
- [ ] Use CDN for static assets
- [ ] Enable gzip compression
- [ ] Implement async processing for long operations
- [ ] Monitor resource usage
- [ ] Set up alerts for performance degradation
- [ ] Regular performance testing

## Quick Optimization Script

```python
# quick_optimize.py
import torch
import time
from src.nlp_analysis.sentiment_analyzer import FinBertSentimentAnalyzer

def benchmark():
    analyzer = FinBertSentimentAnalyzer()
    texts = ["This is a sample review about the product."] * 100
    
    start = time.time()
    results = analyzer.analyze_batch(texts)
    duration = time.time() - start
    
    print(f"GPU Available: {torch.cuda.is_available()}")
    print(f"Batch Size: 100")
    print(f"Duration: {duration:.2f}s")
    print(f"Throughput: {100/duration:.0f} reviews/sec")

if __name__ == "__main__":
    benchmark()
```

## Further Resources

- [PyTorch Performance Tuning](https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html)
- [HuggingFace Optimization](https://huggingface.co/docs/transformers/performance)
- [Python Performance Profiling](https://docs.python.org/3/library/profile.html)
- [Kubernetes Optimization](https://kubernetes.io/docs/concepts/configuration/overview/)