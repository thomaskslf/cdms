import hashlib
import mimetypes
import shutil
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from app.config import settings


def get_storage_root() -> Path:
    root = Path(settings.storage_root)
    root.mkdir(parents=True, exist_ok=True)
    return root


def get_version_dir(customer_id: int, project_id: int, doc_type: str, version_id: int) -> Path:
    path = get_storage_root() / f"customers/{customer_id}/projects/{project_id}/{doc_type}/v{version_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def compute_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def detect_mime_type(file_path: Path, original_filename: str) -> str:
    # Use file extension as primary signal (reliable for most engineering docs)
    ext = Path(original_filename).suffix.lower()
    mime_map = {
        ".pdf": "application/pdf",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".csv": "text/csv",
        ".dxf": "image/vnd.dxf",
        ".dwg": "application/acad",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".tiff": "image/tiff",
        ".tif": "image/tiff",
    }
    return mime_map.get(ext) or mimetypes.guess_type(original_filename)[0] or "application/octet-stream"


async def save_uploaded_file(upload: UploadFile, target_dir: Path) -> tuple[Path, int, str]:
    """Save upload to target_dir/original.<ext>, return (path, size, sha256)."""
    ext = Path(upload.filename).suffix.lower()
    target_path = target_dir / f"original{ext}"

    content = await upload.read()
    target_path.write_bytes(content)

    file_size = len(content)
    sha256 = hashlib.sha256(content).hexdigest()
    return target_path, file_size, sha256


def generate_thumbnail(source_path: Path, target_dir: Path, mime_type: str) -> Optional[Path]:
    """Generate a PNG thumbnail for PDFs and images. Returns thumbnail path or None."""
    try:
        thumb_path = target_dir / "thumbnail.png"

        if mime_type == "application/pdf":
            try:
                import pdfplumber
                from PIL import Image
                import io
                with pdfplumber.open(source_path) as pdf:
                    if pdf.pages:
                        page_img = pdf.pages[0].to_image(resolution=72)
                        page_img.save(str(thumb_path), format="PNG")
                return thumb_path
            except Exception:
                return None

        elif mime_type.startswith("image/"):
            from PIL import Image
            with Image.open(source_path) as img:
                img.thumbnail((400, 400))
                img.save(thumb_path, format="PNG")
            return thumb_path

    except Exception:
        return None

    return None
