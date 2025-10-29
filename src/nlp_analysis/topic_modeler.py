"""
Topic Modeling Module - LDA Implementation
Performs unsupervised topic discovery using Latent Dirichlet Allocation
"""
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction import text 
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TopicModeler:
    """
    Latent Dirichlet Allocation (LDA) topic modeler.
    
    Discovers latent topics in a collection of documents through unsupervised learning.
    Uses CountVectorizer for feature extraction and scikit-learn's LDA implementation.
    """
    
    def __init__(self, n_topics: int = 10):
        """
        Initialize the topic modeler.
        
        Args:
            n_topics: Number of topics to discover (default: 10)
            
        Raises:
            ValueError: If n_topics <= 0
        """
        if n_topics <= 0:
            raise ValueError("n_topics must be greater than 0")
        
        self.n_topics = n_topics
        self.vectorizer = None
        self.lda_model = None
        self.lemmatizer = WordNetLemmatizer()
        logger.info(f"Initializing TopicModeler with n_topics={n_topics}")
        
        # Download required NLTK data
        self._download_nltk_data()
    
    def _download_nltk_data(self):
        """Download required NLTK datasets"""
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            logger.info("Downloading NLTK stopwords...")
            nltk.download('stopwords', quiet=True)
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            logger.info("Downloading NLTK wordnet...")
            nltk.download('wordnet', quiet=True)
        
        try:
            nltk.data.find('corpora/omw-1.4')
        except LookupError:
            logger.info("Downloading NLTK OMW...")
            nltk.download('omw-1.4', quiet=True)
    
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
    
    def fit(self, texts: List[str]) -> 'TopicModeler':
        """
        Fit LDA model to the texts.
        
        Args:
            texts: List of text documents to model
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If texts list is empty or too small
            RuntimeError: If model fitting fails
        """
        if not texts:
            raise ValueError("Cannot fit model with empty text list")
        
        if len(texts) < 2:
            raise ValueError("Need at least 2 documents for topic modeling")
        
        logger.info(f"Preprocessing {len(texts)} documents...")
        processed_texts = self.preprocess_text(texts)
        
        if not processed_texts:
            raise RuntimeError("No valid text documents after preprocessing")
        
        logger.info(f"Creating document-term matrix with max_features=1000...")
        
        try:
            # Create document-term matrix
            self.vectorizer = CountVectorizer(
                max_df=0.95,  # Ignore terms that appear in >95% of docs
                min_df=2,     # Ignore terms that appear in <2 docs
                max_features=1000
            )
            dtm = self.vectorizer.fit_transform(processed_texts)
            logger.info(f"Document-term matrix shape: {dtm.shape}")
            
            if dtm.shape[1] == 0:
                raise RuntimeError("No valid features after vectorization")
            
            # Fit LDA model
            logger.info(f"Fitting LDA model with {self.n_topics} topics...")
            self.lda_model = LatentDirichletAllocation(
                n_components=self.n_topics,
                random_state=42,
                max_iter=10,
                learning_method='online',
                n_jobs=-1  # Use all cores
            )
            self.lda_model.fit(dtm)
            logger.info("LDA model fitted successfully")
            
        except Exception as e:
            logger.error(f"Error fitting LDA model: {e}")
            raise RuntimeError(f"Failed to fit LDA model: {str(e)}")
        
        return self
    
    def get_topics(self, n_words: int = 10) -> Dict[int, List[str]]:
        """
        Extract top words for each topic.
        
        Args:
            n_words: Number of top words to extract per topic
            
        Returns:
            Dictionary mapping topic ID to list of top words
            
        Raises:
            ValueError: If model hasn't been fitted yet
            TypeError: If n_words is invalid
        """
        if not isinstance(n_words, int) or n_words <= 0:
            raise TypeError("n_words must be a positive integer")
        
        if self.lda_model is None or self.vectorizer is None:
            raise ValueError("Model must be fitted first using fit()")
        
        try:
            feature_names = self.vectorizer.get_feature_names_out()
            topics = {}
            
            for topic_idx, topic in enumerate(self.lda_model.components_):
                # Get indices of top n_words with highest weights
                top_features_ind = topic.argsort()[:-n_words - 1:-1]
                top_features = [feature_names[i] for i in top_features_ind]
                topics[topic_idx] = top_features
            
            logger.info(f"Extracted {len(topics)} topics with top {n_words} words each")
            return topics
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            raise RuntimeError(f"Failed to extract topics: {str(e)}")
    
    def transform(self, texts: List[str]) -> pd.DataFrame:
        """
        Transform new texts to topic distributions.
        
        Args:
            texts: List of documents to transform
            
        Returns:
            DataFrame with topic probability distributions for each document
            
        Raises:
            ValueError: If model hasn't been fitted or input is invalid
        """
        if not texts:
            raise ValueError("Cannot transform empty text list")
        
        if self.lda_model is None or self.vectorizer is None:
            raise ValueError("Model must be fitted first using fit()")
        
        try:
            logger.info(f"Transforming {len(texts)} documents to topic distributions...")
            processed_texts = self.preprocess_text(texts)
            
            if not processed_texts:
                logger.warning("No valid documents after preprocessing")
                # Return empty DataFrame with correct structure
                return pd.DataFrame(
                    columns=[f'Topic_{i}' for i in range(self.n_topics)]
                )
            
            dtm = self.vectorizer.transform(processed_texts)
            topic_distributions = self.lda_model.transform(dtm)
            
            df = pd.DataFrame(
                topic_distributions,
                columns=[f'Topic_{i}' for i in range(self.n_topics)]
            )
            logger.info(f"Successfully transformed {len(df)} documents")
            return df
            
        except Exception as e:
            logger.error(f"Error transforming texts: {e}")
            raise RuntimeError(f"Failed to transform texts: {str(e)}")