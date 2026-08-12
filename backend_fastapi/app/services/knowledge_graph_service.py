"""
KnowledgeGraphService — Phase 2 placeholder.

TODO: Build and query a legal knowledge graph.

Planned responsibilities:
  - Extract legal entities (cases, statutes, articles, parties) via NLP / spaCy
  - Construct a Neo4j or NetworkX graph of entity relationships
  - Expose graph traversal queries (e.g. "cases citing article 21")
  - Feed graph context into RAG pipeline for richer answers
"""


class KnowledgeGraphService:
    def build_graph(self):
        # TODO: extract entities from all LegalDocuments
        # TODO: persist edges to Neo4j or in-memory NetworkX
        raise NotImplementedError("KnowledgeGraphService will be implemented in Phase 2")

    def query(self, entity: str) -> list[dict]:
        # TODO: return related entities and relationships
        raise NotImplementedError("KnowledgeGraphService.query will be implemented in Phase 2")
