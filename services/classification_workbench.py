from typing import Any

from sqlalchemy.orm import Session, selectinload

from models.email_message import EmailMessage
from services.classification_schema import ALLOWED_CATEGORIES, BL_COMPARISON


CATEGORY_LABELS = {
    "BL_COMPARISON": "BL Comparison",
    "SI_REQUEST": "SI Request",
    "INVOICE_QUERY": "Invoice Query",
    "GENERAL": "General",
    "SPAM": "Spam",
}

CATEGORY_ACTIONS = {
    "BL_COMPARISON": "Process documents",
    "SI_REQUEST": "Archive / prepare SI workflow",
    "INVOICE_QUERY": "Archive",
    "GENERAL": "Archive",
    "SPAM": "Archive",
}

PIPELINE_STAGES = (
    "Attachment Processing",
    "Document Type Detection",
    "Text/OCR Extraction",
    "Structured Shipment JSON",
    "SI/BL Comparison",
    "Human Review",
    "Report",
)

NEEDS_CLASSIFICATION_KEY = "NEEDS_CLASSIFICATION"


def get_classification_view_model(
    db: Session,
    selected_category: str | None = None,
) -> dict[str, Any]:
    emails = (
        db.query(EmailMessage)
        .options(selectinload(EmailMessage.documents))
        .order_by(EmailMessage.email_id)
        .all()
    )
    return build_classification_view_model(emails, selected_category)


def build_classification_view_model(
    emails: list[EmailMessage],
    selected_category: str | None = None,
) -> dict[str, Any]:
    selected = (
        selected_category
        if selected_category in ALLOWED_CATEGORIES
        else BL_COMPARISON
    )
    groups = {category: [] for category in ALLOWED_CATEGORIES}
    needs_classification = []

    for email in emails:
        item = serialize_email(email)
        if needs_classification_bucket(email):
            needs_classification.append(item)
            continue
        groups[email.category].append(item)

    counts = {category: len(groups[category]) for category in ALLOWED_CATEGORIES}
    selected_emails = groups[selected]

    return {
        "categories": [
            {
                "key": category,
                "label": CATEGORY_LABELS[category],
                "count": counts[category],
                "action": CATEGORY_ACTIONS[category],
            }
            for category in ALLOWED_CATEGORIES
        ],
        "groups": groups,
        "counts": counts,
        "needs_classification": needs_classification,
        "needs_classification_count": len(needs_classification),
        "total_classified": sum(counts.values()),
        "total_emails": len(emails),
        "selected_category": selected,
        "selected_label": CATEGORY_LABELS[selected],
        "selected_action": CATEGORY_ACTIONS[selected],
        "selected_emails": selected_emails,
        "active_email": selected_emails[0] if selected_emails else None,
        "pipeline_stages": PIPELINE_STAGES,
        "bl_category": BL_COMPARISON,
    }


def classification_summary(db: Session) -> dict[str, Any]:
    view_model = get_classification_view_model(db)
    return {
        "categories": view_model["categories"],
        "counts": view_model["counts"],
        "needs_classification_count": view_model["needs_classification_count"],
        "total_classified": view_model["total_classified"],
        "total_emails": view_model["total_emails"],
    }


def needs_classification_bucket(email: EmailMessage) -> bool:
    return (
        email.category not in ALLOWED_CATEGORIES
        or email.classification_source == "missing_ai_key"
    )


def serialize_email(email: EmailMessage) -> dict[str, Any]:
    documents = [
        {
            "id": document.id,
            "filename": document.filename,
            "document_type": document.document_type,
            "status": document.status,
        }
        for document in email.documents
    ]
    body = email.body or ""

    return {
        "id": email.id,
        "email_id": email.email_id,
        "sender": email.sender,
        "subject": email.subject,
        "body": body,
        "body_preview": body[:260],
        "attachment_count": email.attachment_count,
        "category": email.category,
        "classification_confidence": email.classification_confidence,
        "classification_source": email.classification_source,
        "classified_at": email.classified_at.isoformat() if email.classified_at else None,
        "created_at": email.created_at.isoformat() if email.created_at else None,
        "documents": documents,
        "document_types": ", ".join(
            sorted({document["document_type"] for document in documents})
        )
        or "None",
    }
