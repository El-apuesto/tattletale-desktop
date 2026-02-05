import re
from typing import Dict, List, Tuple
from ..utils.config import Config
from ..utils.error_handling import QualityControlError
import logging

logger = logging.getLogger(__name__)

class QualityController:
    """
    Quality control system for verifying satire articles meet all standards.
    """
    
    def __init__(self):
        self.prohibited_phrases = self._load_prohibited_phrases()
        self.required_patterns = self._load_required_patterns()
        self.style_guidelines = self._load_style_guidelines()
    
    def verify_article(self, article: Dict) -> Tuple[bool, List[str]]:
        """
        Verify article meets all quality control requirements.
        
        Args:
            article: Generated satire article
            
        Returns:
            Tuple of (passed, list_of_issues)
        """
        issues = []
        
        # Content Quality Checks
        content_issues = self._check_content_quality(article)
        issues.extend(content_issues)
        
        # Technical Quality Checks
        technical_issues = self._check_technical_quality(article)
        issues.extend(technical_issues)
        
        # Style and Tone Checks
        style_issues = self._check_style_and_tone(article)
        issues.extend(style_issues)
        
        # Metadata Checks
        metadata_issues = self._check_metadata(article)
        issues.extend(metadata_issues)
        
        passed = len(issues) == 0
        
        if passed:
            logger.info(f"Article passed quality control: '{article['headline'][:50]}...'")
        else:
            logger.warning(f"Article failed quality control with {len(issues)} issues: {issues}")
        
        return passed, issues
    
    def _check_content_quality(self, article: Dict) -> List[str]:
        """Check content quality requirements."""
        issues = []
        
        # Check based on real news event
        if not article.get('original_article'):
            issues.append("Missing original article reference")
        
        # Check deadpan tone (no sarcasm markers)
        full_text = self._get_full_text(article)
        for prohibited in self.prohibited_phrases['sarcasm_markers']:
            if prohibited.lower() in full_text.lower():
                issues.append(f"Contains sarcasm marker: '{prohibited}'")
        
        # Check for winking language
        for prohibited in self.prohibited_phrases['winking_language']:
            if prohibited.lower() in full_text.lower():
                issues.append(f"Contains winking language: '{prohibited}'")
        
        # Check for meta-commentary
        for prohibited in self.prohibited_phrases['meta_commentary']:
            if prohibited.lower() in full_text.lower():
                issues.append(f"Contains meta-commentary: '{prohibited}'")
        
        # Check for intelligent humor (at least 2 layers of meaning)
        meaning_layers = self._count_meaning_layers(article)
        if meaning_layers < 2:
            issues.append(f"Insufficient layers of meaning: {meaning_layers} (minimum 2 required)")
        
        # Check for punching up vs down
        if self._punches_down(article):
            issues.append("Article punches down at victims rather than up at power structures")
        
        return issues
    
    def _check_technical_quality(self, article: Dict) -> List[str]:
        """Check technical quality requirements."""
        issues = []
        
        # Check headline length
        headline = article.get('headline', '')
        headline_words = len(headline.split())
        if headline_words < Config.HEADLINE_MIN_WORDS:
            issues.append(f"Headline too short: {headline_words} words (minimum {Config.HEADLINE_MIN_WORDS})")
        if headline_words > Config.HEADLINE_MAX_WORDS:
            issues.append(f"Headline too long: {headline_words} words (maximum {Config.HEADLINE_MAX_WORDS})")
        
        # Check opening paragraph length
        opening = article.get('opening_paragraph', '')
        opening_sentences = len(re.split(r'[.!?]+', opening))
        if opening_sentences < Config.OPENING_PARAGRAPH_MIN_SENTENCES:
            issues.append(f"Opening paragraph too short: {opening_sentences} sentences (minimum {Config.OPENING_PARAGRAPH_MIN_SENTENCES})")
        if opening_sentences > Config.OPENING_PARAGRAPH_MAX_SENTENCES:
            issues.append(f"Opening paragraph too long: {opening_sentences} sentences (maximum {Config.OPENING_PARAGRAPH_MAX_SENTENCES})")
        
        # Check body paragraph count
        body_paragraphs = article.get('body_paragraphs', [])
        if len(body_paragraphs) < Config.BODY_MIN_PARAGRAPHS:
            issues.append(f"Too few body paragraphs: {len(body_paragraphs)} (minimum {Config.BODY_MIN_PARAGRAPHS})")
        if len(body_paragraphs) > Config.BODY_MAX_PARAGRAPHS:
            issues.append(f"Too many body paragraphs: {len(body_paragraphs)} (maximum {Config.BODY_MAX_PARAGRAPHS})")
        
        # Check for expert quotes
        expert_quotes = article.get('expert_quotes', [])
        if len(expert_quotes) < 1:
            issues.append("Missing expert quotes (minimum 1 required)")
        if len(expert_quotes) > 2:
            issues.append(f"Too many expert quotes: {len(expert_quotes)} (maximum 2)")
        
        # Check for prohibited phrases
        for prohibited in self.prohibited_phrases['sources_phrases']:
            if prohibited.lower() in self._get_full_text(article).lower():
                issues.append(f"Contains prohibited phrase: '{prohibited}'")
        
        # Check grammar and style (basic checks)
        grammar_issues = self._check_grammar(article)
        issues.extend(grammar_issues)
        
        return issues
    
    def _check_style_and_tone(self, article: Dict) -> List[str]:
        """Check style and tone requirements."""
        issues = []
        
        full_text = self._get_full_text(article)
        
        # Check for consistent deadpan tone
        if not self._maintains_deadpan_tone(full_text):
            issues.append("Article does not maintain consistent deadpan tone")
        
        # Check for plausible names and titles
        if not self._has_plausible_names(article):
            issues.append("Article contains implausible names or titles")
        
        # Check AP Style compliance (basic)
        ap_style_issues = self._check_ap_style(full_text)
        issues.extend(ap_style_issues)
        
        # Check for intelligent humor vs cheap shots
        if self._contains_cheap_shots(full_text):
            issues.append("Article contains cheap shots rather than intelligent humor")
        
        return issues
    
    def _check_metadata(self, article: Dict) -> List[str]:
        """Check metadata requirements."""
        issues = []
        
        # Check byline
        if not article.get('byline'):
            issues.append("Missing byline")
        
        # Check timestamp
        if not article.get('timestamp'):
            issues.append("Missing timestamp")
        
        # Check category
        if not article.get('category'):
            issues.append("Missing category tag")
        
        # Check satire score
        if not article.get('satire_score'):
            issues.append("Missing satire score")
        elif article['satire_score'] < Config.SATIRE_THRESHOLD:
            issues.append(f"Satire score too low: {article['satire_score']} (minimum {Config.SATIRE_THRESHOLD})")
        
        return issues
    
    def _get_full_text(self, article: Dict) -> str:
        """Get the full text of the article."""
        parts = [
            article.get('headline', ''),
            article.get('opening_paragraph', ''),
            ' '.join(article.get('body_paragraphs', [])),
            ' '.join([quote.get('quote', '') for quote in article.get('expert_quotes', [])])
        ]
        return ' '.join(parts)
    
    def _count_meaning_layers(self, article: Dict) -> int:
        """
        Count layers of meaning/irony in the article.
        """
        layers = 0
        full_text = self._get_full_text(article).lower()
        
        # Layer 1: Surface contradiction
        contradiction_words = ['but', 'however', 'while', 'although', 'despite']
        if any(word in full_text for word in contradiction_words):
            layers += 1
        
        # Layer 2: Systemic hypocrisy
        hypocrisy_patterns = [
            r'claims.*while.*doing',
            r'announces.*but.*continues',
            r'insists.*despite.*evidence'
        ]
        for pattern in hypocrisy_patterns:
            if re.search(pattern, full_text):
                layers += 1
                break
        
        # Layer 3: Institutional irony
        institutional_patterns = [
            r'government.*waste.*except.*defense',
            r'company.*values.*except.*profits',
            r'technology.*connection.*by.*eliminating.*human'
        ]
        for pattern in institutional_patterns:
            if re.search(pattern, full_text):
                layers += 1
                break
        
        return layers
    
    def _punches_down(self, article: Dict) -> bool:
        """
        Check if article punches down at victims rather than up at power structures.
        """
        full_text = self._get_full_text(article).lower()
        
        # Check for punching down indicators
        punching_down_patterns = [
            r'poor.*people.*deserve',
            r'homeless.*should.*just',
            r'immigrants.*are.*problem',
            r'victims.*were.*asking',
            r'workers.*should.*work.*harder'
        ]
        
        for pattern in punching_down_patterns:
            if re.search(pattern, full_text):
                return True
        
        # Check for punching up indicators (good)
        punching_up_patterns = [
            r'ceo.*claims.*while',
            r'politician.*insists.*despite',
            r'company.*announces.*but',
            r'government.*waste.*except'
        ]
        
        for pattern in punching_up_patterns:
            if re.search(pattern, full_text):
                return False
        
        # Default to not punching down if unclear
        return False
    
    def _maintains_deadpan_tone(self, text: str) -> bool:
        """Check if text maintains deadpan tone."""
        # Check for emotional language (should be minimal)
        emotional_words = [
            'outrageous', 'horrifying', 'disgusting', 'shocking',
            'amazing', 'wonderful', 'fantastic', 'terrible'
        ]
        
        emotional_count = sum(1 for word in emotional_words if word in text.lower())
        
        # Allow minimal emotional language
        return emotional_count <= 1
    
    def _has_plausible_names(self, article: Dict) -> bool:
        """Check if article has plausible names and titles."""
        # Check expert quotes for plausible names
        expert_quotes = article.get('expert_quotes', [])
        
        for quote in expert_quotes:
            expert = quote.get('expert', '')
            
            # Check if name follows basic pattern
            if not re.match(r'^(Dr\.|Professor|Mr\.|Ms\.)\s+[A-Z][a-z]+\s+[A-Z][a-z]+', expert):
                return False
        
        return True
    
    def _check_grammar(self, article: Dict) -> List[str]:
        """Check basic grammar issues."""
        issues = []
        full_text = self._get_full_text(article)
        
        # Check for sentence fragments (basic)
        sentences = re.split(r'[.!?]+', full_text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 0 and len(sentence.split()) < 3:
                # Very short sentences might be fragments
                if not re.match(r'^[A-Z]', sentence):
                    issues.append(f"Possible sentence fragment: '{sentence}'")
        
        # Check for double spaces
        if '  ' in full_text:
            issues.append("Contains double spaces")
        
        # Check for missing punctuation at end of sentences
        if re.search(r'[a-zA-Z]\s+[A-Z]', full_text):
            issues.append("Missing punctuation between sentences")
        
        return issues
    
    def _check_ap_style(self, text: str) -> List[str]:
        """Check basic AP Style compliance."""
        issues = []
        
        # Check for Oxford commas (AP style doesn't use them in simple series)
        if re.search(r'\w,\s+\w,\s+and\s+\w', text):
            issues.append("Contains Oxford comma (not AP style)")
        
        # Check for numbers under 10 not spelled out
        if re.search(r'\b[0-9]\b', text):
            issues.append("Contains single-digit number not spelled out (AP style)")
        
        # Check for time formatting (should be 8 a.m., not 8:00 AM)
        if re.search(r'\d{1,2}:\d{2}\s*[AP]M', text):
            issues.append("Time not in AP style format")
        
        return issues
    
    def _contains_cheap_shots(self, text: str) -> bool:
        """Check for cheap shots vs intelligent humor."""
        cheap_shot_patterns = [
            r'florida.*man',
            r'karen.*wants.*manager',
            r'\bboomer\b',
            r'\bmillennial\b.*\b avocado\b',
            r'\bgen.*z\b.*\b tiktok\b'
        ]
        
        for pattern in cheap_shot_patterns:
            if re.search(pattern, text.lower()):
                return True
        
        return False
    
    def _load_prohibited_phrases(self) -> Dict[str, List[str]]:
        """Load lists of prohibited phrases."""
        return {
            'sarcasm_markers': [
                '/s', 'yeah right', 'sure thing', 'wink wink', 'nudge nudge',
                'not', 'as if', 'whatever', 'obviously', 'clearly'
            ],
            'winking_language': [
                'believe it or not', 'you can\'t make this up', 'strangely enough',
                'ironically', 'coincidentally', 'amazingly', 'surprisingly'
            ],
            'meta_commentary': [
                'meanwhile', 'in a shocking turn of events', 'in other news',
                'speaking of which', 'on that note', 'as if that weren\'t enough'
            ],
            'sources_phrases': [
                'based on sources', 'research shows', 'studies indicate',
                'experts say', 'analysts believe', 'according to reports'
            ]
        }
    
    def _load_required_patterns(self) -> Dict[str, List[str]]:
        """Load required patterns for articles."""
        return {
            'headline_patterns': [
                r'[A-Z][a-z]+.*[A-Z][a-z]+',  # At least two capitalized words
                r'\b(announces|claims|reports|discovers|reveals)\b'  # Action words
            ],
            'content_patterns': [
                r'[.!?]',  # Must have punctuation
                r'\b(the|and|or|but)\b',  # Basic connecting words
            ]
        }
    
    def _load_style_guidelines(self) -> Dict:
        """Load style guidelines."""
        return {
            'tone': 'deadpan',
            'perspective': 'serious journalist',
            'target': 'power structures',
            'method': 'revealing truth through observation'
        }
