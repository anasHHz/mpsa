# REST API Reference

Complete reference for the MPSA REST API endpoints, models, and usage patterns.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API has no authentication. For production deployment, consider adding:
- API keys
- JWT tokens
- OAuth2

## Response Format

All responses are in JSON format.

### Success Response

```json
{
  "status": "success",
  "data": {...}
}
```

### Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 400 | Bad Request - Invalid input |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |
| 503 | Service Unavailable - Model not loaded |

## Endpoints

### Health Check

#### GET /health

Check if the API is running and models are loaded.

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "MPSA API is running"
}
```

---

## Sentiment Analysis Endpoints

### Single Sentiment Analysis

#### POST /sentiment/single

Analyze sentiment of a single text.

**Request:**
```bash
curl -X POST "http://localhost:8000/sentiment/single" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This product is amazing!"
  }'
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | string | Yes | Text to analyze (1+ characters) |

**Response:**
```json
{
  "text": "This product is amazing!",
  "sentiment": "positive",
  "confidence": 0.98,
  "probabilities": {
    "positive": 0.98,
    "negative": 0.01,
    "neutral": 0.01
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| text | string | The analyzed text |
| sentiment | string | Sentiment classification: "positive", "negative", or "neutral" |
| confidence | float | Confidence score (0.0 to 1.0) |
| probabilities | object | Probability distribution for each sentiment |

**Error Examples:**

Empty text:
```bash
curl -X POST "http://localhost:8000/sentiment/single" \
  -H "Content-Type: application/json" \
  -d '{"text": ""}'
```

Response (400):
```json
{
  "detail": "Text cannot be empty"
}
```

---

### Batch Sentiment Analysis

#### POST /sentiment/batch

Analyze sentiment of multiple texts simultaneously.

**Request:**
```bash
curl -X POST "http://localhost:8000/sentiment/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Great product!",
      "Terrible quality.",
      "It'\''s okay."
    ]
  }'
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| texts | array | Yes | List of texts (minimum 1 item) |

**Response:**
```json
{
  "count": 3,
  "results": [
    {
      "text": "Great product!",
      "sentiment": "positive",
      "confidence": 0.95,
      "probabilities": {
        "positive": 0.95,
        "negative": 0.03,
        "neutral": 0.02
      }
    },
    {
      "text": "Terrible quality.",
      "sentiment": "negative",
      "confidence": 0.92,
      "probabilities": {
        "positive": 0.02,
        "negative": 0.92,
        "neutral": 0.06
      }
    },
    {
      "text": "It's okay.",
      "sentiment": "neutral",
      "confidence": 0.87,
      "probabilities": {
        "positive": 0.25,
        "negative": 0.15,
        "neutral": 0.60
      }
    }
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| count | integer | Number of texts analyzed |
| results | array | Array of sentiment results (same as single analysis) |

**Parameters:**

- **Optimal batch size**: 32-64 texts (GPU dependent)
- **Maximum batch size**: Limited by available memory
- **Processing time**: ~0.3-0.5 seconds per review with GPU

**Example: Large Batch**
```python
import requests

texts = [f"Review {i}: This is a great product!" for i in range(1000)]

response = requests.post(
    "http://localhost:8000/sentiment/batch",
    json={"texts": texts}
)

results = response.json()
print(f"Analyzed {results['count']} reviews")
```

---

## Topic Modeling Endpoints

### Extract Topics

#### POST /topics/model

Extract topics from documents using LDA.

**Request:**
```bash
curl -X POST "http://localhost:8000/topics/model" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "Battery life is excellent",
      "Screen display is amazing",
      "Fast shipping and good service",
      "Battery drains quickly",
      "Screen has dead pixels"
    ],
    "n_topics": 2
  }'
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| documents | array | Yes | List of documents (minimum 3) |
| n_topics | integer | No | Number of topics (2-20, default: 5) |

**Response:**
```json
{
  "n_documents": 5,
  "n_topics": 2,
  "topics": [
    {
      "topic_id": 0,
      "keywords": ["battery", "life", "excellent", "drains", "quickly"]
    },
    {
      "topic_id": 1,
      "keywords": ["screen", "display", "amazing", "pixels", "dead"]
    }
  ],
  "document_topics": [
    {
      "document": "Battery life is excellent",
      "topics": {
        "topic_0": 0.85,
        "topic_1": 0.15
      }
    },
    {
      "document": "Screen display is amazing",
      "topics": {
        "topic_0": 0.20,
        "topic_1": 0.80
      }
    }
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| n_documents | integer | Number of documents processed |
| n_topics | integer | Number of topics extracted |
| topics | array | Topic information with keywords |
| document_topics | array | Topic distribution for each document |

**Parameters:**

- **Minimum documents**: 3
- **Optimal document count**: 100+
- **n_topics range**: 2-20
- **Processing time**: ~1-5 seconds for 1000 documents

---

## Combined Analysis

### Batch Analysis with Topics

#### POST /analyze/batch-with-topics

Perform sentiment analysis and topic modeling simultaneously.

**Request:**
```bash
curl -X POST "http://localhost:8000/analyze/batch-with-topics" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Great battery and screen!",
      "Fast shipping but poor quality.",
      "Excellent value for money."
    ],
    "n_topics": 2
  }'
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| n_topics | integer | 3 | Number of topics to extract |

**Request Body:**

| Field | Type | Description |
|-------|------|-------------|
| texts | array | Reviews to analyze |

**Response:**
```json
{
  "n_documents": 3,
  "n_topics": 2,
  "extracted_topics": [
    {
      "topic_id": 0,
      "keywords": ["battery", "screen", "quality"]
    },
    {
      "topic_id": 1,
      "keywords": ["shipping", "value", "money"]
    }
  ],
  "results": [
    {
      "index": 0,
      "text": "Great battery and screen!",
      "sentiment": "positive",
      "confidence": 0.96,
      "probabilities": {...},
      "topics": {
        "topic_0": 0.75,
        "topic_1": 0.25
      }
    }
  ],
  "sentiment_summary": {
    "positive": 2,
    "negative": 0,
    "neutral": 1,
    "average_confidence": 0.92
  }
}
```

---

## Data Models

### SentimentRequest

```python
{
  "text": "string"  # 1+ characters
}
```

### SentimentResponse

```python
{
  "text": "string",
  "sentiment": "positive" | "negative" | "neutral",
  "confidence": float,  # 0.0-1.0
  "probabilities": {
    "positive": float,
    "negative": float,
    "neutral": float
  }
}
```

### BatchSentimentRequest

```python
{
  "texts": ["string"]  # 1+ items
}
```

### BatchSentimentResponse

```python
{
  "count": integer,
  "results": [SentimentResponse]
}
```

### TopicModelingRequest

```python
{
  "documents": ["string"],  # 3+ items
  "n_topics": integer  # 2-20
}
```

### TopicResponse

```python
{
  "topic_id": integer,
  "keywords": ["string"]
}
```

### TopicModelingResponse

```python
{
  "n_documents": integer,
  "n_topics": integer,
  "topics": [TopicResponse],
  "document_topics": [
    {
      "document": "string",
      "topics": {
        "topic_0": float,
        "topic_1": float,
        ...
      }
    }
  ]
}
```

---

## Code Examples

### Python with Requests

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Single sentiment
response = requests.post(
    f"{BASE_URL}/sentiment/single",
    json={"text": "Amazing product!"}
)
print(response.json())

# 2. Batch sentiment
response = requests.post(
    f"{BASE_URL}/sentiment/batch",
    json={"texts": ["Good", "Bad", "Okay"]}
)
print(response.json())

# 3. Topic modeling
response = requests.post(
    f"{BASE_URL}/topics/model",
    json={
        "documents": ["text1", "text2", "text3"],
        "n_topics": 2
    }
)
print(response.json())
```

### Python with HTTPx (Async)

```python
import httpx
import asyncio

async def analyze_sentiment(text):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/sentiment/single",
            json={"text": text}
        )
        return response.json()

asyncio.run(analyze_sentiment("Great product!"))
```

### JavaScript/Node.js

```javascript
// Using fetch API
async function analyzeSentiment(text) {
  const response = await fetch('http://localhost:8000/sentiment/single', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text: text })
  });
  
  return await response.json();
}

// Using axios
const axios = require('axios');

axios.post('http://localhost:8000/sentiment/single', {
  text: 'Great product!'
}).then(response => console.log(response.data));
```

### cURL Examples

```bash
# Single sentiment
curl -X POST "http://localhost:8000/sentiment/single" \
  -H "Content-Type: application/json" \
  -d '{"text": "Amazing!"}'

# Batch sentiment
curl -X POST "http://localhost:8000/sentiment/batch" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Good", "Bad"]}'

# Topics
curl -X POST "http://localhost:8000/topics/model" \
  -H "Content-Type: application/json" \
  -d '{"documents": ["doc1", "doc2", "doc3"], "n_topics": 2}'

# Health check
curl http://localhost:8000/health

# Get Swagger docs
curl http://localhost:8000/openapi.json
```

---

## Rate Limiting (Future)

Currently, no rate limiting is implemented. For production:

```python
# Example: 100 requests per minute per IP
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/sentiment/single")
@limiter.limit("100/minute")
async def analyze_sentiment(request):
    ...
```

---

## Error Handling

### Common Errors

| Error | Status | Solution |
|-------|--------|----------|
| "text cannot be empty" | 400 | Provide non-empty text |
| "texts list is empty" | 400 | Provide at least 1 text |
| "n_topics must be between 2 and 20" | 400 | Adjust n_topics |
| "Model not loaded" | 503 | Restart API server |

### Retry Logic

```python
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)

response = session.post("http://localhost:8000/sentiment/single", ...)
```

---

## Performance Guidelines

### Throughput

| Operation | GPU (RTX 2080) | CPU (i7-8700K) |
|-----------|---|---|
| Single sentiment | ~100/sec | ~2/sec |
| Batch 32 sentiments | ~1000/sec | ~20/sec |
| Topic modeling (100 docs) | ~10-20 sec | ~30-40 sec |

### Optimization Tips

1. **Use batch endpoints** for multiple texts
2. **Reuse connections** with connection pooling
3. **Enable compression** with gzip
4. **Cache results** for duplicate requests
5. **Use GPU** if available (10-20x faster)

---

## Monitoring & Logging

The API logs all requests and errors. Check logs with:

```bash
docker-compose logs -f mpsa
```

Monitor with Prometheus metrics (if enabled):

```
http://localhost:8001/metrics
```

---

## Deployment

### Docker

```bash
docker-compose up
```

### Kubernetes

```bash
kubectl apply -f k8s-deployment.yaml
```

### Traditional Server

```bash
python api_server.py
```

---

## OpenAPI/Swagger

Access interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Support & Issues

- Check existing issues: https://github.com/yourusername/mpsa/issues
- Request features: https://github.com/yourusername/mpsa/discussions
- View documentation: README.md, DEVELOPMENT.md, API_REFERENCE.md