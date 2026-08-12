"""
RagService — Phase 2 placeholder.

TODO: Implement Retrieval-Augmented Generation pipeline.

Planned responsibilities:
  - Accept a natural-language legal query
  - Retrieve top-k relevant passages via SemanticSearchService
  - Build a context-augmented prompt
  - Call Llama 3 (local via Ollama or HF) to generate a grounded answer
  - Return answer + cited document references
"""


class RagService:
    def answer(self, query: str) -> dict:
        # TODO: retrieve passages from SemanticSearchService
        # TODO: build prompt with retrieved context
        # TODO: call LLM (Llama 3) for generation
        # TODO: return {"answer": str, "sources": [doc_id, ...]}
        raise NotImplementedError("RagService will be implemented in Phase 2")
