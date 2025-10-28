# src/data_acquisition/amazon_scraper_amzpy.py
from amzpy import AmazonScraper
import pandas as pd
from typing import List, Dict, Optional
import time
import random

class AmazonScraperAmzPy:
    def __init__(self, country_code: str = "in", max_reviews_per_product: int = 100):
        self.scraper = AmazonScraper(country_code=country_code)
        self.max_reviews = max_reviews_per_product
        self.country_code = country_code
    
    def search_products(self, query: str, max_pages: int = 2) -> List[Dict]:
        """Search for products by query"""
        try:
            products = self.scraper.search_products(query=query, max_pages=max_pages)
            return products
        except Exception as e:
            print(f"Error searching products: {e}")
            return []
    
    def get_product_details(self, asin: str) -> Optional[Dict]:
        """Get detailed product information"""
        try:
            url = f"https://www.amazon.{self.country_code}/dp/{asin}"
            product = self.scraper.get_product_details(url)
            return product
        except Exception as e:
            print(f"Error getting product details for {asin}: {e}")
            return None
    
    def get_product_reviews(self, asin: str, max_pages: int = 3) -> List[Dict]:
        """Get reviews for a specific product"""
        try:
            url = f"https://www.amazon.{self.country_code}/dp/{asin}"
            reviews = self.scraper.get_reviews(url, max_pages=max_pages)
            
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
            print(f"Error getting reviews for {asin}: {e}")
            return []
    
    def scrape_competitive_products(self, query: str, competitor_names: List[str]) -> pd.DataFrame:
        """Scrape multiple competing products"""
        all_reviews = []
        
        # Search for products
        products = self.search_products(query)
        print(f"Found {len(products)} products for query: {query}")
        
        # Filter products by competitor names
        competitor_asins = []
        for product in products:
            product_title = product.get('title', '').lower()
            if any(comp.lower() in product_title for comp in competitor_names):
                competitor_asins.append(product['asin'])
        
        print(f"Found {len(competitor_asins)} competitor products")
        
        # Get reviews for each competitor product
        for asin in competitor_asins[:5]:  # Limit to top 5 competitors
            print(f"Scraping reviews for ASIN: {asin}")
            product_details = self.get_product_details(asin)
            reviews = self.get_product_reviews(asin)
            
            for review in reviews:
                review.update({
                    "product_name": product_details.get('title', 'Unknown') if product_details else 'Unknown',
                    "brand": product_details.get('brand', 'Unknown') if product_details else 'Unknown',
                    "price": product_details.get('price', 0) if product_details else 0
                })
            
            all_reviews.extend(reviews)
            
            # Rate limiting
            time.sleep(random.uniform(2, 4))
        
        return pd.DataFrame(all_reviews)