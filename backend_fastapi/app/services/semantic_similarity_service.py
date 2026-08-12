import json

import numpy as np

from sklearn.metrics.pairwise import cosine_similarity

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embedding(text: str):

    if not text:
        return []

    vector = model.encode(text)

    return vector.tolist()


def similarity(vec1, vec2):

    a = np.array(vec1).reshape(1, -1)

    b = np.array(vec2).reshape(1, -1)

    return float(cosine_similarity(a, b)[0][0])


def compare_with_documents(current_embedding, documents):

    results = []

    for doc in documents:

        if not doc.embedding:
            continue

        score = similarity(
            current_embedding,
            json.loads(doc.embedding)
        )

        results.append(
            {
                "id": doc.id,
                "title": doc.title,
                "score": round(score * 100, 2),
                "summary": doc.summary
            }
        )

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:5]