"""Safe, source-aware drafting for citizen-provided legal information."""

from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer
from sqlalchemy.orm import Session

from app.schemas.legal_draft import DraftParty, DraftSection, LegalDraftRequest, LegalDraftResponse
from app.services.legal_research_service import legal_research_service

DISCLAIMER = ("This draft is generated using the information provided by the user and available legal information. "
              "It is intended for informational and drafting assistance only and should be reviewed by a qualified "
              "legal professional before filing or formal use.")


class LegalDraftService:
    """Builds type-specific, editable drafts without fabricating facts or citations."""

    def generate(self, db: Session, data: LegalDraftRequest) -> LegalDraftResponse:
        document_type = data.other_document_type.strip() if data.document_type == "Other Legal Draft" else data.document_type
        sources = self._research(db, data)
        title = data.matter_title.strip() or f"{document_type} — AI-generated legal draft for review"
        court_heading = data.court.strip() or "[COURT / AUTHORITY]"
        sections = self._sections(data, document_type, sources)
        return LegalDraftResponse(
            title=title,
            document_type=document_type,
            court_heading=court_heading,
            parties=data.parties,
            sections=sections,
            prayer=self._text(data.relief_requested, "[DESCRIBE THE RELIEF / REQUEST]") ,
            verification="I state that this draft has been prepared from the information provided and must be reviewed before formal use.",
            signature_fields=["Place: [PLACE]", "Date: [DATE]", "Signature: ____________________", "Name: [NAME]"],
            disclaimer=DISCLAIMER,
            potentially_relevant_provisions=sources,
        )

    def _research(self, db: Session, data: LegalDraftRequest) -> list[dict]:
        query = " ".join(filter(None, [data.subject, data.known_acts, data.known_sections, data.legal_provisions]))
        if not query.strip():
            return []
        try:
            result = legal_research_service.research(db, query)
        except Exception:
            return []
        provisions = []
        for item in (result.get("relevant_judgments") or [])[:3]:
            source = item.get("source_citation") or {}
            provisions.append({
                "label": item.get("case_name") or "Retrieved legal source",
                "summary": item.get("legal_principle") or item.get("why_this_result", [""])[0],
                "source": source.get("case_name") or item.get("citation") or "Repository source",
            })
        return provisions

    def _sections(self, data: LegalDraftRequest, document_type: str, sources: list[dict]) -> list[DraftSection]:
        facts = self._text(data.facts, "[DESCRIBE THE FACTS]")
        legal = self._legal_information(data, sources)
        details = self._details(data)
        normalized = document_type.lower()
        if "notice" in normalized:
            return [DraftSection(heading="Subject", content=self._text(data.subject, "[SUBJECT]")), DraftSection(heading="Facts and circumstances", content=facts), DraftSection(heading="Legal basis", content=legal), DraftSection(heading="Demand / request", content=self._text(data.relief_requested, "[STATE THE DEMAND]")), DraftSection(heading="Compliance", content="You are requested to respond or comply within [TIME PERIOD], subject to professional review."), DraftSection(heading="Additional details", content=details)]
        if "affidavit" in normalized:
            return [DraftSection(heading="Deponent's statement", content="I, [NAME], state the following on the basis of information provided:"), DraftSection(heading="Facts affirmed", content=facts), DraftSection(heading="Legal information", content=legal), DraftSection(heading="Purpose", content=self._text(data.relief_requested, "[STATE THE PURPOSE]")), DraftSection(heading="Additional details", content=details)]
        if "reply" in normalized or "response" in normalized:
            return [DraftSection(heading="Background", content=facts), DraftSection(heading="Response / submissions", content=self._text(data.subject, "[STATE THE RESPONSE]") + "\n\n" + legal), DraftSection(heading="Request", content=self._text(data.relief_requested, "[STATE THE REQUEST]")), DraftSection(heading="Additional details", content=details)]
        return [DraftSection(heading="Introduction and background", content=self._text(data.subject, "[STATE THE SUBJECT / LEGAL ISSUE]") + "\n\n" + facts), DraftSection(heading="Facts of the matter", content=facts), DraftSection(heading="Relevant legal information", content=legal), DraftSection(heading="Grounds / contentions", content="The following matter is placed for consideration based on the facts and legal information stated above. Any legal grounds require professional verification before formal use."), DraftSection(heading="Additional details and documents", content=details)]

    @staticmethod
    def _text(value: str, fallback: str) -> str:
        return value.strip() if value and value.strip() else fallback

    def _legal_information(self, data: LegalDraftRequest, sources: list[dict]) -> str:
        provided = [
            ("User-provided Acts", data.known_acts), ("User-provided Sections", data.known_sections),
            ("User-provided legal provisions", data.legal_provisions), ("User-provided citations", data.judgments_citations),
            ("User-provided research", data.legal_research),
        ]
        content = [f"{label}: {value.strip()}" for label, value in provided if value and value.strip()]
        if sources:
            content.append("Potentially relevant provisions / sources (for professional verification): " + "; ".join(f"{item['label']} — {item['source']}" for item in sources))
        return "\n\n".join(content) or "No legal provision or citation has been asserted. Professional review is required before relying on any legal provision."

    def _details(self, data: LegalDraftRequest) -> str:
        fields = [("Important dates", data.important_dates), ("Events", data.events), ("Documents available", data.documents_available), ("Previous notices", data.previous_notices), ("Previous proceedings", data.previous_proceedings), ("Additional information", data.additional_information)]
        return "\n".join(f"{label}: {value.strip()}" for label, value in fields if value and value.strip()) or "[ADD RELEVANT DOCUMENTS OR OTHER DETAILS IF REQUIRED]"

    def pdf(self, draft: LegalDraftResponse) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2.1*cm, leftMargin=2.1*cm, topMargin=1.8*cm, bottomMargin=1.8*cm)
        styles = getSampleStyleSheet()
        heading = ParagraphStyle("DraftHeading", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#102035"))
        body = ParagraphStyle("DraftBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=10, leading=15, alignment=TA_JUSTIFY, spaceAfter=7)
        centre = ParagraphStyle("DraftCentre", parent=body, alignment=TA_CENTER, fontName="Helvetica-Bold")
        story = [Paragraph("NYAYAAI | LEGAL INTELLIGENCE PLATFORM", centre), Paragraph("AI-GENERATED LEGAL DRAFT FOR REVIEW", centre), HRFlowable(width="100%", color=colors.HexColor("#c9a84c")), Spacer(1, 10), Paragraph(escape(draft.court_heading), centre), Paragraph(escape(draft.title), centre), Paragraph(escape(draft.document_type.upper()), centre), Spacer(1, 10)]
        if draft.parties:
            story += [Paragraph("PARTIES", heading)]
            for party in draft.parties:
                details = ", ".join(filter(None, [party.role, party.name, party.address, party.contact])) or "[PARTY DETAILS]"
                story += [Paragraph(escape(details), body)]
        for index, section in enumerate(draft.sections, 1):
            story += [Paragraph(f"{index}. {escape(section.heading.upper())}", heading), Paragraph(escape(section.content).replace("\n", "<br/>"), body)]
        story += [Paragraph("PRAYER / RELIEF", heading), Paragraph(escape(draft.prayer).replace("\n", "<br/>"), body), Paragraph("VERIFICATION", heading), Paragraph(escape(draft.verification), body)]
        for field in draft.signature_fields: story.append(Paragraph(escape(field), body))
        story += [Spacer(1, 12), HRFlowable(width="100%", color=colors.HexColor("#c9a84c")), Paragraph(escape(draft.disclaimer), ParagraphStyle("Disclaimer", parent=body, fontSize=8, leading=11, textColor=colors.HexColor("#64748b")))]
        doc.build(story, onFirstPage=self._footer, onLaterPages=self._footer)
        buffer.seek(0)
        return buffer

    @staticmethod
    def _footer(canvas, doc):
        canvas.saveState(); canvas.setFont("Helvetica", 8); canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(2.1*cm, 1.1*cm, "NyayaAI | AI-generated legal draft | For review before formal use")
        canvas.drawRightString(A4[0] - 2.1*cm, 1.1*cm, f"Page {doc.page}"); canvas.restoreState()


legal_draft_service = LegalDraftService()
