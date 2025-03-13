"""
Data collectors for retrieving research papers from various sources.
"""

import sys
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import time
import re
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import SOURCES
from src.backend.database import add_paper

class ArxivCollector:
    """Collector for papers from the arXiv repository."""
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    def __init__(self, categories=None, max_results=50):
        """Initialize the ArXiv collector.
        
        Args:
            categories (list): List of arXiv categories to search for
            max_results (int): Maximum number of results to return
        """
        self.categories = categories or SOURCES["arxiv"]["categories"]
        self.max_results = max_results or SOURCES["arxiv"]["max_results"]
    
    def fetch_recent_papers(self, since_days=7):
        """Fetch papers published since a number of days ago.
        
        Args:
            since_days (int): Number of days to look back
            
        Returns:
            list: List of paper data dictionaries
        """
        date_cutoff = datetime.now() - timedelta(days=since_days)
        
        papers = []
        for category in self.categories:
            # Format the search query for the category and date range
            query = f"cat:{category}"
            
            # Build the API request URL
            params = {
                "search_query": query,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "max_results": self.max_results
            }
            
            # Add start parameter for pagination if needed
            # params["start"] = 0
            
            try:
                response = requests.get(self.BASE_URL, params=params)
                response.raise_for_status()
                
                # Parse the XML response
                root = ET.fromstring(response.content)
                
                # Handle entries
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    # Extract paper details
                    paper_id = entry.find('{http://www.w3.org/2005/Atom}id').text
                    paper_id = paper_id.split('/')[-1]  # Extract the arXiv ID
                    
                    title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                    abstract = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
                    
                    # Extract published date
                    published = entry.find('{http://www.w3.org/2005/Atom}published').text
                    published_date = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
                    
                    # Skip if the paper is older than the cutoff
                    if published_date < date_cutoff:
                        continue
                    
                    # Extract authors
                    authors = []
                    for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
                        name = author.find('{http://www.w3.org/2005/Atom}name').text
                        authors.append(name)
                    
                    # Extract URL and PDF URL
                    url = entry.find('{http://www.w3.org/2005/Atom}id').text
                    pdf_url = url.replace('abs', 'pdf') + '.pdf'
                    
                    # Extract categories
                    primary_category = entry.find('{http://arxiv.org/schemas/atom}primary_category')
                    categories = [primary_category.attrib['term']]
                    
                    # Prepare paper data
                    paper_data = {
                        'id': paper_id,
                        'title': title,
                        'abstract': abstract,
                        'authors': authors,
                        'url': url,
                        'pdf_url': pdf_url,
                        'published_date': published_date.isoformat(),
                        'source': 'arxiv',
                        'categories': categories,
                        'retrieved_date': datetime.now().isoformat()
                    }
                    
                    papers.append(paper_data)
                
                # Be nice to the API
                time.sleep(3)
                
            except Exception as e:
                print(f"Error fetching papers from arXiv for category {category}: {e}")
                continue
                
        return papers
    
    def fetch_by_keyword(self, keyword, max_results=50):
        """Fetch papers by keyword search.
        
        Args:
            keyword (str): Keyword to search for
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of paper data dictionaries
        """
        # Format the search query
        query = f"all:{quote_plus(keyword)}"
        if self.categories:
            for category in self.categories:
                query += f" AND cat:{category}"
        
        # Build the API request URL
        params = {
            "search_query": query,
            "sortBy": "relevance",
            "max_results": max_results
        }
        
        papers = []
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            # Parse the XML response
            root = ET.fromstring(response.content)
            
            # Handle entries
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                # Extract paper details
                paper_id = entry.find('{http://www.w3.org/2005/Atom}id').text
                paper_id = paper_id.split('/')[-1]  # Extract the arXiv ID
                
                title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                abstract = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
                
                # Extract published date
                published = entry.find('{http://www.w3.org/2005/Atom}published').text
                published_date = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
                
                # Extract authors
                authors = []
                for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
                    name = author.find('{http://www.w3.org/2005/Atom}name').text
                    authors.append(name)
                
                # Extract URL and PDF URL
                url = entry.find('{http://www.w3.org/2005/Atom}id').text
                pdf_url = url.replace('abs', 'pdf') + '.pdf'
                
                # Extract categories
                primary_category = entry.find('{http://arxiv.org/schemas/atom}primary_category')
                categories = [primary_category.attrib['term']]
                
                # Prepare paper data
                paper_data = {
                    'id': paper_id,
                    'title': title,
                    'abstract': abstract,
                    'authors': authors,
                    'url': url,
                    'pdf_url': pdf_url,
                    'published_date': published_date.isoformat(),
                    'source': 'arxiv',
                    'categories': categories,
                    'retrieved_date': datetime.now().isoformat()
                }
                
                papers.append(paper_data)
            
        except Exception as e:
            print(f"Error fetching papers from arXiv for keyword {keyword}: {e}")
            
        return papers
    
    def save_papers(self, papers):
        """Save papers to the database.
        
        Args:
            papers (list): List of paper data dictionaries
            
        Returns:
            int: Number of papers saved
        """
        saved_count = 0
        for paper in papers:
            if add_paper(paper):
                saved_count += 1
        
        return saved_count


class SSRNCollector:
    """Collector for papers from SSRN.
    
    Note: SSRN doesn't offer a public API, so this implementation uses a hypothetical
    approach. In a real application, you might need to use web scraping or a paid API service.
    """
    
    def fetch_recent_papers(self, topics=None):
        """Fetch papers for given topics.
        
        Args:
            topics (list): List of topics to search for
            
        Returns:
            list: List of paper data dictionaries
        """
        print("SSRN data collection not implemented yet - would require web scraping or a paid API")
        return []


def collect_new_papers():
    """Collect new papers from all configured sources.
    
    Returns:
        dict: Statistics about collected papers
    """
    results = {
        'arxiv': 0,
        'ssrn': 0,
        'total': 0,
        'timestamp': datetime.now().isoformat()
    }
    
    # Collect from arXiv
    arxiv_collector = ArxivCollector()
    arxiv_papers = arxiv_collector.fetch_recent_papers(since_days=7)
    results['arxiv'] = arxiv_collector.save_papers(arxiv_papers)
    
    # Collect from SSRN (not implemented)
    ssrn_collector = SSRNCollector()
    ssrn_papers = ssrn_collector.fetch_recent_papers()
    # results['ssrn'] = ssrn_collector.save_papers(ssrn_papers)
    
    # Calculate total
    results['total'] = results['arxiv'] + results['ssrn']
    
    return results


if __name__ == "__main__":
    # Test the collectors
    results = collect_new_papers()
    print(f"Collected {results['total']} new papers.")
    print(f"- arXiv: {results['arxiv']} papers")
    print(f"- SSRN: {results['ssrn']} papers")