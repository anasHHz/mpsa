"""
Business Intelligence Dashboard - Visualization Components
Generates interactive dashboards for sentiment and competitive analysis
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any


class BusinessIntelligenceDashboard:
    """
    Dashboard for visualizing sentiment analysis and competitive positioning.
    
    Creates interactive charts and metrics using Streamlit and Plotly.
    """
    
    def __init__(self, analysis_results: Dict[str, Any]):
        self.results = analysis_results
    
    def create_sentiment_comparison(self):
        """Enhanced sentiment comparison for FinBERT"""
        st.header("📊 FinBERT Sentiment Analysis")
        
        sentiment_data = self.results['sentiment_data']
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Sentiment Distribution", "Product Comparison", "Detailed Scores"])
        
        with tab1:
            # Sentiment distribution by product
            fig = px.box(
                sentiment_data,
                x='product_name',
                y='sentiment_score',
                color='sentiment_label',
                title='Sentiment Distribution by Product (FinBERT)'
            )
            st.plotly_chart(fig)
            
            # Sentiment composition pie chart
            sentiment_counts = sentiment_data['sentiment_label'].value_counts()
            fig_pie = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title='Overall Sentiment Distribution'
            )
            st.plotly_chart(fig_pie)
        
        with tab2:
            # Average sentiment by product
            avg_sentiment = sentiment_data.groupby('product_name')['sentiment_score'].mean().sort_values()
            fig_bar = px.bar(
                x=avg_sentiment.values,
                y=avg_sentiment.index,
                orientation='h',
                title='Average Sentiment Score by Product',
                labels={'x': 'Average Sentiment Score', 'y': 'Product'}
            )
            st.plotly_chart(fig_bar)
        
        with tab3:
            # Show sentiment confidence scores
            st.subheader("Sentiment Confidence Scores")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_positive = sentiment_data['positive'].mean()
                st.metric("Average Positive Confidence", f"{avg_positive:.3f}")
            
            with col2:
                avg_negative = sentiment_data['negative'].mean()
                st.metric("Average Negative Confidence", f"{avg_negative:.3f}")
            
            with col3:
                avg_neutral = sentiment_data['neutral'].mean()
                st.metric("Average Neutral Confidence", f"{avg_neutral:.3f}")
    
    def create_topic_analysis(self):
        """Display topic modeling results"""
        st.header("📚 Topic Analysis")
        
        topics = self.results.get('topics', {})
        topic_distributions = self.results.get('topic_distributions', pd.DataFrame())
        
        if not topics:
            st.warning("No topic data available")
            return
        
        # Display top topics
        st.subheader("Identified Topics")
        cols = st.columns(min(3, len(topics)))
        
        for idx, (topic_id, words) in enumerate(topics.items()):
            with cols[idx % 3]:
                st.write(f"**Topic {topic_id}**")
                for word in words[:5]:
                    st.write(f"• {word}")
        
        # Topic distribution heatmap
        if not topic_distributions.empty:
            st.subheader("Topic Distribution")
            
            # Create heatmap
            topic_dist_sample = topic_distributions.head(50)
            fig = px.imshow(
                topic_dist_sample.T,
                labels=dict(x="Document", y="Topic", color="Probability"),
                title="Topic Distribution Across Reviews",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Topic prevalence
            st.subheader("Topic Prevalence")
            topic_means = topic_distributions.mean().sort_values(ascending=False)
            fig_bar = px.bar(
                x=topic_means.index,
                y=topic_means.values,
                labels={'x': 'Topic', 'y': 'Average Probability'},
                title='Average Topic Probability Across All Reviews'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    def create_competitive_analysis(self):
        """Enhanced competitive analysis visualization"""
        st.header("🏆 Competitive Positioning")
        
        comp_data = self.results['competitive_analysis'].copy()
        
        if comp_data.empty:
            st.warning("No competitive data available")
            return
        
        # Bubble chart: Sentiment vs Volume vs Rating
        fig = px.scatter(
            comp_data,
            x='review_volume',
            y='avg_sentiment',
            size='avg_rating',
            color='product',
            hover_name='product',
            size_max=60,
            title='Competitive Positioning: Sentiment vs Volume (Size = Avg Rating)',
            labels={
                'review_volume': 'Review Volume',
                'avg_sentiment': 'Average Sentiment Score',
                'avg_rating': 'Average Rating'
            }
        )
        fig.update_traces(marker=dict(opacity=0.7))
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance metrics table
        st.subheader("Performance Metrics")
        comp_data['sentiment_rank'] = comp_data['avg_sentiment'].rank(ascending=False).astype(int)
        comp_data['volume_rank'] = comp_data['review_volume'].rank(ascending=False).astype(int)
        
        display_cols = ['product', 'avg_sentiment', 'review_volume', 'avg_rating', 'sentiment_rank', 'volume_rank']
        st.dataframe(
            comp_data[display_cols].style.highlight_max(
                subset=['avg_sentiment', 'review_volume'],
                color='lightgreen'
            ),
            use_container_width=True
        )