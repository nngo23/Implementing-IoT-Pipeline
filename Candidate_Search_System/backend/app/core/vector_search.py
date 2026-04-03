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
    
    def search_similar(self, query: str, top_k: int = None, industry: str = None, salary_range: Dict[str, int] = None, location_filter: float = None) -> List[Dict]:
        # BUG FIX 1: Only query professional standards if industry is provided.
        # Previously, passing industry=None crashed Qdrant with an invalid MatchValue filter.
        standard_payload = {}
        if industry:
            search_standard = self.client.query_points(
                collection_name=Config.QDRANT_COLLECTION_PROFESSIONALSTANDARD,
                query_filter=models.Filter(must=[
                    models.FieldCondition(key="industry", match=models.MatchValue(value=industry))
                ]),
                with_payload=True)
            # BUG FIX 2: Guard against empty results before accessing index [0].
            # Previously, if no matching standard existed, this threw an IndexError (500).
            if hasattr(search_standard, 'points') and search_standard.points:
                standard_payload = search_standard.points[0].payload

        license_names = []
        if "mandatory_licenses" in standard_payload and isinstance(standard_payload["mandatory_licenses"], list):
            for lic in standard_payload["mandatory_licenses"]:
                if isinstance(lic, dict) and 'name' in lic:
                    license_names.extend([lic['name'], lic.get('name_en', '')])
        standard_query = f"find a professional standard similar to: {standard_payload.get('min_education', '')}, {standard_payload.get('min_education_en', '')}, {license_names}"
        new_query = f"{query}. Based on professional standard details: {standard_query}" if standard_payload else query
        query_embedding = self.embed_texts([new_query])[0]

        # BUG FIX 3: Build must-conditions list first, then only create Filter if non-empty.
        # Previously, `models.Filter(must=[]) or None` always evaluated to the Filter object
        # (it's truthy even when empty), so Qdrant received an invalid empty filter.
        must_conditions = [
            f for f in [
                industry and models.FieldCondition(key="industry", match=models.MatchValue(value=industry)),
                salary_range and models.FieldCondition(key="salary", range=models.Range(gte=salary_range.get('min'), lte=salary_range.get('max'))),
                location_filter and models.FieldCondition(key="location.coordinates", geo_radius=models.GeoRadius(center=models.GeoPoint(lat=60.9634, lon=25.6712), radius=location_filter*1000)),
            ] if f
        ]
        query_filter = models.Filter(must=must_conditions) if must_conditions else None
        collection_info = self.client.get_collection(Config.QDRANT_COLLECTION_NAME)
        total_points = collection_info.points_count
        search_result = self.client.query_points(
            collection_name=Config.QDRANT_COLLECTION_NAME,
            query=query_embedding,
            limit=top_k or total_points,
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