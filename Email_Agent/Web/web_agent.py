import os
import json
from secrets import get_secret
from tavily import TavilyClient
import asyncio
import aiohttp

# Retrieve Tavily API key
tavily_api_key = get_secret("TAVILY_API_KEY")

if not tavily_api_key:
    raise ValueError("Failed to retrieve Tavily API key from Secret Manager")

# Initialize Tavily client
tavily_client = TavilyClient(api_key=tavily_api_key)

async def tavily_search(query, search_depth="advanced", max_results=3, include_raw_content=True):
    """
    Perform a search using Tavily API and get both search results and raw context.
    """
    try:
        print(f"\nDEBUG: Tavily Search")
        print(f"API Key: {tavily_api_key[:5]}...")  # Print first 5 chars of API key
        print(f"Query: {query}")
        print(f"Search depth: {search_depth}")
        print(f"Max results: {max_results}")
        
        # Get search results
        search_response = tavily_client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results,
            include_raw_content=include_raw_content,
            exclude_domains=[
                "mapquest.com",
                "facebook.com",
                "instagram.com", 
                "twitter.com"
            ]
        )
        
        # If we get here, the search was successful
        results = search_response.get('results', [])
        raw_context = ' '.join([r.get('raw_content', '') for r in results if r.get('raw_content')])
        
        print(f"\nSearch completed successfully")
        print(f"Found {len(results)} results")
        print(f"Raw context length: {len(raw_context)}")

        print("Results")
        print("\n\n\n\n\n\n\n\n\n\n\n")
        print("="*50)
        print(results)
        print("="*50)
        print("\n\n\n\n\n\n\n\n\n\n\n")

        print("Raw Context")
        print("\n\n\n\n\n\n\n\n\n\n\n")
        print("="*50)
        print(raw_context)
        print("="*50)
        print("\n\n\n\n\n\n\n\n\n\n\n")
        
        return results, raw_context
        
    except Exception as e:
        print(f"\nDEBUG: Tavily Search Error")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        print(f"Query that caused error: {query}")
        return [], ""

def tavily_context_search(query, max_tokens=4000, **kwargs):
    """
    Perform a context search using Tavily API.
    
    :param query: The search query string
    :param max_tokens: Maximum number of tokens for the context (default: 40000)
    :param kwargs: Additional keyword arguments for the search
    :return: Context string for RAG applications
    """
    try:
        context = tavily_client.get_search_context(
            query=query,
            max_tokens=max_tokens,
            **kwargs
        )
        return context
    except Exception as e:
        print(f"An error occurred during Tavily context search: {str(e)}")
        return None

def tavily_extract_content(query, max_results=2):
    """
    Extract content from URLs found in Tavily search results.
    
    :param query: The search query string
    :param max_results: Maximum number of search results to use for extraction
    :return: Dictionary containing extracted results and failed URLs
    """
    try:
        # First, perform a search to get the URLs
        search_results = tavily_search(query, max_results=max_results)
        urls = [result['url'] for result in search_results]
        
        # Then, extract content from these URLs
        response = tavily_client.extract(urls=urls)
        return response
    except Exception as e:
        print(f"An error occurred during Tavily content extraction: {str(e)}")
        return None

async def tavily_search_extract(query: str) -> tuple[str, str]:
    """
    Perform a search using Tavily API and extract both content and raw context.
    
    Args:
        query: The search query string
    
    Returns:
        tuple: (processed_content, raw_context)
    """
    try:
        print(f"Searching with query: {query}")
        
        # Get regular search results
        results = tavily_search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_raw_content=True  # Include raw content in results
        )
        
        # Get raw context
        raw_context = tavily_client.get_search_context(
            query=query,
            max_tokens=4000,
            search_depth="advanced"
        )
        
        if not results:
            return "No search results found.", raw_context or ""
            
        # Extract and combine relevant content
        content = []
        for result in results:
            content.append(result.get('content', ''))
        
        extracted_content = ' '.join(content)
        
        print(f"Extracted content length: {len(extracted_content)}")
        print(f"Raw context length: {len(raw_context) if raw_context else 0}")
        
        return extracted_content, raw_context
        
    except Exception as e:
        print(f"Error in tavily_search_extract: {str(e)}")
        return f"Error performing search: {str(e)}", ""

if __name__ == "__main__":
    async def main():
        await tavily_search_extract("https://www.prccopack.com/")
    
    # Run the async main function
    asyncio.run(main())
    
    
    
    
    test_domain = "prccopack.com"
    print("\n" + "="*50)
    print("Testing Tavily functions with:", test_domain)
    print("="*50)

    # Test 1: Basic Search
    print("\n1. Testing tavily_search with different parameters:")
    print("-"*30)
    search_results, raw_context = tavily_search(
        query=f"Tell me about",
        url=test_domain,
        search_depth="advanced",
        max_results=3,
    )
    
    print("\nResults:")
    if search_results:
        for result in search_results:
            print(f"\nURL: {result.get('url')}")
            print(f"Content: {result.get('content', '')}...\n")
            print(f"Raw Content: {result.get('raw_content', '')}...\n")
    else:
        print("No results found")

    # Test 2: Context Search
    print("\n2. Testing tavily_context_search:")
    print("-"*30)
    context = tavily_client.get_search_context(
        query=f"What does {test_domain} company do? Their products and services?",
        max_tokens=4000,
        search_depth="advanced",
        include_domains=[test_domain]
    )
    print("Context Results:", context)

    # Test 3: Content Extraction
    print("\n3. Testing tavily_extract_content:")
    print("-"*30)
    extracted = tavily_client.extract(
        urls=[f"https://www.{test_domain}"]
    )
    if extracted:
        print("Extracted Content:")
        print(json.dumps(extracted, indent=2))
