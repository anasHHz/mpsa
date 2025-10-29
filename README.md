# Amazon Customer Sentiment & Competitive Analysis

A comprehensive business intelligence platform that analyzes Amazon product reviews using advanced NLP techniques to extract customer sentiment, identify market trends, and provide competitive insights.

## 🎯 Project Overview

This tool leverages **FinBERT** (a financial domain BERT model) for accurate sentiment analysis combined with **Topic Modeling** (LDA) to understand customer preferences and pain points. It provides competitive intelligence by analyzing multiple competing products on Amazon and visualizing insights through an interactive Streamlit dashboard.

### Key Features

- **Amazon Data Scraping**: Automated collection of product reviews and metadata using the amzpy library
- **FinBERT Sentiment Analysis**: Deep learning-based sentiment classification with confidence scores
- **Topic Modeling**: LDA-based topic extraction to identify key discussion themes
- **Competitive Analysis**: Side-by-side comparison of competing brands and products
- **Interactive Dashboards**: Real-time visualizations with Plotly
- **Multi-Domain Support**: Analyze products from different Amazon regional domains (US, UK, Germany, France, India)

## 📊 Project Structure

```
mpsa/
├── main.py                          # Streamlit application entry point
├── requirements.txt                 # Project dependencies
├── README.md                        # This file
├── docs/
│   └── BUSINESS_CASE_STUDY.md      # Business use cases and analysis framework
├── data/
│   ├── raw/                         # Raw scraped review data
│   ├── processed/                   # Cleaned and analyzed data
│   └── results/                     # Analysis outputs and reports
├── src/
│   ├── data_acquisition/            # Web scraping modules
│   │   ├── base_scraper.py         # Abstract scraper base class
│   │   ├── amazon_scraper_amzpy.py # Amazon-specific scraper implementation
│   │   └── __init__.py
│   ├── nlp_analysis/                # NLP processing modules
│   │   ├── sentiment_analyzer.py    # Placeholder for FinBERT analyzer
│   │   ├── topic_modeler.py         # LDA topic modeling
│   │   └── __init__.py
│   ├── visualization/               # Dashboard and reporting
│   │   ├── dashboards.py            # Streamlit dashboard components
│   │   ├── reports.py               # Report generation
│   │   └── __init__.py
│   └── utils/                       # Configuration and utilities
│       ├── config.py                # Configuration classes
│       └── __init__.py
└── tests/                           # Unit tests (to be implemented)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Windows/Mac/Linux
- ~2GB RAM minimum
- Internet connection (for model downloads and Amazon access)

### Installation

1. **Clone or download the repository:**

   ```powershell
   cd d:\my_folder\presonal\mpsa
   ```
2. **Create and activate virtual environment:**

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. **Install dependencies:**

   ```powershell
   pip install -r requirements.txt
   ```
4. **Download NLTK data (required for topic modeling):**

   ```powershell
   python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')"
   ```

### Running the Application

1. **Start the Streamlit app:**

   ```powershell
   streamlit run main.py
   ```
2. **Open your browser** to `http://localhost:8501`
3. **Configure analysis parameters** in the sidebar:

   - **Product Search Query**: Enter the product category (e.g., "wireless earbuds", "laptop bags")
   - **Competitor Brands**: List competitor brands to analyze (comma-separated)
   - **Max Reviews per Product**: Number of reviews to collect (10-200)
   - **Amazon Domain**: Select regional domain (India, US, UK, Germany, France)
4. **Click "Run Amazon Analysis"** to start the pipeline

## 📋 Dependencies

| Package             | Version | Purpose                           |
| ------------------- | ------- | --------------------------------- |
| streamlit           | Latest  | Web UI framework                  |
| pandas              | Latest  | Data manipulation                 |
| scikit-learn        | Latest  | Machine learning (LDA)            |
| nltk                | Latest  | NLP preprocessing                 |
| transformers        | Latest  | Hugging Face models (for FinBERT) |
| torch               | Latest  | PyTorch backend                   |
| plotly              | Latest  | Interactive visualizations        |
| amzpy               | Latest  | Amazon scraping                   |
| beautifulsoup4      | Latest  | HTML parsing                      |
| requests            | Latest  | HTTP client                       |
| matplotlib, seaborn | Latest  | Static plotting                   |

## 🔍 Core Modules

### 1. Data Acquisition (`src/data_acquisition/`)

**AmazonScraperAmzPy** (`amazon_scraper_amzpy.py`)

- Searches for products by query
- Retrieves product details and reviews
- Filters by competitor brands
- Formats data into pandas DataFrames
- Implements rate limiting to respect Amazon's terms

**Key Methods:**

```python
scraper = AmazonScraperAmzPy(country_code="in", max_reviews_per_product=100)
reviews_df = scraper.scrape_competitive_products(
    query="wireless earbuds",
    competitor_names=["Sony", "Bose", "JBL"]
)
```

### 2. NLP Analysis (`src/nlp_analysis/`)

**TopicModeler** (`topic_modeler.py`)

- Preprocesses text (lowercasing, stopword removal, lemmatization)
- Fits Latent Dirichlet Allocation (LDA) model
- Extracts top words per topic
- Generates topic distributions for documents

**Key Methods:**

```python
modeler = TopicModeler(n_topics=6)
modeler.fit(review_texts)
topics = modeler.get_topics(n_words=10)  # Get top 10 words per topic
topic_dist = modeler.transform(new_reviews)  # Get topic distribution
```

**FinBertSentimentAnalyzer** (referenced in main.py)

- Uses FinBERT (Financial BERT) for sentiment classification
- Returns sentiment labels (positive/negative/neutral)
- Provides confidence scores for each class
- Optimized for domain-specific sentiment detection

### 3. Visualization (`src/visualization/`)

**BusinessIntelligenceDashboard** (`dashboards.py`)

- Creates sentiment comparison charts
- Generates competitive positioning visualizations
- Displays topic analysis results
- Renders confidence score metrics

**Displays:**

- Sentiment distribution by product (box plots)
- Sentiment composition (pie charts)
- Average sentiment scores (bar charts)
- Competitive positioning (bubble charts)
- Raw data explorer

### 4. Configuration (`src/utils/config.py`)

**ScrapingConfig**

- `RATE_LIMIT_DELAY`: Delay between requests (1.0 seconds)
- `MAX_REVIEWS_PER_SOURCE`: Maximum reviews to process
- `USER_AGENT`: Identification string for requests
- `RESPECT_ROBOTS_TXT`: Honor robots.txt directives

## 📊 Analysis Pipeline

```
1. User Input
   ↓
2. Amazon Data Scraping (amzpy)
   ├─ Search for products by query
   ├─ Filter by competitor brands
   └─ Retrieve reviews and metadata
   ↓
3. Text Preprocessing
   ├─ Lower casing
   ├─ Remove special characters
   ├─ Stopword removal
   └─ Lemmatization
   ↓
4. Sentiment Analysis (FinBERT)
   ├─ Classify sentiment (positive/negative/neutral)
   ├─ Extract confidence scores
   └─ Merge with review data
   ↓
5. Topic Modeling (LDA)
   ├─ Fit LDA model
   ├─ Extract top topics
   └─ Generate topic distributions
   ↓
6. Competitive Analysis
   ├─ Aggregate by product
   ├─ Calculate metrics (avg sentiment, volume, rating)
   └─ Rank competitors
   ↓
7. Visualization & Dashboard Display
```

## 📈 Output Metrics

### Sentiment Analysis Outputs

- `sentiment_score`: Numerical sentiment score
- `sentiment_label`: Classification (positive/negative/neutral)
- `positive`: Confidence score for positive class
- `negative`: Confidence score for negative class
- `neutral`: Confidence score for neutral class

### Competitive Analysis Outputs

| Metric         | Description                                 |
| -------------- | ------------------------------------------- |
| Product        | Product name                                |
| Avg Sentiment  | Average sentiment score across all reviews  |
| Review Volume  | Total number of reviews analyzed            |
| Avg Rating     | Average star rating                         |
| Sentiment Rank | Ranking by sentiment (1 = highest)          |
| Volume Rank    | Ranking by review count (1 = most reviewed) |

### Topic Modeling Outputs

- Topic words: Top N words for each identified topic
- Topic distributions: Probability distribution over topics for each review
- Document-level insights: Which topics dominate which reviews

## 🔧 Configuration & Customization

### Adjust Topic Model

```python
# In main.py, line 58
topic_modeler = TopicModeler(n_topics=10)  # Change number of topics
```

### Modify Rate Limiting

```python
# In src/utils/config.py
RATE_LIMIT_DELAY = 2.0  # Increase from 1.0 to be more conservative
```

### Change Scraping Parameters

```python
# In main.py, line 35-39
max_reviews = st.sidebar.slider(
    "Max Reviews per Product",
    min_value=10,
    max_value=500,  # Change from 200 to 500
    value=100  # Change default from 50 to 100
)
```

## ⚠️ Important Notes

### Rate Limiting & Ethics

- The scraper includes rate limiting to avoid overwhelming Amazon's servers
- Respects `robots.txt` directives
- Uses proper User-Agent identification
- Consider Amazon's Terms of Service before large-scale scraping

### Data Quality

- Not all reviews may contain complete information
- Some reviews might be text-based only (no ratings)
- Language: Currently optimized for English reviews
- NLTK downloads happen automatically on first run

### Performance Considerations

- Large datasets (>1000 reviews) may take longer to process
- FinBERT model download (~500MB) on first use
- Topic modeling improves with more documents (recommend 100+)
- Reduce `max_reviews` if memory is constrained

## 🐛 Troubleshooting

### Issue: Import errors for sentiment_analyzer_finbert

```
ModuleNotFoundError: No module named 'sentiment_analyzer_finbert'
```

**Solution**: The file reference in main.py needs the actual implementation. Ensure the module path is correct.

### Issue: NLTK data not found

```
LookupError: Resource not found
```

**Solution**: Run the installation script or call:

```python
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
```

### Issue: Amazon scraper returns no results

**Solutions**:

- Try different search queries
- Verify competitor brand names match product listings
- Check Amazon domain availability for your region
- Increase max_pages parameter in search

### Issue: Streamlit app not loading

**Solution**:

```powershell
streamlit run main.py --logger.level=debug
```

## 📝 Example Usage

```python
# Manual usage outside Streamlit
from src.data_acquisition.amazon_scraper_amzpy import AmazonScraperAmzPy
from src.nlp_analysis.topic_modeler import TopicModeler
import pandas as pd

# 1. Scrape data
scraper = AmazonScraperAmzPy(country_code="com", max_reviews_per_product=100)
reviews_df = scraper.scrape_competitive_products(
    query="noise cancelling headphones",
    competitor_names=["Sony", "Bose", "Sennheiser"]
)

# 2. Topic modeling
modeler = TopicModeler(n_topics=8)
modeler.fit(reviews_df['review_text'].tolist())
topics = modeler.get_topics(n_words=8)
print("Identified topics:", topics)

# 3. Get topic distributions
topic_distributions = modeler.transform(reviews_df['review_text'].tolist())
print(topic_distributions.head())
```

## 🚧 Future Enhancements

- [ ] Multi-language support (Spanish, German, French, etc.)
- [ ] Real-time data refresh capability
- [ ] Historical trend analysis
- [ ] Recommendation generation
- [ ] Export to PDF/Excel reports
- [ ] Database integration for data persistence
- [ ] API endpoint creation
- [ ] Sentiment aspect extraction
- [ ] Competitor price tracking
- [ ] Review quality scoring

## 📚 References & Resources

- [FinBERT Paper](https://arxiv.org/abs/1908.04812)
- [Latent Dirichlet Allocation](https://www.jmlr.org/papers/v3/blei03a.html)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Scikit-learn Topic Modeling](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html)
- [amzpy Library](https://pypi.org/project/amzpy/)

## 📄 License

This project is for educational purposes. Ensure compliance with Amazon's Terms of Service and robots.txt when scraping.

**Last Updated**: 2024

**Status**: Active Development
