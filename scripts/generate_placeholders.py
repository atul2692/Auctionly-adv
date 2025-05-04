import os
import random
from PIL import Image, ImageDraw, ImageFont

def generate_placeholder_image(filename, width, height, bg_color=None, text=None):
    """Generate a placeholder image with random color and optional text"""
    
    if bg_color is None:
        # Generate a random pastel color
        r = random.randint(180, 240)
        g = random.randint(180, 240)
        b = random.randint(180, 240)
        bg_color = (r, g, b)
    else:
        r, g, b = bg_color
    
    # Create image with background color
    image = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)

    # Draw a frame
    frame_width = int(min(width, height) * 0.03)
    draw.rectangle(
        [(frame_width, frame_width), (width - frame_width, height - frame_width)],
        outline=(max(r-60, 0), max(g-60, 0), max(b-60, 0)),
        width=frame_width
    )
    
    # Add text
    if text is None:
        text = f"{width}x{height}"
    
    try:
        font_size = int(min(width, height) * 0.1)
        # Try different font options for Windows
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
    except:
        # If everything fails, use default
        font = ImageFont.load_default()
    
    # Get text dimensions and position
    try:
        text_width, text_height = draw.textsize(text, font=font)
    except:
        # PIL 9.0.0+ compatibility
        try:
            text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
        except:
            text_width, text_height = font.getsize(text)
    
    position = ((width - text_width) // 2, (height - text_height) // 2)
    
    # Draw text with shadow for better visibility
    shadow_color = (max(r-100, 0), max(g-100, 0), max(b-100, 0))
    
    # Try different drawing methods to handle PIL version differences
    try:
        draw.text((position[0]+2, position[1]+2), text, font=font, fill=shadow_color)
        draw.text(position, text, font=font, fill=(255, 255, 255))
    except:
        # Simplified fallback
        draw.text((width//2, height//2), text, fill=(255, 255, 255), anchor="mm")
    
    # Save the image
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_path = os.path.join(base_dir, 'static', 'images', filename)
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    image.save(img_path)
    
    print(f"Created {img_path}")
    return img_path

def generate_auction_sample_images():
    """Generate sample images for the auction site"""
    
    # Create static/images directory if it doesn't exist
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_dir = os.path.join(base_dir, 'static', 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    # Hero image
    generate_placeholder_image('hero-image.jpg', 800, 500, bg_color=(200, 220, 240), text="Auction Hub")
    
    # Product images
    products = [
        ('product1.jpg', "Vintage Watch", (220, 200, 240)),
        ('product2.jpg', "Art Painting", (240, 220, 200)),
        ('product3.jpg', "Antique Desk", (200, 230, 210)),
        ('product4.jpg', "Gold Coins", (240, 230, 200)),
        ('product5.jpg', "Vintage Camera", (210, 210, 230)),
    ]
    
    for filename, text, color in products:
        generate_placeholder_image(filename, 500, 350, bg_color=color, text=text)
    
    # User profile images
    users = [
        ('user1.jpg', "User 1", (220, 220, 240)),
        ('user2.jpg', "User 2", (240, 220, 220)),
        ('user3.jpg', "User 3", (220, 240, 220)),
        ('user4.jpg', "User 4", (230, 220, 240)),
    ]
    
    for filename, text, color in users:
        generate_placeholder_image(filename, 200, 200, bg_color=color, text=text)

if __name__ == "__main__":
    print("Generating placeholder images...")
    generate_auction_sample_images()
    print("Done!") 