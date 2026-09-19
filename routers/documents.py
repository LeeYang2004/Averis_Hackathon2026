from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from models.document import Document


router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
def list_documents(db: Session = Depends(get_db)) -> list[dict]:
    documents = db.query(Document).order_by(Document.created_at.desc()).all()
    return [
        {
            "id": document.id,
            "email_id": document.email_id,
            "filename": document.filename,
            "attachment_path": document.attachment_path,
            "document_type": document.document_type,
            "file_extension": document.file_extension,
            "file_size_bytes": document.file_size_bytes,
            "status": document.status,
            "created_at": document.created_at.isoformat(),
        }
        for document in documents
    ]
