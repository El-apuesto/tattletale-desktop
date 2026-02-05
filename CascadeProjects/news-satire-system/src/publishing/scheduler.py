import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import pytz
from ..utils.config import Config
from ..utils.error_handling import ErrorContext, PublishingError
from ..api.newsdata import NewsDataAPI
from ..api.xkcd import XKCDAPI
from ..generation.satire_engine import SatireEngine
from ..generation.quality_control import QualityController
from ..storage.archive import ArchiveManager
from ..publishing.metadata import MetadataGenerator

logger = logging.getLogger(__name__)

class PublishingScheduler:
    """
    Manages the 8 AM/8 PM CST publishing schedule for satire articles.
    """
    
    def __init__(self):
        self.news_api = NewsDataAPI()
        self.xkcd_api = XKCDAPI()
        self.satire_engine = SatireEngine()
        self.quality_controller = QualityController()
        self.archive_manager = ArchiveManager()
        self.metadata_generator = MetadataGenerator()
        
        # Set timezone
        self.timezone = pytz.timezone(Config.TIMEZONE)
        
        # Track published articles to avoid duplicates
        self.published_headlines = set()
        self.load_published_headlines()
    
    def start_scheduler(self):
        """Start the publishing scheduler."""
        logger.info("Starting publishing scheduler...")
        
        # Schedule publishing times
        for publish_time in Config.PUBLISH_TIMES:
            schedule.every().day.at(publish_time).do(self.run_publishing_cycle, 
                                                    cycle_time=publish_time)
        
        logger.info(f"Scheduled publishing for times: {Config.PUBLISH_TIMES}")
        
        # Run the scheduler
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(300)  # Wait 5 minutes before continuing
    
    def run_publishing_cycle(self, cycle_time: str):
        """
        Run a complete publishing cycle.
        
        Args:
            cycle_time: The scheduled time for this cycle ("08:00" or "20:00")
        """
        logger.info(f"Starting publishing cycle for {cycle_time}")
        
        with ErrorContext(f"Publishing cycle {cycle_time}", self.cleanup_cycle):
            try:
                # Step 1: Fetch news from previous 12 hours
                news_articles = self.fetch_news_for_cycle(cycle_time)
                
                if not news_articles:
                    logger.warning("No news articles found for this cycle")
                    return
                
                # Step 2: Generate satire articles
                satire_articles = self.generate_satire_articles(news_articles)
                
                if not satire_articles:
                    logger.warning("No satire articles generated for this cycle")
                    return
                
                # Step 3: Add XKCD comics
                articles_with_comics = self.add_comics_to_articles(satire_articles)
                
                # Step 4: Generate metadata
                complete_articles = self.generate_metadata_for_articles(articles_with_comics)
                
                # Step 5: Quality control final check
                final_articles = self.final_quality_check(complete_articles)
                
                # Step 6: Publish articles
                published_articles = self.publish_articles(final_articles)
                
                # Step 7: Archive articles
                self.archive_published_articles(published_articles)
                
                logger.info(f"Successfully published {len(published_articles)} articles for {cycle_time} cycle")
                
            except Exception as e:
                logger.error(f"Publishing cycle failed: {str(e)}")
                raise PublishingError(f"Cycle {cycle_time} failed: {str(e)}")
    
    def fetch_news_for_cycle(self, cycle_time: str) -> List[Dict]:
        """Fetch news articles for the current cycle."""
        logger.info("Fetching news articles...")
        
        try:
            # Fetch news from previous 12 hours
            news_articles = self.news_api.fetch_news(hours_back=12)
            
            # Filter out already covered stories
            filtered_articles = []
            for article in news_articles:
                headline = article.get('title', '')
                if not self.is_already_covered(headline):
                    filtered_articles.append(article)
            
            logger.info(f"Fetched {len(filtered_articles)} new articles from {len(news_articles)} total")
            return filtered_articles
            
        except Exception as e:
            logger.error(f"Failed to fetch news: {str(e)}")
            raise
    
    def generate_satire_articles(self, news_articles: List[Dict]) -> List[Dict]:
        """Generate satire articles from news."""
        logger.info(f"Generating satire from {len(news_articles)} news articles...")
        
        satire_articles = []
        failed_articles = []
        
        for news_article in news_articles:
            try:
                # Generate satire
                satire_article = self.satire_engine.transform_article(news_article)
                
                # Quality control check
                passed, issues = self.quality_controller.verify_article(satire_article)
                
                if passed:
                    satire_articles.append(satire_article)
                    logger.info(f"Generated satire: '{satire_article['headline'][:50]}...'")
                else:
                    logger.warning(f"Article failed quality control: {issues}")
                    failed_articles.append(news_article)
                
            except Exception as e:
                logger.error(f"Failed to generate satire for article: {str(e)}")
                failed_articles.append(news_article)
        
        # Log failed articles for manual review
        if failed_articles:
            logger.warning(f"Failed to process {len(failed_articles)} articles - marked for manual review")
            self.mark_for_manual_review(failed_articles)
        
        # Ensure we have minimum required articles
        if len(satire_articles) < Config.MIN_ARTICLES_PER_CYCLE:
            logger.warning(f"Only {len(satire_articles)} articles generated (minimum {Config.MIN_ARTICLES_PER_CYCLE})")
        
        # Limit to maximum articles
        if len(satire_articles) > Config.MAX_ARTICLES_PER_CYCLE:
            satire_articles = satire_articles[:Config.MAX_ARTICLES_PER_CYCLE]
            logger.info(f"Limited to {Config.MAX_ARTICLES_PER_CYCLE} articles")
        
        return satire_articles
    
    def add_comics_to_articles(self, articles: List[Dict]) -> List[Dict]:
        """Add XKCD comics to articles."""
        logger.info("Adding XKCD comics to articles...")
        
        articles_with_comics = []
        
        for article in articles:
            try:
                # Extract keywords for comic matching
                keywords = self.extract_keywords_from_article(article)
                category = article.get('category', '')
                
                # Find relevant comic
                comic = self.xkcd_api.find_relevant_comic(keywords, category)
                
                if comic:
                    article['xkcd_comic'] = comic
                    article['comic_html'] = self.xkcd_api.get_comic_html(comic)
                    logger.info(f"Added comic to article: '{article['headline'][:30]}...'")
                else:
                    logger.warning(f"No comic found for article: '{article['headline'][:30]}...'")
                    article['xkcd_comic'] = None
                    article['comic_html'] = ""
                
                articles_with_comics.append(article)
                
            except Exception as e:
                logger.error(f"Failed to add comic to article: {str(e)}")
                article['xkcd_comic'] = None
                article['comic_html'] = ""
                articles_with_comics.append(article)
        
        return articles_with_comics
    
    def generate_metadata_for_articles(self, articles: List[Dict]) -> List[Dict]:
        """Generate metadata for articles."""
        logger.info("Generating metadata for articles...")
        
        complete_articles = []
        
        for article in articles:
            try:
                # Generate SEO metadata
                seo_metadata = self.metadata_generator.generate_seo_metadata(article)
                
                # Generate social media metadata
                social_metadata = self.metadata_generator.generate_social_metadata(article)
                
                # Generate internal metadata
                internal_metadata = self.metadata_generator.generate_internal_metadata(article)
                
                # Add metadata to article
                article['seo_metadata'] = seo_metadata
                article['social_metadata'] = social_metadata
                article['internal_metadata'] = internal_metadata
                
                complete_articles.append(article)
                
            except Exception as e:
                logger.error(f"Failed to generate metadata for article: {str(e)}")
                # Still include the article without metadata
                complete_articles.append(article)
        
        return complete_articles
    
    def final_quality_check(self, articles: List[Dict]) -> List[Dict]:
        """Final quality check before publishing."""
        logger.info("Performing final quality check...")
        
        final_articles = []
        
        for article in articles:
            try:
                # Final quality control
                passed, issues = self.quality_controller.verify_article(article)
                
                if passed:
                    final_articles.append(article)
                else:
                    logger.warning(f"Article failed final quality check: {issues}")
                    self.mark_for_manual_review([article])
                
            except Exception as e:
                logger.error(f"Final quality check failed: {str(e)}")
                self.mark_for_manual_review([article])
        
        return final_articles
    
    def publish_articles(self, articles: List[Dict]) -> List[Dict]:
        """Publish articles to the website/platform."""
        logger.info(f"Publishing {len(articles)} articles...")
        
        published_articles = []
        
        for article in articles:
            try:
                # Add to published headlines tracking
                self.published_headlines.add(article['headline'])
                
                # Here you would integrate with your CMS or publishing platform
                # For now, we'll just log and mark as published
                article['published'] = True
                article['publish_date'] = datetime.now(self.timezone).isoformat()
                
                published_articles.append(article)
                logger.info(f"Published article: '{article['headline'][:50]}...'")
                
            except Exception as e:
                logger.error(f"Failed to publish article: {str(e)}")
                self.mark_for_manual_review([article])
        
        # Save published headlines
        self.save_published_headlines()
        
        return published_articles
    
    def archive_published_articles(self, articles: List[Dict]):
        """Archive published articles."""
        logger.info(f"Archiving {len(articles)} articles...")
        
        for article in articles:
            try:
                self.archive_manager.archive_article(article)
            except Exception as e:
                logger.error(f"Failed to archive article: {str(e)}")
    
    def extract_keywords_from_article(self, article: Dict) -> List[str]:
        """Extract keywords from article for comic matching."""
        keywords = []
        
        # Extract from headline
        headline = article.get('headline', '').lower()
        keywords.extend(headline.split())
        
        # Extract from category
        category = article.get('category', '').lower()
        keywords.append(category)
        
        # Extract key entities (simplified)
        full_text = f"{headline} {article.get('opening_paragraph', '')}"
        
        # Look for capitalized words (potential entities)
        import re
        entities = re.findall(r'\b[A-Z][a-z]+\b', full_text)
        keywords.extend([entity.lower() for entity in entities])
        
        # Remove common words and limit
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [kw for kw in keywords if kw not in stop_words and len(kw) > 2]
        
        return list(set(keywords))[:10]  # Return up to 10 unique keywords
    
    def is_already_covered(self, headline: str) -> bool:
        """Check if a headline has already been covered."""
        # Simple similarity check - in production, you'd use more sophisticated NLP
        for published_headline in self.published_headlines:
            if self.headlines_similar(headline, published_headline):
                return True
        return False
    
    def headlines_similar(self, headline1: str, headline2: str) -> bool:
        """Check if two headlines are similar."""
        # Simple word overlap check
        words1 = set(headline1.lower().split())
        words2 = set(headline2.lower().split())
        
        # If more than 60% of words overlap, consider similar
        if not words1 or not words2:
            return False
        
        overlap = len(words1.intersection(words2))
        total = len(words1.union(words2))
        
        return overlap / total > 0.6
    
    def load_published_headlines(self):
        """Load previously published headlines."""
        try:
            # In production, this would load from a database
            # For now, we'll use a simple file-based approach
            import os
            headlines_file = "data/published_headlines.txt"
            
            if os.path.exists(headlines_file):
                with open(headlines_file, 'r', encoding='utf-8') as f:
                    self.published_headlines = set(line.strip() for line in f if line.strip())
                
                logger.info(f"Loaded {len(self.published_headlines)} published headlines")
        except Exception as e:
            logger.error(f"Failed to load published headlines: {str(e)}")
            self.published_headlines = set()
    
    def save_published_headlines(self):
        """Save published headlines."""
        try:
            import os
            os.makedirs("data", exist_ok=True)
            
            headlines_file = "data/published_headlines.txt"
            with open(headlines_file, 'w', encoding='utf-8') as f:
                for headline in self.published_headlines:
                    f.write(f"{headline}\n")
            
            logger.info(f"Saved {len(self.published_headlines)} published headlines")
        except Exception as e:
            logger.error(f"Failed to save published headlines: {str(e)}")
    
    def mark_for_manual_review(self, articles: List[Dict]):
        """Mark articles for manual review."""
        try:
            import os
            import json
            from datetime import datetime
            
            os.makedirs("data/manual_review", exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/manual_review/review_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Marked {len(articles)} articles for manual review: {filename}")
        except Exception as e:
            logger.error(f"Failed to mark articles for manual review: {str(e)}")
    
    def cleanup_cycle(self):
        """Cleanup after a publishing cycle."""
        # This would include any cleanup operations needed
        pass
    
    def run_immediate_cycle(self):
        """Run an immediate publishing cycle (for testing)."""
        logger.info("Running immediate publishing cycle...")
        self.run_publishing_cycle("IMMEDIATE")
