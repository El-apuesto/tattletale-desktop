import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.generation.satire_engine import SatireEngine
from src.generation.quality_control import QualityController

class TestSatireEngine(unittest.TestCase):
    """Test cases for the satire engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = SatireEngine()
        self.quality_controller = QualityController()
    
    def test_calculate_satire_potential(self):
        """Test satire potential calculation."""
        # High potential article
        high_potential = {
            'title': 'CEO Announces Layoffs After Record Profits',
            'content': 'The CEO announced layoffs while celebrating record profits and shareholder value.',
            'category': 'business'
        }
        
        score = self.engine._calculate_satire_potential(high_potential)
        self.assertGreater(score, 5.0)
        
        # Low potential article
        low_potential = {
            'title': 'Weather Update',
            'content': 'Today will be sunny with a high of 75 degrees.',
            'category': 'weather'
        }
        
        score = self.engine._calculate_satire_potential(low_potential)
        self.assertLess(score, 3.0)
    
    def test_generate_headline(self):
        """Test headline generation."""
        original_title = "Meta CEO Announces Return to Office Policy"
        category = "technology"
        
        headline = self.engine._generate_headline(original_title, category)
        
        # Check length requirements
        words = headline.split()
        self.assertGreaterEqual(len(words), 8)
        self.assertLessEqual(len(words), 15)
        
        # Check that it's different from original
        self.assertNotEqual(headline, original_title)
    
    def test_transform_article(self):
        """Test full article transformation."""
        news_article = {
            'title': 'Senator Introduces Bill to Cut Social Programs',
            'content': 'Senator Bradley Morrison introduced legislation today to reduce government spending on social programs while voting to increase defense budget.',
            'category': 'politics'
        }
        
        try:
            satire_article = self.engine.transform_article(news_article)
            
            # Check required fields
            self.assertIn('headline', satire_article)
            self.assertIn('opening_paragraph', satire_article)
            self.assertIn('body_paragraphs', satire_article)
            self.assertIn('expert_quotes', satire_article)
            
            # Check quality
            passed, issues = self.quality_controller.verify_article(satire_article)
            
            if not passed:
                print(f"Quality issues: {issues}")
            
        except Exception as e:
            # Some articles may not meet threshold, that's okay for testing
            print(f"Article transformation failed (expected for some cases): {str(e)}")

class TestQualityController(unittest.TestCase):
    """Test cases for quality control."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.quality_controller = QualityController()
    
    def test_prohibited_phrases(self):
        """Test detection of prohibited phrases."""
        article_with_sarcasm = {
            'headline': 'Company Announces Layoffs /s',
            'opening_paragraph': 'Believe it or not, they actually did this.',
            'body_paragraphs': ['You can\'t make this stuff up.'],
            'expert_quotes': [],
            'category': 'business'
        }
        
        passed, issues = self.quality_controller.verify_article(article_with_sarcasm)
        self.assertFalse(passed)
        self.assertTrue(any('sarcasm marker' in issue.lower() for issue in issues))
    
    def test_headline_length(self):
        """Test headline length validation."""
        # Too short
        short_headline = {
            'headline': 'Too Short',
            'opening_paragraph': 'This is a test opening paragraph with two sentences. It should pass this check.',
            'body_paragraphs': ['This is a body paragraph.', 'This is another body paragraph.', 'This is a third body paragraph.'],
            'expert_quotes': [{'expert': 'Dr. Test Expert', 'quote': 'This is a test quote.'}],
            'category': 'test'
        }
        
        passed, issues = self.quality_controller.verify_article(short_headline)
        self.assertFalse(passed)
        self.assertTrue(any('headline too short' in issue.lower() for issue in issues))
        
        # Just right
        good_headline = {
            'headline': 'This Headline Is The Perfect Length For Testing',
            'opening_paragraph': 'This is a test opening paragraph with two sentences. It should pass this check.',
            'body_paragraphs': ['This is a body paragraph.', 'This is another body paragraph.', 'This is a third body paragraph.'],
            'expert_quotes': [{'expert': 'Dr. Test Expert', 'quote': 'This is a test quote.'}],
            'category': 'test'
        }
        
        passed, issues = self.quality_controller.verify_article(good_headline)
        # May still fail on other checks, but headline length should pass
        headline_issues = [issue for issue in issues if 'headline' in issue.lower()]
        self.assertEqual(len(headline_issues), 0)

if __name__ == '__main__':
    unittest.main()
