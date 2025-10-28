# main.py - Streamlit App
import streamlit as st
import pandas as pd
#from src.data_acquisition.google_play_scraper import GooglePlayScraper
#from src.data_acquisition.amazon_scraper import AmazonScraper
from src.nlp_analysis.sentiment_analyzer import SentimentAnalyzer
from src.nlp_analysis.topic_modeler import TopicModeler
from src.visualization.dashboards import BusinessIntelligenceDashboard

def main():
    st.set_page_config(
        page_title="Business Strategy Analyzer",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("Multi-Platform Customer Sentiment & Competitive Analysis")
    st.markdown("""
    This tool analyzes customer reviews across multiple platforms to extract 
    actionable business intelligence and competitive insights.
    """)
    
    # Sidebar for input
    st.sidebar.header("Analysis Configuration")
    product_category = st.sidebar.text_input(
        "Product Category", 
        "project management software"
    )
    
    competitors = st.sidebar.text_area(
        "Competitors (comma-separated)",
        "Trello, Asana, Monday.com, Jira"
    ).split(',')
    
    platforms = st.sidebar.multiselect(
        "Platforms to Analyze",
        ["Google Play", "App Store", "Amazon", "Reddit"],
        default=["Google Play", "App Store"]
    )
    
    if st.sidebar.button("Run Analysis"):
        with st.spinner("Collecting and analyzing data..."):
            # Initialize components
            sentiment_analyzer = SentimentAnalyzer()
            topic_modeler = TopicModeler()
            
            # Placeholder for actual data collection
            # In practice, you would call the scrapers here
            sample_data = generate_sample_data()
            
            # Perform analysis
            sentiment_results = sentiment_analyzer.analyze_batch(
                sample_data['review_text'].tolist()
            )
            
            topic_modeler.fit(sample_data['review_text'].tolist())
            topics = topic_modeler.get_topics()
            
            # Prepare results
            analysis_results = {
                'sentiment_data': sample_data.merge(sentiment_results, on='review_text', how='left'),
                'topics': topics,
                'competitive_analysis': generate_competitive_analysis(sample_data),
                'topic_distributions': topic_modeler.transform(
                    sample_data['review_text'].tolist()
                )
            }
            
            # Display dashboard
            dashboard = BusinessIntelligenceDashboard(analysis_results)
            dashboard.create_sentiment_comparison()
            dashboard.create_topic_analysis()
            dashboard.create_competitive_analysis()

def generate_sample_data():
    """Generate sample data for demonstration"""
    # In practice, this would be real scraped data
    return pd.DataFrame({
        'platform': ['Google Play'] * 50 + ['App Store'] * 50,
        'product': ['Trello'] * 25 + ['Asana'] * 25 + ['Trello'] * 25 + ['Asana'] * 25,
        'review_text': [
            "Great app for task management", 
            "UI could be better",
            "Love the collaboration features",
            "Too expensive for what it offers"
        ] * 25,
        'rating': [5, 2, 4, 3] * 25
    })

def generate_competitive_analysis(data):
    """Generate competitive analysis data"""
    return pd.DataFrame({
        'product': ['Trello', 'Asana', 'Monday.com', 'Jira'],
        'avg_sentiment': [0.4, 0.3, 0.35, 0.25],
        'review_volume': [1000, 800, 600, 1200]
    })

if __name__ == "__main__":
    main()