from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from services.email_classifier import EmailClassifier
from services.input_importer import InputDataImporter, reset_database


router = APIRouter(prefix="/api", tags=["api"])


@router.get("/status")
def api_status() -> dict[str, str]:
    return {"status": "ready"}


@router.post("/classify-email")
def classify_email(payload: dict) -> dict[str, str]:
    classifier = EmailClassifier()
    category = classifier.classify(
        subject=str(payload.get("subject", "")),
        body=str(payload.get("body", "")),
        attachments=payload.get("attachments", []),
    )
    return {"category": category}


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
