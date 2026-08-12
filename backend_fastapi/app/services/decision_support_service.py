from app.models.legal_document import LegalDocument


class DecisionSupportService:

    def analyze(self, doc: LegalDocument, query: str):

        category = doc.category.value

        # Default values
        principle = "General legal principle"
        legal_issue = "Legal issue related to the searched query"
        applicability = "Review facts of the case before applying this precedent."
        strength = "Medium"


        if category == "LANDMARK_CASE":

            strength = "High"

            title = doc.title.lower()

            if "kesavananda" in title:
                legal_issue = (
                    "Whether Parliament has unlimited power to amend the Constitution"
                )

                principle = (
                    "Basic Structure Doctrine — Parliament cannot amend "
                    "the Constitution in a way that destroys its basic structure."
                )

                applicability = (
                    "Applicable in constitutional amendment cases "
                    "where fundamental constitutional features are affected."
                )


            elif "maneka" in title:

                legal_issue = (
                    "Protection of personal liberty and fairness of procedure"
                )

                principle = (
                    "Article 21 must be interpreted broadly with "
                    "principles of fairness and reasonableness."
                )

                applicability = (
                    "Applicable in cases involving violation of fundamental rights."
                )


            else:

                principle = (
                    "Judicial precedent established by the Supreme Court."
                )


        elif category == "ACT":

            strength = "High"

            legal_issue = (
                "Statutory interpretation and application of legal provisions"
            )

            principle = (
                "Relevant provisions of the Act govern the legal issue."
            )

            applicability = (
                "Applicable when facts fall within the scope of the statute."
            )


        elif category == "JUDGMENT":

            strength = "Medium"

            legal_issue = (
                "Interpretation of law based on judicial reasoning"
            )

            principle = (
                "Court reasoning can guide similar legal disputes."
            )

            applicability = (
                "Depends on similarity between present facts and decided case."
            )


        return {

            "recommendation":
                "This document is relevant and can support legal analysis.",

            "legal_issue":
                legal_issue,

            "principle_established":
                principle,

            "precedent_strength":
                strength,

            "applicability":
                applicability,

            "relevance":
                "High",

            "reason":
                f"The document matches the legal issue: '{query}'."
        }


decision_support_service = DecisionSupportService()