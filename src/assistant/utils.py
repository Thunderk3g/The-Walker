from langsmith import traceable
from tavily import TavilyClient
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

def deduplicate_and_format_sources(search_response, max_tokens_per_source=1000, include_raw_content=True):
    """
    Takes either a single search response or list of responses from Tavily API and formats them.
    Limits the raw_content to approximately max_tokens_per_source.
    include_raw_content specifies whether to include the raw_content from Tavily in the formatted string.
    
    Args:
        search_response: Either:
            - A dict with a 'results' key containing a list of search results
            - A list of dicts, each containing search results
            
    Returns:
        str: Formatted string with deduplicated sources
    """
    # Convert input to list of results
    if isinstance(search_response, dict):
        sources_list = search_response['results']
    elif isinstance(search_response, list):
        sources_list = []
        for response in search_response:
            if isinstance(response, dict) and 'results' in response:
                sources_list.extend(response['results'])
            else:
                sources_list.extend(response)
    else:
        raise ValueError("Input must be either a dict with 'results' or a list of search results")
    
    # Deduplicate by URL
    unique_sources = {}
    for source in sources_list:
        if source['url'] not in unique_sources:
            unique_sources[source['url']] = source
    
    # Format output
    formatted_text = "Sources:\n\n"
    for i, source in enumerate(unique_sources.values(), 1):
        formatted_text += f"Source {source['title']}:\n===\n"
        formatted_text += f"URL: {source['url']}\n===\n"
        formatted_text += f"Most relevant content from source: {source['content']}\n===\n"
        if include_raw_content:
            # Using rough estimate of 4 characters per token
            char_limit = max_tokens_per_source * 4
            # Handle None raw_content
            raw_content = source.get('raw_content', '')
            if raw_content is None:
                raw_content = ''
                print(f"Warning: No raw_content found for source {source['url']}")
            if len(raw_content) > char_limit:
                raw_content = raw_content[:char_limit] + "... [truncated]"
            formatted_text += f"Full source content limited to {max_tokens_per_source} tokens: {raw_content}\n\n"
                
    return formatted_text.strip()

def format_sources(search_results):
    """Format search results into a bullet-point list of sources.
    
    Args:
        search_results (dict or str or list): Tavily search response containing results,
                                             already formatted string, or list of sources
        
    Returns:
        str: Formatted string with sources and their URLs
    """
    # If search_results is already a string, return it as is
    if isinstance(search_results, str):
        return search_results
    
    # If search_results is a list, format each item
    if isinstance(search_results, list):
        # Check if the list contains dictionaries with title and url
        if all(isinstance(item, dict) and 'title' in item and 'url' in item for item in search_results):
            return '\n'.join(
                f"* {source['title']} : {source['url']}"
                for source in search_results
            )
        # If it's a list of strings, just join them
        elif all(isinstance(item, str) for item in search_results):
            return '\n'.join(search_results)
        # For any other list, convert to string
        else:
            return '\n'.join(str(item) for item in search_results)
    
    # If search_results is a dictionary with 'results' key
    if isinstance(search_results, dict) and 'results' in search_results:
        return '\n'.join(
            f"* {source['title']} : {source['url']}"
            for source in search_results['results']
        )
    
    # Fallback for any other type
    return str(search_results)

@traceable
def tavily_search(query, include_raw_content=True, max_results=3):
    """ Search the web using the Tavily API.
    
    Args:
        query (str): The search query to execute
        include_raw_content (bool): Whether to include the raw_content from Tavily in the formatted string
        max_results (int): Maximum number of results to return
        
    Returns:
        dict: Tavily search response containing:
            - results (list): List of search result dictionaries, each containing:
                - title (str): Title of the search result
                - url (str): URL of the search result
                - content (str): Snippet/summary of the content
                - raw_content (str): Full content of the page if available"""
    
    # Ensure API key is set
    api_key = os.environ.get("TAVILY_API_KEY")
    
    if not api_key:
        print("Warning: TAVILY_API_KEY not found in environment variables")
        return {
            "results": [
                {
                    "title": "API Key Error",
                    "url": "https://example.com",
                    "content": "Tavily API key not found. Please set the TAVILY_API_KEY environment variable.",
                    "raw_content": ""
                }
            ]
        }
    
    # Create client with explicit API key
    tavily_client = TavilyClient(api_key=api_key)
    
    try:
        return tavily_client.search(query, 
                            max_results=max_results, 
                            include_raw_content=include_raw_content)
    except Exception as e:
        print(f"Error in Tavily search: {e}")
        # Return a minimal structure to prevent downstream errors
        return {
            "results": [
                {
                    "title": "Error in search",
                    "url": "https://example.com",
                    "content": f"Search failed: {str(e)}. Please check your Tavily API key.",
                    "raw_content": ""
                }
            ]
        }

def format_citation(source: Dict[str, Any], citation_style: str = "APA") -> str:
    """Format a citation according to the specified style.
    
    Args:
        source (Dict[str, Any]): Source information including title, url, and author if available
        citation_style (str): Citation style (APA, MLA, Chicago, IEEE)
        
    Returns:
        str: Formatted citation string
    """
    # Get current date for "retrieved on" information
    current_date = datetime.now().strftime('%B %d, %Y')
    
    # Extract source information
    title = source.get('title', 'No title')
    url = source.get('url', '')
    author = source.get('author', 'No author')
    published_date = source.get('published_date', '')
    
    # Format based on citation style
    if citation_style.upper() == 'APA':
        if published_date:
            return f"{author}. ({published_date}). {title}. Retrieved on {current_date} from {url}"
        else:
            return f"{author}. (n.d.). {title}. Retrieved on {current_date} from {url}"
            
    elif citation_style.upper() == 'MLA':
        return f"{author}. \"{title}.\" Web. {current_date}. <{url}>."
        
    elif citation_style.upper() == 'CHICAGO':
        return f"{author}. \"{title}.\" Accessed {current_date}. {url}."
        
    elif citation_style.upper() == 'IEEE':
        return f"[{source.get('citation_number', 1)}] {author}, \"{title},\" {published_date or 'n.d.'}, [Online]. Available: {url}. [Accessed: {current_date}]."
        
    else:
        # Default to APA if style not recognized
        return f"{author}. (n.d.). {title}. Retrieved on {current_date} from {url}"

def extract_citation_info(source: Dict[str, Any]) -> Dict[str, Any]:
    """Extract citation information from a source.
    
    Args:
        source (Dict[str, Any]): Source information from search results
        
    Returns:
        Dict[str, Any]: Structured citation information
    """
    # Try to extract author information from content
    content = source.get('content', '')
    raw_content = source.get('raw_content', '')
    
    # Simple heuristic to find potential authors
    author = "No author"
    if "by " in content.lower():
        author_start = content.lower().find("by ") + 3
        author_end = content.find(",", author_start)
        if author_end != -1:
            author = content[author_start:author_end].strip()
    
    # Try to find a publication date
    published_date = ""
    date_indicators = ["published on", "published:", "date:", "published"]
    for indicator in date_indicators:
        if indicator in raw_content.lower():
            # Simple date extraction heuristic - would need improvement in production
            idx = raw_content.lower().find(indicator) + len(indicator)
            date_end = raw_content.find(".", idx)
            if date_end != -1:
                published_date = raw_content[idx:date_end].strip()
                break
    
    return {
        'title': source.get('title', 'No title'),
        'url': source.get('url', ''),
        'author': author,
        'published_date': published_date,
        'retrieved_date': datetime.now().strftime('%B %d, %Y')
    }

def count_citations_in_text(text: str) -> int:
    """Count the number of citations in a text.
    
    Args:
        text (str): Text to analyze for citations
        
    Returns:
        int: Number of citations found
    """
    # Look for common citation patterns
    # This is a simplified approach - would need to be enhanced for production
    citation_count = 0
    
    # Count [1], [2], etc. style citations (IEEE)
    import re
    ieee_citations = re.findall(r'\[\d+\]', text)
    citation_count += len(ieee_citations)
    
    # Count (Author, Year) style citations (APA)
    apa_citations = re.findall(r'\([A-Za-z]+,?\s+\d{4}\)', text)
    citation_count += len(apa_citations)
    
    # Count "Author" style citations (MLA)
    mla_citations = re.findall(r'\"[A-Za-z]+\"', text)
    citation_count += len(mla_citations)
    
    return citation_count

def validate_paper_structure(sections: Dict[str, Optional[str]], min_sections: int = 6) -> Dict[str, Any]:
    """Validate the structure of a research paper.
    
    Args:
        sections (Dict[str, Optional[str]]): Dictionary of section names to content
        min_sections (int): Minimum number of completed sections required
        
    Returns:
        Dict[str, Any]: Validation results
    """
    # Count completed sections
    completed_sections = sum(1 for content in sections.values() if content)
    
    # Check if critical sections are present
    critical_sections = ['abstract', 'introduction', 'methodology', 'results', 'conclusion']
    missing_critical = [section for section in critical_sections if not sections.get(section)]
    
    # Estimate average section length
    section_lengths = [len(content) for content in sections.values() if content]
    avg_length = sum(section_lengths) / len(section_lengths) if section_lengths else 0
    
    return {
        'valid': completed_sections >= min_sections and not missing_critical,
        'completed_sections': completed_sections,
        'missing_critical_sections': missing_critical,
        'avg_section_length': avg_length,
        'suggestions': [
            f"Add content for {section}" for section in missing_critical
        ] if missing_critical else []
    }