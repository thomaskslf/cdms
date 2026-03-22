from pathlib import Path
from app.extractors.base import BaseExtractor, ExtractionResult
from app.extractors.pdf_extractor import PdfExtractor
from app.extractors.excel_extractor import ExcelExtractor
from app.extractors.dxf_extractor import DxfExtractor
from app.extractors.image_extractor import ImageExtractor

_extractors: list[BaseExtractor] = [
    PdfExtractor(),
    ExcelExtractor(),
    DxfExtractor(),
    ImageExtractor(),
]


def extract(file_path: Path, mime_type: str) -> ExtractionResult:
    for extractor in _extractors:
        if extractor.supports(mime_type):
            return extractor.extract(file_path)
    return ExtractionResult(text="", structured_data={}, metadata={})
