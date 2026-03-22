"""
BOM (Stückliste) comparator using pandas merge on part number.
Handles different column naming conventions via alias mapping.
"""
from app.comparators.base import BaseComparator, ComparisonOutput

# Maps canonical column names to possible aliases found in real-world BOMs
COLUMN_ALIASES: dict[str, list[str]] = {
    "part_number": ["sachnummer", "artikelnummer", "sap-nr", "part no", "part_no", "partnumber",
                    "artikel", "nr", "id", "item no", "item_no"],
    "quantity":    ["menge", "qty", "anzahl", "quantity", "count"],
    "description": ["bezeichnung", "description", "name", "benennung", "artikel-bezeichnung"],
    "unit":        ["einheit", "unit", "me"],
    "pos":         ["pos", "position", "lfd nr", "lfd.nr"],
}


def _normalize_columns(df) -> "pd.DataFrame":
    import pandas as pd
    col_map = {}
    for col in df.columns:
        col_lower = col.lower().strip()
        for canonical, aliases in COLUMN_ALIASES.items():
            if col_lower in aliases or col_lower == canonical:
                col_map[col] = canonical
                break
    return df.rename(columns=col_map)


def _reconstruct_df(extracted_data: dict) -> "pd.DataFrame":
    import pandas as pd
    sheets = extracted_data.get("sheets", {})
    if not sheets:
        return pd.DataFrame()
    # Take the first non-empty sheet
    for sheet_data in sheets.values():
        cols = sheet_data.get("columns", [])
        rows = sheet_data.get("rows", [])
        if cols and rows:
            df = pd.DataFrame(rows, columns=cols)
            return _normalize_columns(df)
    return pd.DataFrame()


class BomComparator(BaseComparator):
    def compare(self, version_a, version_b) -> ComparisonOutput:
        try:
            import pandas as pd

            df_a = _reconstruct_df(version_a.extracted_data or {})
            df_b = _reconstruct_df(version_b.extracted_data or {})

            if df_a.empty or df_b.empty:
                # Fall back to text diff if no structured data
                from app.comparators.text_comparator import TextComparator
                return TextComparator().compare(version_a, version_b)

            # Need a key column for merge
            key_col = "part_number" if "part_number" in df_a.columns else df_a.columns[0]

            merged = pd.merge(
                df_a, df_b,
                on=key_col,
                how="outer",
                suffixes=("_old", "_new"),
                indicator=True,
            )

            added_df   = merged[merged["_merge"] == "right_only"]
            removed_df = merged[merged["_merge"] == "left_only"]
            both_df    = merged[merged["_merge"] == "both"]

            # Detect changed rows (quantity or description differ)
            changed_mask = pd.Series([False] * len(both_df), index=both_df.index)
            for col in ["quantity", "description"]:
                old_col = f"{col}_old"
                new_col = f"{col}_new"
                if old_col in both_df.columns and new_col in both_df.columns:
                    changed_mask |= (both_df[old_col].fillna("") != both_df[new_col].fillna(""))

            changed_df   = both_df[changed_mask]
            unchanged_df = both_df[~changed_mask]

            total_a = len(df_a)
            total_b = len(df_b)
            changes_count = len(added_df) + len(removed_df) + len(changed_df)

            parts = []
            if len(added_df):
                parts.append(f"{len(added_df)} Teile neu")
            if len(removed_df):
                parts.append(f"{len(removed_df)} Teile entfernt")
            if len(changed_df):
                parts.append(f"{len(changed_df)} Teile geändert")
            summary = ", ".join(parts) if parts else "Keine Änderungen"

            similarity = 1.0 - (changes_count / max(total_a, total_b, 1))

            return ComparisonOutput(
                comparison_type="bom",
                summary=summary,
                changes_count=changes_count,
                diff_data={
                    "added":           added_df[[key_col]].to_dict("records"),
                    "removed":         removed_df[[key_col]].to_dict("records"),
                    "changed":         changed_df.fillna("").to_dict("records"),
                    "unchanged_count": len(unchanged_df),
                    "total_old":       total_a,
                    "total_new":       total_b,
                },
                similarity=max(0.0, similarity),
            )
        except Exception as e:
            return ComparisonOutput(
                comparison_type="bom",
                summary=f"Vergleich fehlgeschlagen: {e}",
                changes_count=0,
                diff_data={"error": str(e)},
            )
