from sqlalchemy import Column, String, DateTime, func, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from ..core.database import Base

class AIAnalysisLog(Base):
    __tablename__ = "ai_analysis_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    request_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    request_payload = Column(JSONB, nullable=False)
    response_payload = Column(JSONB, nullable=False)
    ai_model_used = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="ai_analysis_logs")

