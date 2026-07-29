from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.document_vault import DocumentVault
from app.schemas.document_vault import DocumentVaultCreate, DocumentVaultResponse

router = APIRouter(prefix="/api/v1/vault", tags=["Document Vault"])


@router.post("/upload", response_model=DocumentVaultResponse)
def upload_document(doc: DocumentVaultCreate, db: Session = Depends(get_db)):
    """Upload metadata for a digitised receipt or recipe."""
    record = DocumentVault(
        doc_type=doc.doc_type,
        title=doc.title,
        file_path=doc.file_path,
        metadata_json=doc.metadata_json
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/list", response_model=list[DocumentVaultResponse])
def list_documents(db: Session = Depends(get_db)):
    """Retrieves all logged documents in the vault."""
    return db.query(DocumentVault).order_by(DocumentVault.uploaded_at.desc()).all()
