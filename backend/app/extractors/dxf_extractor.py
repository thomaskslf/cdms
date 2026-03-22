from pathlib import Path
from app.extractors.base import BaseExtractor, ExtractionResult


class DxfExtractor(BaseExtractor):
    SUPPORTED_MIME_TYPES = {"image/vnd.dxf", "application/acad"}

    def extract(self, file_path: Path) -> ExtractionResult:
        try:
            import ezdxf
            doc = ezdxf.readfile(str(file_path))
            msp = doc.modelspace()

            # Count entity types
            entity_counts: dict[str, int] = {}
            for entity in msp:
                etype = entity.dxftype()
                entity_counts[etype] = entity_counts.get(etype, 0) + 1

            # Extract header variables (safe subset)
            safe_header_keys = ["$ACADVER", "$INSUNITS", "$MEASUREMENT", "$DIMSCALE",
                                 "$LTSCALE", "$TEXTSIZE", "$LIMMIN", "$LIMMAX"]
            header_vars = {}
            for key in safe_header_keys:
                try:
                    val = doc.header.get(key)
                    if val is not None:
                        header_vars[key] = str(val)
                except Exception:
                    pass

            # Extract title block text (ATTRIB / TEXT entities in paper space)
            title_texts = []
            try:
                for layout in doc.layouts:
                    for entity in layout:
                        if entity.dxftype() in ("TEXT", "MTEXT"):
                            try:
                                title_texts.append(entity.dxf.text)
                            except Exception:
                                pass
                        elif entity.dxftype() == "ATTRIB":
                            try:
                                title_texts.append(f"{entity.dxf.tag}: {entity.dxf.text}")
                            except Exception:
                                pass
            except Exception:
                pass

            layer_names = [layer.dxf.name for layer in doc.layers]

            text = "\n".join(title_texts) if title_texts else ""

            return ExtractionResult(
                text=text,
                structured_data={
                    "entity_counts": entity_counts,
                    "header": header_vars,
                    "layers": layer_names,
                },
                metadata={"dxf_version": doc.dxfversion, "layer_count": len(layer_names)},
            )
        except Exception as e:
            return ExtractionResult(error=str(e))
