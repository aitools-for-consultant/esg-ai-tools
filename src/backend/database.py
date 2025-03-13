"""
Database models and operations for the ESG & Finance AI Research Assistant.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import DB_PATH

def init_db():
    """Initialize the database with required tables."""
    DB_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create papers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS papers (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        abstract TEXT,
        authors TEXT,
        url TEXT,
        pdf_url TEXT,
        published_date TEXT,
        source TEXT,
        categories TEXT,
        retrieved_date TEXT,
        embedding_id TEXT,
        UNIQUE(id)
    )
    ''')
    
    # Create summaries table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paper_id TEXT,
        summary TEXT,
        esg_relevance_score REAL,
        finance_relevance_score REAL,
        key_findings TEXT,
        keywords TEXT,
        created_date TEXT,
        FOREIGN KEY (paper_id) REFERENCES papers(id)
    )
    ''')
    
    # Create embeddings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paper_id TEXT,
        embedding BLOB,
        model TEXT,
        created_date TEXT,
        FOREIGN KEY (paper_id) REFERENCES papers(id)
    )
    ''')
    
    # Create user_queries table to track user interests
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT,
        timestamp TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

def add_paper(paper_data):
    """Add a new paper to the database.
    
    Args:
        paper_data (dict): Dictionary containing paper details
    
    Returns:
        bool: Success status
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Convert list fields to JSON strings
        if 'authors' in paper_data and isinstance(paper_data['authors'], list):
            paper_data['authors'] = json.dumps(paper_data['authors'])
        if 'categories' in paper_data and isinstance(paper_data['categories'], list):
            paper_data['categories'] = json.dumps(paper_data['categories'])
        
        # Add retrieved date if not present
        if 'retrieved_date' not in paper_data:
            paper_data['retrieved_date'] = datetime.now().isoformat()
            
        cursor.execute('''
        INSERT OR REPLACE INTO papers (
            id, title, abstract, authors, url, pdf_url, published_date, 
            source, categories, retrieved_date, embedding_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            paper_data.get('id'),
            paper_data.get('title'),
            paper_data.get('abstract'),
            paper_data.get('authors'),
            paper_data.get('url'),
            paper_data.get('pdf_url'),
            paper_data.get('published_date'),
            paper_data.get('source'),
            paper_data.get('categories'),
            paper_data.get('retrieved_date'),
            paper_data.get('embedding_id')
        ))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding paper to database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def add_summary(summary_data):
    """Add a summary for a paper.
    
    Args:
        summary_data (dict): Dictionary containing summary details
        
    Returns:
        bool: Success status
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        if isinstance(summary_data.get('keywords', []), list):
            summary_data['keywords'] = json.dumps(summary_data.get('keywords', []))
            
        if isinstance(summary_data.get('key_findings', []), list):
            summary_data['key_findings'] = json.dumps(summary_data.get('key_findings', []))
            
        if 'created_date' not in summary_data:
            summary_data['created_date'] = datetime.now().isoformat()
            
        cursor.execute('''
        INSERT INTO summaries (
            paper_id, summary, esg_relevance_score, finance_relevance_score,
            key_findings, keywords, created_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            summary_data.get('paper_id'),
            summary_data.get('summary'),
            summary_data.get('esg_relevance_score'),
            summary_data.get('finance_relevance_score'),
            summary_data.get('key_findings'),
            summary_data.get('keywords'),
            summary_data.get('created_date')
        ))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding summary to database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def add_embedding(embedding_data):
    """Add an embedding for a paper.
    
    Args:
        embedding_data (dict): Dictionary containing embedding details
        
    Returns:
        int: ID of the inserted embedding or None on failure
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        if 'created_date' not in embedding_data:
            embedding_data['created_date'] = datetime.now().isoformat()
            
        # Convert embedding vector to binary
        if isinstance(embedding_data.get('embedding'), list):
            embedding_data['embedding'] = json.dumps(embedding_data['embedding'])
            
        cursor.execute('''
        INSERT INTO embeddings (
            paper_id, embedding, model, created_date
        ) VALUES (?, ?, ?, ?)
        ''', (
            embedding_data.get('paper_id'),
            embedding_data.get('embedding'),
            embedding_data.get('model'),
            embedding_data.get('created_date')
        ))
        
        embedding_id = cursor.lastrowid
        
        # Update the paper with the embedding_id
        cursor.execute('''
        UPDATE papers SET embedding_id = ? WHERE id = ?
        ''', (embedding_id, embedding_data.get('paper_id')))
        
        conn.commit()
        return embedding_id
    except Exception as e:
        print(f"Error adding embedding to database: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_papers(limit=100, offset=0, category=None, query=None):
    """Get papers from the database with optional filtering.
    
    Args:
        limit (int): Maximum number of papers to return
        offset (int): Offset for pagination
        category (str): Optional category filter
        query (str): Optional text search query
        
    Returns:
        list: List of paper dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    sql = "SELECT * FROM papers"
    params = []
    
    # Add filters if provided
    where_clauses = []
    if category:
        where_clauses.append("categories LIKE ?")
        params.append(f'%{category}%')
    
    if query:
        where_clauses.append("(title LIKE ? OR abstract LIKE ?)")
        params.extend([f'%{query}%', f'%{query}%'])
    
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
    
    sql += " ORDER BY published_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    try:
        cursor.execute(sql, params)
        papers = [dict(row) for row in cursor.fetchall()]
        
        # Parse JSON strings back to lists
        for paper in papers:
            if paper['authors']:
                try:
                    paper['authors'] = json.loads(paper['authors'])
                except:
                    pass
            if paper['categories']:
                try:
                    paper['categories'] = json.loads(paper['categories'])
                except:
                    pass
        
        return papers
    except Exception as e:
        print(f"Error retrieving papers: {e}")
        return []
    finally:
        conn.close()

def get_paper_with_summary(paper_id):
    """Get a paper with its summary and embedding.
    
    Args:
        paper_id (str): ID of the paper
        
    Returns:
        dict: Paper data with summary and embedding
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Get the paper
        cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
        paper = dict(cursor.fetchone() or {})
        
        if not paper:
            return None
            
        # Parse JSON strings
        if paper.get('authors'):
            try:
                paper['authors'] = json.loads(paper['authors'])
            except:
                pass
        if paper.get('categories'):
            try:
                paper['categories'] = json.loads(paper['categories'])
            except:
                pass
        
        # Get the summary
        cursor.execute("SELECT * FROM summaries WHERE paper_id = ? ORDER BY created_date DESC LIMIT 1", (paper_id,))
        summary_row = cursor.fetchone()
        if summary_row:
            summary = dict(summary_row)
            if summary.get('keywords'):
                try:
                    summary['keywords'] = json.loads(summary['keywords'])
                except:
                    pass
            if summary.get('key_findings'):
                try:
                    summary['key_findings'] = json.loads(summary['key_findings'])
                except:
                    pass
            paper['summary'] = summary
        
        return paper
    except Exception as e:
        print(f"Error retrieving paper with summary: {e}")
        return None
    finally:
        conn.close()

def search_by_embedding(embedding_vector, limit=5):
    """Search for papers by embedding similarity.
    
    Args:
        embedding_vector (list): Embedding vector to search with
        limit (int): Maximum number of results
        
    Returns:
        list: Similar papers with similarity scores
    """
    # This would be more efficient with a vector database like FAISS or Pinecone
    # For SQLite, we'll implement a simple but less efficient approach
    # This would need to be optimized for production use
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Get all embeddings
        cursor.execute("SELECT * FROM embeddings")
        embeddings = [dict(row) for row in cursor.fetchall()]
        
        results = []
        embedding_vec_json = json.dumps(embedding_vector)
        
        for emb in embeddings:
            try:
                db_vector = json.loads(emb['embedding'])
                # Compute cosine similarity (simplified)
                similarity = compute_similarity(embedding_vector, db_vector)
                
                results.append({
                    'paper_id': emb['paper_id'],
                    'similarity': similarity
                })
            except:
                continue
                
        # Sort by similarity (descending)
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Get the top papers
        top_results = results[:limit]
        paper_ids = [r['paper_id'] for r in top_results]
        
        # Get the paper data
        papers = []
        for i, paper_id in enumerate(paper_ids):
            paper = get_paper_with_summary(paper_id)
            if paper:
                paper['similarity'] = top_results[i]['similarity']
                papers.append(paper)
                
        return papers
    except Exception as e:
        print(f"Error searching by embedding: {e}")
        return []
    finally:
        conn.close()

def compute_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors.
    
    Args:
        vec1 (list): First vector
        vec2 (list): Second vector
        
    Returns:
        float: Similarity score between 0 and 1
    """
    import numpy as np
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    similarity = dot_product / (norm_v1 * norm_v2)
    return float(similarity)

def log_user_query(query):
    """Log a user query to track interests.
    
    Args:
        query (str): User's query
        
    Returns:
        bool: Success status
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO user_queries (query, timestamp)
        VALUES (?, ?)
        ''', (query, datetime.now().isoformat()))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error logging user query: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# Initialize database when module is imported
if __name__ == "__main__":
    init_db()