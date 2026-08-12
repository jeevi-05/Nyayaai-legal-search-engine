import json

from app.core.database import SessionLocal
from app.models.legal_document import LegalDocument
from app.services.embedding_service import EmbeddingService


db = SessionLocal()

embedding_service = EmbeddingService()


documents = db.query(LegalDocument).all()


for doc in documents:

    if doc.extracted_text:

        print(
            "Generating:",
            doc.title
        )

        embedding = embedding_service.embed(
            doc.extracted_text
        )


        doc.embedding = json.dumps(
            embedding
        )


db.commit()

db.close()


print("Embeddings generated successfully")