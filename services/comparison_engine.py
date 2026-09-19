from typing import Any


COMPARISON_FIELDS = (
    "shipper",
    "consignee",
    "notify_party",
    "port_of_loading",
    "port_of_discharge",
    "container_count",
    "gross_weight_kg",
)


class ComparisonEngine:
    def compare(self, si_data: dict[str, Any], bl_data: dict[str, Any]) -> dict[str, Any]:
        mismatches = []
        missing = []

        for field in COMPARISON_FIELDS:
            si_value = si_data.get(field)
            bl_value = bl_data.get(field)

            if si_value in (None, "") or bl_value in (None, ""):
                missing.append(field)
            elif str(si_value).strip().casefold() != str(bl_value).strip().casefold():
                mismatches.append(field)

        if missing:
            status = "NEEDS_REVIEW"
        elif mismatches:
            status = "MISMATCH"
        else:
            status = "OK"

        return {
            "status": status,
            "has_defect": bool(mismatches),
            "defect_fields": mismatches,
            "review_reason": "missing_value" if missing else None,
            "missing_fields": missing,
        }
