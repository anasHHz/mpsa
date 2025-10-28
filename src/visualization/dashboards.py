# src/visualization/dashboards.py - Updated for FinBERT
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class BusinessIntelligenceDashboard:
    def __init__(self, analysis_results: Dict):
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
    
    def create_competitive_analysis(self):
        """Enhanced competitive analysis"""
        st.header("🏆 Competitive Positioning")
        
        comp_data = self.results['competitive_analysis']
        
        # Bubble chart: Sentiment vs Volume vs Rating
        fig = px.scatter(
            comp_data,
            x='review_volume',
            y='avg_sentiment',
            size='avg_rating',
            color='product',
            hover_name='product',
            size_max=60,
            title='Competitive Positioning: Sentiment vs Volume (Size = Avg Rating)'
        )
        fig.update_traces(marker=dict(opacity=0.7))
        st.plotly_chart(fig)
        
        # Performance metrics table
        st.subheader("Performance Metrics")
        comp_data['sentiment_rank'] = comp_data['avg_sentiment'].rank(ascending=False)
        comp_data['volume_rank'] = comp_data['review_volume'].rank(ascending=False)
        st.dataframe(comp_data.style.highlight_max(subset=['avg_sentiment', 'review_volume']))