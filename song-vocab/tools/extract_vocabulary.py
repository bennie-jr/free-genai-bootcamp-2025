import re

def extract_vocabulary(lyrics: str) -> list[str]:
    """Extracts vocabulary words from lyrics. Simple version."""
    # Remove punctuation and numbers, convert to lowercase, split into words
    words = re.findall(r'\b\w+\b', lyrics.lower())
    # Remove common stop words (can be extended) - for now just a few very common ones
    stop_words = set(['the', 'a', 'an', 'in', 'on', 'at', 'is', 'are', 'and', 'but', 'or'])
    vocabulary = [word for word in words if word not in stop_words and len(word) > 2] # longer than 2 chars to avoid very short words
    return list(set(vocabulary)) # unique words

if __name__ == '__main__':
    example_lyrics = """
    Bohemian Rhapsody
    Is this the real life? Is this just fantasy?
    Caught in a landslide, no escape from reality
    """
    vocabulary = extract_vocabulary(example_lyrics)
    print(vocabulary)