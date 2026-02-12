import os
from dotenv import load_dotenv
from pathlib import Path
import json

# Load .env file
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    APP_NAME: str = "Recruitment AI Bot"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    # Gemini AI Settings
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    # Qdrant Settings
    QDRANT_HOST = os.getenv('QDRANT_HOST', 'localhost')
    QDRANT_PORT = int(os.getenv('QDRANT_PORT', 6333))
    QDRANT_COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME', 'candidates')
    # Embedding Settings
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'jinaai/jina-embeddings-v3')
    TOP_K_RESULTS = 5
    MAX_TOP_K = 20
    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / 'data'
    RAW_DIR = DATA_DIR / 'rawData'
    PROCESSED_DIR = DATA_DIR / 'processedData'
    CANDIDATES_FILE = RAW_DIR / 'candidates.json'
    QDRANT_COLLECTION_PROFESSIONALSTANDARD = os.getenv('QDRANT_COLLECTION_PROFESSIONALSTANDARD', 'professional_standards')
    STANDARDS_FILE = RAW_DIR / 'professionalStandard.json'

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", 5432)
    DB_NAME = os.getenv("DB_NAME")

Config = Config()