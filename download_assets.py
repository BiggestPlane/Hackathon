import urllib.request
import os

# Create assets directory if it doesn't exist
os.makedirs('assets/images', exist_ok=True)

# URLs for the images
images = {
    'shrek.png': 'https://raw.githubusercontent.com/example/assets/main/shrek.png',
    'toilet.png': 'https://raw.githubusercontent.com/example/assets/main/toilet.png',
    'swamp.png': 'https://raw.githubusercontent.com/example/assets/main/swamp.png'
}

# Download each image
for filename, url in images.items():
    try:
        urllib.request.urlretrieve(url, f'assets/images/{filename}')
        print(f'Downloaded {filename}')
    except Exception as e:
        print(f'Failed to download {filename}: {e}') 