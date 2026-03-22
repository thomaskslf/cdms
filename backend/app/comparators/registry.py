from app.comparators.base import BaseComparator
from app.comparators.text_comparator import TextComparator
from app.comparators.bom_comparator import BomComparator
from app.comparators.dxf_comparator import DxfComparator

_DXF_MIMES = {"image/vnd.dxf", "application/acad"}
_TABULAR_MIMES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "text/csv",
}


def get_comparator(doc_type: str, mime_a: str, mime_b: str) -> BaseComparator:
    if doc_type == "stückliste" and (mime_a in _TABULAR_MIMES or mime_b in _TABULAR_MIMES):
        return BomComparator()
    if mime_a in _DXF_MIMES or mime_b in _DXF_MIMES:
        return DxfComparator()
    return TextComparator()
