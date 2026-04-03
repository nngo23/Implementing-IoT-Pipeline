import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from transformers import AutoModel
from app.config import Config

def setup_vector_db():
    
    # Load data
    print(f"Loading candidates from: {Config.CANDIDATES_FILE}")
    with open(Config.CANDIDATES_FILE, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    print(f"Loaded {len(candidates)} candidates\n")
    
    # Load encoder
    print(f"Loading embedding model: {Config.EMBEDDING_MODEL}")
    encoder =  AutoModel.from_pretrained("jinaai/jina-embeddings-v3", trust_remote_code=True)
    print("Model loaded\n")
    
    # Connect Qdrant
    print(f"Connecting to Qdrant at {Config.QDRANT_HOST}:{Config.QDRANT_PORT}")
    client = QdrantClient(host=Config.QDRANT_HOST, port=Config.QDRANT_PORT)
    
    try:
        collections = client.get_collections()
        print("Connected to Qdrant\n")
    except Exception as e:
        print(f"Failed to connect to Qdrant: {e}")
        return
    
    # Delete old collection
    print(f"Deleting old collection: {Config.QDRANT_COLLECTION_NAME}")
    try:
        client.delete_collection(Config.QDRANT_COLLECTION_NAME)
        print("Old collection deleted\n")
    except:
        print("No existing collection to delete\n")
    
    # Create new collection
    print(f"Creating new collection: {Config.QDRANT_COLLECTION_NAME}")
    client.create_collection(
        collection_name=Config.QDRANT_COLLECTION_NAME,
        vectors_config=VectorParams(size=1024 , distance=Distance.COSINE)
    )
    
    # Encode and prepare points
    points = []
    for idx, candidate in enumerate(candidates):
        # Build text representation - FIX: handle nested education field
        education_text = ""
        if isinstance(candidate.get('education'), dict):
            education_text = f"{candidate['education'].get('level', '')} {candidate['education'].get('field', '')} {candidate['education'].get('institution', '')}"
        else:
            education_text = str(candidate.get('education', ''))
        
        # Build comprehensive text for embedding
        text_parts = [
            candidate.get('name', ''),
            candidate.get('industry', ''),
            candidate.get('category', ''),
            candidate.get('role', ''),
            candidate.get('role_en', ''),
            ' '.join(candidate.get('skills', [])),
            str(candidate.get('experience_years', '')),
            education_text,
            candidate.get('summary', ''),
            candidate.get('location', {}).get('city', ''),
            candidate.get('location', {}).get('postal code', ''),
        ]
        
        # Add licenses
        if 'licenses' in candidate and isinstance(candidate['licenses'], list):
            text_parts.extend([lic.get('name', '') for lic in candidate['licenses']])
        
        # Add languages
        if 'languages' in candidate and isinstance(candidate['languages'], list):
            text_parts.extend([lang.get('language', '') for lang in candidate['languages']])
        
        text = ' '.join(filter(None, text_parts))
        
        # Encode to vector
        vector = encoder.encode(text,task="retrieval.passage").tolist()
        
        # Create point
        points.append(PointStruct(
            id=idx, 
            vector=vector, 
            payload=candidate
        ))
        
        # Progress indicator
        if (idx + 1) % 10 == 0:
            print(f"   Processed: {idx + 1}/{len(candidates)} candidates...")
    
    
    # Upload to Qdrant
    client.upsert(
        collection_name=Config.QDRANT_COLLECTION_NAME, 
        points=points
    )
    print("Upload complete\n")
    
    # Verify
    info = client.get_collection(Config.QDRANT_COLLECTION_NAME)
    print(f"Collection verified: {info.points_count} points stored\n")
    

if __name__ == "__main__":
    setup_vector_db()