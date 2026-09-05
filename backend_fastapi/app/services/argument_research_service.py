from sqlalchemy.orm import Session

from app.services.legal_research_service import legal_research_service


class ArgumentResearchService:
    def analyze(self, db: Session, argument: str | dict) -> dict:
        if isinstance(argument, dict):
            case_issue = (argument.get("case_issue") or "").strip()
            legal_argument = (argument.get("legal_argument") or "").strip()
            opposite_argument = (argument.get("opposite_argument") or "").strip()
            case_type = (argument.get("case_type") or "").strip()
            relevant_law = (argument.get("relevant_law") or "").strip()
            query = "\n".join(filter(None, [case_issue, legal_argument, case_type, relevant_law]))
        else:
            case_issue, legal_argument, opposite_argument, case_type, relevant_law = "", argument, "", "", ""
            query = argument
        research = legal_research_service.research(db, query)
        cases = research["relevant_judgments"]
        support = [{"case": item["case_name"], "case_name": item["case_name"], "court": item["court"], "year": item["year"],
                    "relevant_paragraph": item["important_paragraph"],
                    "why_supports": f"Addresses the pleaded issue and provides authority relevant to the advocate's position ({', '.join(item['why_this_result']).lower()}).",
                    "argument_strength_score": round(item["similarity_score"], 2), "reason": item["important_paragraph"]["text"],
                    "source_citation": item["source_citation"]} for item in cases]
        weaknesses = ["No directly matching authority was retrieved."] if not cases else [
            "Verify that the factual record matches the cited authority.",
            "Check whether later decisions limit, distinguish, or overrule the authority.",
        ]
        counter_arguments = [opposite_argument] if opposite_argument else [
            "The opposing party may distinguish the cited authorities on facts, statute, or procedural posture.",
            "The opposing party may contend that the authorities do not establish the relief sought on the present record.",
        ]
        strong_points = [f"{item['case_name']} supports the proposition with {item['argument_strength_score']}% retrieval relevance." for item in support[:3]]
        return {
            "argument_summary": legal_argument or argument,
            "legal_classification": {"legal_principle": self._principle(support), "legal_area": case_type or "Indian legal proceedings", "applicable_provisions": relevant_law or legal_research_service.extract_query_metadata(query)["acts_sections"]},
            "supporting_authorities": support,
            "legal_reasoning": self._reasoning(support, case_issue or query),
            "counter_arguments": counter_arguments,
            "counter_strategy": ["Distinguish the opposing authority on its facts and procedural posture.", "Tie the requested relief to the applicable statutory provision and the cited paragraphs."],
            "weakness_detection": weaknesses,
            "argument_strength": {"score": research["confidence_score"], "strong_points": strong_points or ["The submission requires stronger source support."], "weak_points": weaknesses, "risk_factors": ["Outcome depends on factual fit and any later or contrary precedent."]},
            "court_submission_draft": self._submission(case_issue, legal_argument, support, relevant_law),
            "your_argument": legal_argument or argument,
            "weakness_analysis": weaknesses, "suggested_responses": ["Address factual distinctions directly and anchor each submission to the cited paragraph."],
            "confidence_score": research["confidence_score"],
        }

    @staticmethod
    def _principle(support: list[dict]) -> str:
        return "The applicable legal principle is supported by the retrieved authorities and must be applied to the pleaded facts." if support else "No legal principle could be reliably classified from the retrieved authorities."

    @staticmethod
    def _reasoning(support: list[dict], issue: str) -> str:
        if not support:
            return f"The retrieved record does not yet provide sufficient authority to strengthen the argument on: {issue}."
        return f"The authorities strengthen the argument on '{issue}' because each supplies a judicial passage addressing the relevant legal issue. Their force depends on factual similarity, statutory fit, and precedential status."

    @staticmethod
    def _submission(issue: str, argument: str, support: list[dict], law: str) -> str:
        authority = support[0]["case_name"] if support else "the authorities placed on record"
        provision = f" under {law}" if law else ""
        return f"It is respectfully submitted that, on the issue of {issue or 'the matter before this Court'}, the applicant's position, namely that {argument or 'the relief sought is legally warranted'}, is supported{provision} by the principles discussed in {authority}. The Court is therefore invited to apply those principles to the established facts and grant the relief sought."


argument_research_service = ArgumentResearchService()
