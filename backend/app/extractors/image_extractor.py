from pathlib import Path
from app.extractors.base import BaseExtractor, ExtractionResult


class ImageExtractor(BaseExtractor):
    SUPPORTED_MIME_TYPES = {"image/jpeg", "image/png", "image/tiff"}

    def extract(self, file_path: Path) -> ExtractionResult:
        try:
            from PIL import Image
            img = Image.open(file_path)
            metadata = {
                "size": list(img.size),
                "mode": img.mode,
                "format": img.format,
            }
            # Try EXIF
            try:
                exif_data = img._getexif()
                if exif_data:
                    metadata["exif"] = {str(k): str(v) for k, v in list(exif_data.items())[:20]}
            except Exception:
                pass

            # OCR with pytesseract (lightweight, no model download needed)
            text = ""
            try:
                import pytesseract
                text = pytesseract.image_to_string(img, lang="deu+eng")
            except Exception:
                pass  # OCR optional — file still stored without text

            return ExtractionResult(text=text, structured_data={}, metadata=metadata)
        except Exception as e:
            return ExtractionResult(error=str(e))
