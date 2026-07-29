import json
import uuid
import math
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.rag_chunk import EducationalDocumentChunk
from app.schemas.rag import (
    DocumentIngestionRequest,
    RAGQueryRequest,
    GroundedAnswerResponse,
    DocumentChunk,
)
from app.ai.groq_service import _get_groq_client

logger = logging.getLogger(__name__)


def generate_simple_embedding(text: str, dim: int = 64) -> List[float]:
    """
    Generates a deterministic 64-dimensional normalized vector embedding for text.
    Ensures vector similarity search without requiring heavy external dependencies.
    """
    vec = [0.0] * dim
    words = text.lower().split()
    for idx, word in enumerate(words):
        val = sum(ord(c) for c in word)
        pos = val % dim
        vec[pos] += math.log(len(word) + 1.0) * (1.0 + (idx % 3) * 0.1)

    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
    return float(dot)


class RAGEngine:
    """
    Phase 12: Retrieval-Augmented Generation Engine for Educational & Child Knowledge.
    Pipeline:
    Document -> Text extraction & Chunking -> Embedding -> Storage -> Vector Retrieval with Family Isolation -> Grounded AI Answer
    """

    def __init__(self, db: Session):
        self.db = db

    def chunk_text(self, text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
        words = text.split()
        if len(words) <= chunk_size:
            return [text]

        chunks = []
        i = 0
        while i < len(words):
            chunk_words = words[i : i + chunk_size]
            chunks.append(" ".join(chunk_words))
            i += chunk_size - overlap
        return chunks

    def ingest_document(self, req: DocumentIngestionRequest) -> Dict[str, Any]:
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        text_chunks = self.chunk_text(req.raw_content)

        created_chunks = []
        for idx, chunk_text in enumerate(text_chunks):
            c_id = f"{doc_id}_c{idx}"
            embedding = generate_simple_embedding(chunk_text)

            chunk_record = EducationalDocumentChunk(
                chunk_id=c_id,
                document_id=doc_id,
                child_id=req.child_id,
                family_id=req.family_id,
                subject=req.subject,
                topic=req.topic,
                document_type=req.document_type,
                privacy_level=req.privacy_level,
                title=req.title,
                chunk_index=idx,
                content=chunk_text,
                embedding_json=json.dumps(embedding),
            )
            self.db.add(chunk_record)
            created_chunks.append(c_id)

        self.db.commit()
        return {
            "document_id": doc_id,
            "chunks_ingested": len(created_chunks),
            "title": req.title,
            "family_id": req.family_id,
            "child_id": req.child_id,
        }

    def retrieve_relevant_chunks(self, req: RAGQueryRequest) -> List[Dict[str, Any]]:
        query_vec = generate_simple_embedding(req.query)

        # STRICT ISOLATION FILTERING: Filter exclusively by family_id and child_id
        db_query = self.db.query(EducationalDocumentChunk).filter(
            EducationalDocumentChunk.family_id == req.family_id,
            EducationalDocumentChunk.child_id == req.child_id,
        )

        if req.subject:
            db_query = db_query.filter(EducationalDocumentChunk.subject.ilike(req.subject))

        candidate_chunks = db_query.all()
        scored_chunks = []

        for chunk in candidate_chunks:
            chunk_vec = json.loads(chunk.embedding_json)
            score = cosine_similarity(query_vec, chunk_vec)
            scored_chunks.append({
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "title": chunk.title,
                "subject": chunk.subject,
                "topic": chunk.topic,
                "content": chunk.content,
                "score": score,
            })

        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[: req.top_k]

    def generate_grounded_answer(self, req: RAGQueryRequest) -> GroundedAnswerResponse:
        chunks = self.retrieve_relevant_chunks(req)

        if not chunks:
            return GroundedAnswerResponse(
                query=req.query,
                answer="No relevant educational documents found in your authorized library for this query.",
                retrieved_chunks_count=0,
                source_documents=[],
            )

        context_str = "\n\n".join([f"--- Source ({c['title']} - {c['subject']}) ---\n{c['content']}" for c in chunks])

        client = _get_groq_client()
        if client:
            prompt_content = f"""
You are the KinNest Educational RAG Assistant.
Answer the child's query using ONLY the retrieved study document context below.

RETRIEVED STUDY CONTEXT:
{context_str}

QUERY:
{req.query}

STRICT RULE: Base your answer exclusively on the provided context. If the answer is not in the context, clearly state that.
"""
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt_content}],
                    temperature=0.2,
                    max_tokens=800,
                )
                answer_text = response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"Groq RAG completion error: {e}")
                answer_text = f"Based on your notes ({chunks[0]['title']}):\n{chunks[0]['content']}"
        else:
            answer_text = f"Based on your study notes for {chunks[0]['subject']} ({chunks[0]['title']}):\n{chunks[0]['content']}"

        sources = [{"title": c["title"], "subject": c["subject"], "chunk_id": c["chunk_id"]} for c in chunks]

        return GroundedAnswerResponse(
            query=req.query,
            answer=answer_text,
            retrieved_chunks_count=len(chunks),
            source_documents=sources,
        )
