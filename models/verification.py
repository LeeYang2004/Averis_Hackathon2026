from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(
        String(50),
        ForeignKey("email_messages.email_id"),
        nullable=False,
        index=True,
    )
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True, index=True)
    category = Column(String(50), nullable=False, default="GENERAL", index=True)
    result = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False, default=0.0)
    reviewer_status = Column(String(50), nullable=False, default="pending")
    review_reason = Column(String(50), nullable=True)
    has_defect = Column(Boolean, nullable=False, default=False)
    defect_fields = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    email = relationship("EmailMessage", back_populates="verifications")
    document = relationship("Document", back_populates="verifications")
