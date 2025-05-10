import re
import unicodedata

def slugify(text):
    # Ensure text is a str (in case bytes slip in)
    if not isinstance(text, str):
        text = text.decode('utf-8')

    # Normalize accents/diacritics
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    
    # Replace non-word characters with hyphens
    text = re.sub(r'[^\w\s-]', '', text.lower())
    
    # Replace spaces and multiple hyphens with a single hyphen
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    
    return text
