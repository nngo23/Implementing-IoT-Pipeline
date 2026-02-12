from qdrant_client import QdrantClient, models
from transformers import AutoModel
from typing import List, Dict, Optional
from app.config import Config


class VectorSearch:
    def __init__(self):
        self.encoder = AutoModel.from_pretrained(
            "jinaai/jina-embeddings-v3",
            trust_remote_code=True
        )
        self.client = QdrantClient(
            host=Config.QDRANT_HOST,
            port=Config.QDRANT_PORT
        )

    # ---------------------------
    # Embed Query
    # ---------------------------
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self.encoder.encode(
            texts,
            task="retrieval.query"
        ).tolist()

    # ---------------------------
    # Collection Info
    # ---------------------------
    def get_collection_info(self) -> Dict:
        try:
            return {
                "status": "ok",
                "candidates_collection":
                    self.client.get_collection(Config.QDRANT_COLLECTION_NAME),
                "professional_standards_collection":
                    self.client.get_collection(Config.QDRANT_COLLECTION_PROFESSIONALSTANDARD)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ---------------------------
    # Search Similar Candidates
    # ---------------------------
    def search_similar(
        self,
        query: str,
        top_k: int = Config.TOP_K_RESULTS,
        industry: Optional[str] = None,
        salary_range: Optional[Dict[str, int]] = None,
        location_filter: Optional[float] = None,
        feedback_weights: Optional[Dict[str, float]] = None
    ) -> List[Dict]:

        # ---------------------------
        # 1️⃣ Get professional standard
        # ---------------------------
        standard_payload = {}

        if industry:
            try:
                standard_search = self.client.query_points(
                    collection_name=Config.QDRANT_COLLECTION_PROFESSIONALSTANDARD,
                    query_filter=models.Filter(must=[
                        models.FieldCondition(
                            key="industry",
                            match=models.MatchValue(value=industry)
                        )
                    ]),
                    limit=1,
                    with_payload=True
                )

                if hasattr(standard_search, "points") and standard_search.points:
                    standard_payload = standard_search.points[0].payload

            except Exception:
                pass

        # Extract licenses
        license_names = []
        if isinstance(standard_payload.get("mandatory_licenses"), list):
            for lic in standard_payload["mandatory_licenses"]:
                if isinstance(lic, dict):
                    license_names.append(lic.get("name", ""))
                    license_names.append(lic.get("name_en", ""))

        # Build enriched query
        standard_query = (
            f"{standard_payload.get('min_education', '')}, "
            f"{standard_payload.get('min_education_en', '')}, "
            f"{license_names}"
        )

        new_query = f"{query}. Based on professional standard: {standard_query}"

        query_embedding = self.embed_texts([new_query])[0]

        # ---------------------------
        # 2️⃣ Build Filters Safely
        # ---------------------------
        must_conditions = []

        if industry:
            must_conditions.append(
                models.FieldCondition(
                    key="industry",
                    match=models.MatchValue(value=industry)
                )
            )

        if salary_range:
            must_conditions.append(
                models.FieldCondition(
                    key="salary",
                    range=models.Range(
                        gte=salary_range.get("min"),
                        lte=salary_range.get("max")
                    )
                )
            )

        if location_filter:
            must_conditions.append(
                models.FieldCondition(
                    key="location.coordinates",
                    geo_radius=models.GeoRadius(
                        center=models.GeoPoint(lat=60.9634, lon=25.6712),
                        radius=location_filter * 1000
                    )
                )
            )

        query_filter = models.Filter(must=must_conditions) if must_conditions else None

        # ---------------------------
        # 3️⃣ Vector Search
        # ---------------------------
        search_result = self.client.query_points(
            collection_name=Config.QDRANT_COLLECTION_NAME,
            query=query_embedding,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        )

        results = []
        points = search_result.points if hasattr(search_result, "points") else search_result

        for i, hit in enumerate(points, 1):

            base_score = hit.score * 100

            # 🔥 Apply feedback multiplier dynamically
            if feedback_weights and hit.id in feedback_weights:
                base_score *= feedback_weights[hit.id]

            results.append({
                "ranking": i,
                "id": hit.id,
                "score": round(base_score, 2),
                **hit.payload
            })

        return results


# ✅ IMPORTANT FIX
vector_search = VectorSearch()
