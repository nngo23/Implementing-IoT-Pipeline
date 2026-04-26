"""
vector_search.py — optimised VectorSearch (STRICT ROLE FIX VERSION)
"""

import logging
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient, models
from transformers import AutoModel

from app.config import Config

logger = logging.getLogger(__name__)


class VectorSearch:
    _encoder: Optional[Any] = None

    @classmethod
    def _get_encoder(cls):
        if cls._encoder is None:
            logger.info("Loading embedding model %s …", Config.EMBEDDING_MODEL)
            cls._encoder = AutoModel.from_pretrained(
                "jinaai/jina-embeddings-v3",
                trust_remote_code=True
            )
            logger.info("Embedding model loaded.")
        return cls._encoder

    def __init__(self):
        self.client = QdrantClient(
            host=Config.QDRANT_HOST,
            port=Config.QDRANT_PORT
        )

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self._get_encoder().encode(
            texts,
            task="retrieval.query"
        ).tolist()

    # ─────────────────────────────────────────────
    # MAIN SEARCH
    # ─────────────────────────────────────────────
    def search_similar(
        self,
        query: str,
        top_k: Optional[int] = None,
        industry: Optional[str] = None,
        salary_range: Optional[Dict[str, int]] = None,
        location_filter: Optional[float] = None,
        role_keywords: Optional[List[str]] = None,
    ) -> List[Dict]:

        # ─────────────────────────────────────────
        # 0. HARD GUARD — industry required
        # ─────────────────────────────────────────
        if not industry:
            logger.info("No industry → returning empty results")
            return []

        # ─────────────────────────────────────────
        # 1. Professional standard lookup
        # ─────────────────────────────────────────
        standard_payload: Dict = {}

        try:
            std_result = self.client.query_points(
                collection_name=Config.QDRANT_COLLECTION_PROFESSIONALSTANDARD,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="industry",
                            match=models.MatchValue(value=industry),
                        )
                    ]
                ),
                with_payload=[
                    "name", "email", "industry", "category",
                    "role", "role_en", "skills",
                    "experience_years", "salary",
                    "location", "licenses", "languages",
                    "summary", "qualification_issues"
                ],
            )

            if getattr(std_result, "points", None):
                standard_payload = std_result.points[0].payload

        except Exception as exc:
            logger.warning("Professional standard lookup failed: %s", exc)

        # ─────────────────────────────────────────
        # 2. Enrich query
        # ─────────────────────────────────────────
        license_names: List[str] = []

        for lic in standard_payload.get("mandatory_licenses", []):
            if isinstance(lic, dict):
                license_names += [
                    lic.get("name", ""),
                    lic.get("name_en", "")
                ]

        if standard_payload:
            standard_query = (
                f"professional standard: "
                f"{standard_payload.get('min_education', '')}, "
                f"{standard_payload.get('min_education_en', '')}, "
                f"{license_names}"
            )
            enriched_query = f"{query}. {standard_query}"
        else:
            enriched_query = query

        query_embedding = self.embed_texts([enriched_query])[0]

        # ─────────────────────────────────────────
        # 3. Qdrant filters
        # ─────────────────────────────────────────
        must_conditions = []

        if industry:
            must_conditions.append(
                models.FieldCondition(
                    key="industry",
                    match=models.MatchValue(value=industry),
                )
            )

        if salary_range:
            must_conditions.append(
                models.FieldCondition(
                    key="salary",
                    range=models.Range(
                        gte=salary_range.get("min"),
                        lte=salary_range.get("max"),
                    ),
                )
            )

        if location_filter:
            must_conditions.append(
                models.FieldCondition(
                    key="location.coordinates",
                    geo_radius=models.GeoRadius(
                        center=models.GeoPoint(
                            lat=60.9634,
                            lon=25.6712
                        ),
                        radius=location_filter * 1000,
                    ),
                )
            )

        query_filter = models.Filter(must=must_conditions) if must_conditions else None

        limit = top_k * 2 if top_k else 20

        search_result = self.client.query_points(
            collection_name=Config.QDRANT_COLLECTION_NAME,
            query=query_embedding,
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
        )

        points = getattr(search_result, "points", search_result)

        results = [
            {
                "ranking": i,
                "id": hit.id,
                "score": round(hit.score * 100, 2),
                **hit.payload
            }
            for i, hit in enumerate(points, 1)
        ]

        # ─────────────────────────────────────────
        # 4. 🔥 STRICT ROLE FILTER (FIXED)
        # ─────────────────────────────────────────
        if role_keywords:
            kw_lower = [kw.lower() for kw in role_keywords]

            filtered = []
            for c in results:
                role_text = (c.get("role_en") or "").lower()

                # MUST MATCH AT LEAST ONE ROLE KEYWORD
                if any(kw in role_text for kw in kw_lower):
                    filtered.append(c)

            # 🚫 HARD FAILURE MODE (IMPORTANT FIX)
            if not filtered:
                logger.info(
                    "STRICT ROLE FILTER FAILED: %s → returning 0 results",
                    role_keywords
                )
                return []

            results = filtered

        return results


vector_search = VectorSearch()