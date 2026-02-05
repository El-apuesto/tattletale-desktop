import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "pub_39e106ccf96046c5bfe5d6dd1d9f6bed")
    NEWSDATA_BASE_URL = "https://newsdata.io/api/1/news"
    
    XKCD_BASE_URL = "https://xkcd.com"
    XKCD_INFO_URL = "https://xkcd.com/info.0.json"
    
    # Publishing Schedule
    PUBLISH_TIMES = ["08:00", "20:00"]  # 8 AM and 8 PM CST
    TIMEZONE = "America/Chicago"
    
    # Content Generation
    MIN_ARTICLES_PER_CYCLE = 3
    MAX_ARTICLES_PER_CYCLE = 8
    SATIRE_THRESHOLD = 7.0  # Minimum quality score (0-10)
    
    # Quality Control
    HEADLINE_MIN_WORDS = 8
    HEADLINE_MAX_WORDS = 15
    OPENING_PARAGRAPH_MIN_SENTENCES = 2
    OPENING_PARAGRAPH_MAX_SENTENCES = 3
    BODY_MIN_PARAGRAPHS = 3
    BODY_MAX_PARAGRAPHS = 5
    
    # Retry Configuration
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 300  # 5 minutes
    
    # Storage
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///articles.db")
    ARTICLES_DIR = "data/articles"
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_DIR = "logs"
    
    # OpenAI (for advanced content generation)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-4-turbo-preview"
