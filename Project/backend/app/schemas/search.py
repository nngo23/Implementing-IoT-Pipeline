from pydantic import BaseModel, Field
from typing import Optional, Dict, Any ,List


class SearchRequest(BaseModel):
    query: str = Field(..., description="The search query string")
    top_k: Optional[int] = Field(5, description="Number of top results to return")
    salary_range: Optional[Dict[str, int]] = Field(
        None, description="Desired salary range with 'min' and 'max' keys"
    )
    industry: Optional[str] = Field(
        None, description="List of industries to filter the search results"
    )
    location_filter: Optional[float] = Field(
        None,
        description="Location-based filtering with postal code, city, and search radius in km",
        example= 30
    )
    
    

class SearchResultItem(BaseModel):
    # Basic Info
    id: str
    name: str
    industry: str
    category: str
    role: str
    role_en: str
    
    # Skills & Experience
    skills: List[str]
    experience_years: int
    
   
    education: Dict[str, str]  
    additional_education: List[Dict[str, Any]]  
    
    # Licenses (array of dicts)
    licenses: List[Dict[str, str]] 
    
    # Location (nested dict)
    location: Dict[str, Any]  
    
    # Languages (array of dicts)
    languages: List[Dict[str, str]]  
    
    # Employment Info
    salary: int
    availability: str
    applicable_tes: str
    
    # Summary & Qualification
    summary: str
    qualification_issues: List[str]
    
    # Match Score & Explanation (added by search)
    match_score: float = Field(..., description="Similarity score from vector search (0-1)")
    explanation: str = Field(..., description="AI-generated explanation of why this candidate matches")


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem] = Field(..., description="List of search results")