from duckduckgo_search import DDGS

def search_web(query: str) -> str:
    """Search the web using DuckDuckGo."""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
        
    if not results:
        return "No results found"
        
    # Format results
    formatted_results = []
    for r in results:
        formatted_results.append(f"Title: {r['title']}\nLink: {r['link']}\nSnippet: {r['body']}\n")
    
    return "\n".join(formatted_results)

if __name__ == '__main__':
    search_results = search_web("lyrics for Bohemian Rhapsody by Queen")
    print(search_results)