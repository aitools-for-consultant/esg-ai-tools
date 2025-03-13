"""
Configuration file for the ESG & Finance AI Research Assistant.
"""

import os
from pathlib import Path

# Project paths
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
SRC_DIR = ROOT_DIR / "src"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "papers").mkdir(exist_ok=True)
(DATA_DIR / "embeddings").mkdir(exist_ok=True)
(DATA_DIR / "db").mkdir(exist_ok=True)

# Database configuration
DB_PATH = DATA_DIR / "db" / "research.db"

# API Keys (preferably load from environment variables)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Paper sources configuration
SOURCES = {
    "arxiv": {
        "categories": ["q-fin", "econ", "stat.AP"],  # Finance, Economics, Applied Statistics
        "max_results": 50,
        "sort_by": "submittedDate",
        "sort_order": "descending"
    },
    "ssrn": {
        "topics": ["ESG", "Environmental Finance", "Social Finance", "Governance", 
                  "Sustainable Finance", "Green Finance", "Climate Finance"]
    }
}

# Agent configuration
AGENT_CONFIG = {
    "model": "gpt-4o",
    "temperature": 0.1,
    "max_tokens": 4000
}

# Embedding configuration
EMBEDDING_MODEL = "text-embedding-3-large"

# Schedule configuration (in minutes)
SCHEDULE = {
    "data_collection": 1440,  # Daily
    "data_processing": 360,   # Every 6 hours
}

# ESG & Finance specific terms for improved model context
ESG_FINANCE_TERMS = [
    "ESG", "Environmental, Social, and Governance", "Sustainability", 
    "Carbon Footprint", "Green Bonds", "Social Impact", "Corporate Governance",
    "Climate Risk", "Sustainable Development Goals", "SDGs", "CSR",
    "Impact Investing", "Ethical Investing", "SRI", "Green Finance",
    "Climate Finance", "Transition Risk", "Physical Risk", "Stranded Assets",
    "TCFD", "SASB", "GRI", "Net Zero", "Carbon Neutral", "Paris Agreement"
]