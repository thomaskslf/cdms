from app.comparators.base import BaseComparator, ComparisonOutput


class DxfComparator(BaseComparator):
    def compare(self, version_a, version_b) -> ComparisonOutput:
        data_a = version_a.extracted_data or {}
        data_b = version_b.extracted_data or {}

        # Compare entity counts
        counts_a = data_a.get("entity_counts", {})
        counts_b = data_b.get("entity_counts", {})
        all_entity_types = set(counts_a.keys()) | set(counts_b.keys())

        entity_changes = {}
        for etype in sorted(all_entity_types):
            c_a = counts_a.get(etype, 0)
            c_b = counts_b.get(etype, 0)
            if c_a != c_b:
                entity_changes[etype] = {"old": c_a, "new": c_b, "delta": c_b - c_a}

        # Compare header variables
        header_a = data_a.get("header", {})
        header_b = data_b.get("header", {})
        all_header_keys = set(header_a.keys()) | set(header_b.keys())
        header_changes = {}
        for key in sorted(all_header_keys):
            v_a = header_a.get(key, "—")
            v_b = header_b.get(key, "—")
            if v_a != v_b:
                header_changes[key] = {"old": v_a, "new": v_b}

        # Compare layers
        layers_a = set(data_a.get("layers", []))
        layers_b = set(data_b.get("layers", []))
        added_layers   = sorted(layers_b - layers_a)
        removed_layers = sorted(layers_a - layers_b)

        changes_count = len(entity_changes) + len(header_changes) + len(added_layers) + len(removed_layers)

        parts = []
        if entity_changes:
            parts.append(f"{len(entity_changes)} Entitätstypen verändert")
        if added_layers:
            parts.append(f"{len(added_layers)} Layer hinzugefügt")
        if removed_layers:
            parts.append(f"{len(removed_layers)} Layer entfernt")
        if header_changes:
            parts.append(f"{len(header_changes)} Header-Variablen geändert")
        summary = ", ".join(parts) if parts else "Keine Änderungen"

        # Rough similarity based on entity count changes
        total_entities_a = sum(counts_a.values()) or 1
        changed_entities = sum(abs(v["delta"]) for v in entity_changes.values())
        similarity = max(0.0, 1.0 - changed_entities / total_entities_a)

        return ComparisonOutput(
            comparison_type="dxf",
            summary=summary,
            changes_count=changes_count,
            diff_data={
                "entity_changes": entity_changes,
                "header_changes": header_changes,
                "added_layers": added_layers,
                "removed_layers": removed_layers,
            },
            similarity=similarity,
        )
