import os
from tavily import TavilyClient
import json

def test_tavily_search():
    """
    Test the Tavily search API.
    
    This function performs a search using the Tavily API and prints the results.
    It's useful for verifying that your API key is working correctly.
    """
    # Get API key from environment
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        print("Error: TAVILY_API_KEY environment variable not set")
        return
    
    # Initialize client
    client = TavilyClient(api_key=api_key)
    
    # Perform search
    try:
        query = "What are the latest developments in AI research?"
        print(f"Searching for: {query}")
        
        response = client.search(
            query=query,
            search_depth="advanced",
            include_raw_content=True,
            max_results=3
        )
        
        # Print results
        print("\nSearch Results:")
        print(json.dumps(response, indent=2))
        
        # Print number of results
        print(f"\nFound {len(response['results'])} results")
        
    except Exception as e:
        print(f"Error during Tavily search: {e}")

if __name__ == "__main__":
    test_tavily_search() 