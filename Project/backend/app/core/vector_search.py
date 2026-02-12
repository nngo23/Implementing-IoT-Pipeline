from qdrant_client import QdrantClient, models
from transformers import AutoModel
from typing import Any, List, Dict
from app.config import Config

class VectorSearch:
    def __init__(self):
        self.encoder = AutoModel.from_pretrained("jinaai/jina-embeddings-v3", trust_remote_code=True)
        self.client = QdrantClient(host=Config.QDRANT_HOST, port=Config.QDRANT_PORT)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self.encoder.encode(texts, task="retrieval.query").tolist()
    
    def get_collection_info(self) -> Dict:
        try:
            info_candidates_collection = self.client.get_collection(Config.QDRANT_COLLECTION_NAME)
            info_standards_collection = self.client.get_collection(Config.QDRANT_COLLECTION_PROFESSIONALSTANDARD)
            return {
                "status": "ok",
                "candidates_collection": info_candidates_collection,
                "professional_standards_collection": info_standards_collection
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def search_similar(self, query: str, top_k: int = Config.TOP_K_RESULTS, industry: str = None, salary_range: Dict[str, int] = None, location_filter: float = None) -> List[Dict]:
        search_standard = self.client.query_points(
            collection_name=Config.QDRANT_COLLECTION_PROFESSIONALSTANDARD,
            query_filter=models.Filter(must=[
                models.FieldCondition(key="industry", match=models.MatchValue(value=industry))
            ]),
            with_payload=True)
        standard_payload = search_standard.points[0].payload if hasattr(search_standard, 'points') and search_standard.points else {}
        license_names = []
        if "mandatory_licenses" in standard_payload and isinstance(standard_payload["mandatory_licenses"], list):
            for lic in standard_payload["mandatory_licenses"]:
                if isinstance(lic, dict) and 'name' in lic:
                    license_names.extend([lic['name'], lic.get('name_en', '')])
        standard_query = f"find a professional standard similar to: {standard_payload.get('min_education', '')}, {standard_payload.get('min_education_en', '')}, {license_names}"
        new_query = f"{query}. Based on professional standard details: {standard_query}"
        query_embedding = self.embed_texts([new_query])[0]
        query_filter = models.Filter(must=[
            f for f in [
                industry and models.FieldCondition(key="industry", match=models.MatchValue(value=industry)),
                salary_range and models.FieldCondition(key="salary", range=models.Range(gte=salary_range.get('min'), lte=salary_range.get('max'))),
                location_filter and models.FieldCondition(key="location.coordinates", geo_radius=models.GeoRadius(center=models.GeoPoint(lat=60.9634, lon=25.6712), radius=location_filter*1000)),
            ] if f
        ]) or None
        search_result = self.client.query_points(
            collection_name=Config.QDRANT_COLLECTION_NAME,
            query=query_embedding,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        )
        
        results = []
        points = search_result.points if hasattr(search_result, 'points') else search_result
        
        for i, hit in enumerate(points, 1):  
            results.append({
                "ranking": i,
                "id": hit.id,
                "score": round(hit.score * 100, 2),
                **hit.payload
            })
        return results
vector_search = VectorSearch()