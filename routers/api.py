from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from models.email_message import EmailMessage, utc_now
from services.email_classifier import EmailClassifier
from services.input_importer import InputDataImporter, reset_database


router = APIRouter(prefix="/api", tags=["api"])


@router.get("/status")
def api_status() -> dict[str, str]:
    return {"status": "ready"}


@router.post("/classify-email")
def classify_email(payload: dict) -> dict[str, str | float | None]:
    classifier = EmailClassifier()
    result = classifier.classify(
        subject=str(payload.get("subject", "")),
        body=str(payload.get("body", "")),
        attachments=payload.get("attachments", []),
    )
    return result.to_dict()


@router.post("/classify-imported-emails")
def classify_imported_emails(db: Session = Depends(get_db)) -> dict[str, int | str]:
    classifier = EmailClassifier()
    emails = db.query(EmailMessage).order_by(EmailMessage.email_id).all()

    for email in emails:
        result = classifier.classify(
            subject=email.subject,
            body=email.body,
            attachments=[document.attachment_path for document in email.documents],
        )
        email.category = result.category
        email.classification_confidence = result.confidence
        email.classification_source = result.source
        email.classified_at = utc_now()

    db.commit()
    return {"status": "classified", "emails": len(emails)}


@router.post("/import-input-data")
def import_input_data(
    reset: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> dict[str, int | str]:
    if reset:
        reset_database()

    result = InputDataImporter().import_all(db)
    return {
        "status": "imported",
        "emails": result["emails"],
        "documents": result["documents"],
    }
