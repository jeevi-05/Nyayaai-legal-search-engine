import enum

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    Enum,
    DateTime,
    UniqueConstraint,
)

from app.core.database import Base



class DocumentCategory(str, enum.Enum):

    ACT = "ACT"

    LANDMARK_CASE = "LANDMARK_CASE"

    JUDGMENT = "JUDGMENT"




class LegalDocument(Base):

    __tablename__ = "legal_documents"


    __table_args__ = (

        UniqueConstraint(
            "source_file",
            "category",
            name="uq_source_category"
        ),

    )



    id = Column(

        Integer,

        primary_key=True,

        index=True,

        autoincrement=True

    )



    title = Column(

        String,

        nullable=False

    )

    # Normalised judicial-document metadata.  Legacy fields remain for compatibility.
    case_name = Column(String, nullable=True, index=True)
    bench = Column(String, nullable=True)
    judgment_date = Column(String, nullable=True)
    acts = Column(Text, nullable=True)
    sections = Column(Text, nullable=True)
    paragraphs = Column(Text, nullable=True)  # JSON: [{number, text}]



    short_title = Column(

        String,

        nullable=True

    )



    source_file = Column(

        String,

        nullable=False

    )



    category = Column(

        Enum(DocumentCategory),

        nullable=False

    )



    description = Column(

        Text,

        nullable=True

    )



    citation = Column(

        String,

        nullable=True

    )



    year = Column(

        Integer,

        nullable=True

    )



    court = Column(

        String,

        nullable=True

    )



    source = Column(

        String,

        nullable=True

    )



    tags = Column(

        Text,

        nullable=True

    )



    file_type = Column(

        String,

        nullable=True

    )



    file_path = Column(

        String,

        nullable=True

    )



    # Extracted PDF text

    extracted_text = Column(

        Text,

        nullable=True

    )



    # AI generated summary

    summary = Column(

        Text,

        nullable=True

    )



    # Sentence Transformer embedding stored as JSON string

    embedding = Column(

        Text,

        nullable=True

    )



    uploaded_by = Column(

        String,

        nullable=True

    )



    # Indian Kanoon integration fields

    external_id = Column(

        String,

        nullable=True,

        index=True

    )



    document_url = Column(

        String,

        nullable=True

    )



    pdf_path = Column(

        String,

        nullable=True

    )



    case_type = Column(

        String,

        nullable=True

    )



    # Case detail fields

    judgment_text = Column(

        Text,

        nullable=True

    )



    acts_sections = Column(

        Text,

        nullable=True

    )



    judges = Column(

        String,

        nullable=True

    )



    case_facts = Column(

        Text,

        nullable=True

    )



    legal_issues = Column(

        Text,

        nullable=True

    )



    arguments = Column(

        Text,

        nullable=True

    )



    court_reasoning = Column(

        Text,

        nullable=True

    )



    final_decision = Column(

        Text,

        nullable=True

    )



    loaded_at = Column(

        DateTime(timezone=True),

        nullable=False,

        default=lambda: datetime.now(timezone.utc)

    )
