"""
REST API for the ESG & Finance AI Research Assistant.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from pathlib import Path
# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.backend.scheduler import get_scheduler
from src.backend.data_collectors import collect_new_papers
from src.backend.ai_processing import process_new_papers, PaperProcessingAgent
from src.backend.database import (
    get_papers, get_paper_with_summary, log_user_query,
    search_by_embedding
)
from config.config import OPENAI_API_KEY

app = Flask(__name__)
# Enable CORS for all routes and origins
CORS(app)

@app.route('/api/status', methods=['GET'])
def api_status():
    """Get the status of the ESG & Finance AI Research Assistant."""
    scheduler = get_scheduler()
    status = scheduler.get_status()
    return jsonify(status)

@app.route('/api/papers', methods=['GET'])
def api_papers():
    """Get a list of papers."""
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    category = request.args.get('category')
    query = request.args.get('query')
    
    papers = get_papers(limit=limit, offset=offset, category=category, query=query)
    return jsonify(papers)

@app.route('/api/paper/<paper_id>', methods=['GET'])
def api_paper(paper_id):
    """Get details of a specific paper."""
    paper = get_paper_with_summary(paper_id)
    if paper:
        return jsonify(paper)
    else:
        return jsonify({'error': 'Paper not found'}), 404

@app.route('/api/collect', methods=['POST'])
def api_collect():
    """Collect papers immediately."""
    stats = collect_new_papers()
    return jsonify(stats)

@app.route('/api/process', methods=['POST'])
def api_process():
    """Process papers immediately."""
    limit = int(request.json.get('limit', 10))
    stats = process_new_papers(limit=limit)
    return jsonify(stats)

@app.route('/api/brief', methods=['POST'])
def api_brief():
    """Generate a research brief."""
    if not request.json or 'query' not in request.json:
        return jsonify({'error': 'No query provided'}), 400
    
    query = request.json['query']
    log_user_query(query)
    
    agent = PaperProcessingAgent()
    brief = agent.generate_research_brief(query)
    return jsonify(brief)

@app.route('/api/scheduler/start', methods=['POST'])
def api_scheduler_start():
    """Start the scheduler."""
    scheduler = get_scheduler()
    success = scheduler.start()
    return jsonify({'success': success})

@app.route('/api/scheduler/stop', methods=['POST'])
def api_scheduler_stop():
    """Stop the scheduler."""
    scheduler = get_scheduler()
    success = scheduler.stop()
    return jsonify({'success': success})

@app.route('/api/search', methods=['POST'])
def api_search():
    """Search by query embedding."""
    if not request.json or 'query' not in request.json:
        return jsonify({'error': 'No query provided'}), 400
    
    query = request.json['query']
    limit = int(request.json.get('limit', 5))
    
    # Log the query
    log_user_query(query)
    
    # Generate embedding and search
    agent = PaperProcessingAgent()
    try:
        query_embedding_response = agent.client.embeddings.create(
            input=query,
            model="text-embedding-3-large"
        )
        query_embedding = query_embedding_response.data[0].embedding
        
        # Search for similar papers
        similar_papers = search_by_embedding(query_embedding, limit=limit)
        return jsonify(similar_papers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def start_api(host='0.0.0.0', port=5001, debug=False):
    """Start the API server."""
    # Check for OpenAI API key
    if not OPENAI_API_KEY:
        print("Warning: OPENAI_API_KEY environment variable is not set")
        print("Set it with: export OPENAI_API_KEY=your-api-key")
    
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    start_api(debug=True)