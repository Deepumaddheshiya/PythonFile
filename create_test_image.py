from PIL import Image
import base64

# Create a test image (300x300 pixels)
img = Image.new('RGB', (300, 300), color=(73, 109, 137))
img.save('test_image.png')

# Convert to base64
with open('test_image.png', 'rb') as f:
    img_base64 = base64.b64encode(f.read()).decode('utf-8')

full_data_url = 'data:image/png;base64,' + img_base64

print("✅ Test image created: test_image.png")
print(f"\n📋 Full data URL for Postman:\n")
print(full_data_url)
print(f"\n📊 Image capacity: 300x300 = 90,000 pixels = ~33KB of data")
