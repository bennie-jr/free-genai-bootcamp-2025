import httpx

def get_page_content(url: str) -> str:
    """Fetches the content of a webpage and returns it as text."""
    try:
        response = httpx.get(url, follow_redirects=True, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.text
    except httpx.RequestError as e:
        return f"Error fetching URL {url}: {e}"
    except httpx.HTTPError as e:
        return f"HTTP error fetching URL {url}: {e}"

if __name__ == '__main__':
    page_content = get_page_content("https://www.azlyrics.com/lyrics/queen/bohemianrhapsody.html") # Example URL
    if "Bohemian Rhapsody" in page_content:
        print("Successfully fetched page content.")
    else:
        print("Failed to fetch or content does not contain expected text.")