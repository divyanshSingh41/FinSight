from pathlib import Path
from typing import Any

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

AI_SERVICE_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = AI_SERVICE_ROOT.parent
CHROMA_PATH = PROJECT_ROOT / "storage" / "chroma"
COLLECTION_NAME = "finsight_filings"


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
AI_SERVICE_ROOT = Path(__file__).resolve().parents[2]

persist_path = Path(CHROMA_PATH)
if not persist_path.is_absolute():
    persist_path = (AI_SERVICE_ROOT / persist_path).resolve()

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=str(CHROMA_PATH),
    embedding_function=embeddings,
)


def retrieve_filings(question: str, *, ticker: str | None = None, fiscal_year: str | None = None, k: int = 5) -> list[dict[str, Any]]:
    """Retrieve filing passages, optionally limited to a company and fiscal year."""
    if not question.strip():
        raise ValueError("question must not be empty")

    filters = []
    if ticker:
        filters.append({"ticker": ticker.upper()})
    if fiscal_year:
        filters.append({"fiscal_year": fiscal_year})

    metadata_filter = None
    if len(filters) == 1:
        metadata_filter = filters[0]
    elif len(filters) > 1:
        metadata_filter = {"$and": filters}

    results = vector_store.similarity_search_with_score(
        question,
        k=k,
        filter=metadata_filter,
    )

    passages = []
    for document, distance in results:
        passages.append({
            "text": document.page_content,
            "company": document.metadata.get("company"),
            "ticker": document.metadata.get("ticker"),
            "fiscal_year": document.metadata.get("fiscal_year"),
            "document_type": document.metadata.get("document_type"),
            "page_number": document.metadata.get("page_number"),
            "source_url": document.metadata.get("source_url"),
            "distance": float(distance),
        })

    return passages
