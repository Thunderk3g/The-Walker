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
            if raw_content:
                if len(raw_content) > char_limit:
                    raw_content = raw_content[:char_limit] + "... [truncated]"
                formatted_text += f"Raw content: {raw_content}\n===\n"
        formatted_text += "\n"
    
    return formatted_text

def format_sources(search_results):
    """
    Format search results into a structured string.
    
    Args:
        search_results: List of search result dictionaries
        
    Returns:
        str: Formatted string with sources
    """
    if not search_results:
        return "No sources found."
    
    formatted_text = "Sources:\n\n"
    
    for i, result in enumerate(search_results, 1):
        # Extract basic information
        title = result.get('title', 'No title')
        url = result.get('url', 'No URL')
        content = result.get('content', 'No content')
        
        # Format the source
        formatted_text += f"Source {i}: {title}\n"
        formatted_text += f"URL: {url}\n"
        formatted_text += f"Content: {content}\n\n"
        
        # Add publication date if available
        if 'published_date' in result and result['published_date']:
            formatted_text += f"Published: {result['published_date']}\n"
        
        # Add author if available
        if 'author' in result and result['author']:
            formatted_text += f"Author: {result['author']}\n"
        
        formatted_text += "---\n\n"
    
    return formatted_text

@traceable
def tavily_search(query, include_raw_content=True, max_results=3):
    """
    Perform a search using the Tavily API.
    
    Args:
        query: Search query string
        include_raw_content: Whether to include raw content in results
        max_results: Maximum number of results to return
        
    Returns:
        dict: Search response from Tavily
    """
    # Get API key from environment
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable not set")
    
    # Initialize client
    client = TavilyClient(api_key=api_key)
    
    # Perform search
    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            include_raw_content=include_raw_content,
            max_results=max_results
        )
        return response
    except Exception as e:
        print(f"Error during Tavily search: {e}")
        # Return empty results on error
        return {"results": []}

def format_citation(source: Dict[str, Any], citation_style: str) -> str:
    """
    Format a citation according to the specified style.
    
    Args:
        source: Source dictionary with citation information
        citation_style: Citation style (APA, MLA, Chicago, IEEE)
        
    Returns:
        str: Formatted citation
    """
    # Extract citation information
    info = extract_citation_info(source)
    
    # Format according to style
    if citation_style.upper() == "APA":
        # APA format
        authors = info['authors'] if info['authors'] else "No author"
        year = info['year'] if info['year'] else "n.d."
        title = info['title'] if info['title'] else "No title"
        publisher = info['publisher'] if info['publisher'] else "No publisher"
        url = info['url']
        
        citation = f"{authors} ({year}). {title}. {publisher}. Retrieved from {url}"
    
    elif citation_style.upper() == "MLA":
        # MLA format
        authors = info['authors'] if info['authors'] else "No author"
        title = info['title'] if info['title'] else "No title"
        publisher = info['publisher'] if info['publisher'] else "No publisher"
        year = info['year'] if info['year'] else "n.d."
        url = info['url']
        
        citation = f"{authors}. \"{title}.\" {publisher}, {year}, {url}."
    
    else:
        # Default format (simplified)
        authors = info['authors'] if info['authors'] else "No author"
        year = info['year'] if info['year'] else "n.d."
        title = info['title'] if info['title'] else "No title"
        url = info['url']
        
        citation = f"{authors} ({year}). {title}. Retrieved from {url}"
    
    return citation

def extract_citation_info(source: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract citation information from a source.
    
    Args:
        source: Source dictionary
        
    Returns:
        dict: Extracted citation information
    """
    # Initialize with default values
    info = {
        'authors': None,
        'title': None,
        'year': None,
        'publisher': None,
        'url': None,
        'date_accessed': datetime.now().strftime("%Y-%m-%d")
    }
    
    # Extract information from source
    if 'title' in source and source['title']:
        info['title'] = source['title']
    
    if 'url' in source and source['url']:
        info['url'] = source['url']
    
    # Extract author if available
    if 'author' in source and source['author']:
        info['authors'] = source['author']
    
    # Extract year from published_date if available
    if 'published_date' in source and source['published_date']:
        try:
            # Try to parse date and extract year
            date_obj = datetime.strptime(source['published_date'], "%Y-%m-%d")
            info['year'] = date_obj.year
        except:
            # If parsing fails, use the raw value
            info['year'] = source['published_date']
    
    # Extract publisher/domain from URL
    if info['url']:
        try:
            from urllib.parse import urlparse
            domain = urlparse(info['url']).netloc
            info['publisher'] = domain
        except:
            pass
    
    return info

def count_citations_in_text(text: str) -> int:
    """
    Count the number of citations in a text.
    
    Args:
        text: Text to analyze
        
    Returns:
        int: Number of citations
    """
    import re
    
    # Count citations in various formats
    
    # APA style: (Author, Year)
    apa_pattern = r'\([A-Za-z]+(?:\s+et\s+al\.)?(?:,\s+\d{4})\)'
    apa_count = len(re.findall(apa_pattern, text))
    
    # MLA style: (Author page)
    mla_pattern = r'\([A-Za-z]+(?:\s+et\s+al\.)?(?:\s+\d+)\)'
    mla_count = len(re.findall(mla_pattern, text))
    
    # URL citations
    url_pattern = r'https?://\S+'
    url_count = len(re.findall(url_pattern, text))
    
    # Numbered citations: [1], [2], etc.
    numbered_pattern = r'\[\d+\]'
    numbered_count = len(re.findall(numbered_pattern, text))
    
    # Return total count
    return apa_count + mla_count + url_count + numbered_count

def validate_paper_structure(sections: Dict[str, Optional[str]], min_sections: int = 6) -> Dict[str, Any]:
    """
    Validate the structure of a research paper.
    
    Args:
        sections: Dictionary of section names to content
        min_sections: Minimum number of completed sections required
        
    Returns:
        dict: Validation results
    """
    # Count completed sections
    completed_sections = sum(1 for content in sections.values() if content)
    
    # Check if required sections are present and have content
    required_sections = ['abstract', 'introduction', 'literature_review', 'conclusion', 'references']
    missing_required = [section for section in required_sections if section not in sections or not sections[section]]
    
    # Validate section lengths
    section_lengths = {section: len(content) if content else 0 for section, content in sections.items()}
    
    # Check if abstract is too long (typically should be 150-250 words)
    abstract_too_long = False
    if 'abstract' in sections and sections['abstract']:
        word_count = len(sections['abstract'].split())
        abstract_too_long = word_count > 300
    
    # Prepare validation results
    validation_results = {
        'completed_sections': completed_sections,
        'min_sections_met': completed_sections >= min_sections,
        'missing_required_sections': missing_required,
        'section_lengths': section_lengths,
        'abstract_too_long': abstract_too_long,
        'passed': completed_sections >= min_sections and not missing_required
    }
    
    return validation_results 