# main.py - Updated with amzpy and FinBERT
import streamlit as st
import pandas as pd
from src.data_acquisition.amazon_scraper_amzpy import AmazonScraperAmzPy
from src.nlp_analysis.sentiment_analyzer_finbert import FinBertSentimentAnalyzer
from src.nlp_analysis.topic_modeler import TopicModeler
from src.visualization.dashboards import BusinessIntelligenceDashboard

def main():
    st.set_page_config(
        page_title="Amazon Business Intelligence Analyzer",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("Amazon Customer Sentiment & Competitive Analysis")
    st.markdown("""
    Analyze customer reviews from Amazon using FinBERT for accurate sentiment analysis 
    and competitive intelligence.
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
    
    if st.sidebar.button("Run Amazon Analysis"):
        with st.spinner("Collecting and analyzing Amazon data..."):
            try:
                # Initialize components
                scraper = AmazonScraperAmzPy(
                    country_code=country_code.strip(),
                    max_reviews_per_product=max_reviews
                )
                
                sentiment_analyzer = FinBertSentimentAnalyzer()
                topic_modeler = TopicModeler(n_topics=6)
                
                # Scrape data
                st.info("🕸️ Scraping Amazon product reviews...")
                reviews_df = scraper.scrape_competitive_products(
                    query=product_query,
                    competitor_names=[c.strip() for c in competitors if c.strip()]
                )
                
                if reviews_df.empty:
                    st.error("No reviews found. Try different search terms or competitors.")
                    return
                
                st.success(f"✅ Collected {len(reviews_df)} reviews")
                
                # Perform sentiment analysis
                st.info("🧠 Analyzing sentiment with FinBERT...")
                sentiment_results = sentiment_analyzer.analyze_batch(
                    reviews_df['review_text'].tolist()
                )
                
                # Merge sentiment results
                analysis_df = reviews_df.merge(
                    sentiment_results, 
                    on='review_text', 
                    how='left'
                )
                
                # Topic modeling
                st.info("📊 Performing topic analysis...")
                topic_modeler.fit(analysis_df['review_text'].tolist())
                topics = topic_modeler.get_topics(n_words=8)
                topic_distributions = topic_modeler.transform(
                    analysis_df['review_text'].tolist()
                )
                
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
                st.error(f"Analysis failed: {str(e)}")
                st.info("💡 Try using a different Amazon domain or search query")

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