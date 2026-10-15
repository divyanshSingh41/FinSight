import argparse
import re
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHROMA_PATH = PROJECT_ROOT / "storage" / "chroma"
COLLECTION_NAME = "finsight_filings"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def safe_id_part(value: str) -> str:
    """Convert a value to a stable, ID-safe string."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Index a company's annual report in the FinSight Chroma collection."
    )
    parser.add_argument("--company", required=True, help="Company's full name")
    parser.add_argument("--ticker", required=True, help="Ticker, e.g. RELIANCE")
    parser.add_argument("--fiscal-year", required=True, help="Fiscal year, e.g. 2023-24")
    parser.add_argument("--pdf", required=True, help="PDF path, relative to this folder or absolute")
    parser.add_argument(
        "--source-url",
        required=True,
        help="Official URL where the report was obtained",
    )
    parser.add_argument(
        "--document-type",
        default="integrated_annual_report",
        help="Document type label; defaults to integrated_annual_report",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.is_absolute():
        pdf_path = (Path.cwd() / pdf_path).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages = PyPDFLoader(str(pdf_path)).load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        add_start_index=True,
    )
    chunks = splitter.split_documents(pages)

    if not chunks:
        raise ValueError(
            "No text chunks were extracted. Check whether the PDF contains selectable text."
        )

    ticker_id = safe_id_part(args.ticker)
    year_id = safe_id_part(args.fiscal_year)
    document_type_id = safe_id_part(args.document_type)

    chunk_counts_by_page = {}
    ids = []

    for chunk in chunks:
        page_index = int(chunk.metadata.get("page", 0))
        page_number = page_index + 1

        chunk_counts_by_page[page_number] = (
            chunk_counts_by_page.get(page_number, 0) + 1
        )
        chunk_number = chunk_counts_by_page[page_number]

        chunk.metadata = {
            "company": args.company,
            "ticker": args.ticker.upper(),
            "fiscal_year": args.fiscal_year,
            "document_type": args.document_type,
            "page_number": page_number,
            "source_url": args.source_url,
            "filename": pdf_path.name,
            "start_index": int(chunk.metadata.get("start_index", 0)),
        }

        ids.append(
            f"{ticker_id}_{year_id}_{document_type_id}"
            f"_page_{page_number}_chunk_{chunk_number}"
        )

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_PATH),
        embedding_function=embeddings,
    )

    # Stable IDs let you rerun this same report without duplicating its chunks.
    vector_store.add_documents(documents=chunks, ids=ids)

    print(f"Indexed {len(chunks)} chunks from {len(pages)} pages.")
    print(f"Company: {args.company} ({args.ticker.upper()})")
    print(f"Fiscal year: {args.fiscal_year}")
    print(f"Chroma collection: {COLLECTION_NAME}")
    print(f"Chroma database: {CHROMA_PATH}")


if __name__ == "__main__":
    main()