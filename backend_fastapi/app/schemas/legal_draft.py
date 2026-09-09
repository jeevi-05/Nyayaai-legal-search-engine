from typing import Literal

from pydantic import BaseModel, Field


class DraftParty(BaseModel):
    name: str = ""
    role: str = ""
    address: str = ""
    contact: str = ""


class LegalDraftRequest(BaseModel):
    document_type: str = Field(min_length=2, max_length=80)
    other_document_type: str = Field(default="", max_length=160)
    matter_title: str = Field(default="", max_length=250)
    jurisdiction: str = Field(default="", max_length=160)
    state: str = Field(default="", max_length=100)
    district: str = Field(default="", max_length=100)
    court: str = Field(default="", max_length=160)
    case_type: str = Field(default="", max_length=100)
    subject: str = Field(default="", max_length=500)
    case_status: str = Field(default="", max_length=160)
    incident_date: str = Field(default="", max_length=80)
    case_number: str = Field(default="", max_length=120)
    parties: list[DraftParty] = Field(default_factory=list, max_length=20)
    facts: str = Field(min_length=20, max_length=20000)
    important_dates: str = Field(default="", max_length=4000)
    events: str = Field(default="", max_length=6000)
    documents_available: str = Field(default="", max_length=4000)
    previous_notices: str = Field(default="", max_length=4000)
    previous_proceedings: str = Field(default="", max_length=4000)
    known_acts: str = Field(default="", max_length=2000)
    known_sections: str = Field(default="", max_length=2000)
    legal_provisions: str = Field(default="", max_length=4000)
    judgments_citations: str = Field(default="", max_length=4000)
    legal_research: str = Field(default="", max_length=8000)
    relief_requested: str = Field(min_length=10, max_length=10000)
    additional_information: str = Field(default="", max_length=8000)


class DraftSection(BaseModel):
    heading: str
    content: str


class LegalDraftResponse(BaseModel):
    title: str
    document_type: str
    court_heading: str
    parties: list[DraftParty]
    sections: list[DraftSection]
    prayer: str
    verification: str
    signature_fields: list[str]
    disclaimer: str
    potentially_relevant_provisions: list[dict] = Field(default_factory=list)


class PdfRequest(BaseModel):
    draft: LegalDraftResponse
