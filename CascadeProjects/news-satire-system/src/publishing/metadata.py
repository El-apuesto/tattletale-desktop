from typing import Dict, List
from datetime import datetime
import re
from ..utils.config import Config
import logging

logger = logging.getLogger(__name__)

class MetadataGenerator:
    """
    Generates SEO, social media, and internal metadata for articles.
    """
    
    def __init__(self):
        self.site_name = "The Satire Chronicle"
        self.base_url = "https://satirechronicle.com"
    
    def generate_seo_metadata(self, article: Dict) -> Dict:
        """
        Generate SEO metadata for an article.
        
        Args:
            article: The satire article
            
        Returns:
            Dictionary containing SEO metadata
        """
        try:
            headline = article.get('headline', '')
            opening_paragraph = article.get('opening_paragraph', '')
            category = article.get('category', '')
            
            # Title tag
            title_tag = f"{headline} | {self.site_name}"
            
            # Meta description (155 characters max)
            meta_description = self._generate_meta_description(opening_paragraph)
            
            # Keywords (5-8 relevant terms)
            keywords = self._generate_keywords(article)
            
            # Canonical URL
            canonical_url = self._generate_canonical_url(article)
            
            # Open Graph tags
            og_tags = {
                'og:title': headline,
                'og:description': meta_description,
                'og:type': 'article',
                'og:url': canonical_url,
                'og:site_name': self.site_name,
                'og:locale': 'en_US'
            }
            
            # Twitter Card tags
            twitter_tags = {
                'twitter:card': 'summary_large_image',
                'twitter:title': headline,
                'twitter:description': meta_description,
                'twitter:site': '@satirechronicle'
            }
            
            # Article-specific meta tags
            article_tags = {
                'article:section': category,
                'article:published_time': article.get('timestamp', ''),
                'article:author': article.get('byline', 'Staff Writer')
            }
            
            seo_metadata = {
                'title_tag': title_tag,
                'meta_description': meta_description,
                'keywords': keywords,
                'canonical_url': canonical_url,
                'open_graph': og_tags,
                'twitter_card': twitter_tags,
                'article_tags': article_tags
            }
            
            logger.debug(f"Generated SEO metadata for: '{headline[:30]}...'")
            return seo_metadata
            
        except Exception as e:
            logger.error(f"Failed to generate SEO metadata: {str(e)}")
            return self._get_default_seo_metadata()
    
    def generate_social_metadata(self, article: Dict) -> Dict:
        """
        Generate social media metadata for different platforms.
        
        Args:
            article: The satire article
            
        Returns:
            Dictionary containing social media metadata
        """
        try:
            headline = article.get('headline', '')
            opening_paragraph = article.get('opening_paragraph', '')
            
            # Extract first sentence for social previews
            first_sentence = self._extract_first_sentence(opening_paragraph)
            
            # Twitter/X (280 characters max)
            twitter_text = self._generate_twitter_text(headline, first_sentence)
            
            # Facebook (longer, more descriptive)
            facebook_text = self._generate_facebook_text(headline, opening_paragraph)
            
            # LinkedIn (more formal, business-focused)
            linkedin_text = self._generate_linkedin_text(headline, article)
            
            # Image metadata
            image_metadata = self._generate_image_metadata(article)
            
            social_metadata = {
                'twitter': {
                    'text': twitter_text,
                    'hashtags': self._generate_hashtags(article),
                    'image': image_metadata
                },
                'facebook': {
                    'text': facebook_text,
                    'image': image_metadata
                },
                'linkedin': {
                    'text': linkedin_text,
                    'image': image_metadata
                }
            }
            
            logger.debug(f"Generated social metadata for: '{headline[:30]}...'")
            return social_metadata
            
        except Exception as e:
            logger.error(f"Failed to generate social metadata: {str(e)}")
            return self._get_default_social_metadata()
    
    def generate_internal_metadata(self, article: Dict) -> Dict:
        """
        Generate internal metadata for tagging and organization.
        
        Args:
            article: The satire article
            
        Returns:
            Dictionary containing internal metadata
        """
        try:
            # Publishing metadata
            publishing_metadata = {
                'publish_date': article.get('timestamp', ''),
                'publish_time': datetime.now().strftime('%H:%M:%S'),
                'cycle': self._determine_publish_cycle(),
                'author': article.get('byline', 'Staff Writer'),
                'editor': 'Auto-Editor',
                'status': 'published'
            }
            
            # Category metadata
            category_metadata = {
                'primary_category': article.get('category', ''),
                'secondary_categories': self._determine_secondary_categories(article),
                'tags': self._generate_internal_tags(article)
            }
            
            # Source metadata
            source_metadata = {
                'original_source': self._extract_original_source(article),
                'original_headline': self._extract_original_headline(article),
                'original_url': self._extract_original_url(article),
                'satire_score': article.get('satire_score', 0)
            }
            
            # Entity metadata
            entity_metadata = {
                'people': self._extract_people_entities(article),
                'organizations': self._extract_organization_entities(article),
                'locations': self._extract_location_entities(article),
                'themes': self._extract_themes(article)
            }
            
            # Analytics metadata
            analytics_metadata = {
                'estimated_read_time': self._estimate_read_time(article),
                'content_length': self._calculate_content_length(article),
                'complexity_score': self._calculate_complexity_score(article)
            }
            
            internal_metadata = {
                'publishing': publishing_metadata,
                'categories': category_metadata,
                'source': source_metadata,
                'entities': entity_metadata,
                'analytics': analytics_metadata
            }
            
            logger.debug(f"Generated internal metadata for: '{article.get('headline', '')[:30]}...'")
            return internal_metadata
            
        except Exception as e:
            logger.error(f"Failed to generate internal metadata: {str(e)}")
            return self._get_default_internal_metadata()
    
    def _generate_meta_description(self, opening_paragraph: str) -> str:
        """Generate meta description from opening paragraph."""
        # Remove extra whitespace and limit to 155 characters
        cleaned = re.sub(r'\s+', ' ', opening_paragraph.strip())
        
        if len(cleaned) <= 155:
            return cleaned
        
        # Truncate at word boundary
        truncated = cleaned[:152]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            truncated = truncated[:last_space]
        
        return truncated + '...'
    
    def _generate_keywords(self, article: Dict) -> List[str]:
        """Generate 5-8 relevant keywords."""
        keywords = []
        
        # Add category
        category = article.get('category', '')
        if category:
            keywords.append(category)
        
        # Add satire-related keywords
        keywords.extend(['satire', 'news', 'comedy'])
        
        # Extract keywords from headline
        headline = article.get('headline', '').lower()
        headline_words = [word for word in headline.split() if len(word) > 3]
        keywords.extend(headline_words[:3])
        
        # Extract entities
        full_text = f"{headline} {article.get('opening_paragraph', '')}"
        
        # Look for capitalized words (potential entities)
        entities = re.findall(r'\b[A-Z][a-z]+\b', full_text)
        keywords.extend([entity.lower() for entity in entities[:2]])
        
        # Remove duplicates and limit to 8
        keywords = list(set(keywords))[:8]
        
        return keywords
    
    def _generate_canonical_url(self, article: Dict) -> str:
        """Generate canonical URL for the article."""
        headline = article.get('headline', '')
        
        # Create URL-friendly slug
        slug = re.sub(r'[^a-z0-9]+', '-', headline.lower())
        slug = slug.strip('-')
        
        # Add date prefix
        date_prefix = datetime.now().strftime('%Y/%m/%d')
        
        return f"{self.base_url}/{date_prefix}/{slug}"
    
    def _extract_first_sentence(self, text: str) -> str:
        """Extract the first sentence from text."""
        sentences = re.split(r'[.!?]+', text)
        if sentences:
            return sentences[0].strip()
        return text.strip()
    
    def _generate_twitter_text(self, headline: str, first_sentence: str) -> str:
        """Generate Twitter/X text (280 chars max)."""
        twitter_text = f"{headline} {first_sentence}"
        
        if len(twitter_text) <= 280:
            return twitter_text
        
        # Truncate to fit
        truncated = twitter_text[:277]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            truncated = truncated[:last_space]
        
        return truncated + '...'
    
    def _generate_facebook_text(self, headline: str, opening_paragraph: str) -> str:
        """Generate Facebook text (more descriptive)."""
        # Facebook allows longer text, so we can use more of the opening
        sentences = re.split(r'[.!?]+', opening_paragraph)
        
        if len(sentences) >= 2:
            facebook_text = f"{headline} {sentences[0].strip()}. {sentences[1].strip()}."
        else:
            facebook_text = f"{headline} {opening_paragraph}"
        
        return facebook_text
    
    def _generate_linkedin_text(self, headline: str, article: Dict) -> str:
        """Generate LinkedIn text (more formal, business-focused)."""
        category = article.get('category', '')
        
        # Professional framing
        if category == 'business':
            linkedin_text = f"Breaking: {headline}\n\nAnalysis of corporate strategy and market implications in today's business landscape."
        elif category == 'politics':
            linkedin_text = f"Political Analysis: {headline}\n\nExamination of policy decisions and their impact on governance and public policy."
        elif category == 'technology':
            linkedin_text = f"Tech Industry Update: {headline}\n\nAnalysis of technological developments and their implications for innovation and digital transformation."
        else:
            linkedin_text = f"Industry Analysis: {headline}\n\nExamination of current events and their broader implications."
        
        return linkedin_text
    
    def _generate_image_metadata(self, article: Dict) -> Dict:
        """Generate image metadata for social sharing."""
        # Use XKCD comic if available
        comic = article.get('xkcd_comic')
        
        if comic:
            return {
                'url': comic.get('img', ''),
                'alt_text': comic.get('alt', ''),
                'width': comic.get('width', 500),
                'height': comic.get('height', 400),
                'type': 'image/png'
            }
        
        # Fallback to default image
        return {
            'url': f"{self.base_url}/images/default-satire.jpg",
            'alt_text': "Political and corporate satire news",
            'width': 1200,
            'height': 630,
            'type': 'image/jpeg'
        }
    
    def _generate_hashtags(self, article: Dict) -> List[str]:
        """Generate relevant hashtags."""
        hashtags = ['#satire', '#news']
        
        category = article.get('category', '')
        if category:
            hashtags.append(f'#{category}')
        
        # Add topic-specific hashtags
        headline = article.get('headline', '').lower()
        
        if 'government' in headline or 'politics' in headline:
            hashtags.append('#politics')
        if 'company' in headline or 'business' in headline:
            hashtags.append('#business')
        if 'tech' in headline or 'technology' in headline:
            hashtags.append('#technology')
        
        return hashtags[:5]  # Limit to 5 hashtags
    
    def _determine_publish_cycle(self) -> str:
        """Determine which publish cycle this is."""
        current_hour = datetime.now().hour
        
        if 6 <= current_hour < 10:
            return "morning"
        elif 18 <= current_hour < 22:
            return "evening"
        else:
            return "other"
    
    def _determine_secondary_categories(self, article: Dict) -> List[str]:
        """Determine secondary categories for the article."""
        secondary = []
        headline = article.get('headline', '').lower()
        
        # Cross-category detection
        if 'government' in headline and 'business' in headline:
            secondary.extend(['politics', 'business'])
        if 'technology' in headline:
            secondary.append('technology')
        if 'health' in headline:
            secondary.append('health')
        
        return list(set(secondary))
    
    def _generate_internal_tags(self, article: Dict) -> List[str]:
        """Generate internal tags for organization."""
        tags = []
        
        # Satirical techniques
        tags.append('deadpan')
        tags.append('irony')
        
        # Target types
        headline = article.get('headline', '').lower()
        if 'ceo' in headline or 'company' in headline:
            tags.append('corporate-satire')
        if 'politician' in headline or 'government' in headline:
            tags.append('political-satire')
        if 'tech' in headline:
            tags.append('tech-satire')
        
        # Quality indicators
        satire_score = article.get('satire_score', 0)
        if satire_score >= 8:
            tags.append('high-quality')
        
        return tags
    
    def _extract_original_source(self, article: Dict) -> str:
        """Extract original news source."""
        original = article.get('original_article', {})
        return original.get('source_id', 'Unknown')
    
    def _extract_original_headline(self, article: Dict) -> str:
        """Extract original news headline."""
        original = article.get('original_article', {})
        return original.get('title', '')
    
    def _extract_original_url(self, article: Dict) -> str:
        """Extract original news URL."""
        original = article.get('original_article', {})
        return original.get('link', '')
    
    def _extract_people_entities(self, article: Dict) -> List[str]:
        """Extract people entities from article."""
        entities = []
        
        # Extract from expert quotes
        expert_quotes = article.get('expert_quotes', [])
        for quote in expert_quotes:
            expert = quote.get('expert', '')
            if expert:
                entities.append(expert)
        
        # Extract from headline and content
        full_text = f"{article.get('headline', '')} {article.get('opening_paragraph', '')}"
        
        # Look for titles followed by names
        name_patterns = [
            r'(?:CEO|President|Senator|Governor|Dr\.|Professor)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:said|announced|claimed|reported)'
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, full_text)
            entities.extend(matches)
        
        return list(set(entities))
    
    def _extract_organization_entities(self, article: Dict) -> List[str]:
        """Extract organization entities from article."""
        entities = []
        
        full_text = f"{article.get('headline', '')} {article.get('opening_paragraph', '')}"
        
        # Common organization patterns
        org_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Inc\.|Corp\.|LLC|Company|Corporation)',
            r'(?:Meta|Google|Amazon|Apple|Microsoft|Tesla|Netflix)',
            r'(?:Congress|Senate|House|White House|Pentagon|CIA|FBI)'
        ]
        
        for pattern in org_patterns:
            matches = re.findall(pattern, full_text)
            entities.extend(matches)
        
        return list(set(entities))
    
    def _extract_location_entities(self, article: Dict) -> List[str]:
        """Extract location entities from article."""
        entities = []
        
        full_text = f"{article.get('headline', '')} {article.get('opening_paragraph', '')}"
        
        # Common location patterns
        location_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:City|State|Country)',
            r'(?:Washington|New York|California|Texas|Florida|Chicago|Boston)',
            r'United States|America|U\.S\.'
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, full_text)
            entities.extend(matches)
        
        return list(set(entities))
    
    def _extract_themes(self, article: Dict) -> List[str]:
        """Extract thematic elements from article."""
        themes = []
        
        headline = article.get('headline', '').lower()
        full_text = self._get_full_text(article).lower()
        
        # Theme detection
        theme_keywords = {
            'hypocrisy': ['hypocrisy', 'contradiction', 'double standard', 'claims while'],
            'corporate-speak': ['synergy', 'paradigm', 'leverage', 'optimize', 'streamline'],
            'political-theater': ['bipartisan', 'fiscal responsibility', 'government waste'],
            'technological-irony': ['innovation', 'disruption', 'transformation'],
            'economic-inequality': ['shareholder value', 'cost savings', 'efficiency']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in full_text for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _estimate_read_time(self, article: Dict) -> int:
        """Estimate reading time in minutes."""
        full_text = self._get_full_text(article)
        word_count = len(full_text.split())
        
        # Average reading speed: 200 words per minute
        read_time = max(1, round(word_count / 200))
        
        return read_time
    
    def _calculate_content_length(self, article: Dict) -> int:
        """Calculate content length in characters."""
        return len(self._get_full_text(article))
    
    def _calculate_complexity_score(self, article: Dict) -> float:
        """Calculate content complexity score (0-1)."""
        full_text = self._get_full_text(article)
        
        # Simple complexity metrics
        avg_sentence_length = self._calculate_avg_sentence_length(full_text)
        complex_words = self._count_complex_words(full_text)
        
        # Normalize to 0-1 scale
        complexity = min(1.0, (avg_sentence_length / 20 + complex_words / 100) / 2)
        
        return round(complexity, 2)
    
    def _get_full_text(self, article: Dict) -> str:
        """Get full text of article for analysis."""
        parts = [
            article.get('headline', ''),
            article.get('opening_paragraph', ''),
            ' '.join(article.get('body_paragraphs', [])),
            ' '.join([quote.get('quote', '') for quote in article.get('expert_quotes', [])])
        ]
        return ' '.join(parts)
    
    def _calculate_avg_sentence_length(self, text: str) -> float:
        """Calculate average sentence length."""
        sentences = re.split(r'[.!?]+', text)
        if not sentences:
            return 0
        
        total_words = sum(len(sentence.split()) for sentence in sentences)
        return total_words / len(sentences)
    
    def _count_complex_words(self, text: str) -> int:
        """Count complex words (3+ syllables, simplified)."""
        words = text.lower().split()
        complex_count = 0
        
        for word in words:
            # Simplified syllable count based on vowel groups
            vowel_groups = len(re.findall(r'[aeiou]+', word))
            if vowel_groups >= 3:
                complex_count += 1
        
        return complex_count
    
    def _get_default_seo_metadata(self) -> Dict:
        """Get default SEO metadata for fallback."""
        return {
            'title_tag': f'Satire News | {self.site_name}',
            'meta_description': 'Deadpan satire of current events and news.',
            'keywords': ['satire', 'news', 'comedy', 'politics', 'business'],
            'canonical_url': self.base_url,
            'open_graph': {},
            'twitter_card': {},
            'article_tags': {}
        }
    
    def _get_default_social_metadata(self) -> Dict:
        """Get default social metadata for fallback."""
        return {
            'twitter': {'text': '', 'hashtags': [], 'image': {}},
            'facebook': {'text': '', 'image': {}},
            'linkedin': {'text': '', 'image': {}}
        }
    
    def _get_default_internal_metadata(self) -> Dict:
        """Get default internal metadata for fallback."""
        return {
            'publishing': {},
            'categories': {},
            'source': {},
            'entities': {},
            'analytics': {}
        }
