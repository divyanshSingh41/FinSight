from pathlib import Path
from pypdf import PdfReader

pdf_path = Path("../data/sample_data/reliance_consolidated_2023_24.pdf")

if not pdf_path.exists():
    raise FileNotFoundError(f"PDF not found: {pdf_path.resolve()}")

reader = PdfReader(pdf_path)
print(f"Pages: {len(reader.pages)}")

for page_number, page in enumerate(reader.pages[:5], start=1):
    text = page.extract_text() or ""
    print(f"\n--- Page {page_number}: {len(text)} characters ---")
    print(text[:500])