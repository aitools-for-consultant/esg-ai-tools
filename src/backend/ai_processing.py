"""
AI processing module for the ESG & Finance AI Research Assistant.
This module uses OpenAI agents to process papers, including summarization,
categorization, keyword extraction, and recommendation.
"""
import sys
import json
from pathlib import Path
from datetime import datetime
import numpy as np
import time

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from openai import OpenAI
from agents import Agent, Computer
from agents.agent_output import AgentOutputSchema

from config.config import OPENAI_API_KEY, AGENT_CONFIG, EMBEDDING_MODEL, ESG_FINANCE_TERMS
from src.backend.database import (
    get_papers, get_paper_with_summary, add_summary, add_embedding,
    search_by_embedding
)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

class PaperProcessingAgent:
    """Agent for processing papers using OpenAI."""
    
    def __init__(self):
        """Initialize the paper processing agent."""
        self.client = client
        
        # Set up the agent with the ESG & Finance context
        self.esg_finance_context = (
            "You are an expert in ESG (Environmental, Social, and Governance) and Finance research. "
            "You have deep knowledge of sustainable finance, impact investing, climate finance, "
            "and related areas. You're skilled at analyzing academic papers and extracting key insights "
            "related to ESG and financial markets.\n\n"
            "Relevant terms in this field include: " + ", ".join(ESG_FINANCE_TERMS)
        )

        # Initialize the agent
        self.agent = Agent.from_args(
            instructions=self.esg_finance_context,
            model=AGENT_CONFIG["model"],
            temperature=AGENT_CONFIG["temperature"]
        )
        
        # Initialize the computer for complex tasks
        self.computer = Computer.from_args(
            instructions=self.esg_finance_context,
            model=AGENT_CONFIG["model"],
            temperature=AGENT_CONFIG["temperature"]
        )

    def summarize_paper(self, paper):
        """Summarize a research paper.
        
        Args:
            paper (dict): Paper data
            
        Returns:
            dict: Summary data
        """
        print(f"Summarizing paper: {paper['title']}")

        # Prepare the prompt
        prompt = f"""
        # Paper Analysis Task
        
        ## Paper Information
        Title: {paper['title']}
        Authors: {", ".join(paper['authors']) if isinstance(paper['authors'], list) else paper['authors']}
        Abstract: {paper['abstract']}
        
        ## Analysis Instructions
        Analyze this academic paper from an ESG and Finance perspective.
        
        Please provide:
        1. A concise summary (3-5 sentences)
        2. ESG relevance score (0-100)
        3. Finance relevance score (0-100) 
        4. 3-5 key findings or contributions
        5. 5-8 relevant keywords
        
        Format your response as a JSON object with these keys:
        - summary: string
        - esg_relevance_score: number
        - finance_relevance_score: number  
        - key_findings: list of strings
        - keywords: list of strings
        
        Consider these ESG focus areas:
        - Environmental: Climate change, resource use, pollution, biodiversity
        - Social: Human capital, product liability, stakeholder opposition
        - Governance: Corporate governance, corporate behavior
        
        And these Finance focus areas:
        - Asset pricing, portfolio management, risk management
        - Corporate finance, sustainable investing, green bonds
        - Financial markets, ESG investing, impact measurement
        """

        # Execute the agent task
        try:
            result = self.agent.run(prompt)
            
            # Parse the output and extract JSON
            json_output = self._extract_json_from_response(result)
            
            if json_output:
                # Create summary data
                summary_data = {
                    'paper_id': paper['id'],
                    'summary': json_output.get('summary', ''),
                    'esg_relevance_score': json_output.get('esg_relevance_score', 0),
                    'finance_relevance_score': json_output.get('finance_relevance_score', 0),
                    'key_findings': json_output.get('key_findings', []),
                    'keywords': json_output.get('keywords', []),
                    'created_date': datetime.now().isoformat()
                }
                
                return summary_data
            else:
                print(f"Failed to parse summary response for paper: {paper['id']}")
                return None
        except Exception as e:
            print(f"Error summarizing paper {paper['id']}: {e}")
            return None
    
    def compute_embedding(self, paper):
        """Compute embedding for a paper.
        
        Args:
            paper (dict): Paper data
            
        Returns:
            dict: Embedding data
        """
        try:
            # Prepare the text to embed (title + abstract)
            text_to_embed = f"{paper['title']} {paper['abstract']}"
            
            # Get embedding
            response = self.client.embeddings.create(
                input=text_to_embed,
                model=EMBEDDING_MODEL
            )
            
            # Extract the embedding vector
            embedding_vector = response.data[0].embedding
            
            # Create embedding data
            embedding_data = {
                'paper_id': paper['id'],
                'embedding': embedding_vector,
                'model': EMBEDDING_MODEL,
                'created_date': datetime.now().isoformat()
            }
            
            return embedding_data
        except Exception as e:
            print(f"Error computing embedding for paper {paper['id']}: {e}")
            return None
    
    def generate_research_brief(self, query, num_results=5):
        """Generate a research brief based on a user query.
        
        Args:
            query (str): User's research query
            num_results (int): Number of papers to include
            
        Returns:
            dict: Research brief data
        """
        print(f"Generating research brief for query: {query}")
        
        # First, generate an embedding for the query
        try:
            query_embedding_response = self.client.embeddings.create(
                input=query,
                model=EMBEDDING_MODEL
            )
            query_embedding = query_embedding_response.data[0].embedding
            
            # Search for similar papers
            similar_papers = search_by_embedding(query_embedding, limit=num_results)
            
            if not similar_papers:
                return {
                    'query': query,
                    'timestamp': datetime.now().isoformat(),
                    'message': "No relevant papers found for your query."
                }
                
            # Prepare paper information for the research brief
            paper_info = []
            for paper in similar_papers:
                paper_info.append({
                    'title': paper['title'],
                    'authors': paper['authors'],
                    'summary': paper.get('summary', {}).get('summary', 'No summary available'),
                    'key_findings': paper.get('summary', {}).get('key_findings', []),
                    'url': paper['url']
                })
                
            # Prepare the prompt for the research brief
            prompt = f"""
            # Research Brief Generation Task
            
            ## Query
            "{query}"
            
            ## Relevant Papers
            {json.dumps(paper_info, indent=2)}
            
            ## Instructions
            Generate a comprehensive research brief based on the user's query and the relevant papers provided.
            
            Your brief should include:
            1. An executive summary (2-3 paragraphs)
            2. Key themes and findings across the papers
            3. Research gaps or opportunities
            4. Practical implications for ESG and Finance professionals
            5. Recommended next steps or areas for further research
            
            Format your response as a well-structured research brief with these sections clearly labeled.
            Keep the focus on ESG and Finance implications.
            """
            
            # Execute the computer task for detailed analysis
            result = self.computer.run(prompt)
            
            # Create research brief data
            research_brief = {
                'query': query,
                'papers': paper_info,
                'brief': result,
                'timestamp': datetime.now().isoformat()
            }
            
            return research_brief
            
        except Exception as e:
            print(f"Error generating research brief: {e}")
            return {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _extract_json_from_response(self, response):
        """Extract JSON from agent response.
        
        Args:
            response (str): Agent response
            
        Returns:
            dict: Extracted JSON data or None
        """
        try:
            # First try to parse the entire response as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # If that fails, try to find JSON within the response
            import re
            json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
            match = re.search(json_pattern, response)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
                    
            # Another common pattern: {...}
            json_pattern = r'\{[\s\S]*\}'
            match = re.search(json_pattern, response)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
                    
            print(f"Failed to extract JSON from response: {response}")
            return None


def process_new_papers(limit=10):
    """Process newly added papers that don't have summaries or embeddings.
    
    Args:
        limit (int): Maximum number of papers to process
        
    Returns:
        dict: Statistics about processed papers
    """
    results = {
        'summarized': 0,
        'embedded': 0,
        'errors': 0,
        'timestamp': datetime.now().isoformat()
    }
    
    # Get papers that need processing
    papers = get_papers(limit=limit)
    if not papers:
        print("No papers to process")
        return results
        
    # Initialize the agent
    agent = PaperProcessingAgent()
    
    # Process each paper
    for paper in papers:
        try:
            # Check if this paper already has a summary and embedding
            paper_with_data = get_paper_with_summary(paper['id'])
            
            if paper_with_data and 'summary' in paper_with_data:
                # Summary exists, skip
                print(f"Paper {paper['id']} already has a summary, skipping...")
                continue
                
            # Generate summary
            summary_data = agent.summarize_paper(paper)
            if summary_data:
                # Save the summary to the database
                if add_summary(summary_data):
                    results['summarized'] += 1
                    print(f"Added summary for paper {paper['id']}")
                
            # Generate embedding
            embedding_data = agent.compute_embedding(paper)
            if embedding_data:
                # Save the embedding to the database
                if add_embedding(embedding_data):
                    results['embedded'] += 1
                    print(f"Added embedding for paper {paper['id']}")
            
            # Be nice to the API
            time.sleep(2)
            
        except Exception as e:
            print(f"Error processing paper {paper['id']}: {e}")
            results['errors'] += 1
    
    return results


if __name__ == "__main__":
    # Test paper processing
    stats = process_new_papers(limit=5)
    print(f"Processed papers statistics: {stats}")
    
    # Test research brief generation
    agent = PaperProcessingAgent()
    brief = agent.generate_research_brief("climate finance impact on corporate governance")
    print(f"Generated research brief: {brief['brief'][:200]}...")