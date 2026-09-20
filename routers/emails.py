from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from models.email_message import EmailMessage


router = APIRouter(prefix="/emails", tags=["emails"])


@router.get("")
def list_emails(db: Session = Depends(get_db)) -> list[dict]:
    emails = db.query(EmailMessage).order_by(EmailMessage.email_id).all()
    return [
        {
            "id": email.id,
            "email_id": email.email_id,
            "from": email.sender,
            "subject": email.subject,
            "attachment_count": email.attachment_count,
            "category": email.category,
            "classification_confidence": email.classification_confidence,
            "classification_source": email.classification_source,
            "classified_at": (
                email.classified_at.isoformat() if email.classified_at else None
            ),
            "created_at": email.created_at.isoformat(),
        }
        for email in emails
    ]


@router.get("/{email_id}")
def get_email(email_id: str, db: Session = Depends(get_db)) -> dict:
    email = (
        db.query(EmailMessage)
        .filter(EmailMessage.email_id == email_id)
        .one_or_none()
    )
    if email is None:
        raise HTTPException(status_code=404, detail="Email not found")

    return {
        "id": email.id,
        "email_id": email.email_id,
        "from": email.sender,
        "subject": email.subject,
        "body": email.body,
        "attachment_count": email.attachment_count,
        "category": email.category,
        "classification_confidence": email.classification_confidence,
        "classification_source": email.classification_source,
        "classified_at": email.classified_at.isoformat() if email.classified_at else None,
        "attachments": [
            {
                "id": document.id,
                "filename": document.filename,
                "attachment_path": document.attachment_path,
                "document_type": document.document_type,
                "file_extension": document.file_extension,
                "file_size_bytes": document.file_size_bytes,
                "status": document.status,
            }
            for document in email.documents
        ],
    }
