# Development Guide for MPSA

This guide provides instructions for setting up the development environment and contributing to the Amazon Market Sentiment Analysis project.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Docker Development](#docker-development)
- [API Development](#api-development)
- [Code Quality](#code-quality)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Development Environment Setup

### Prerequisites

- Python 3.9+
- Git
- Docker (optional)
- Virtual environment manager (venv or conda)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mpsa
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

5. **Set up environment variables** (optional)
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Project Structure

```
mpsa/
├── src/
│   ├── api/                    # REST API using FastAPI
│   ├── data_acquisition/       # Web scraping modules
│   ├── nlp_analysis/          # NLP models (sentiment, topics)
│   ├── utils/                 # Utilities and configuration
│   └── visualization/         # Dashboard and reporting
├── tests/                      # Unit tests
├── data/
│   ├── raw/                   # Raw scraped data
│   ├── processed/             # Processed data
│   └── results/               # Analysis results
├── docs/                      # Documentation
├── main.py                    # Streamlit application
├── api_server.py              # FastAPI server
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker container definition
├── docker-compose.yml         # Multi-container setup
├── pytest.ini                 # Pytest configuration
└── README.md                  # Project README
```

## Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run tests with coverage
```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

### Run specific test file
```bash
pytest tests/test_sentiment_analyzer.py -v
```

### Run tests with markers
```bash
# Unit tests only
pytest tests/ -m unit

# NLP tests only
pytest tests/ -m nlp

# Skip slow tests
pytest tests/ -m "not slow"
```

### Run tests in parallel
```bash
pytest tests/ -n auto
```

## Docker Development

### Build Docker image
```bash
docker build -t mpsa:latest .
```

### Run with Docker Compose
```bash
docker-compose up -d
```

### Build and run with Docker Compose
```bash
docker-compose up --build
```

### Access the application
- Streamlit: http://localhost:8501
- API: http://localhost:8000

### View logs
```bash
docker-compose logs -f mpsa
```

### Stop containers
```bash
docker-compose down
```

### Remove volumes (clean data)
```bash
docker-compose down -v
```

## API Development

### Running the FastAPI server

1. **Using uvicorn directly**
   ```bash
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Using Python script**
   ```bash
   python api_server.py
   ```

### API Documentation

Once the server is running, access the interactive documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Testing API endpoints

Using curl:
```bash
# Single sentiment analysis
curl -X POST "http://localhost:8000/sentiment/single" \
  -H "Content-Type: application/json" \
  -d '{"text": "This product is amazing!"}'

# Batch sentiment analysis
curl -X POST "http://localhost:8000/sentiment/batch" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Great product!", "Terrible quality.", "It'\''s okay."]}'

# Topic modeling
curl -X POST "http://localhost:8000/topics/model" \
  -H "Content-Type: application/json" \
  -d '{"documents": ["Product quality is excellent", "Shipping was fast", "Customer service helped me"], "n_topics": 2}'
```

Using Python requests:
```python
import requests

# Single sentiment
response = requests.post(
    "http://localhost:8000/sentiment/single",
    json={"text": "Amazing product!"}
)
print(response.json())

# Batch sentiment
response = requests.post(
    "http://localhost:8000/sentiment/batch",
    json={"texts": ["Great!", "Bad.", "Okay."]}
)
print(response.json())
```

## Code Quality

### Code formatting

Using Black:
```bash
black src/ tests/
```

### Import sorting

Using isort:
```bash
isort src/ tests/
```

### Linting

Using Flake8:
```bash
flake8 src/ tests/ --max-line-length=120
```

Using Pylint:
```bash
pylint src/
```

### Type checking

Using mypy:
```bash
mypy src/
```

### Pre-commit hooks

Set up pre-commit hooks to run checks automatically:
```bash
pip install pre-commit
pre-commit install
```

## Deployment

### Local Streamlit deployment
```bash
streamlit run main.py --server.port 8501
```

### Docker deployment
```bash
# Build image
docker build -t mpsa:v1.0 .

# Run container
docker run -p 8501:8501 -v $(pwd)/data:/app/data mpsa:v1.0
```

### Kubernetes deployment (if applicable)
```bash
kubectl apply -f k8s-deployment.yaml
```

### Production considerations

1. **Environment variables**: Use `.env` files or secrets management
2. **Logging**: Configure proper logging levels for production
3. **Error handling**: Enable comprehensive error tracking
4. **Performance**: Monitor resource usage and optimize as needed
5. **Security**: Implement rate limiting and input validation
6. **Caching**: Use Redis for caching expensive operations

## Troubleshooting

### Issue: NLTK data not found
**Solution**: Download required NLTK data
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Issue: CUDA/GPU not detected
**Solution**: Check PyTorch installation
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

### Issue: Module import errors
**Solution**: Ensure PYTHONPATH includes project root
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/mpsa"
```

### Issue: Docker build fails
**Solution**: Clean and rebuild
```bash
docker-compose down -v
docker-compose build --no-cache
```

### Issue: Tests fail on import
**Solution**: Install package in development mode
```bash
pip install -e .
```

### Issue: Memory issues with large datasets
**Solution**: Process data in batches and increase system resources
```bash
# In Docker
docker-compose.yml: Add memory limit configurations
```

## Contributing

1. Create a feature branch from `develop`
   ```bash
   git checkout -b feature/your-feature
   ```

2. Make your changes and ensure tests pass
   ```bash
   pytest tests/ -v
   ```

3. Format code
   ```bash
   black src/ tests/
   isort src/ tests/
   ```

4. Commit with descriptive messages
   ```bash
   git commit -m "Add feature: description"
   ```

5. Push and create a Pull Request
   ```bash
   git push origin feature/your-feature
   ```

## Performance Optimization

### Model Caching
Models are cached using Streamlit's `@st.cache_resource` decorator to avoid reloading.

### Batch Processing
Sentiment analysis supports batch processing for better performance on large datasets.

### Multi-core LDA
Topic modeling uses multi-core processing. Adjust in `TopicModeler.fit()`:
```python
n_jobs=-1  # Use all available cores
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [Pytest Documentation](https://docs.pytest.org/)