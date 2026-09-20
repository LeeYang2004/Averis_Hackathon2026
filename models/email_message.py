from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EmailMessage(Base):
    __tablename__ = "email_messages"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String(50), nullable=False, unique=True, index=True)
    sender = Column(String(255), nullable=False, index=True)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    attachment_count = Column(Integer, nullable=False, default=0)
    category = Column(String(50), nullable=True, index=True)
    classification_confidence = Column(Float, nullable=True)
    classification_source = Column(String(50), nullable=True)
    classified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    documents = relationship(
        "Document",
        back_populates="email",
        cascade="all, delete-orphan",
    )
    verifications = relationship(
        "Verification",
        back_populates="email",
        cascade="all, delete-orphan",
    )
    extractions = relationship(
        "Extraction",
        back_populates="email",
        cascade="all, delete-orphan",
    )
