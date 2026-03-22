from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class ExtractionResult:
    text: str = ""
    structured_data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class BaseExtractor(ABC):
    SUPPORTED_MIME_TYPES: set[str] = set()

    def supports(self, mime_type: str) -> bool:
        return mime_type in self.SUPPORTED_MIME_TYPES

    @abstractmethod
    def extract(self, file_path: Path) -> ExtractionResult:
        pass
