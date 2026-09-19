from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from models.document import Document
from models.email_message import EmailMessage
from models.verification import Verification


router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    total_emails = db.query(EmailMessage).count()
    total_documents = db.query(Document).count()
    pending_review = (
        db.query(Verification)
        .filter(Verification.reviewer_status == "pending")
        .count()
    )
    mismatch_detected = (
        db.query(Verification)
        .filter(Verification.result == "MISMATCH")
        .count()
    )
    completed_verification = (
        db.query(Verification)
        .filter(Verification.reviewer_status == "completed")
        .count()
    )

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "stats": {
                "total_emails": total_emails,
                "total_documents": total_documents,
                "pending_review": pending_review,
                "mismatch_detected": mismatch_detected,
                "completed_verification": completed_verification,
            },
        },
    )
