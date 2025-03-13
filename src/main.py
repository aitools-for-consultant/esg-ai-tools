"""
Main application file for the ESG & Finance AI Research Assistant.
"""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

import argparse
from datetime import datetime
import json
import os

from config.config import DATA_DIR, OPENAI_API_KEY
from src.backend.scheduler import get_scheduler
from src.backend.data_collectors import collect_new_papers
from src.backend.ai_processing import process_new_papers, PaperProcessingAgent
from src.backend.database import get_papers, get_paper_with_summary, log_user_query

def init_app():
    """Initialize the application."""
    # Ensure data directories exist
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "papers").mkdir(exist_ok=True)
    (DATA_DIR / "embeddings").mkdir(exist_ok=True)
    (DATA_DIR / "db").mkdir(exist_ok=True)
    
    # Check if OpenAI API key is set
    if not OPENAI_API_KEY:
        print("Warning: OPENAI_API_KEY environment variable is not set.")
        print("Set it with: export OPENAI_API_KEY=your-api-key")
        return False
    
    return True

def start_scheduler():
    """Start the scheduler."""
    scheduler = get_scheduler()
    success = scheduler.start()
    
    if success:
        print("Scheduler started successfully")
        print("The ESG & Finance AI Research Assistant will collect and process papers on schedule")
    else:
        print("Failed to start scheduler")
    
    return success

def stop_scheduler():
    """Stop the scheduler."""
    scheduler = get_scheduler()
    success = scheduler.stop()
    
    if success:
        print("Scheduler stopped successfully")
    else:
        print("Failed to stop scheduler")
    
    return success

def scheduler_status():
    """Get the scheduler status."""
    scheduler = get_scheduler()
    status = scheduler.get_status()
    
    print(f"Scheduler running: {status['running']}")
    if status['last_collection']:
        print(f"Last collection: {status['last_collection']}")
        if 'collection_stats' in status and status['collection_stats']:
            print(f"  Collected: {status['collection_stats'].get('total', 0)} papers")
    
    if status['last_processing']:
        print(f"Last processing: {status['last_processing']}")
        if 'processing_stats' in status and status['processing_stats']:
            print(f"  Summarized: {status['processing_stats'].get('summarized', 0)} papers")
            print(f"  Embedded: {status['processing_stats'].get('embedded', 0)} papers")
    
    return status

def collect_papers():
    """Collect papers immediately."""
    print("Starting paper collection...")
    stats = collect_new_papers()
    
    print(f"Collection completed:")
    print(f"  Total collected: {stats['total']} papers")
    print(f"  From arXiv: {stats['arxiv']} papers")
    print(f"  From SSRN: {stats['ssrn']} papers")
    
    return stats

def process_papers(limit=10):
    """Process papers immediately."""
    print(f"Starting paper processing (limit: {limit})...")
    stats = process_new_papers(limit=limit)
    
    print("Processing completed:")
    print(f"  Summarized: {stats['summarized']} papers")
    print(f"  Embedded: {stats['embedded']} papers")
    print(f"  Errors: {stats['errors']}")
    
    return stats

def list_papers(limit=10, category=None, query=None):
    """List papers from the database."""
    papers = get_papers(limit=limit, category=category, query=query)
    
    print(f"Found {len(papers)} papers:")
    for i, paper in enumerate(papers):
        print(f"{i+1}. {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors']) if isinstance(paper['authors'], list) else paper['authors']}")
        print(f"   URL: {paper['url']}")
        print(f"   Date: {paper['published_date']}")
        print()
    
    return papers

def generate_research_brief(query):
    """Generate a research brief for a query."""
    if not query:
        print("Error: Query is required")
        return None
    
    print(f"Generating research brief for query: {query}")
    
    # Log the user query
    log_user_query(query)
    
    # Create an agent and generate a brief
    agent = PaperProcessingAgent()
    brief = agent.generate_research_brief(query)
    
    if 'brief' in brief:
        print("\n--- Research Brief ---\n")
        print(brief['brief'])
        print("\n--- End of Brief ---\n")
        
        # Save the brief to a file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_brief_{timestamp}.txt"
        filepath = DATA_DIR / filename
        
        with open(filepath, 'w') as f:
            f.write(f"Query: {query}\n")
            f.write(f"Date: {datetime.now().isoformat()}\n\n")
            f.write(brief['brief'])
        
        print(f"Research brief saved to: {filepath}")
    else:
        print("No research brief generated.")
        if 'error' in brief:
            print(f"Error: {brief['error']}")
        elif 'message' in brief:
            print(f"Message: {brief['message']}")
    
    return brief

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='ESG & Finance AI Research Assistant')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # start command
    start_parser = subparsers.add_parser('start', help='Start the scheduler')
    
    # stop command
    stop_parser = subparsers.add_parser('stop', help='Stop the scheduler')
    
    # status command
    status_parser = subparsers.add_parser('status', help='Get scheduler status')
    
    # collect command
    collect_parser = subparsers.add_parser('collect', help='Collect papers immediately')
    
    # process command
    process_parser = subparsers.add_parser('process', help='Process papers immediately')
    process_parser.add_argument('--limit', type=int, default=10, help='Maximum number of papers to process')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List papers')
    list_parser.add_argument('--limit', type=int, default=10, help='Maximum number of papers to list')
    list_parser.add_argument('--category', type=str, help='Filter by category')
    list_parser.add_argument('--query', type=str, help='Search query')
    
    # brief command
    brief_parser = subparsers.add_parser('brief', help='Generate a research brief')
    brief_parser.add_argument('query', type=str, help='Research query')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize the application
    if not init_app():
        return 1
    
    # Run the appropriate command
    if args.command == 'start':
        start_scheduler()
    elif args.command == 'stop':
        stop_scheduler()
    elif args.command == 'status':
        scheduler_status()
    elif args.command == 'collect':
        collect_papers()
    elif args.command == 'process':
        process_papers(limit=args.limit)
    elif args.command == 'list':
        list_papers(limit=args.limit, category=args.category, query=args.query)
    elif args.command == 'brief':
        generate_research_brief(args.query)
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())