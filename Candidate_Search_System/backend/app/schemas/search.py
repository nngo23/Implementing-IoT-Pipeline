from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List


class SearchRequest(BaseModel):
    query: str = Field(..., description="The search query string")

    top_k: Optional[int] = Field(
        5, description="Number of top results to return"
    )

    salary_range: Optional[Dict[str, int]] = Field(
        None, description="Salary range with 'min' and 'max'"
    )

    industry: Optional[str] = Field(
        None, description="Industry filter"
    )

    location_filter: Optional[float] = Field(
        None, description="Search radius in km"
    )

    # 🔴 STRICT ROLE FILTER (NO FALLBACK)
    role_keywords: Optional[List[str]] = Field(
        None,
        description=(
            "STRICT role filter (e.g. ['doctor','physician']). "
            "Results MUST match role_en."
        ),
    )

    # 🔥 From parser
    role_detected: Optional[bool] = Field(
        False,
        description="True when a valid role keyword was detected"
    )

    output_channel: Optional[str] = Field(
        "slack", description="slack or email"
    )

    recipient_email: Optional[str] = Field(
        None, description="Required if output_channel='email'"
    )

    # ─────────────────────────────────────────────
    # NORMALIZATION
    # ─────────────────────────────────────────────

    @field_validator("salary_range", mode="before")
    @classmethod
    def normalize_salary(cls, v):
        return None if v in ("null", "", None) else v

    @field_validator("industry", mode="before")
    @classmethod
    def normalize_industry(cls, v):
        return None if v in ("null", "", None) else v

    @field_validator("location_filter", mode="before")
    @classmethod
    def normalize_location(cls, v):
        return None if v in ("null", "", None) else v

    @field_validator("output_channel", mode="before")
    @classmethod
    def normalize_channel(cls, v):
        return "slack" if v in ("null", "", None) else v

    @field_validator("recipient_email", mode="before")
    @classmethod
    def normalize_email(cls, v):
        return None if v in ("null", "", None) else v

    @field_validator("role_keywords", mode="before")
    @classmethod
    def normalize_roles(cls, v):
        return None if v in ("null", "", None) else v

    # ─────────────────────────────────────────────
    # 🔥 STRICT ROLE ENFORCEMENT
    # ─────────────────────────────────────────────

    @field_validator("role_keywords")
    @classmethod
    def enforce_role_consistency(cls, v, info):
        data = info.data
        role_detected = data.get("role_detected", False)

        # Prevent fallback → force empty list
        if role_detected and not v:
            return []

        return v


# ─────────────────────────────────────────────
# RESPONSE MODELS
# ─────────────────────────────────────────────

class SearchResultItem(BaseModel):
    id: str
    name: str
    email: str
    industry: str
    category: str
    role: str
    role_en: str
    skills: List[str]
    experience_years: int
    education: Dict[str, str]
    additional_education: List[Dict[str, Any]]
    licenses: List[Dict[str, str]]
    location: Dict[str, Any]
    languages: List[Dict[str, str]]
    salary: int
    availability: str
    applicable_tes: str
    summary: str
    qualification_issues: List[str]

    match_score: float = Field(..., description="Similarity score (0-100)")
    explanation: str = Field(..., description="AI-generated explanation")


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem] = Field(
        ..., description="List of results"
    )