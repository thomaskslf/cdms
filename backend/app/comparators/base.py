from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ComparisonOutput:
    comparison_type: str
    summary: str
    changes_count: int
    diff_data: dict[str, Any] = field(default_factory=dict)
    similarity: float = 1.0  # 0.0 = completely different, 1.0 = identical


class BaseComparator(ABC):
    @abstractmethod
    def compare(self, version_a, version_b) -> ComparisonOutput:
        pass
