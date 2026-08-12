from typing import Optional

from fastapi import APIRouter, Depends, Form, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
import os

from app.core.database import get_db

from app.middleware.auth import get_current_user

from app.models.legal_document import DocumentCategory
from app.models.user import User

from app.schemas.document import DocumentResponse
from app.schemas.dashboard import ApiResponse

from app.services import document_service


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)



def _doc(doc):

    return DocumentResponse.model_validate(
        doc
    ).model_dump(
        by_alias=True,
        mode="json"
    )




@router.get("")
def get_all(
    db: Session = Depends(get_db)
):

    docs = document_service.get_all(db)

    return JSONResponse(
        content=ApiResponse.ok(
            "All documents",
            [_doc(d) for d in docs]
        ).model_dump(mode="json")
    )




@router.get("/category/{category}")
def get_by_category(
    category: DocumentCategory,
    db: Session = Depends(get_db)
):

    docs = document_service.get_by_category(
        db,
        category
    )

    return JSONResponse(
        content=ApiResponse.ok(
            f"Documents in {category.value}",
            [_doc(d) for d in docs]
        ).model_dump(mode="json")
    )




@router.get("/count")
def count(
    db: Session = Depends(get_db)
):

    return JSONResponse(
        content=ApiResponse.ok(
            "Total documents",
            document_service.count(db)
        ).model_dump(mode="json")
    )




@router.get("/{doc_id}/download")
def download_pdf(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Download the PDF for a document.
    Checks pdf_path first (Indian Kanoon), then file_path (uploaded docs).
    """
    doc = document_service.get_by_id(db, doc_id)

    path = doc.pdf_path or doc.file_path

    if not path or not os.path.isfile(path):
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "PDF file not found on server", "data": None},
        )

    safe_name = os.path.basename(path)
    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=safe_name,
    )


@router.get("/{doc_id}")
def get_by_id(
    doc_id:int,
    db: Session = Depends(get_db)
):

    doc = document_service.get_by_id(
        db,
        doc_id
    )

    return JSONResponse(
        content=ApiResponse.ok(
            "Document found",
            _doc(doc)
        ).model_dump(mode="json")
    )




@router.post("/upload", status_code=201)
def upload(

    file: UploadFile = File(...),

    title: str = Form(...),

    category: str = Form(...),

    description: Optional[str] = Form(None),

    citation: Optional[str] = Form(None),

    year: Optional[str] = Form(None),

    court: Optional[str] = Form(None),

    tags: Optional[str] = Form(None),


    db: Session = Depends(get_db),


    current_user: User = Depends(get_current_user)

):


    result = document_service.upload(

        db,

        file,

        title,

        category,

        description,

        citation,

        year,

        court,

        tags,

        current_user

    )



    return JSONResponse(

        status_code=201,

        content={

            "success": True,

            "message":
            "Uploaded and semantic analysis completed",

            "data": result

        }

    )





@router.delete("/{doc_id}")
def delete(

    doc_id:int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    document_service.delete(
        db,
        doc_id
    )


    return JSONResponse(

        content=ApiResponse.ok(
            "Deleted",
            None
        ).model_dump()

    )