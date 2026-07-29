import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.profile import ChildProfile
from app.models.rag_chunk import EducationalDocumentChunk
from app.schemas.rag import DocumentIngestionRequest, RAGQueryRequest
from app.services.rag_engine import RAGEngine


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    # Family 1 (Alpha) - Child 1 (Emma)
    child_1 = ChildProfile(
        family_id="fam_alpha",
        name="Emma",
        date_of_birth=date(2012, 5, 10),
        age=14,
        gender="FEMALE",
        education_stage="SECONDARY_SCHOOL",
        parent_contact="+1-555-1010",
    )
    # Family 2 (Beta) - Child 2 (Liam)
    child_2 = ChildProfile(
        family_id="fam_beta",
        name="Liam",
        date_of_birth=date(2013, 8, 20),
        age=13,
        gender="MALE",
        education_stage="SECONDARY_SCHOOL",
        parent_contact="+1-555-2020",
    )

    session.add_all([child_1, child_2])
    session.commit()
    session.refresh(child_1)
    session.refresh(child_2)

    yield session
    session.close()


def test_document_ingestion_and_retrieval(db_session):
    rag = RAGEngine(db=db_session)

    # Ingest study notes for Emma (fam_alpha, child_id=1)
    doc_req = DocumentIngestionRequest(
        child_id=1,
        family_id="fam_alpha",
        subject="Biology",
        topic="Photosynthesis",
        document_type="STUDY_NOTES",
        privacy_level="FAMILY_ONLY",
        title="Photosynthesis Fundamentals",
        raw_content="Photosynthesis is the process used by plants to convert light energy into chemical energy stored in glucose molecules.",
    )
    res = rag.ingest_document(doc_req)
    assert res["chunks_ingested"] > 0

    # Query as Emma
    query_req = RAGQueryRequest(
        child_id=1,
        family_id="fam_alpha",
        query="What is photosynthesis?",
        subject="Biology",
    )
    grounded = rag.generate_grounded_answer(query_req)

    assert grounded.retrieved_chunks_count > 0
    assert "Photosynthesis" in grounded.answer or "photosynthesis" in grounded.answer
    assert grounded.source_documents[0]["title"] == "Photosynthesis Fundamentals"


def test_cross_family_rag_retrieval_isolation(db_session):
    rag = RAGEngine(db=db_session)

    # Ingest document for Family Alpha (Emma, child_id=1)
    rag.ingest_document(
        DocumentIngestionRequest(
            child_id=1,
            family_id="fam_alpha",
            subject="History",
            topic="World War II",
            document_type="STUDY_NOTES",
            privacy_level="FAMILY_ONLY",
            title="Secret Family History Notes",
            raw_content="Private notes regarding Family Alpha's history thesis.",
        )
    )

    # Family Beta (Liam, child_id=2) queries for History Notes
    beta_query = RAGQueryRequest(
        child_id=2,
        family_id="fam_beta",
        query="What are the secret family history notes?",
        subject="History",
    )

    chunks = rag.retrieve_relevant_chunks(beta_query)
    # Asserts that Liam cannot retrieve any chunks from Family Alpha
    assert len(chunks) == 0

    grounded_res = rag.generate_grounded_answer(beta_query)
    assert grounded_res.retrieved_chunks_count == 0
    assert "No relevant educational documents found in your authorized library" in grounded_res.answer
