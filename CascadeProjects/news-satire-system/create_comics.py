#!/usr/bin/env python3
"""
Quick script to create custom comics for articles
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.generation.comic_generator import ComicGenerator
from src.storage.archive import ArchiveManager

def create_comic_for_article(article_headline: str, category: str = "general"):
    """Create a comic for a sample article."""
    
    # Create sample article
    sample_article = {
        'headline': article_headline,
        'opening_paragraph': f"This is a satirical take on {article_headline.lower()}. The situation reveals the inherent contradictions in modern corporate and political life.",
        'body_paragraphs': [
            "Experts suggest this represents a fundamental shift in how we understand the issue.",
            "The implications are far-reaching and affect everyone involved.",
            "Only time will tell how this situation will resolve itself."
        ],
        'expert_quotes': [
            {
                'expert': 'Dr. Sarah Mitchell',
                'quote': 'This is a classic example of systemic dysfunction.',
                'affiliation': 'Institute for Critical Thinking'
            }
        ],
        'category': category,
        'satire_score': 8.5,
        'byline': 'Staff Writer',
        'timestamp': '2024-01-15 10:00:00'
    }
    
    # Generate comic
    generator = ComicGenerator()
    comic_metadata = generator.generate_comic(sample_article)
    
    print(f"✅ Comic created: {comic_metadata['filename']}")
    print(f"📍 URL: {comic_metadata['url']}")
    print(f"🎭 Characters: {', '.join(comic_metadata.get('characters', []))}")
    print(f"💬 Situation: {comic_metadata.get('situation', 'Unknown')}")
    print(f"📝 Dialogue: {' | '.join(comic_metadata.get('dialogue', []))}")
    
    return comic_metadata

def create_sample_comics():
    """Create sample comics for different categories."""
    
    sample_articles = [
        {
            'headline': 'CEO Announces Record Layoffs After Record Profits',
            'category': 'business'
        },
        {
            'headline': 'Politician Discovers Government Waste Only In Programs That Help Poor People',
            'category': 'politics'
        },
        {
            'headline': 'Tech CEO Who Built Remote Tools Demands Return To Office',
            'category': 'technology'
        },
        {
            'headline': 'Company Celebrates Innovation By Firing Innovation Team',
            'category': 'business'
        },
        {
            'headline': 'Senator Claims To Support Small Business While Voting For Big Corporations',
            'category': 'politics'
        }
    ]
    
    generator = ComicGenerator()
    
    print("🎨 Creating sample comics...\n")
    
    for i, article_data in enumerate(sample_articles, 1):
        print(f"📰 Article {i}: {article_data['headline']}")
        
        comic_metadata = generator.generate_comic({
            'headline': article_data['headline'],
            'opening_paragraph': f"Breaking news about {article_data['headline'].lower()}.",
            'category': article_data['category']
        })
        
        print(f"   ✅ Generated: {comic_metadata['filename']}")
        print(f"   🎭 Style: {comic_metadata.get('style', 'unknown')}")
        print(f"   💬 Dialogue: {len(comic_metadata.get('dialogue', []))} panels")
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Create comic for custom headline
        headline = ' '.join(sys.argv[1:])
        category = "general"
        
        if "--business" in sys.argv:
            category = "business"
        elif "--politics" in sys.argv:
            category = "politics"
        elif "--tech" in sys.argv:
            category = "technology"
        
        # Remove category flags from headline
        headline = headline.replace("--business", "").replace("--politics", "").replace("--tech", "").strip()
        
        create_comic_for_article(headline, category)
    else:
        # Create sample comics
        create_sample_comics()
