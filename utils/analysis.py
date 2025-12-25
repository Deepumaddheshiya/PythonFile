from PIL import Image, ImageEnhance

def analyze_image(image_path, output_path):
    """
    Creates an LSB enhancement of the image to visualize noise.
    """
    img = Image.open(image_path)
    img = img.convert('RGB')
    
    pixels = img.load()
    width, height = img.size
    
    # Create the analysis image
    analysis_img = Image.new('RGB', (width, height))
    analysis_pixels = analysis_img.load()
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            
            # Extract LSBs and scale them up to be visible (0 or 255)
            # We multiply by 255 so 1 becomes 255 (white) and 0 becomes 0 (black)
            # This is a bit extreme, maybe 85 * (1 or 0) for each channel to preserve color?
            # Let's try to just boosting the signal: 
            # (pixel & 0x01) * 255 is the standard LSB view.
            
            nr = (r & 1) * 255
            ng = (g & 1) * 255
            nb = (b & 1) * 255
            
            analysis_pixels[x, y] = (nr, ng, nb)
            
    analysis_img.save(output_path)
    return True
