from pathlib import Path
from app.extractors.base import BaseExtractor, ExtractionResult


class PdfExtractor(BaseExtractor):
    SUPPORTED_MIME_TYPES = {"application/pdf"}

    def extract(self, file_path: Path) -> ExtractionResult:
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                pages_text = []
                all_tables = []
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    pages_text.append(text)
                    tables = page.extract_tables()
                    if tables:
                        all_tables.extend(tables)
                metadata = dict(pdf.metadata) if pdf.metadata else {}
                return ExtractionResult(
                    text="\n".join(pages_text),
                    structured_data={"tables": all_tables, "page_count": len(pdf.pages)},
                    metadata=metadata,
                )
        except Exception as e:
            return ExtractionResult(error=str(e))
