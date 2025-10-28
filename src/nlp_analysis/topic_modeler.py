# src/nlp_analysis/topic_modeler.py
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction import text 
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List, Dict

class TopicModeler:
    def __init__(self, n_topics: int = 10):
        self.n_topics = n_topics
        self.vectorizer = None
        self.lda_model = None
        self.lemmatizer = WordNetLemmatizer()
        
        # Download required NLTK data
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
    
    def preprocess_text(self, texts: List[str]) -> List[str]:
        """Clean and preprocess text for topic modeling"""
        processed_texts = []
        stop_words = set(stopwords.words('english'))
        
        for text in texts:
            if pd.isna(text):
                continue
                
            # Convert to lowercase
            text = text.lower()
            
            # Remove special characters and digits
            text = re.sub(r'[^a-zA-Z\s]', '', text)
            
            # Tokenize and remove stopwords
            tokens = text.split()
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                     if token not in stop_words and len(token) > 2]
            
            processed_texts.append(' '.join(tokens))
        
        return processed_texts
    
    def fit(self, texts: List[str]):
        """Fit LDA model to the texts"""
        processed_texts = self.preprocess_text(texts)
        
        # Create document-term matrix
        self.vectorizer = CountVectorizer(
            max_df=0.95, 
            min_df=2, 
            max_features=1000
        )
        dtm = self.vectorizer.fit_transform(processed_texts)
        
        # Fit LDA model
        self.lda_model = LatentDirichletAllocation(
            n_components=self.n_topics,
            random_state=42
        )
        self.lda_model.fit(dtm)
        
        return self
    
    def get_topics(self, n_words: int = 10) -> Dict[int, List[str]]:
        """Get top words for each topic"""
        if self.lda_model is None or self.vectorizer is None:
            raise ValueError("Model must be fitted first")
        
        feature_names = self.vectorizer.get_feature_names_out()
        topics = {}
        
        for topic_idx, topic in enumerate(self.lda_model.components_):
            top_features_ind = topic.argsort()[:-n_words - 1:-1]
            top_features = [feature_names[i] for i in top_features_ind]
            topics[topic_idx] = top_features
        
        return topics
    
    def transform(self, texts: List[str]) -> pd.DataFrame:
        """Transform new texts to topic distributions"""
        processed_texts = self.preprocess_text(texts)
        dtm = self.vectorizer.transform(processed_texts)
        topic_distributions = self.lda_model.transform(dtm)
        
        return pd.DataFrame(
            topic_distributions,
            columns=[f'Topic_{i}' for i in range(self.n_topics)]
        )