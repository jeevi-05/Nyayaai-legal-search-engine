from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.legal_document import DocumentCategory



class DocumentResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )


    id: int

    title: str

    source_file: str

    category: DocumentCategory

    description: Optional[str] = None

    citation: Optional[str] = None

    year: Optional[int] = None

    court: Optional[str] = None

    source: Optional[str] = None

    tags: Optional[str] = None

    file_type: Optional[str] = None

    file_path: Optional[str] = None

    uploaded_by: Optional[str] = None

    # Indian Kanoon fields
    external_id:  Optional[str] = None
    document_url: Optional[str] = None
    pdf_path:     Optional[str] = None
    case_type:    Optional[str] = None

    # MODULE 2 FIELDS

    extracted_text: Optional[str] = None

    summary: Optional[str] = None


    loaded_at: datetime