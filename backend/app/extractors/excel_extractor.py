from pathlib import Path
from app.extractors.base import BaseExtractor, ExtractionResult


class ExcelExtractor(BaseExtractor):
    SUPPORTED_MIME_TYPES = {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "text/csv",
    }

    def extract(self, file_path: Path) -> ExtractionResult:
        try:
            import pandas as pd

            if file_path.suffix.lower() == ".csv":
                df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
                sheets_data = {"Sheet1": self._df_to_dict(df)}
                text = df.to_string(index=False)
                row_count = len(df)
            else:
                xls = pd.read_excel(file_path, sheet_name=None, dtype=str, keep_default_na=False)
                sheets_data = {name: self._df_to_dict(df) for name, df in xls.items()}
                text = "\n\n".join(f"=== {name} ===\n{df.to_string(index=False)}" for name, df in xls.items())
                row_count = sum(len(df) for df in xls.values())

            return ExtractionResult(
                text=text,
                structured_data={"sheets": sheets_data},
                metadata={"row_count": row_count, "sheet_count": len(sheets_data)},
            )
        except Exception as e:
            return ExtractionResult(error=str(e))

    def _df_to_dict(self, df) -> dict:
        return {
            "columns": list(df.columns),
            "rows": df.values.tolist(),
        }
