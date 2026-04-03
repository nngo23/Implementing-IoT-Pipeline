from pydantic import BaseModel, Field
from typing import Optional, Dict, Any 
class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="Status of the service")
    version: Optional[str] = Field(None, description="Version of the service")
    qdrant: Dict[str, Any] = Field(..., description="Health status of the Qdrant service")
