# Custom Comic Creation Guide

## Overview

The system includes a **Custom Comic Generator** that creates original comics for your satire articles instead of using XKCD. This gives you complete control over the visual style and content.

## Quick Start

### 1. Create Your First Comic

```bash
python create_comics.py "CEO Announces Layoffs After Record Profits" --business
```

### 2. Create Sample Comics

```bash
python create_comics.py
```

### 3. Set Up Assets

```bash
python assets/create_sample_templates.py
```

## Features

### 🎭 **Character Types**
- **CEO**: Business executive with briefcase
- **Politician**: Formal attire with microphone
- **Tech Bro**: Casual tech worker with laptop
- **Worker**: Regular employee at desk
- **Expert**: Academic with books

### 📰 **Comic Templates**
- **Single Panel**: 800x600px
- **Two Panel**: 800x400px (side by side)
- **Three Panel**: 900x300px (horizontal strip)
- **Four Panel**: 800x800px (2x2 grid)

### 🎨 **Visual Styles**
- **Newspaper**: Classic black and white, formal
- **Bold**: Thick lines, prominent text
- **Minimalist**: Clean, modern look

## How It Works

### 1. **Article Analysis**
```python
# The system analyzes your article for:
# - Main characters (CEO, politician, etc.)
# - Key concepts (hypocrisy, corporate speak)
# - Situation type (layoff announcement, office mandate)
# - Dialogue opportunities
```

### 2. **Template Selection**
```python
# Based on article complexity:
# 1-2 dialogue lines → Single/Two panel
# 3 dialogue lines → Three panel
# 4+ dialogue lines → Four panel
```

### 3. **Dialogue Generation**
```python
# Situation-specific dialogue templates:
'layoff_announcement': [
    "We're optimizing our human resources.",
    "This is about shareholder value.",
    "You're not being fired, you're being liberated."
]
```

### 4. **Visual Creation**
```python
# Generates panels with:
# - Character positioning
# - Text bubbles with dialogue
# - Proper borders and styling
# - Automatic text wrapping
```

## Integration with Main System

### Update the Publishing Scheduler

```python
# In src/publishing/scheduler.py

from src.generation.comic_generator import ComicGenerator

class PublishingScheduler:
    def __init__(self):
        # ... existing init code
        self.comic_generator = ComicGenerator()
    
    def add_comics_to_articles(self, articles: List[Dict]) -> List[Dict]:
        """Add custom comics to articles."""
        
        for article in articles:
            try:
                # Generate custom comic
                comic_metadata = self.comic_generator.generate_comic(article)
                
                if comic_metadata:
                    article['custom_comic'] = comic_metadata
                    article['comic_html'] = self.comic_generator.get_comic_html(comic_metadata)
                    logger.info(f"Added custom comic to article")
                else:
                    # Fallback to XKCD
                    comic = self.xkcd_api.find_relevant_comic(keywords, category)
                    article['xkcd_comic'] = comic
                    
            except Exception as e:
                logger.error(f"Failed to generate custom comic: {str(e)}")
                # Use XKCD as fallback
                # ... existing XKCD code
        
        return articles
```

## Customization Options

### 1. **Add New Characters**

```python
# In src/generation/comic_generator.py

self.characters['journalist'] = {
    'description': 'News reporter with notepad',
    'props': ['microphone', 'camera', 'notepad'],
    'expressions': ['investigating', 'reporting', 'interviewing']
}
```

### 2. **Create New Situations**

```python
# Add new dialogue templates
self.dialogue_templates['product_launch'] = [
    "This will revolutionize the industry!",
    "We're disrupting the status quo.",
    "The synergy is unprecedented."
]
```

### 3. **Custom Styles**

```python
# Add new visual style
self.styles['retro'] = {
    'bg_color': (255, 248, 220),  # Antique white
    'line_color': (139, 69, 19),   # Brown
    'text_color': (0, 0, 0),       # Black
    'font_size': 22,
    'panel_border': 3
}
```

## Advanced Features

### 1. **Character Sprites**

Create detailed character sprites:

```python
def create_detailed_character(self, character_type: str, expression: str):
    """Create detailed character with expressions."""
    
    if character_type == 'ceo':
        # Draw CEO with specific expression
        if expression == 'smug':
            # Add confident smile
        elif expression == 'worried':
            # Add concerned look
```

### 2. **Background Elements**

Add backgrounds to panels:

```python
def add_background_elements(self, panel, situation: str):
    """Add relevant background elements."""
    
    if situation == 'office_mandate':
        # Draw office background
        # Add desks, computers, etc.
    elif situation == 'political_deadlock':
        # Draw capitol building background
```

### 3. **Props and Objects**

Add interactive elements:

```python
def add_props(self, panel, character: str, props: List[str]):
    """Add character props."""
    
    if 'briefcase' in props:
        # Draw briefcase in character's hand
    if 'microphone' in props:
        # Draw microphone
```

## File Structure

```
assets/
├── comic_templates/
│   ├── single_panel.png
│   ├── two_panel.png
│   ├── three_panel.png
│   └── four_panel.png
├── characters/
│   ├── ceo.png
│   ├── politician.png
│   ├── tech_worker.png
│   └── worker.png
└── fonts/
    ├── comic_font.ttf
    └── bold_font.ttf

data/generated_comics/
├── ceo_announces_layoffs_20240115_143022.png
├── politician_discovers_waste_20240115_143045.png
└── ...
```

## Quality Control

### Comic Validation

```python
def validate_comic(self, comic_metadata: Dict) -> Tuple[bool, List[str]]:
    """Validate generated comic quality."""
    
    issues = []
    
    # Check file exists
    if not os.path.exists(comic_metadata.get('filename', '')):
        issues.append("Comic file not found")
    
    # Check dimensions
    if comic_metadata.get('width', 0) < 400:
        issues.append("Comic too small")
    
    # Check dialogue length
    dialogue = comic_metadata.get('dialogue', [])
    if len(dialogue) == 0:
        issues.append("No dialogue generated")
    
    return len(issues) == 0, issues
```

### Manual Review

Comics that fail validation are marked for manual review:

```python
# Saved to data/manual_review/comics/
{
    "comic_metadata": {...},
    "article": {...},
    "validation_issues": ["No dialogue generated"],
    "review_status": "pending"
}
```

## Performance Optimization

### 1. **Template Caching**

```python
# Cache generated templates
template_cache = {}

def get_cached_template(self, template_name: str):
    if template_name not in template_cache:
        template_cache[template_name] = self.load_template(template_name)
    return template_cache[template_name]
```

### 2. **Batch Generation**

```python
def generate_comics_batch(self, articles: List[Dict]) -> List[Dict]:
    """Generate comics for multiple articles efficiently."""
    
    comics = []
    for article in articles:
        comic = self.generate_comic(article)
        comics.append(comic)
    
    return comics
```

### 3. **Background Processing**

```python
import asyncio

async def generate_comic_async(self, article: Dict):
    """Generate comic asynchronously."""
    
    loop = asyncio.get_event_loop()
    comic = await loop.run_in_executor(None, self.generate_comic, article)
    return comic
```

## Troubleshooting

### Common Issues

1. **Font Not Found**
   ```python
   # Solution: Use default font
   try:
       font = ImageFont.truetype("arial.ttf", 24)
   except:
       font = ImageFont.load_default()
   ```

2. **Text Overflow**
   ```python
   # Solution: Implement text wrapping
   lines = self.wrap_text(text, font, max_width)
   ```

3. **Small Output**
   ```python
   # Solution: Ensure minimum dimensions
   width = max(width, 400)
   height = max(height, 300)
   ```

### Debug Mode

```python
# Enable debug logging
import logging
logging.getLogger('src.generation.comic_generator').setLevel(logging.DEBUG)
```

## Examples

### Business Article
```
Input: "CEO Announces Layoffs After Record Profits"
Output: 2-panel comic with CEO and worker
Panel 1 CEO: "We're optimizing our human resources."
Panel 2 Worker: "But we had record profits?"
```

### Political Article
```
Input: "Senator Claims Fiscal Responsibility"
Output: 3-panel comic with politician
Panel 1: "We must cut wasteful spending!"
Panel 2: *(Points to social programs)*
Panel 3: *(Votes for defense increase)*
```

### Tech Article
```
Input: "Tech CEO Demands Return to Office"
Output: 2-panel comic with tech worker and CEO
Panel 1 CEO: "Innovation requires physical presence!"
Panel 2 Worker: *(On video call)* "But we make remote tools?"
```

## Next Steps

1. **Run the setup script** to create basic assets
2. **Test with sample articles** using the create_comics.py script
3. **Customize characters** for your specific needs
4. **Integrate with main system** by updating the scheduler
5. **Add advanced features** like backgrounds and props

Your custom comics will match the deadpan, satirical tone of your articles while providing unique visual content that enhances the humor and commentary.
