from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from models.document import Document
from models.email_message import EmailMessage, utc_now
from models.extraction import Extraction
from services.email_classifier import EmailClassifier
from services.classification_workbench import classification_summary
from services.extraction_service import ExtractionService
from services.input_importer import InputDataImporter, reset_database


router = APIRouter(prefix="/api", tags=["api"])


@router.get("/status")
def api_status() -> dict[str, str]:
    return {"status": "ready"}


@router.get("/classification-summary")
def get_classification_summary(db: Session = Depends(get_db)) -> dict:
    return classification_summary(db)


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


@router.get("/extractions")
def list_extractions(db: Session = Depends(get_db)) -> list[dict]:
    extractions = db.query(Extraction).order_by(Extraction.id).all()
    return [ExtractionService.serialize(record) for record in extractions]


@router.post("/extract/{email_id}")
def extract_email(email_id: str, db: Session = Depends(get_db)) -> dict:
    email = (
        db.query(EmailMessage)
        .filter(EmailMessage.email_id == email_id)
        .one_or_none()
    )
    if email is None:
        raise HTTPException(status_code=404, detail="Email not found")

    return ExtractionService().process_email(db, email)


@router.post("/extract-all")
def extract_all(db: Session = Depends(get_db)) -> dict[str, int | str | list]:
    email_ids = (
        db.query(Document.email_id)
        .filter(Document.document_type.in_(("SI", "BL")))
        .distinct()
        .order_by(Document.email_id)
        .all()
    )

    service = ExtractionService()
    results = []
    for (email_id,) in email_ids:
        email = (
            db.query(EmailMessage)
            .filter(EmailMessage.email_id == email_id)
            .one_or_none()
        )
        if email is None:
            continue
        results.append(service.process_email(db, email))

    return {
        "status": "extracted",
        "emails": len(results),
        "results": results,
    }
