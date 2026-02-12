from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from app.db.database import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(String(100))
    feedback_type = Column(String(10))
    reason = Column(Text)
    auto_tags = Column(ARRAY(String))
    created_at = Column(TIMESTAMP, server_default=func.now())