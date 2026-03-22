"""
Document classification based on 5 signals:
  1. Folder path (highest weight: 0.5)
  2. Filename patterns (0.4)
  3. Content keywords (0.3)
  4. File extension (0.2)
  5. MIME type (0.1)
"""
import re
from typing import Optional

DOC_TYPE_RULES: dict[str, dict] = {
    "stückliste": {
        "folder_patterns": [r"st.ck", r"\bBOM\b", r"parts.?list", r"material"],
        "filename_patterns": [r"st.ck", r"\bSTL\b", r"\bBOM\b", r"parts.?list", r"material"],
        "content_keywords": ["SACHNUMMER", "ARTIKELNUMMER", "BEZEICHNUNG", "MENGE", "POSITION",
                             "POS\b", "QTY", "PART.NO", "STÜCKLISTE"],
        "extensions": {".xlsx", ".xls", ".csv"},
        "mime_types": {
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
            "text/csv",
        },
    },
    "zeichnung": {
        "folder_patterns": [r"zeichn", r"\bZNG\b", r"drawing", r"\bDRW\b"],
        "filename_patterns": [r"zeichn", r"\bZNG\b", r"drawing", r"\bDRW\b", r"\bZTG\b"],
        "content_keywords": ["MASSTAB", "TOLERANZ", "DIN ISO", "ZEICHNUNG", "ANSICHT",
                             "SCHNITT", "DETAIL", "NORMTEIL"],
        "extensions": {".pdf", ".dxf", ".dwg"},
        "mime_types": {"image/vnd.dxf", "application/acad"},
    },
    "bestückzeichnung": {
        "folder_patterns": [r"best.ck", r"\bBSZ\b", r"placement", r"assembly.?plan"],
        "filename_patterns": [r"best.ck", r"\bBSZ\b", r"placement", r"assembly.?plan"],
        "content_keywords": ["BESTÜCKPLAN", "REFERENZPUNKT", "\bSMD\b", "\bTHT\b",
                             "BESTÜCKUNG", "LEITERPLATTE"],
        "extensions": {".pdf", ".dxf", ".dwg"},
        "mime_types": set(),
    },
    "montagezeichnung": {
        "folder_patterns": [r"montage", r"\bMNT\b", r"assembly.?draw", r"einbau"],
        "filename_patterns": [r"montage", r"\bMNT\b", r"assembly.?draw", r"einbau"],
        "content_keywords": ["MONTAGE", "EINBAULAGE", "ANZUGSMOMENT", "MONTAGEZEICHNUNG",
                             "EINBAUZEICHNUNG"],
        "extensions": {".pdf", ".dxf", ".dwg"},
        "mime_types": set(),
    },
    "key_anweisung": {
        "folder_patterns": [r"anweisung", r"instruction", r"\bAWI\b", r"\bSOP\b", r"arbeits"],
        "filename_patterns": [r"anweisung", r"instruction", r"\bAWI\b", r"\bSOP\b", r"arbeits"],
        "content_keywords": ["ARBEITSANWEISUNG", "SCHRITT", "WARNUNG", "ACHTUNG", "HINWEIS",
                             "GEFAHR", "PROCEDURE", "INSTRUCTION"],
        "extensions": {".pdf"},
        "mime_types": set(),
    },
    "unterbaugruppe": {
        "folder_patterns": [r"unterbau", r"\bUBG\b", r"subassembly", r"baugruppe"],
        "filename_patterns": [r"unterbau", r"\bUBG\b", r"subassembly", r"baugruppe"],
        "content_keywords": ["BAUGRUPPE", "SUBASSEMBLY", "UNTERBAUGRUPPE"],
        "extensions": {".pdf", ".dxf", ".dwg"},
        "mime_types": set(),
    },
}

CONFIDENCE_THRESHOLD = 0.6


def classify_document(
    filename: str,
    mime_type: str,
    folder_path: Optional[str] = None,
    extracted_text: Optional[str] = None,
) -> tuple[str, float]:
    """
    Returns (doc_type, confidence_score).
    Confidence < CONFIDENCE_THRESHOLD means the user should confirm.
    """
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    text_upper = (extracted_text or "").upper()
    folder_upper = (folder_path or "").upper().replace("\\", "/")
    filename_lower = filename.lower()

    scores: dict[str, float] = {}

    for doc_type, rules in DOC_TYPE_RULES.items():
        score = 0.0

        # Signal 1: Folder path (weight 0.5)
        for pattern in rules["folder_patterns"]:
            if re.search(pattern, folder_upper, re.IGNORECASE):
                score += 0.5
                break

        # Signal 2: Filename patterns (weight 0.4)
        for pattern in rules["filename_patterns"]:
            if re.search(pattern, filename_lower, re.IGNORECASE):
                score += 0.4
                break

        # Signal 3: Content keywords (weight 0.3, capped at 0.3)
        if text_upper:
            keyword_hits = sum(
                1 for kw in rules["content_keywords"]
                if re.search(kw, text_upper, re.IGNORECASE)
            )
            score += min(0.3, keyword_hits * 0.06)

        # Signal 4: Extension (weight 0.2)
        if ext in rules["extensions"]:
            score += 0.2

        # Signal 5: MIME type (weight 0.1)
        if mime_type in rules["mime_types"]:
            score += 0.1

        scores[doc_type] = score

    if not any(s > 0 for s in scores.values()):
        return "zeichnung", 0.0

    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]

    # Normalize to 0-1 range (max possible is ~1.5)
    normalized = min(1.0, best_score / 1.0)

    return best_type, normalized
