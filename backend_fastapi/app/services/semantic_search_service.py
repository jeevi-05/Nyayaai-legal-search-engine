import json
import numpy as np

from sqlalchemy.orm import Session

from app.models.legal_document import LegalDocument

from app.services.embedding_service import EmbeddingService

from app.services.decision_support_service import decision_support_service



class SemanticSearchService:


    def __init__(self):

        self.embedding_service = EmbeddingService()



    def cosine_similarity(
        self,
        vec1,
        vec2
    ):

        vec1 = np.array(vec1)
        vec2 = np.array(vec2)


        if (
            np.linalg.norm(vec1) == 0
            or np.linalg.norm(vec2) == 0
        ):

            return 0



        similarity = (

            np.dot(vec1, vec2)

            /

            (
                np.linalg.norm(vec1)
                *
                np.linalg.norm(vec2)
            )

        )


        return float(similarity)





    # ==========================================
    # LEGAL RESEARCH SEARCH
    # Used by ResearchPage
    # ==========================================

    def search(
        self,
        db: Session,
        query: str,
        top_k: int = 5
    ):


        query_embedding = self.embedding_service.embed(
            query
        )


        documents = db.query(
            LegalDocument
        ).filter(

            LegalDocument.embedding.isnot(None)

        ).all()



        results = []



        for doc in documents:


            try:

                stored_embedding = json.loads(
                    doc.embedding
                )


                similarity = self.cosine_similarity(

                    query_embedding,

                    stored_embedding

                )


            except Exception:

                continue




            decision = decision_support_service.analyze(

                doc,

                query

            )



            results.append(

                {

                    "id": doc.id,

                    "title": doc.title,

                    "category":
                        doc.category.value
                        if doc.category
                        else None,


                    "year": doc.year,

                    "court": doc.court,

                    "citation": doc.citation,

                    "description": doc.description,

                    "summary": doc.summary,


                    "similarity":

                        round(
                            similarity * 100,
                            2
                        ),



                    "match_reason":

                        self.generate_reason(

                            similarity,

                            doc

                        ),



                    "decision_support":

                        decision

                }

            )



        results.sort(

            key=lambda x:x["similarity"],

            reverse=True

        )



        return results[:top_k]







    # ==========================================
    # UPLOAD DOCUMENT SIMILARITY SEARCH
    # Used after PDF upload
    # ==========================================

    def search_similar_documents(
        self,
        db: Session,
        embedding,
        current_document_id: int,
        top_k: int = 5
    ):



        documents = db.query(

            LegalDocument

        ).filter(

            LegalDocument.embedding.isnot(None),

            LegalDocument.id != current_document_id

        ).all()




        results = []



        for doc in documents:


            try:


                stored_embedding = json.loads(

                    doc.embedding

                )


                similarity = self.cosine_similarity(

                    embedding,

                    stored_embedding

                )


            except Exception:

                continue




            decision = decision_support_service.analyze(

                doc,

                doc.title

            )




            results.append(

                {

                    "id": doc.id,

                    "title": doc.title,


                    "category":

                        doc.category.value
                        if doc.category
                        else None,


                    "year": doc.year,


                    "court": doc.court,


                    "citation": doc.citation,


                    "summary": doc.summary,


                    "similarity":

                        round(

                            similarity * 100,

                            2

                        ),



                    "match_reason":

                        self.generate_reason(

                            similarity,

                            doc

                        ),



                    "decision_support":

                        decision

                }

            )




        results.sort(

            key=lambda x:x["similarity"],

            reverse=True

        )



        return results[:top_k]







    def generate_reason(

        self,

        score,

        doc=None

    ):


        if score >= 0.85:

            return (

                "Highly similar legal matter based on "
                "facts, legal principles and judicial reasoning."

            )


        elif score >= 0.70:

            return (

                "Related legal issue found with similar "
                "arguments and statutory interpretation."

            )


        elif score >= 0.50:

            return (

                "Moderately related case based on "
                "legal context and concepts."

            )


        else:

            return (

                "Contains some related legal concepts "
                "but limited similarity."

            )





semantic_search_service = SemanticSearchService()