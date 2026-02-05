from typing import Dict, List, Set, Tuple
from datetime import datetime
import re
from ..utils.config import Config
import logging

logger = logging.getLogger(__name__)

class TaggingSystem:
    """
    Intelligent tagging system for organizing and categorizing articles.
    """
    
    def __init__(self):
        self.category_keywords = self._load_category_keywords()
        self.theme_keywords = self._load_theme_keywords()
        self.entity_patterns = self._load_entity_patterns()
        self.satirical_techniques = self._load_satirical_techniques()
    
    def generate_tags(self, article: Dict) -> Dict[str, List[str]]:
        """
        Generate comprehensive tags for an article.
        
        Args:
            article: Complete article with all metadata
            
        Returns:
            Dictionary containing different types of tags
        """
        try:
            # Extract text content
            full_text = self._extract_full_text(article)
            headline = article.get('headline', '')
            
            # Generate different tag types
            category_tags = self._generate_category_tags(article, full_text)
            theme_tags = self._generate_theme_tags(full_text)
            entity_tags = self._generate_entity_tags(full_text)
            technique_tags = self._generate_technique_tags(article, full_text)
            quality_tags = self._generate_quality_tags(article)
            temporal_tags = self._generate_temporal_tags(article)
            
            # Combine all tags
            all_tags = {
                'categories': category_tags,
                'themes': theme_tags,
                'entities': entity_tags,
                'techniques': technique_tags,
                'quality': quality_tags,
                'temporal': temporal_tags,
                'all': list(set(category_tags + theme_tags + entity_tags + 
                               technique_tags + quality_tags + temporal_tags))
            }
            
            logger.debug(f"Generated {len(all_tags['all'])} tags for article")
            return all_tags
            
        except Exception as e:
            logger.error(f"Failed to generate tags: {str(e)}")
            return self._get_default_tags()
    
    def find_related_articles_by_tags(self, article_tags: Dict[str, List[str]], 
                                     all_article_tags: List[Dict], limit: int = 5) -> List[Tuple[str, float]]:
        """
        Find related articles based on tag similarity.
        
        Args:
            article_tags: Tags for the reference article
            all_article_tags: List of tags for all articles
            limit: Maximum related articles
            
        Returns:
            List of (article_id, similarity_score) tuples
        """
        try:
            reference_tags = set(article_tags.get('all', []))
            
            similarities = []
            for article_tag_data in all_article_tags:
                if article_tag_data.get('id') == article_tags.get('id'):
                    continue  # Skip self
                
                article_tags_set = set(article_tag_data.get('tags', {}).get('all', []))
                
                # Calculate Jaccard similarity
                if reference_tags and article_tags_set:
                    intersection = len(reference_tags.intersection(article_tags_set))
                    union = len(reference_tags.union(article_tags_set))
                    similarity = intersection / union if union > 0 else 0
                    
                    if similarity > 0.1:  # Minimum similarity threshold
                        similarities.append((article_tag_data.get('id'), similarity))
            
            # Sort by similarity and return top matches
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"Failed to find related articles by tags: {str(e)}")
            return []
    
    def get_tag_statistics(self, all_tags: List[Dict]) -> Dict:
        """
        Get statistics about tag usage.
        
        Args:
            all_tags: List of tag data for all articles
            
        Returns:
            Dictionary with tag statistics
        """
        try:
            tag_counts = {}
            category_counts = {}
            theme_counts = {}
            technique_counts = {}
            
            for article_tags in all_tags:
                tags = article_tags.get('tags', {})
                
                # Count all tags
                for tag in tags.get('all', []):
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
                
                # Count categories
                for category in tags.get('categories', []):
                    category_counts[category] = category_counts.get(category, 0) + 1
                
                # Count themes
                for theme in tags.get('themes', []):
                    theme_counts[theme] = theme_counts.get(theme, 0) + 1
                
                # Count techniques
                for technique in tags.get('techniques', []):
                    technique_counts[technique] = technique_counts.get(technique, 0) + 1
            
            # Get top tags in each category
            top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]
            top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
            top_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            top_techniques = sorted(technique_counts.items(), key=lambda x: x[1], reverse=True)
            
            stats = {
                'total_unique_tags': len(tag_counts),
                'top_tags': top_tags,
                'top_categories': top_categories,
                'top_themes': top_themes,
                'top_techniques': top_techniques,
                'average_tags_per_article': sum(len(tags.get('all', [])) for tags in all_tags) / len(all_tags) if all_tags else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get tag statistics: {str(e)}")
            return {}
    
    def _extract_full_text(self, article: Dict) -> str:
        """Extract full text content from article."""
        parts = [
            article.get('headline', ''),
            article.get('opening_paragraph', ''),
            ' '.join(article.get('body_paragraphs', [])),
            ' '.join([quote.get('quote', '') for quote in article.get('expert_quotes', [])])
        ]
        return ' '.join(parts).lower()
    
    def _generate_category_tags(self, article: Dict, text: str) -> List[str]:
        """Generate category tags based on content."""
        categories = []
        
        # Primary category from article metadata
        primary_category = article.get('category', '').lower()
        if primary_category:
            categories.append(primary_category)
        
        # Secondary categories based on keywords
        for category, keywords in self.category_keywords.items():
            if any(keyword in text for keyword in keywords):
                if category != primary_category:
                    categories.append(category)
        
        return list(set(categories))
    
    def _generate_theme_tags(self, text: str) -> List[str]:
        """Generate theme tags based on content analysis."""
        themes = []
        
        for theme, keywords in self.theme_keywords.items():
            if any(keyword in text for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _generate_entity_tags(self, text: str) -> List[str]:
        """Generate entity tags (people, organizations, locations)."""
        entities = []
        
        # People entities
        people_patterns = self.entity_patterns['people']
        for pattern in people_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities.extend(matches)
        
        # Organization entities
        org_patterns = self.entity_patterns['organizations']
        for pattern in org_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities.extend(matches)
        
        # Location entities
        location_patterns = self.entity_patterns['locations']
        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities.extend(matches)
        
        # Clean and deduplicate
        entities = [entity.strip().title() for entity in entities if len(entity.strip()) > 2]
        return list(set(entities))
    
    def _generate_technique_tags(self, article: Dict, text: str) -> List[str]:
        """Generate satirical technique tags."""
        techniques = []
        
        for technique, indicators in self.satirical_techniques.items():
            score = 0
            
            for indicator in indicators:
                if indicator in text:
                    score += 1
            
            # Require multiple indicators for technique detection
            if score >= 2:
                techniques.append(technique)
            elif score == 1 and technique in ['irony', 'contradiction']:
                # Single indicator is enough for these core techniques
                techniques.append(technique)
        
        return techniques
    
    def _generate_quality_tags(self, article: Dict) -> List[str]:
        """Generate quality-related tags."""
        quality_tags = []
        
        satire_score = article.get('satire_score', 0)
        
        if satire_score >= 9:
            quality_tags.append('premium-quality')
        elif satire_score >= 7:
            quality_tags.append('high-quality')
        elif satire_score >= 5:
            quality_tags.append('standard-quality')
        else:
            quality_tags.append('low-quality')
        
        # Content length tags
        full_text = self._extract_full_text(article)
        word_count = len(full_text.split())
        
        if word_count >= 500:
            quality_tags.append('long-form')
        elif word_count >= 300:
            quality_tags.append('standard-length')
        else:
            quality_tags.append('short-form')
        
        # Complexity tag
        if 'complex' in full_text or 'sophisticated' in full_text:
            quality_tags.append('complex-satire')
        elif 'simple' in text or 'obvious' in text:
            quality_tags.append('straightforward-satire')
        
        return quality_tags
    
    def _generate_temporal_tags(self, article: Dict) -> List[str]:
        """Generate temporal tags."""
        temporal_tags = []
        
        # Time of day
        publish_time = article.get('timestamp', '')
        if publish_time:
            try:
                dt = datetime.fromisoformat(publish_time.replace('Z', '+00:00'))
                hour = dt.hour
                
                if 6 <= hour < 12:
                    temporal_tags.append('morning-publish')
                elif 12 <= hour < 18:
                    temporal_tags.append('afternoon-publish')
                elif 18 <= hour < 22:
                    temporal_tags.append('evening-publish')
                else:
                    temporal_tags.append('night-publish')
                    
            except Exception:
                pass
        
        # Day of week
        try:
            dt = datetime.fromisoformat(publish_time.replace('Z', '+00:00'))
            day_name = dt.strftime('%A').lower()
            temporal_tags.append(f'{day_name}-publish')
        except Exception:
            pass
        
        # Recency
        try:
            dt = datetime.fromisoformat(publish_time.replace('Z', '+00:00'))
            days_ago = (datetime.now(dt.tzinfo) - dt).days
            
            if days_ago == 0:
                temporal_tags.append('today')
            elif days_ago == 1:
                temporal_tags.append('yesterday')
            elif days_ago <= 7:
                temporal_tags.append('this-week')
            elif days_ago <= 30:
                temporal_tags.append('this-month')
            else:
                temporal_tags.append('archived')
        except Exception:
            pass
        
        return temporal_tags
    
    def _load_category_keywords(self) -> Dict[str, List[str]]:
        """Load category keyword mappings."""
        return {
            'politics': [
                'senator', 'congress', 'president', 'government', 'policy',
                'election', 'vote', 'democrat', 'republican', 'legislation',
                'federal', 'state', 'mayor', 'governor', 'campaign'
            ],
            'business': [
                'ceo', 'company', 'corporation', 'revenue', 'profit',
                'layoffs', 'earnings', 'stock', 'market', 'investment',
                'merger', 'acquisition', 'board', 'shareholder', 'executive'
            ],
            'technology': [
                'tech', 'software', 'app', 'startup', 'innovation',
                'ai', 'artificial intelligence', 'machine learning', 'data',
                'algorithm', 'platform', 'digital', 'cyber', 'programming'
            ],
            'science': [
                'research', 'study', 'scientist', 'university', 'discovery',
                'experiment', 'climate', 'environment', 'medical', 'health',
                'space', 'nasa', 'physics', 'biology', 'chemistry'
            ],
            'health': [
                'health', 'medical', 'hospital', 'doctor', 'patient',
                'disease', 'treatment', 'medicine', 'pharmaceutical', 'fda',
                'covid', 'vaccine', 'healthcare', 'insurance'
            ]
        }
    
    def _load_theme_keywords(self) -> Dict[str, List[str]]:
        """Load theme keyword mappings."""
        return {
            'hypocrisy': [
                'claims while', 'insists despite', 'announces but', 'contradiction',
                'double standard', 'says one thing does another', 'ironic'
            ],
            'corporate-speak': [
                'synergy', 'paradigm', 'leverage', 'optimize', 'streamline',
                'rightsizing', 'restructuring', 'operational excellence', 'shareholder value'
            ],
            'political-theater': [
                'bipartisan', 'fiscal responsibility', 'government waste',
                'taxpayer money', 'national security', 'public interest'
            ],
            'technological-irony': [
                'innovation', 'disruption', 'transformation', 'digital',
                'automation', 'efficiency', 'productivity'
            ],
            'economic-inequality': [
                'wealth gap', 'income inequality', 'ceo pay', 'minimum wage',
                'worker rights', 'union', 'labor', 'class'
            ],
            'media-critique': [
                'mainstream media', 'fake news', 'journalism', 'press',
                'reporting', 'coverage', 'narrative', 'framing'
            ]
        }
    
    def _load_entity_patterns(self) -> Dict[str, List[str]]:
        """Load entity recognition patterns."""
        return {
            'people': [
                r'(?:senator|president|ceo|dr\.|professor)\s+([a-z]+\s+[a-z]+)',
                r'([a-z]+\s+[a-z]+)\s+(?:said|announced|claimed|reported|stated)',
                r'(?:mr\.|ms\.|mrs\.)\s+([a-z]+\s+[a-z]+)'
            ],
            'organizations': [
                r'([a-z]+(?:\s+[a-z]+)*)\s+(?:inc\.|corp\.|llc|company|corporation)',
                r'(?:meta|google|amazon|apple|microsoft|tesla|netflix|facebook)',
                r'(?:congress|senate|house|white house|pentagon|cia|fbi|doj)'
            ],
            'locations': [
                r'([a-z]+\s+[a-z]+)\s+(?:city|state|country)',
                r'(?:washington|new york|california|texas|florida|chicago|boston)',
                r'united states|america|u\.s\.|europe|asia'
            ]
        }
    
    def _load_satirical_techniques(self) -> Dict[str, List[str]]:
        """Load satirical technique indicators."""
        return {
            'irony': [
                'ironically', 'contradiction', 'paradox', 'hypocrisy',
                'claims while', 'insists despite', 'announces but'
            ],
            'exaggeration': [
                'unprecedented', 'historic', 'revolutionary', 'groundbreaking',
                'extraordinary', 'remarkable', 'stunning'
            ],
            'understatement': [
                'slight', 'minor', 'modest', 'somewhat', 'rather',
                'quite', 'fairly', 'relatively'
            ],
            'deadpan': [
                'reported', 'announced', 'stated', 'according to',
                'officials say', 'data shows', 'analysis indicates'
            ],
            'wordplay': [
                'literally', 'technically', 'officially', 'formally',
                'essentially', 'basically', 'fundamentally'
            ],
            'juxtaposition': [
                'while', 'whereas', 'however', 'but', 'although',
                'despite', 'in contrast', 'on the other hand'
            ]
        }
    
    def _get_default_tags(self) -> Dict[str, List[str]]:
        """Get default tags for fallback."""
        return {
            'categories': ['general'],
            'themes': [],
            'entities': [],
            'techniques': ['deadpan'],
            'quality': ['standard-quality'],
            'temporal': ['archived'],
            'all': ['general', 'deadpan', 'standard-quality', 'archived']
        }
