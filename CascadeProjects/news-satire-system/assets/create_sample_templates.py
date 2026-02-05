#!/usr/bin/env python3
"""
Create sample comic templates and assets
"""

import os
from PIL import Image, ImageDraw

def create_basic_templates():
    """Create basic comic panel templates."""
    
    templates_dir = "assets/comic_templates"
    os.makedirs(templates_dir, exist_ok=True)
    
    # Single panel template
    single_panel = Image.new('RGB', (800, 600), (255, 255, 255))
    draw = ImageDraw.Draw(single_panel)
    draw.rectangle([10, 10, 790, 590], outline=(0, 0, 0), width=3)
    single_panel.save(os.path.join(templates_dir, "single_panel.png"))
    
    # Two panel template
    two_panel = Image.new('RGB', (800, 400), (255, 255, 255))
    draw = ImageDraw.Draw(two_panel)
    draw.rectangle([10, 10, 390, 390], outline=(0, 0, 0), width=3)
    draw.rectangle([410, 10, 790, 390], outline=(0, 0, 0), width=3)
    two_panel.save(os.path.join(templates_dir, "two_panel.png"))
    
    # Three panel template
    three_panel = Image.new('RGB', (900, 300), (255, 255, 255))
    draw = ImageDraw.Draw(three_panel)
    draw.rectangle([10, 10, 290, 290], outline=(0, 0, 0), width=3)
    draw.rectangle([310, 10, 590, 290], outline=(0, 0, 0), width=3)
    draw.rectangle([610, 10, 890, 290], outline=(0, 0, 0), width=3)
    three_panel.save(os.path.join(templates_dir, "three_panel.png"))
    
    # Four panel template
    four_panel = Image.new('RGB', (800, 800), (255, 255, 255))
    draw = ImageDraw.Draw(four_panel)
    draw.rectangle([10, 10, 390, 390], outline=(0, 0, 0), width=3)
    draw.rectangle([410, 10, 790, 390], outline=(0, 0, 0), width=3)
    draw.rectangle([10, 410, 390, 790], outline=(0, 0, 0), width=3)
    draw.rectangle([410, 410, 790, 790], outline=(0, 0, 0), width=3)
    four_panel.save(os.path.join(templates_dir, "four_panel.png"))
    
    print("✅ Created basic comic panel templates")

def create_character_sprites():
    """Create simple character sprites."""
    
    sprites_dir = "assets/characters"
    os.makedirs(sprites_dir, exist_ok=True)
    
    # CEO sprite (simple stick figure with tie)
    ceo_sprite = Image.new('RGB', (100, 150), (255, 255, 255))
    draw = ImageDraw.Draw(ceo_sprite)
    
    # Head
    draw.ellipse([40, 20, 60, 40], outline=(0, 0, 0), width=2)
    # Body
    draw.line([50, 40, 50, 100], fill=(0, 0, 0), width=2)
    # Arms
    draw.line([50, 60, 30, 80], fill=(0, 0, 0), width=2)
    draw.line([50, 60, 70, 80], fill=(0, 0, 0), width=2)
    # Legs
    draw.line([50, 100, 40, 140], fill=(0, 0, 0), width=2)
    draw.line([50, 100, 60, 140], fill=(0, 0, 0), width=2)
    # Tie
    draw.polygon([(48, 45, 52, 45, 50, 70)], fill=(0, 0, 0))
    
    ceo_sprite.save(os.path.join(sprites_dir, "ceo.png"))
    
    # Politician sprite (with flag)
    politician_sprite = Image.new('RGB', (100, 150), (255, 255, 255))
    draw = ImageDraw.Draw(politician_sprite)
    
    # Head
    draw.ellipse([40, 20, 60, 40], outline=(0, 0, 0), width=2)
    # Body
    draw.line([50, 40, 50, 100], fill=(0, 0, 0), width=2)
    # Arms (one pointing)
    draw.line([50, 60, 30, 80], fill=(0, 0, 0), width=2)
    draw.line([50, 60, 80, 70], fill=(0, 0, 0), width=2)
    # Legs
    draw.line([50, 100, 40, 140], fill=(0, 0, 0), width=2)
    draw.line([50, 100, 60, 140], fill=(0, 0, 0), width=2)
    # Flag
    draw.rectangle([75, 50, 95, 65], fill=(255, 0, 0))
    draw.line([75, 50, 75, 80], fill=(0, 0, 0), width=1)
    
    politician_sprite.save(os.path.join(sprites_dir, "politician.png"))
    
    # Tech worker sprite (with laptop)
    tech_sprite = Image.new('RGB', (100, 150), (255, 255, 255))
    draw = ImageDraw.Draw(tech_sprite)
    
    # Head (with glasses)
    draw.ellipse([40, 20, 60, 40], outline=(0, 0, 0), width=2)
    draw.rectangle([42, 28, 48, 32], outline=(0, 0, 0), width=1)
    draw.rectangle([52, 28, 58, 32], outline=(0, 0, 0), width=1)
    # Body
    draw.line([50, 40, 50, 100], fill=(0, 0, 0), width=2)
    # Arms (typing)
    draw.line([50, 60, 30, 90], fill=(0, 0, 0), width=2)
    draw.line([50, 60, 70, 90], fill=(0, 0, 0), width=2)
    # Legs
    draw.line([50, 100, 40, 140], fill=(0, 0, 0), width=2)
    draw.line([50, 100, 60, 140], fill=(0, 0, 0), width=2)
    # Laptop
    draw.rectangle([20, 85, 80, 95], fill=(128, 128, 128))
    draw.rectangle([25, 95, 75, 100], fill=(64, 64, 64))
    
    tech_sprite.save(os.path.join(sprites_dir, "tech_worker.png"))
    
    print("✅ Created character sprites")

def create_fallback_comic():
    """Create a fallback comic image."""
    
    output_dir = "data/generated_comics"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create simple "Comic Unavailable" image
    fallback = Image.new('RGB', (400, 300), (240, 240, 240))
    draw = ImageDraw.Draw(fallback)
    
    # Border
    draw.rectangle([10, 10, 390, 290], outline=(0, 0, 0), width=2)
    
    # Text
    try:
        # Try to use a larger font
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    text_lines = [
        "Comic",
        "Unavailable",
        "",
        "Satire system",
        "generating..."
    ]
    
    y_offset = 100
    for line in text_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (400 - text_width) // 2
        draw.text((x, y_offset), line, fill=(0, 0, 0), font=font)
        y_offset += 30
    
    fallback.save(os.path.join(output_dir, "fallback_comic.png"))
    print("✅ Created fallback comic")

if __name__ == "__main__":
    print("🎨 Creating comic assets...")
    
    create_basic_templates()
    create_character_sprites()
    create_fallback_comic()
    
    print("\n✅ All comic assets created successfully!")
    print("📁 Check:")
    print("   - assets/comic_templates/")
    print("   - assets/characters/")
    print("   - data/generated_comics/")
