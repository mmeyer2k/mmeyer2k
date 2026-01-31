#!/usr/bin/env python3
"""Generate animated starfield GIF with username overlay."""

import random
import math
from PIL import Image, ImageDraw, ImageFont

# Config
WIDTH = 850
HEIGHT = 200
FRAMES = 60
DURATION_MS = 50  # 50ms per frame = 20fps, 3 second loop
BG_COLOR = (13, 17, 23)  # GitHub dark
TEXT = "mmeyer2k"

# Star layers: (count, min_size, max_size, speed, min_brightness, max_brightness)
LAYERS = [
    (50, 1, 1, 0.3, 80, 120),    # Distant - slow, dim
    (35, 1, 2, 0.7, 120, 180),   # Mid - medium
    (20, 2, 3, 1.5, 180, 255),   # Close - fast, bright
]

random.seed(42)  # Reproducible stars

def generate_stars(layer_config):
    """Generate star positions for a layer."""
    count, min_size, max_size, speed, min_b, max_b = layer_config
    stars = []
    for _ in range(count):
        stars.append({
            'x': random.uniform(0, WIDTH),
            'y': random.uniform(0, HEIGHT),
            'size': random.randint(min_size, max_size),
            'brightness': random.randint(min_b, max_b),
            'twinkle_phase': random.uniform(0, 2 * math.pi),
            'twinkle_speed': random.uniform(0.1, 0.3),
        })
    return stars, speed

def draw_frame(stars_layers, frame_num, total_frames):
    """Draw a single frame."""
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Draw stars
    for stars, speed in stars_layers:
        for star in stars:
            # Calculate position with wrapping
            x = (star['x'] + speed * frame_num * (WIDTH / total_frames)) % WIDTH
            y = star['y']
            
            # Twinkle effect for close stars
            twinkle = math.sin(star['twinkle_phase'] + frame_num * star['twinkle_speed'])
            brightness = int(star['brightness'] * (0.7 + 0.3 * twinkle))
            brightness = max(60, min(255, brightness))
            
            color = (brightness, brightness, brightness)
            size = star['size']
            
            if size == 1:
                draw.point((int(x), int(y)), fill=color)
            else:
                draw.ellipse([int(x)-size//2, int(y)-size//2, 
                             int(x)+size//2, int(y)+size//2], fill=color)
    
    # Draw text with glow effect
    try:
        # Try to find a monospace font
        for font_name in ['/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
                          '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf',
                          '/usr/share/fonts/truetype/ubuntu/UbuntuMono-B.ttf']:
            try:
                font = ImageFont.truetype(font_name, 56)
                break
            except:
                continue
        else:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), TEXT, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (WIDTH - text_width) // 2
    y = (HEIGHT - text_height) // 2 - bbox[1]
    
    # Draw glow (multiple offset layers)
    glow_color = (88, 166, 255, 40)  # Blue-ish glow
    for offset in range(6, 0, -1):
        glow_brightness = int(255 * (1 - offset/8))
        gc = (glow_brightness//4, glow_brightness//3, glow_brightness//2)
        for dx in range(-offset, offset+1):
            for dy in range(-offset, offset+1):
                if dx*dx + dy*dy <= offset*offset:
                    draw.text((x + dx, y + dy), TEXT, font=font, fill=gc)
    
    # Draw main text
    draw.text((x, y), TEXT, font=font, fill=(230, 237, 243))
    
    return img

def main():
    print("Generating stars...")
    stars_layers = [generate_stars(layer) for layer in LAYERS]
    
    print(f"Rendering {FRAMES} frames...")
    frames = []
    for i in range(FRAMES):
        frame = draw_frame(stars_layers, i, FRAMES)
        frames.append(frame)
        if (i + 1) % 10 == 0:
            print(f"  Frame {i + 1}/{FRAMES}")
    
    print("Saving GIF...")
    frames[0].save(
        'header.gif',
        save_all=True,
        append_images=frames[1:],
        duration=DURATION_MS,
        loop=0,  # Infinite loop
        optimize=True
    )
    print("Done! Created header.gif")

if __name__ == '__main__':
    main()
