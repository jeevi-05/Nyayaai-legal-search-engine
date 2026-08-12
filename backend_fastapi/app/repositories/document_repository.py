from sqlalchemy.orm import Session
from app.models.legal_document import LegalDocument, DocumentCategory


def get_all(db: Session) -> list[LegalDocument]:
    return db.query(LegalDocument).all()


def get_by_id(db: Session, doc_id: int) -> LegalDocument | None:
    return db.query(LegalDocument).filter(LegalDocument.id == doc_id).first()


def get_by_category(db: Session, category: DocumentCategory) -> list[LegalDocument]:
    return db.query(LegalDocument).filter(LegalDocument.category == category).all()


def count(db: Session) -> int:
    return db.query(LegalDocument).count()


def exists_by_source_and_category(db: Session, source_file: str, category: DocumentCategory) -> bool:
    return (
        db.query(LegalDocument.id)
        .filter(LegalDocument.source_file == source_file, LegalDocument.category == category)
        .scalar()
        is not None
    )


def create_document(db: Session, doc: LegalDocument) -> LegalDocument:
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def delete_document(db: Session, doc: LegalDocument) -> None:
    db.delete(doc)
    db.commit()


def exists_by_external_id(db: Session, external_id: str) -> bool:
    return (
        db.query(LegalDocument.id)
        .filter(LegalDocument.external_id == external_id)
        .scalar()
        is not None
    )


def get_by_external_id(db: Session, external_id: str) -> LegalDocument | None:
    return (
        db.query(LegalDocument)
        .filter(LegalDocument.external_id == external_id)
        .first()
    )
