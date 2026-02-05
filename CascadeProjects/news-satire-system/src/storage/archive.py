import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import create_engine, Column, String, DateTime, Text, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..utils.config import Config
from ..utils.error_handling import StorageError, log_function_call
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class Article(Base):
    """SQLAlchemy model for archived articles."""
    __tablename__ = 'articles'
    
    id = Column(String, primary_key=True)
    headline = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    publish_date = Column(DateTime, nullable=False)
    satire_score = Column(Float)
    original_source = Column(String)
    original_headline = Column(String)
    tags = Column(Text)  # JSON string
    metadata = Column(Text)  # JSON string
    comic_data = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

class ArchiveManager:
    """
    Manages article archiving, storage, and retrieval.
    """
    
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Ensure articles directory exists
        os.makedirs(Config.ARTICLES_DIR, exist_ok=True)
    
    @log_function_call
    def archive_article(self, article: Dict) -> str:
        """
        Archive an article with full metadata.
        
        Args:
            article: Complete article with all metadata
            
        Returns:
            Article ID
        """
        try:
            # Generate unique ID
            article_id = self._generate_article_id(article)
            
            # Prepare article data
            article_data = self._prepare_article_data(article, article_id)
            
            # Store in database
            self._store_in_database(article_data)
            
            # Store as JSON file (backup)
            self._store_as_file(article, article_id)
            
            # Update search index
            self._update_search_index(article, article_id)
            
            logger.info(f"Archived article: '{article['headline'][:50]}...' (ID: {article_id})")
            return article_id
            
        except Exception as e:
            logger.error(f"Failed to archive article: {str(e)}")
            raise StorageError(f"Archive failed: {str(e)}")
    
    def get_article_by_id(self, article_id: str) -> Optional[Dict]:
        """
        Retrieve an article by ID.
        
        Args:
            article_id: Unique article identifier
            
        Returns:
            Article data or None if not found
        """
        try:
            session = self.Session()
            
            # Try database first
            article_record = session.query(Article).filter_by(id=article_id).first()
            
            if article_record:
                article = self._reconstruct_article_from_record(article_record)
                session.close()
                return article
            
            # Fallback to file system
            article = self._load_from_file(article_id)
            session.close()
            return article
            
        except Exception as e:
            logger.error(f"Failed to retrieve article {article_id}: {str(e)}")
            return None
    
    def search_articles(self, query: str, category: str = None, date_from: datetime = None, 
                       date_to: datetime = None, limit: int = 50) -> List[Dict]:
        """
        Search archived articles.
        
        Args:
            query: Search query
            category: Filter by category
            date_from: Start date filter
            date_to: End date filter
            limit: Maximum results
            
        Returns:
            List of matching articles
        """
        try:
            session = self.Session()
            
            # Build query
            db_query = session.query(Article)
            
            # Text search
            if query:
                db_query = db_query.filter(
                    Article.headline.contains(query) |
                    Article.content.contains(query)
                )
            
            # Category filter
            if category:
                db_query = db_query.filter(Article.category == category)
            
            # Date filters
            if date_from:
                db_query = db_query.filter(Article.publish_date >= date_from)
            
            if date_to:
                db_query = db_query.filter(Article.publish_date <= date_to)
            
            # Order and limit
            articles = db_query.order_by(Article.publish_date.desc()).limit(limit).all()
            
            # Reconstruct articles
            results = [self._reconstruct_article_from_record(article) for article in articles]
            
            session.close()
            logger.info(f"Search found {len(results)} articles for query: '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    def get_articles_by_date(self, date: datetime) -> List[Dict]:
        """
        Get all articles published on a specific date.
        
        Args:
            date: Date to retrieve articles for
            
        Returns:
            List of articles from that date
        """
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        return self.search_articles(
            query="",
            date_from=start_of_day,
            date_to=end_of_day,
            limit=100
        )
    
    def get_this_day_in_history(self, years_back: int = 5) -> List[Dict]:
        """
        Get articles published on this day in previous years.
        
        Args:
            years_back: How many years to look back
            
        Returns:
            List of historical articles
        """
        try:
            today = datetime.now()
            historical_articles = []
            
            for year in range(1, years_back + 1):
                historical_date = today.replace(year=today.year - year)
                year_articles = self.get_articles_by_date(historical_date)
                historical_articles.extend(year_articles)
            
            # Sort by date
            historical_articles.sort(key=lambda x: x.get('publish_date', ''), reverse=True)
            
            logger.info(f"Found {len(historical_articles)} articles from this day in history")
            return historical_articles
            
        except Exception as e:
            logger.error(f"Failed to get historical articles: {str(e)}")
            return []
    
    def get_related_articles(self, article: Dict, limit: int = 5) -> List[Dict]:
        """
        Find articles related to the given article.
        
        Args:
            article: Reference article
            limit: Maximum related articles
            
        Returns:
            List of related articles
        """
        try:
            # Extract keywords and category
            category = article.get('category', '')
            keywords = self._extract_search_keywords(article)
            
            # Search for related articles
            related = self.search_articles(
                query=' '.join(keywords[:3]),  # Use top 3 keywords
                category=category,
                limit=limit * 2  # Get more to filter
            )
            
            # Filter out the original article
            original_id = article.get('id', '')
            related = [a for a in related if a.get('id', '') != original_id]
            
            # Calculate similarity scores and return top matches
            scored_related = []
            for related_article in related:
                score = self._calculate_similarity(article, related_article)
                scored_related.append((score, related_article))
            
            # Sort by similarity and return top matches
            scored_related.sort(key=lambda x: x[0], reverse=True)
            
            return [article for score, article in scored_related[:limit]]
            
        except Exception as e:
            logger.error(f"Failed to get related articles: {str(e)}")
            return []
    
    def get_article_statistics(self) -> Dict:
        """
        Get statistics about archived articles.
        
        Returns:
            Dictionary with various statistics
        """
        try:
            session = self.Session()
            
            # Total articles
            total_articles = session.query(Article).count()
            
            # Articles by category
            category_stats = {}
            categories = session.query(Article.category).distinct().all()
            for (category,) in categories:
                count = session.query(Article).filter_by(category=category).count()
                category_stats[category] = count
            
            # Recent activity
            last_week = datetime.utcnow() - timedelta(days=7)
            recent_articles = session.query(Article).filter(
                Article.created_at >= last_week
            ).count()
            
            # Average satire score
            avg_score = session.query(Article.satire_score).filter(
                Article.satire_score.isnot(None)
            ).all()
            
            if avg_score:
                avg_satire_score = sum(score[0] for score in avg_score) / len(avg_score)
            else:
                avg_satire_score = 0
            
            session.close()
            
            stats = {
                'total_articles': total_articles,
                'articles_by_category': category_stats,
                'articles_last_week': recent_articles,
                'average_satire_score': round(avg_satire_score, 2),
                'archive_size_mb': self._calculate_archive_size()
            }
            
            logger.info(f"Generated archive statistics: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return {}
    
    def _generate_article_id(self, article: Dict) -> str:
        """Generate unique article ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        headline_hash = hash(article.get('headline', '')) % 10000
        return f"{timestamp}_{headline_hash}"
    
    def _prepare_article_data(self, article: Dict, article_id: str) -> Dict:
        """Prepare article data for storage."""
        return {
            'id': article_id,
            'headline': article.get('headline', ''),
            'content': json.dumps(article),
            'category': article.get('category', ''),
            'publish_date': datetime.fromisoformat(article.get('timestamp', datetime.now().isoformat())),
            'satire_score': article.get('satire_score', 0),
            'original_source': article.get('internal_metadata', {}).get('source', {}).get('original_source', ''),
            'original_headline': article.get('internal_metadata', {}).get('source', {}).get('original_headline', ''),
            'tags': json.dumps(article.get('internal_metadata', {}).get('categories', {}).get('tags', [])),
            'metadata': json.dumps(article.get('internal_metadata', {})),
            'comic_data': json.dumps(article.get('xkcd_comic', {}))
        }
    
    def _store_in_database(self, article_data: Dict):
        """Store article in database."""
        session = self.Session()
        
        try:
            article_record = Article(**article_data)
            session.add(article_record)
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    
    def _store_as_file(self, article: Dict, article_id: str):
        """Store article as JSON file (backup)."""
        try:
            filename = f"{Config.ARTICLES_DIR}/{article_id}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(article, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            logger.warning(f"Failed to store article as file: {str(e)}")
    
    def _update_search_index(self, article: Dict, article_id: str):
        """Update search index for the article."""
        # This could integrate with Elasticsearch or other search engine
        # For now, we'll rely on database text search
        pass
    
    def _reconstruct_article_from_record(self, record: Article) -> Dict:
        """Reconstruct full article from database record."""
        try:
            article = json.loads(record.content)
            article['id'] = record.id
            return article
        except Exception as e:
            logger.error(f"Failed to reconstruct article: {str(e)}")
            return {}
    
    def _load_from_file(self, article_id: str) -> Optional[Dict]:
        """Load article from JSON file."""
        try:
            filename = f"{Config.ARTICLES_DIR}/{article_id}.json"
            
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                article['id'] = article_id
                return article
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load article from file: {str(e)}")
            return None
    
    def _extract_search_keywords(self, article: Dict) -> List[str]:
        """Extract keywords for searching related articles."""
        keywords = []
        
        # From headline
        headline = article.get('headline', '').lower()
        keywords.extend(headline.split())
        
        # From tags
        tags = article.get('internal_metadata', {}).get('categories', {}).get('tags', [])
        keywords.extend(tags)
        
        # From entities
        entities = article.get('internal_metadata', {}).get('entities', {})
        keywords.extend(entities.get('people', []))
        keywords.extend(entities.get('organizations', []))
        
        # Clean and deduplicate
        keywords = [kw.lower().strip() for kw in keywords if len(kw.strip()) > 2]
        return list(set(keywords))
    
    def _calculate_similarity(self, article1: Dict, article2: Dict) -> float:
        """Calculate similarity score between two articles."""
        score = 0.0
        
        # Category match
        if article1.get('category') == article2.get('category'):
            score += 0.3
        
        # Keyword overlap
        keywords1 = set(self._extract_search_keywords(article1))
        keywords2 = set(self._extract_search_keywords(article2))
        
        if keywords1 and keywords2:
            overlap = len(keywords1.intersection(keywords2))
            total = len(keywords1.union(keywords2))
            score += (overlap / total) * 0.5
        
        # Theme overlap
        themes1 = set(article1.get('internal_metadata', {}).get('entities', {}).get('themes', []))
        themes2 = set(article2.get('internal_metadata', {}).get('entities', {}).get('themes', []))
        
        if themes1 and themes2:
            theme_overlap = len(themes1.intersection(themes2))
            theme_total = len(themes1.union(themes2))
            score += (theme_overlap / theme_total) * 0.2
        
        return score
    
    def _calculate_archive_size(self) -> float:
        """Calculate archive size in MB."""
        try:
            total_size = 0
            
            # Calculate database size (simplified)
            for root, dirs, files in os.walk(Config.ARTICLES_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
            
            return round(total_size / (1024 * 1024), 2)  # Convert to MB
            
        except Exception as e:
            logger.error(f"Failed to calculate archive size: {str(e)}")
            return 0.0
