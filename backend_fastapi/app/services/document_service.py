import os
import json
import shutil

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings

from app.models.legal_document import (
    LegalDocument,
    DocumentCategory
)

from app.models.user import User

from app.repositories import document_repository

from app.services.pdf_processor import (
    extract_text,
    generate_summary
)

from app.services.embedding_service import EmbeddingService

from app.services.semantic_search_service import semantic_search_service



settings = get_settings()


embedding_service = EmbeddingService()



def get_all(db: Session):

    return document_repository.get_all(db)



def get_by_id(
    db: Session,
    doc_id: int
):

    doc = document_repository.get_by_id(
        db,
        doc_id
    )


    if not doc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )


    return doc




def get_by_category(
    db: Session,
    category: DocumentCategory
):

    return document_repository.get_by_category(
        db,
        category
    )




def count(db: Session):

    return document_repository.count(db)






def upload(
    db: Session,
    file: UploadFile,
    title: str,
    category: str,
    description: str | None,
    citation: str | None,
    year: str | None,
    court: str | None,
    tags: str | None,
    admin: User
):


    # Validate PDF

    if (
        not file.filename
        or not file.filename.lower().endswith(".pdf")
    ):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )



    # Validate category

    try:

        doc_category = DocumentCategory(
            category.upper()
        )


    except ValueError:

        raise HTTPException(
            status_code=400,
            detail="Invalid category"
        )



    filename = _sanitize(
        file.filename
    )



    # Duplicate check

    if document_repository.exists_by_source_and_category(
        db,
        filename,
        doc_category
    ):

        raise HTTPException(
            status_code=409,
            detail="Document already exists"
        )



    # Save file

    file_path = _save_file(
        file,
        doc_category,
        filename
    )



    # Extract text

    extracted_text = extract_text(
        file_path
    )



    # Generate summary

    summary = generate_summary(
        extracted_text
    )



    # Generate embedding

    embedding = embedding_service.embed(
        extracted_text
    )


    embedding_json = json.dumps(
        embedding
    )



    # Year conversion

    parsed_year = None


    if year:

        try:

            parsed_year = int(year)

        except ValueError:

            parsed_year = None




    # Create document

    document = LegalDocument(

        title=title,

        source_file=filename,

        file_path=file_path,

        category=doc_category,

        description=description,

        citation=citation,

        year=parsed_year,

        court=court,

        tags=tags,

        file_type="PDF",

        extracted_text=extracted_text,

        summary=summary,

        embedding=embedding_json,

        uploaded_by=(
            admin.email
            if admin
            else "system"
        )

    )



    # Save first

    saved_document = document_repository.create_document(
        db,
        document
    )



    # Semantic search

    similar_cases = semantic_search_service.search_similar_documents(
        db,
        embedding,
        saved_document.id,
        top_k=6
    )



    # Remove uploaded document itself

    filtered_cases = []


    for case in similar_cases:

        if case["id"] != saved_document.id:

            filtered_cases.append(case)



    filtered_cases = filtered_cases[:5]



    return {


        "uploaded_document": {

            "id": saved_document.id,

            "title": saved_document.title,

            "summary": saved_document.summary,

            "category": saved_document.category.value,

            "year": saved_document.year,

            "court": saved_document.court

        },


        "similar_cases": filtered_cases

    }








def delete(
    db: Session,
    doc_id: int
):


    doc = document_repository.get_by_id(
        db,
        doc_id
    )


    if not doc:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )



    document_repository.delete_document(
        db,
        doc
    )






def _sanitize(
    filename: str
):

    import re


    return re.sub(
        r"[^a-zA-Z0-9._\-]",
        "_",
        filename
    )






def _save_file(
    file: UploadFile,
    category: DocumentCategory,
    filename: str
):


    folder = os.path.join(
        settings.UPLOAD_DIR,
        category.value.lower()
    )



    os.makedirs(
        folder,
        exist_ok=True
    )



    destination = os.path.join(
        folder,
        filename
    )



    with open(
        destination,
        "wb"
    ) as buffer:


        shutil.copyfileobj(
            file.file,
            buffer
        )



    return destination