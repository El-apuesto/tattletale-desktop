import os
import random
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
from ..utils.config import Config
from ..utils.error_handling import log_function_call
import logging

logger = logging.getLogger(__name__)

class ComicGenerator:
    """
    Generates custom comics for news satire articles.
    """
    
    def __init__(self):
        self.fonts_dir = "assets/fonts"
        self.templates_dir = "assets/comic_templates"
        self.output_dir = "data/generated_comics"
        
        # Ensure directories exist
        os.makedirs(self.fonts_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Comic styles
        self.styles = {
            'newspaper': {
                'bg_color': (255, 255, 255),
                'line_color': (0, 0, 0),
                'text_color': (0, 0, 0),
                'font_size': 24,
                'panel_border': 3
            },
            'minimalist': {
                'bg_color': (240, 240, 240),
                'line_color': (50, 50, 50),
                'text_color': (30, 30, 30),
                'font_size': 20,
                'panel_border': 2
            },
            'bold': {
                'bg_color': (255, 255, 255),
                'line_color': (0, 0, 0),
                'text_color': (0, 0, 0),
                'font_size': 28,
                'panel_border': 4
            }
        }
        
        # Character templates
        self.characters = {
            'ceo': {
                'description': 'Business executive in suit',
                'props': ['briefcase', 'phone', 'chart'],
                'expressions': ['smug', 'worried', 'excited', 'confused']
            },
            'politician': {
                'description': 'Politician in formal attire',
                'props': ['microphone', 'flag', 'document'],
                'expressions': 'serious', 'smiling', 'pointing', 'shocked'
            },
            'tech_bro': {
                'description': 'Tech worker in casual attire',
                'props': ['laptop', 'coffee', 'headphones'],
                'expressions': ['enthusiastic', 'tired', 'coding', 'presenting']
            },
            'worker': {
                'description': 'Regular employee',
                'props': ['coffee mug', 'desk', 'computer'],
                'expressions': ['tired', 'confused', 'frustrated', 'resigned']
            },
            'expert': {
                'description': 'Academic or expert',
                'props': ['book', 'glasses', 'pointer'],
                'expressions': ['serious', 'explaining', 'thoughtful', 'concerned']
            }
        }
        
        # Comic templates
        self.templates = {
            'single_panel': {
                'width': 800,
                'height': 600,
                'panels': 1
            },
            'two_panel': {
                'width': 800,
                'height': 400,
                'panels': 2
            },
            'three_panel': {
                'width': 900,
                'height': 300,
                'panels': 3
            },
            'four_panel': {
                'width': 800,
                'height': 800,
                'panels': 4
            }
        }
    
    @log_function_call
    def generate_comic(self, article: Dict) -> Dict:
        """
        Generate a custom comic based on article content.
        
        Args:
            article: Satire article with headline and content
            
        Returns:
            Comic metadata dictionary
        """
        try:
            # Analyze article for comic elements
            comic_elements = self._analyze_article_for_comic(article)
            
            # Choose template and style
            template = self._choose_template(comic_elements)
            style = self._choose_style(article.get('category', ''))
            
            # Generate comic panels
            comic_image = self._create_comic_panels(comic_elements, template, style)
            
            # Add text and dialogue
            final_comic = self._add_comic_text(comic_image, comic_elements, style)
            
            # Save comic
            comic_filename = self._save_comic(final_comic, article)
            
            # Create metadata
            comic_metadata = self._create_comic_metadata(comic_filename, comic_elements, article)
            
            logger.info(f"Generated custom comic: {comic_filename}")
            return comic_metadata
            
        except Exception as e:
            logger.error(f"Failed to generate comic: {str(e)}")
            return self._get_fallback_comic(article)
    
    def _analyze_article_for_comic(self, article: Dict) -> Dict:
        """
        Analyze article to extract comic elements.
        
        Args:
            article: Satire article
            
        Returns:
            Dictionary with comic elements
        """
        headline = article.get('headline', '').lower()
        content = article.get('opening_paragraph', '').lower()
        category = article.get('category', '')
        
        # Identify main characters
        characters = []
        if 'ceo' in headline or 'executive' in headline or category == 'business':
            characters.append('ceo')
        if 'politician' in headline or 'senator' in headline or category == 'politics':
            characters.append('politician')
        if 'tech' in headline or category == 'technology':
            characters.append('tech_bro')
        if 'worker' in content or 'employee' in content:
            characters.append('worker')
        
        # Default character if none found
        if not characters:
            characters = ['expert']
        
        # Extract key concepts for dialogue
        concepts = self._extract_key_concepts(headline + ' ' + content)
        
        # Determine comic situation
        situation = self._determine_situation(headline, category)
        
        # Generate dialogue ideas
        dialogue = self._generate_dialogue_ideas(concepts, situation, characters)
        
        return {
            'characters': characters,
            'concepts': concepts,
            'situation': situation,
            'dialogue': dialogue,
            'category': category,
            'headline': headline
        }
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts for comic dialogue."""
        # Look for satirical concepts
        concept_patterns = {
            'hypocrisy': ['claims while', 'insists despite', 'announces but'],
            'corporate speak': ['synergy', 'paradigm', 'leverage', 'optimize'],
            'political doublespeak': ['fiscal responsibility', 'government waste'],
            'tech irony': ['innovation', 'disruption', 'transformation']
        }
        
        concepts = []
        for concept, keywords in concept_patterns.items():
            if any(keyword in text for keyword in keywords):
                concepts.append(concept)
        
        # Extract specific entities
        words = text.split()
        entities = [word for word in words if word[0].isupper() and len(word) > 4]
        concepts.extend(entities[:3])  # Add up to 3 entities
        
        return concepts[:5]  # Limit to 5 concepts
    
    def _determine_situation(self, headline: str, category: str) -> str:
        """Determine the comic situation based on article."""
        if 'layoffs' in headline or 'fired' in headline:
            return 'layoff_announcement'
        elif 'return to office' in headline:
            return 'office_mandate'
        elif 'ai' in headline or 'automation' in headline:
            return 'tech_replacement'
        elif 'government shutdown' in headline:
            return 'political_deadlock'
        elif 'record profits' in headline:
            return 'corporate_celebration'
        elif 'innovation' in headline:
            return 'tech_presentation'
        else:
            return 'general_statement'
    
    def _generate_dialogue_ideas(self, concepts: List[str], situation: str, characters: List[str]) -> List[str]:
        """Generate dialogue ideas for the comic."""
        dialogue_templates = {
            'layoff_announcement': [
                "We're optimizing our human resources.",
                "This is about shareholder value.",
                "You're not being fired, you're being liberated.",
                "Think of this as a career opportunity."
            ],
            'office_mandate': [
                "Innovation requires physical proximity.",
                "We need more hallway conversations.",
                "Productivity happens in person.",
                "Remote work is so 2020."
            ],
            'tech_replacement': [
                "The AI can do your job better.",
                "This will streamline operations.",
                "Humans are the bottleneck.",
                "Welcome to the future."
            ],
            'political_deadlock': [
                "We need bipartisan support.",
                "The other side won't compromise.",
                "This is about fiscal responsibility.",
                "Think of the children!"
            ],
            'corporate_celebration': [
                "Record profits mean record bonuses!",
                "Our strategy is working perfectly.",
                "The market has spoken.",
                "Innovation drives success."
            ],
            'tech_presentation': [
                "This will revolutionize everything.",
                "We're disrupting the industry.",
                "It's a paradigm shift.",
                "The synergy is amazing."
            ],
            'general_statement': [
                "We're committed to excellence.",
                "This represents a new direction.",
                "The data is clear.",
                "Experts agree on this."
            ]
        }
        
        # Get relevant dialogue
        situation_dialogue = dialogue_templates.get(situation, dialogue_templates['general_statement'])
        
        # Add concept-specific dialogue
        concept_dialogue = []
        for concept in concepts:
            if concept == 'hypocrisy':
                concept_dialogue.append("Do as I say, not as I do.")
            elif concept == 'corporate speak':
                concept_dialogue.append("We need to leverage our synergies.")
            elif concept == 'political doublespeak':
                concept_dialogue.append("This is about responsible spending.")
        
        # Combine and select dialogue
        all_dialogue = situation_dialogue + concept_dialogue
        return random.sample(all_dialogue, min(3, len(all_dialogue)))
    
    def _choose_template(self, comic_elements: Dict) -> Dict:
        """Choose comic template based on elements."""
        num_characters = len(comic_elements['characters'])
        dialogue_length = len(comic_elements['dialogue'])
        
        if dialogue_length <= 1:
            return self.templates['single_panel']
        elif dialogue_length == 2:
            return self.templates['two_panel']
        elif dialogue_length == 3:
            return self.templates['three_panel']
        else:
            return self.templates['four_panel']
    
    def _choose_style(self, category: str) -> Dict:
        """Choose comic style based on category."""
        if category == 'politics':
            return self.styles['newspaper']
        elif category == 'business':
            return self.styles['bold']
        elif category == 'technology':
            return self.styles['minimalist']
        else:
            return self.styles['newspaper']
    
    def _create_comic_panels(self, comic_elements: Dict, template: Dict, style: Dict) -> Image.Image:
        """Create basic comic panel structure."""
        width = template['width']
        height = template['height']
        num_panels = template['panels']
        
        # Create base image
        comic = Image.new('RGB', (width, height), style['bg_color'])
        draw = ImageDraw.Draw(comic)
        
        # Calculate panel dimensions
        if num_panels == 1:
            panels = [(0, 0, width, height)]
        elif num_panels == 2:
            panel_width = width // 2
            panels = [
                (0, 0, panel_width, height),
                (panel_width, 0, width, height)
            ]
        elif num_panels == 3:
            panel_width = width // 3
            panels = [
                (0, 0, panel_width, height),
                (panel_width, 0, panel_width * 2, height),
                (panel_width * 2, 0, width, height)
            ]
        else:  # 4 panels
            panel_width = width // 2
            panel_height = height // 2
            panels = [
                (0, 0, panel_width, panel_height),
                (panel_width, 0, width, panel_height),
                (0, panel_height, panel_width, height),
                (panel_width, panel_height, width, height)
            ]
        
        # Draw panel borders
        border_width = style['panel_border']
        for panel in panels:
            x1, y1, x2, y2 = panel
            draw.rectangle([x1, y1, x2-border_width, y2-border_width], 
                         outline=style['line_color'], width=border_width)
        
        return comic
    
    def _add_comic_text(self, comic_image: Image.Image, comic_elements: Dict, style: Dict) -> Image.Image:
        """Add text and dialogue to comic."""
        draw = ImageDraw.Draw(comic_image)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("arial.ttf", style['font_size'])
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # Add dialogue to panels
        dialogue = comic_elements['dialogue']
        num_panels = len(dialogue)
        
        if num_panels == 1:
            # Single panel - put text at bottom
            text = dialogue[0]
            self._add_text_bubble(comic_image, draw, text, 
                                comic_image.width//2, comic_image.height - 100, 
                                font, style)
        elif num_panels == 2:
            # Two panels
            panel_width = comic_image.width // 2
            for i, text in enumerate(dialogue):
                x = panel_width // 2 + (i * panel_width)
                y = comic_image.height // 2
                self._add_text_bubble(comic_image, draw, text, x, y, font, style)
        elif num_panels == 3:
            # Three panels
            panel_width = comic_image.width // 3
            for i, text in enumerate(dialogue):
                x = panel_width // 2 + (i * panel_width)
                y = comic_image.height // 2
                self._add_text_bubble(comic_image, draw, text, x, y, font, style)
        else:
            # Four panels
            panel_width = comic_image.width // 2
            panel_height = comic_image.height // 2
            positions = [
                (panel_width//2, panel_height//2),
                (panel_width + panel_width//2, panel_height//2),
                (panel_width//2, panel_height + panel_height//2),
                (panel_width + panel_width//2, panel_height + panel_height//2)
            ]
            for i, text in enumerate(dialogue[:4]):
                x, y = positions[i]
                self._add_text_bubble(comic_image, draw, text, x, y, font, style)
        
        return comic_image
    
    def _add_text_bubble(self, image: Image.Image, draw: ImageDraw.Draw, text: str, 
                         x: int, y: int, font, style: Dict):
        """Add a text bubble to the comic."""
        if not font:
            font = ImageFont.load_default()
        
        # Calculate text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Add padding
        padding = 20
        bubble_width = text_width + (padding * 2)
        bubble_height = text_height + (padding * 2)
        
        # Calculate bubble position
        bubble_x = x - bubble_width // 2
        bubble_y = y - bubble_height // 2
        
        # Ensure bubble stays within image bounds
        bubble_x = max(10, min(bubble_x, image.width - bubble_width - 10))
        bubble_y = max(10, min(bubble_y, image.height - bubble_height - 10))
        
        # Draw bubble
        draw.rectangle([bubble_x, bubble_y, bubble_x + bubble_width, bubble_y + bubble_height],
                     fill=style['bg_color'], outline=style['line_color'], width=2)
        
        # Draw text
        text_x = bubble_x + padding
        text_y = bubble_y + padding
        
        # Word wrap if needed
        max_width = bubble_width - (padding * 2)
        lines = self._wrap_text(text, font, max_width)
        
        for i, line in enumerate(lines):
            line_y = text_y + (i * text_height)
            draw.text((text_x, line_y), line, fill=style['text_color'], font=font)
    
    def _wrap_text(self, text: str, font, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _save_comic(self, comic_image: Image.Image, article: Dict) -> str:
        """Save the generated comic."""
        # Generate filename
        headline_words = article.get('headline', '').split()[:5]
        filename_base = '_'.join(word.lower().replace(',', '').replace('.', '') for word in headline_words)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_base}_{timestamp}.png"
        
        # Save comic
        filepath = os.path.join(self.output_dir, filename)
        comic_image.save(filepath, 'PNG')
        
        return filename
    
    def _create_comic_metadata(self, filename: str, comic_elements: Dict, article: Dict) -> Dict:
        """Create metadata for the generated comic."""
        return {
            'filename': filename,
            'url': f"/static/comics/{filename}",
            'title': f"Custom Comic: {article.get('headline', 'Untitled')[:50]}",
            'alt_text': f"Satirical comic about {comic_elements.get('situation', 'current events')}",
            'width': 800,  # Default width
            'height': 600,  # Default height
            'source': 'custom_generated',
            'type': 'comic',
            'characters': comic_elements.get('characters', []),
            'situation': comic_elements.get('situation', ''),
            'dialogue': comic_elements.get('dialogue', []),
            'style': comic_elements.get('category', 'newspaper'),
            'license': 'Generated by News Satire System',
            'created_at': datetime.now().isoformat()
        }
    
    def _get_fallback_comic(self, article: Dict) -> Dict:
        """Get fallback comic if generation fails."""
        return {
            'filename': 'fallback_comic.png',
            'url': '/static/comics/fallback_comic.png',
            'title': 'Comic Unavailable',
            'alt_text': 'Satirical comic placeholder',
            'width': 400,
            'height': 300,
            'source': 'fallback',
            'type': 'comic',
            'license': 'Generated by News Satire System'
        }
    
    def get_comic_html(self, comic_metadata: Dict) -> str:
        """Generate HTML for displaying the custom comic."""
        if not comic_metadata:
            return ""
        
        img_url = comic_metadata.get('url', '')
        alt_text = comic_metadata.get('alt_text', '')
        title = comic_metadata.get('title', '')
        
        return f'''
        <div class="custom-comic">
            <figure class="article-figure">
                <img src="{img_url}" 
                     alt="{alt_text}" 
                     title="{title}"
                     class="comic-image" />
                <figcaption class="comic-caption">
                    {title}
                </figcaption>
            </figure>
        </div>
        '''
