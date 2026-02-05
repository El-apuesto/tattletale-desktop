# Automated News Satire System

A sophisticated system that transforms real news into deadpan satire, maintaining the aesthetic dignity of premium journalism while revealing uncomfortable truths about power, hypocrisy, and systemic dysfunction.

## System Overview

The system operates on a strict 12-hour cycle (8 AM/8 PM CST) to:
- Fetch real news from NewsData.io (previous 12 hours)
- Transform stories into deadpan satire using advanced NLP
- Integrate XKCD comics for visual commentary
- Publish high-quality content with rigorous quality control

## Core Philosophy

The best satire doesn't announce itself. It presents absurdity as normalcy and trusts the reader to feel the vertigo. Every article is written as if genuinely doing straightforward reporting—the reader's realization that reality itself has become satirical is the punchline.

## Key Features

- **Automated Content Generation**: Real news → Deadpan satire
- **Quality Control**: 20-point checklist for every article
- **XKCD Integration**: Relevant comics with proper attribution
- **Archive System**: Indefinite storage with intelligent tagging
- **Error Handling**: Robust retry mechanisms and fallbacks
- **SEO Optimization**: Complete metadata generation
- **Social Media Integration**: Platform-specific preview generation

## Project Structure

```
news-satire-system/
├── src/
│   ├── api/
│   │   ├── newsdata.py          # NewsData.io integration
│   │   └── xkcd.py              # XKCD API integration
│   ├── generation/
│   │   ├── satire_engine.py     # Core satire generation logic
│   │   ├── quality_control.py   # Quality verification system
│   │   └── templates.py         # Article templates
│   ├── publishing/
│   │   ├── scheduler.py         # 8 AM/8 PM cycle management
│   │   └── metadata.py          # SEO and social metadata
│   ├── storage/
│   │   ├── archive.py           # Article storage and retrieval
│   │   └── tagging.py           # Intelligent tagging system
│   └── utils/
│       ├── error_handling.py    # Retry mechanisms
│       └── config.py            # Configuration management
├── tests/
├── logs/
├── data/
│   └── articles/
└── requirements.txt
```

## Installation & Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure API keys in `src/utils/config.py`
4. Set up the scheduler: `python src/publishing/scheduler.py`

## API Keys Required

- **NewsData.io**: `pub_39e106ccf96046c5bfe5d6dd1d9f6bed`
- **XKCD**: Free (no API key required)

## Quality Standards

Every article must pass a 20-point quality control checklist covering:
- Content quality (verifiable news, deadpan tone, intelligent humor)
- Technical quality (structure, grammar, AP style)
- Comic integration (proper display and attribution)
- Metadata completeness (SEO, social media, internal tags)

## Error Handling

- NewsData.io failures: Log error, retry after 5 minutes, send alert
- XKCD API failures: Use cached comic or skip comic integration
- Generation failures: Log for manual review, continue with remaining stories
- Low quality stories: Skip rather than publish mediocre content

## License

Proprietary - Internal use only
