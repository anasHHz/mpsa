# src/visualization/dashboards.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict

class BusinessIntelligenceDashboard:
    def __init__(self, analysis_results: Dict):
        self.results = analysis_results
    
    def create_sentiment_comparison(self):
        """Compare sentiment across platforms and competitors"""
        st.header("Sentiment Analysis Dashboard")
        
        # Sentiment by platform
        fig = px.box(
            self.results['sentiment_data'], 
            x='platform', 
            y='sentiment_score',
            title='Sentiment Distribution by Platform'
        )
        st.plotly_chart(fig)
    
    def create_topic_analysis(self):
        """Visualize topic modeling results"""
        st.header("Topic Analysis")
        
        topics = self.results['topics']
        
        # Create topic visualization
        for topic_id, words in topics.items():
            st.subheader(f"Topic {topic_id}")
            st.write(" | ".join(words))
            
            # Topic prevalence across platforms
            topic_data = self.results['topic_distributions']
            if not topic_data.empty:
                fig = px.histogram(
                    topic_data, 
                    x=f'Topic_{topic_id}',
                    title=f'Topic {topic_id} Distribution'
                )
                st.plotly_chart(fig)
    
    def create_competitive_analysis(self):
        """Competitive positioning charts"""
        st.header("Competitive Analysis")
        
        # Sentiment vs Volume scatter plot
        comp_data = self.results['competitive_analysis']
        
        fig = px.scatter(
            comp_data,
            x='review_volume',
            y='avg_sentiment',
            size='review_volume',
            color='product',
            hover_name='product',
            title='Competitive Positioning: Sentiment vs Volume'
        )
        st.plotly_chart(fig)
    
    def create_trend_analysis(self):
        """Sentiment trends over time"""
        st.header("Trend Analysis")
        
        if 'time_series_data' in self.results:
            time_data = self.results['time_series_data']
            
            fig = px.line(
                time_data,
                x='date',
                y='sentiment_score',
                color='product',
                title='Sentiment Trends Over Time'
            )
            st.plotly_chart(fig)

def create_static_report(analysis_results: Dict, output_path: str):
    """Create professional PDF report"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Sentiment distribution
    sns.boxplot(
        data=analysis_results['sentiment_data'],
        x='platform',
        y='sentiment_score',
        ax=axes[0,0]
    )
    axes[0,0].set_title('Sentiment Distribution by Platform')
    
    # Competitive analysis
    comp_data = analysis_results['competitive_analysis']
    axes[0,1].scatter(
        comp_data['review_volume'],
        comp_data['avg_sentiment'],
        s=100
    )
    for i, product in enumerate(comp_data['product']):
        axes[0,1].annotate(
            product, 
            (comp_data['review_volume'].iloc[i], comp_data['avg_sentiment'].iloc[i])
        )
    axes[0,1].set_title('Competitive Positioning')
    axes[0,1].set_xlabel('Review Volume')
    axes[0,1].set_ylabel('Average Sentiment')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')