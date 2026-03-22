import difflib
from app.comparators.base import BaseComparator, ComparisonOutput


class TextComparator(BaseComparator):
    def compare(self, version_a, version_b) -> ComparisonOutput:
        text_a = (version_a.extracted_text or "").splitlines()
        text_b = (version_b.extracted_text or "").splitlines()

        matcher = difflib.SequenceMatcher(None, text_a, text_b, autojunk=False)
        opcodes = matcher.get_opcodes()
        similarity = matcher.ratio()

        hunks = []
        inserts = deletes = replaces = 0

        for tag, i1, i2, j1, j2 in opcodes:
            if tag == "equal":
                continue
            hunk = {
                "type": tag,
                "lines_a": text_a[i1:i2],
                "lines_b": text_b[j1:j2],
                "pos_a": [i1, i2],
                "pos_b": [j1, j2],
            }
            hunks.append(hunk)
            if tag == "insert":
                inserts += j2 - j1
            elif tag == "delete":
                deletes += i2 - i1
            elif tag == "replace":
                replaces += 1

        parts = []
        if inserts:
            parts.append(f"{inserts} Zeilen hinzugefügt")
        if deletes:
            parts.append(f"{deletes} Zeilen entfernt")
        if replaces:
            parts.append(f"{replaces} Abschnitte geändert")
        summary = ", ".join(parts) if parts else "Keine Änderungen"

        return ComparisonOutput(
            comparison_type="text",
            summary=summary,
            changes_count=len(hunks),
            diff_data={"hunks": hunks, "lines_a": len(text_a), "lines_b": len(text_b)},
            similarity=similarity,
        )
