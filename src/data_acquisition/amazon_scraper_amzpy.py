"""
Amazon Scraper Module - amzpy Implementation
Handles scraping of Amazon product reviews and metadata
"""
from amzpy import AmazonScraper
import pandas as pd
from typing import List, Dict, Optional
import time
import random
import logging

logger = logging.getLogger(__name__)


class AmazonScraperAmzPy:
    """
    Amazon product scraper using the amzpy library.
    
    Retrieves product information and customer reviews from Amazon
    with support for multiple regional domains.
    """
    
    def __init__(self, country_code: str = "in", max_reviews_per_product: int = 100):
        """
        Initialize Amazon scraper.
        
        Args:
            country_code: Amazon domain code (in, com, co.uk, de, fr)
            max_reviews_per_product: Maximum reviews to retrieve per product
        """
        self.scraper = AmazonScraper(country_code=country_code)
        self.max_reviews = max_reviews_per_product
        self.country_code = country_code
        self.base_url = f"https://www.amazon.{country_code}"
    
    def search_products(self, query: str, max_pages: int = 2) -> List[Dict]:
        """
        Search for products by query.
        
        Args:
            query: Product search query
            max_pages: Number of search result pages to retrieve
            
        Returns:
            List of product dictionaries containing ASIN and title
        """
        try:
            logger.info(f"Searching for products: {query}")
            products = self.scraper.search_products(query=query, max_pages=max_pages)
            logger.info(f"Found {len(products)} products")
            return products
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    def get_product_details(self, asin: str) -> Optional[Dict]:
        """
        Get detailed product information.
        
        Args:
            asin: Amazon Standard Identification Number
            
        Returns:
            Dictionary with product details or None if error
        """
        try:
            url = f"{self.base_url}/dp/{asin}"
            product = self.scraper.get_product_details(url)
            logger.info(f"Retrieved details for ASIN: {asin}")
            return product
        except Exception as e:
            logger.warning(f"Error getting product details for {asin}: {e}")
            return None
    
    def get_product_reviews(self, asin: str, max_pages: int = 3) -> List[Dict]:
        """
        Get reviews for a specific product.
        
        Args:
            asin: Amazon Standard Identification Number
            max_pages: Number of review pages to retrieve
            
        Returns:
            List of review dictionaries
        """
        try:
            url = f"{self.base_url}/dp/{asin}"
            reviews = self.scraper.get_reviews(url, max_pages=max_pages)
            logger.info(f"Retrieved {len(reviews)} reviews for ASIN: {asin}")
            
            # Format reviews to match our schema
            formatted_reviews = []
            for review in reviews[:self.max_reviews]:
                formatted_review = {
                    "review_id": review.get('review_id', f"{asin}_{len(formatted_reviews)}"),
                    "review_text": review.get('review_text', ''),
                    "score": review.get('rating', 0),
                    "user_name": review.get('reviewer_name', 'Anonymous'),
                    "date": review.get('review_date', ''),
                    "title": review.get('review_title', ''),
                    "platform": "amazon",
                    "product_id": asin,
                    "verified_purchase": review.get('verified_purchase', False)
                }
                formatted_reviews.append(formatted_review)
            
            return formatted_reviews
            
        except Exception as e:
            logger.error(f"Error getting reviews for {asin}: {e}")
            return []
    
    def scrape_competitive_products(
        self, 
        query: str, 
        competitor_names: List[str]
    ) -> pd.DataFrame:
        """
        Scrape multiple competing products.
        
        Args:
            query: Product category search query
            competitor_names: List of competitor brand names to filter
            
        Returns:
            DataFrame containing all reviews with product information
        """
        all_reviews = []
        
        # Search for products
        products = self.search_products(query)
        if not products:
            logger.warning(f"No products found for query: {query}")
            return pd.DataFrame()
        
        logger.info(f"Found {len(products)} products for query: {query}")
        
        # Filter products by competitor names
        competitor_asins = []
        for product in products:
            product_title = product.get('title', '').lower()
            if any(comp.lower() in product_title for comp in competitor_names):
                competitor_asins.append(product['asin'])
        
        logger.info(f"Found {len(competitor_asins)} competitor products")
        
        if not competitor_asins:
            logger.warning("No competitor products found matching criteria")
            return pd.DataFrame()
        
        # Get reviews for each competitor product
        for idx, asin in enumerate(competitor_asins[:5], 1):  # Limit to top 5
            try:
                logger.info(f"Scraping [{idx}/5] ASIN: {asin}")
                product_details = self.get_product_details(asin)
                reviews = self.get_product_reviews(asin)
                
                for review in reviews:
                    review.update({
                        "product_name": product_details.get('title', 'Unknown') if product_details else 'Unknown',
                        "brand": product_details.get('brand', 'Unknown') if product_details else 'Unknown',
                        "price": product_details.get('price', 0) if product_details else 0
                    })
                
                all_reviews.extend(reviews)
                
                # Rate limiting - be respectful to Amazon
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"Error processing ASIN {asin}: {e}")
                continue
        
        logger.info(f"Total reviews collected: {len(all_reviews)}")
        return pd.DataFrame(all_reviews)