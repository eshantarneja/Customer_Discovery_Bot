"""
Module for handling web search operations.
"""
import asyncio
import aiohttp
from typing import Dict, Any, Tuple
from Classes.contacts import Contact
# Using a relative import since web_agent.py is in the same directory
from .web_agent import tavily_search

async def search_web(contact: dict) -> dict:
    """
    Perform web searches for company and person information concurrently.
    
    :param contact: Dictionary with contact information
    :return: Dictionary with company and person information
    """
    try:
        # Create tasks for both searches
        if contact['company_domain']:
            company_query = f"About {contact['company']} "
        else:
            company_query = contact['company']
        
        person_query = f" About {contact['name']} who works at {contact['company']} as {contact['job_title']}"
        
        print("\n" + "="*50)
        print("Starting web searches:")
        print(f"Company query: {company_query}")
        print(f"Person query: {person_query}")
        print("="*50 + "\n")
        
        # Run both searches concurrently
        company_task = asyncio.create_task(tavily_search(company_query))
        person_task = asyncio.create_task(tavily_search(person_query))
        
        # Wait for both searches to complete
        company_results, person_results = await asyncio.gather(company_task, person_task)
        
        # OpenAI's maximum length with safety margin
        MAX_PER_SECTION = 400000  # 800k total, split evenly

        # Truncate and combine results
        company_info = str(company_results[0])[:MAX_PER_SECTION] if company_results else ''
        person_info = str(person_results[0])[:MAX_PER_SECTION] if person_results else ''
        
        # Debug print the results
        print("\n" + "="*50)
        print("Search Results:")
        print(f"Company info found: {'Yes' if company_info else 'No'}")
        print(f"Company info length: {len(company_info)}")
        print(f"Person info found: {'Yes' if person_info else 'No'}")
        print(f"Person info length: {len(person_info)}")
        print("="*50 + "\n")
        
        return {
            'company_info': company_info or '',  # Ensure we return empty string if None
            'person_info': person_info or ''     # Ensure we return empty string if None
        }
    except Exception as e:
        print(f"Error in web search: {str(e)}")
        return {
            'company_info': '',
            'person_info': ''
        }
