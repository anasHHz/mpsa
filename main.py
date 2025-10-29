"""
Amazon Business Intelligence Analyzer - Main Application
Streamlit web interface for sentiment and competitive analysis
"""
import streamlit as st
import pandas as pd
import logging
from src.data_acquisition.amazon_scraper_amzpy import AmazonScraperAmzPy
from src.nlp_analysis.sentiment_analyzer import FinBertSentimentAnalyzer
from src.nlp_analysis.topic_modeler import TopicModeler
from src.visualization.dashboards import BusinessIntelligenceDashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@st.cache_resource
def load_models():
    """Cache models to avoid reloading on every run"""
    try:
        logger.info("Loading FinBERT model...")
        sentiment_analyzer = FinBertSentimentAnalyzer()
        logger.info("FinBERT model loaded successfully")
        return sentiment_analyzer
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        st.error("Failed to load sentiment analysis model. Please ensure transformers and torch are installed.")
        return None


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Amazon Business Intelligence Analyzer",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Amazon Customer Sentiment & Competitive Analysis")
    st.markdown("""
    Analyze customer reviews from Amazon using **FinBERT** for accurate sentiment analysis 
    combined with **LDA topic modeling** to uncover market insights and competitive positioning.
    
    ---
    """)
    
    # Sidebar for configuration
    st.sidebar.header("Analysis Configuration")
    
    product_query = st.sidebar.text_input(
        "Product Search Query", 
        "wireless earbuds"
    )
    
    competitors = st.sidebar.text_area(
        "Competitor Brands (comma-separated)",
        "Sony, Bose, JBL, Samsung, OnePlus"
    ).split(',')
    
    max_reviews = st.sidebar.slider(
        "Max Reviews per Product",
        min_value=10,
        max_value=200,
        value=50
    )
    
    country_code = st.sidebar.selectbox(
        "Amazon Domain",
        ["in", "com", "co.uk", "de", "fr"],
        index=0
    )
    
    if st.sidebar.button("🚀 Run Amazon Analysis", use_container_width=True):
        with st.spinner("Collecting and analyzing Amazon data..."):
            try:
                # Load cached models
                sentiment_analyzer = load_models()
                if sentiment_analyzer is None:
                    st.error("Cannot proceed without sentiment analyzer. Please check dependencies.")
                    return
                
                # Initialize components
                logger.info(f"Initializing scraper for domain: {country_code}")
                scraper = AmazonScraperAmzPy(
                    country_code=country_code.strip(),
                    max_reviews_per_product=max_reviews
                )
                
                logger.info("Initializing topic modeler")
                topic_modeler = TopicModeler(n_topics=6)
                
                # Scrape data
                st.info("🕸️ Scraping Amazon product reviews...")
                logger.info(f"Starting scrape for query: {product_query}")
                
                competitor_list = [c.strip() for c in competitors if c.strip()]
                if not competitor_list:
                    st.warning("No competitor brands specified. Using query alone.")
                    competitor_list = []
                
                reviews_df = scraper.scrape_competitive_products(
                    query=product_query,
                    competitor_names=competitor_list
                )
                
                if reviews_df.empty:
                    st.error("❌ No reviews found. Try different search terms or competitors.")
                    logger.warning(f"No reviews found for query: {product_query}")
                    return
                
                st.success(f"✅ Collected {len(reviews_df)} reviews")
                
                # Perform sentiment analysis
                st.info("🧠 Analyzing sentiment with FinBERT...")
                logger.info("Starting sentiment analysis")
                try:
                    sentiment_results = sentiment_analyzer.analyze_batch(
                        reviews_df['review_text'].tolist()
                    )
                    logger.info(f"Sentiment analysis completed for {len(sentiment_results)} reviews")
                except Exception as e:
                    logger.error(f"Sentiment analysis failed: {e}")
                    st.error(f"Sentiment analysis failed: {str(e)}")
                    return
                
                # Merge sentiment results
                analysis_df = reviews_df.merge(
                    sentiment_results, 
                    on='review_text', 
                    how='left'
                )
                
                # Topic modeling
                st.info("📊 Performing topic analysis...")
                logger.info("Starting topic modeling")
                try:
                    review_texts = analysis_df['review_text'].dropna().tolist()
                    if len(review_texts) < 10:
                        st.warning("⚠️ Not enough reviews for topic modeling (need at least 10)")
                        topic_modeler.fit(review_texts) if review_texts else None
                    else:
                        topic_modeler.fit(review_texts)
                    
                    topics = topic_modeler.get_topics(n_words=8)
                    topic_distributions = topic_modeler.transform(review_texts)
                    logger.info(f"Topic modeling identified {len(topics)} topics")
                except Exception as e:
                    logger.error(f"Topic modeling failed: {e}")
                    st.warning(f"Topic modeling encountered an issue: {str(e)}")
                    topics = {}
                    topic_distributions = pd.DataFrame()
                
                # Competitive analysis
                competitive_analysis = analysis_df.groupby('product_name').agg({
                    'sentiment_score': 'mean',
                    'review_text': 'count',
                    'score': 'mean'
                }).reset_index()
                competitive_analysis.columns = [
                    'product', 'avg_sentiment', 'review_volume', 'avg_rating'
                ]
                
                # Prepare results
                analysis_results = {
                    'reviews_data': analysis_df,
                    'sentiment_data': analysis_df,
                    'topics': topics,
                    'competitive_analysis': competitive_analysis,
                    'topic_distributions': topic_distributions,
                    'metadata': {
                        'total_reviews': len(analysis_df),
                        'products_analyzed': analysis_df['product_name'].unique().tolist(),
                        'query_used': product_query
                    }
                }
                
                # Display dashboard
                st.success("✅ Analysis complete! Displaying insights...")
                dashboard = BusinessIntelligenceDashboard(analysis_results)
                dashboard.create_sentiment_comparison()
                dashboard.create_topic_analysis()
                dashboard.create_competitive_analysis()
                
                # Show raw data
                with st.expander("View Raw Data"):
                    st.dataframe(analysis_df)
                
            except Exception as e:
                logger.error(f"Analysis pipeline failed: {e}", exc_info=True)
                st.error(f"❌ Analysis failed: {str(e)}")
                st.info("💡 Troubleshooting tips:")
                st.info("• Try using a different Amazon domain or search query")
                st.info("• Use more specific competitor brand names")
                st.info("• Reduce the maximum number of reviews to process")
                st.info("• Check your internet connection")
    
    # Display info panel
    with st.sidebar.expander("ℹ️ About This Tool"):
        st.markdown("""
        **Features:**
        - 🕸️ Automated Amazon review scraping
        - 🧠 FinBERT sentiment classification
        - 📊 LDA topic modeling
        - 🏆 Competitive analysis
        
        **Model Details:**
        - **FinBERT**: Sentiment classification (negative/neutral/positive)
        - **LDA**: Unsupervised topic discovery
        
        **Recommendations:**
        - Start with 50-100 reviews for quick analysis
        - Use 2-3 competitor brands for best results
        - Results improve with more data
        """)

def generate_sample_data():
    """Fallback sample data"""
    return pd.DataFrame({
        'platform': ['Amazon'] * 50,
        'product_name': ['Sony WH-1000XM4'] * 25 + ['Bose QuietComfort'] * 25,
        'review_text': [
            "Excellent noise cancellation and sound quality",
            "Battery life could be better but overall great",
            "Comfortable for long listening sessions",
            "Too expensive for what you get"
        ] * 25,
        'score': [5, 4, 5, 3] * 25
    })

if __name__ == "__main__":
    main()