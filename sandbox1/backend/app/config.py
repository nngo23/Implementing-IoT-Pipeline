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
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    # Qdrant Settings
    QDRANT_HOST = os.getenv('QDRANT_HOST', 'localhost')
    QDRANT_PORT = int(os.getenv('QDRANT_PORT', 6333))
    QDRANT_COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME', 'candidates')
    # Embedding Settings
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'jinaai/jina-embeddings-v3')
    TOP_K_RESULTS = 5
    
    TOP_K_SEARCHS = 20
    # Voice Settings
    N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'medium')
    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / 'data'
    RAW_DIR = DATA_DIR / 'rawData'
    PROCESSED_DIR = DATA_DIR / 'processedData'
    CANDIDATES_FILE = RAW_DIR / 'candidates.json'
    QDRANT_COLLECTION_PROFESSIONALSTANDARD = os.getenv('QDRANT_COLLECTION_PROFESSIONALSTANDARD', 'professional_standards')
    STANDARDS_FILE = RAW_DIR / 'professionalStandard.json'
    


Config = Config()