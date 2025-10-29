# Quick Start Guide for MPSA

Get up and running with Amazon Market Sentiment Analysis in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- 10 GB free disk space (for models and data)
- (Optional) Git for cloning the repository

## Option 1: Quick Start with Streamlit UI (Recommended for Beginners)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd mpsa

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Download Required Data

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Step 4: Run the Application

```bash
streamlit run main.py
```

The application will open automatically in your browser at `http://localhost:8501`

## Option 2: REST API (For Developers)

### Step 1-3: Same as Above

Follow steps 1-3 from Option 1

### Step 4: Start the API Server

```bash
python api_server.py
```

The API will be available at `http://localhost:8000`

### Step 5: Test the API

Visit `http://localhost:8000/docs` for interactive API documentation.

### Example: Analyze Sentiment

```bash
curl -X POST "http://localhost:8000/sentiment/single" \
  -H "Content-Type: application/json" \
  -d '{"text": "This product is amazing!"}'
```

### Example: Python Client

```python
import requests

response = requests.post(
    "http://localhost:8000/sentiment/single",
    json={"text": "Excellent quality and fast delivery!"}
)
print(response.json())
```

## Option 3: Docker (Easiest)

### Step 1: Install Docker

Download and install from https://www.docker.com/products/docker-desktop

### Step 2: Run with Docker Compose

```bash
# Clone the repository
git clone <repository-url>
cd mpsa

# Start services
docker-compose up
```

### Step 3: Access the Application

- **Streamlit UI**: http://localhost:8501
- **REST API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Redis Cache**: localhost:6379 (internal)

To stop: Press `Ctrl+C`

## Quick API Examples

### 1. Single Sentiment Analysis

```python
import requests

url = "http://localhost:8000/sentiment/single"
response = requests.post(
    url,
    json={"text": "I love this product!"}
)
print(response.json())
```

**Response:**
```json
{
    "text": "I love this product!",
    "sentiment": "positive",
    "confidence": 0.98,
    "probabilities": {
        "positive": 0.98,
        "negative": 0.01,
        "neutral": 0.01
    }
}
```

### 2. Batch Sentiment Analysis

```python
url = "http://localhost:8000/sentiment/batch"
response = requests.post(
    url,
    json={
        "texts": [
            "Great product!",
            "Not good.",
            "It's okay."
        ]
    }
)
print(response.json())
```

### 3. Topic Modeling

```python
url = "http://localhost:8000/topics/model"
response = requests.post(
    url,
    json={
        "documents": [
            "Battery life is excellent",
            "Screen quality is amazing",
            "Shipping was fast",
            "Great customer support"
        ],
        "n_topics": 2
    }
)
print(response.json())
```

### 4. Combined Analysis

```python
url = "http://localhost:8000/analyze/batch-with-topics"
response = requests.post(
    url,
    json={
        "texts": ["Your reviews here..."],
        "n_topics": 3
    }
)
print(response.json())
```

## Using the Streamlit Dashboard

### Main Features

1. **Review Analysis Tab**
   - Enter competitor ASIN
   - Set number of reviews to analyze
   - View real-time sentiment distribution

2. **Topic Analysis Tab**
   - Extract key topics from reviews
   - View topic keywords
   - Analyze topic prevalence

3. **Competitive Analysis Tab**
   - Compare multiple competitors
   - View sentiment trends
   - Generate insights

4. **Troubleshooting Sidebar**
   - Verify model loading
   - Check configuration
   - View system information

## Common Tasks

### Analyze Competitor Reviews

```python
from src.data_acquisition.amazon_scraper_amzpy import AmazonScraperAmzPy
from src.nlp_analysis.sentiment_analyzer import FinBertSentimentAnalyzer

# Scrape reviews
scraper = AmazonScraperAmzPy()
reviews = scraper.get_reviews("ASIN_HERE", max_reviews=100)

# Analyze sentiment
analyzer = FinBertSentimentAnalyzer()
results = analyzer.analyze_batch(reviews)

# Get sentiment distribution
positive = sum(1 for r in results if r['sentiment'] == 'positive')
print(f"Positive reviews: {positive}/{len(results)}")
```

### Extract Topics

```python
from src.nlp_analysis.topic_modeler import TopicModeler
import pandas as pd

# Load reviews
df = pd.read_csv('reviews.csv')
texts = df['review_text'].tolist()

# Model topics
modeler = TopicModeler(n_topics=5)
modeler.fit(texts)
topics = modeler.get_topics()

# Print topics
for topic in topics:
    print(f"Keywords: {', '.join(topic['keywords'][:5])}")
```

## Troubleshooting

### Issue: Module not found error
**Solution**: Ensure you're in the project directory and virtual environment is activated
```bash
cd mpsa
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Issue: Port already in use
**Solution**: Use a different port
```bash
streamlit run main.py --server.port 8502
# or
python api_server.py --port 8001
```

### Issue: NLTK data not found
**Solution**: Download NLTK data
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Issue: Out of memory
**Solution**: Process data in smaller batches
```python
batch_size = 16
for i in range(0, len(texts), batch_size):
    batch = texts[i:i + batch_size]
    results = analyzer.analyze_batch(batch)
```

### Issue: Model download fails
**Solution**: Pre-download the model manually
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_name = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
```

## Next Steps

### 1. Read the Documentation

- **README.md** - Complete project documentation
- **DEVELOPMENT.md** - Development setup and guidelines
- **API_GUIDE.md** - Detailed API reference

### 2. Run Examples

```bash
python examples/api_usage.py
```

### 3. Run Tests

```bash
pytest tests/ -v
```

### 4. Explore the Code

Key files to understand:
- `src/nlp_analysis/sentiment_analyzer.py` - Sentiment analysis engine
- `src/nlp_analysis/topic_modeler.py` - Topic extraction
- `src/api/main.py` - REST API endpoints
- `main.py` - Streamlit web interface

## Configuration

### Basic Configuration

Create a `.env` file (copy from `.env.example`):

```ini
LOG_LEVEL=INFO
MAX_REVIEWS=100
FINBERT_MODEL=ProsusAI/finbert
```

### Advanced Configuration

Edit `src/utils/config.py` for more options:
- Scraping parameters
- Analysis settings
- Logging configuration
- Platform-specific settings

## Performance Tips

1. **Use GPU if available**
   - NVIDIA GPU with CUDA 11.8+
   - Approximately 10-20x faster than CPU

2. **Process in batches**
   - Larger batches are more efficient
   - Default: 32 reviews per batch

3. **Cache results**
   - Models are cached automatically
   - Results are stored in memory during session

4. **Use Docker for production**
   - Consistent environment
   - Easy scaling with docker-compose

## API Documentation

Access interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Support

- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub discussions
- **Documentation**: See README.md and DEVELOPMENT.md

## Next: Production Deployment

For deploying to production:
1. Review PERFORMANCE.md for optimization
2. Check DEVELOPMENT.md for deployment options
3. Use Docker containers for consistency
4. Set up monitoring and logging
5. Configure environment variables

---

**Ready?** Start with:
```bash
streamlit run main.py
```

**Questions?** Check README.md or DEVELOPMENT.md