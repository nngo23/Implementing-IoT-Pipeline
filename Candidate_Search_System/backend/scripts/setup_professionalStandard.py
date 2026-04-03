import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from transformers import AutoModel
from app.config import Config

def setup_vector_db():
    print(" Starting Vector Database Setup...\n")
    
    # Load data
    print(f" Loading professional standards from: {Config.STANDARDS_FILE}")
    with open(Config.STANDARDS_FILE, 'r', encoding='utf-8') as f:
        standards = json.load(f)
    print(f" Loaded {len(standards)} professional standards\n")
    
    # Load encoder
    print(f" Loading embedding model: {Config.EMBEDDING_MODEL}")
    encoder =  AutoModel.from_pretrained("jinaai/jina-embeddings-v3", trust_remote_code=True)
    print(" Model loaded\n")
    
    # Connect Qdrant
    print(f" Connecting to Qdrant at {Config.QDRANT_HOST}:{Config.QDRANT_PORT}")
    client = QdrantClient(host=Config.QDRANT_HOST, port=Config.QDRANT_PORT)
    
    try:
        collections = client.get_collections()
        print(" Connected to Qdrant\n")
    except Exception as e:
        print(f" Failed to connect to Qdrant: {e}")
        return
    
    # Delete old collection
    print(f"  Deleting old collection: {Config.QDRANT_COLLECTION_PROFESSIONALSTANDARD}")
    try:
        client.delete_collection(Config.QDRANT_COLLECTION_PROFESSIONALSTANDARD)
        print("Old collection deleted\n")
    except:
        print("No existing collection to delete\n")
    
    # Create new collection
    print(f" Creating new collection: {Config.QDRANT_COLLECTION_PROFESSIONALSTANDARD}")
    client.create_collection(
        collection_name=Config.QDRANT_COLLECTION_PROFESSIONALSTANDARD,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
    )
    print("Collection created\n")
    
    # Encode and prepare points
    print("Encoding professional standards...")
    points = []
    for idx, standard in enumerate(standards):
        # Build comprehensive text for embedding
        text_parts = [
            standard.get('industry', ''),
            standard.get('industry_en', ''),
            standard.get('role_fi', ''),
            standard.get('role_en', ''),
            standard.get('min_education', ''),
            standard.get('min_education_en', ''),
            standard.get('issuing_authority', ''),
            standard.get('applicable_tes', ''),
            standard.get('applicable_tes_en', ''),

        ]
        
        # Add licenses
        if 'mandatory_licenses' in standard and isinstance(standard['mandatory_licenses'], list):
            for lic in standard['mandatory_licenses']:
                if isinstance(lic, dict):
                    text_parts.extend([lic.get('name', ''), lic.get('name_en', '')])
        
        text = ' '.join(filter(None, text_parts))
        
        # Encode to vector
        vector = encoder.encode(text,task="retrieval.passage").tolist()
        
        # Create point
        points.append(PointStruct(
            id=idx, 
            vector=vector, 
            payload=standard
        ))
        
        # Progress indicator
        if (idx + 1) % 10 == 0:
            print(f"   Processed: {idx + 1}/{len(standards)} ...")
    
    
    # Upload to Qdrant
    print("Uploading to Qdrant...")
    client.upsert(
        collection_name=Config.QDRANT_COLLECTION_PROFESSIONALSTANDARD, 
        points=points
    )
    print("Upload complete\n")
    
    # Verify
    info = client.get_collection(Config.QDRANT_COLLECTION_PROFESSIONALSTANDARD)
    

if __name__ == "__main__":
    setup_vector_db()