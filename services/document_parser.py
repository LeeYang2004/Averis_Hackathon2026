import re

from pydantic import BaseModel

from services.field_normalizer import (
    normalize_whitespace_unicode,
    parse_container_count,
    parse_gross_weight_kg,
)


class ShipmentFields(BaseModel):
    shipper: str | None = None
    consignee: str | None = None
    notify_party: str | None = None
    port_of_loading: str | None = None
    port_of_discharge: str | None = None
    container_count: int | None = None
    gross_weight_kg: float | None = None


# A line is a candidate "Label: value" pair only if it doesn't start with
# whitespace -- address/continuation lines in these documents are always
# indented and semicolon-delimited (no colon), so they never match.
_LABEL_LINE_RE = re.compile(r"^(\S[^:]*):\s*(.*)$")


def _canonical_field_for_label(label: str) -> str | None:
    text = label.strip().upper()

    if "NOTIFY" in text:
        return "notify_party"
    if "TO THE ORDER OF" in text:
        return "consignee"
    if "CONSIGNEE" in text:
        return "consignee"
    if "SHIPPER" in text:
        return "shipper"
    if "PORT OF LOADING" in text or "LOAD PORT" in text or text == "POL":
        return "port_of_loading"
    if "PORT OF DISCHARGE" in text or "DISCHARGE PORT" in text or text == "POD":
        return "port_of_discharge"
    if "CONTAINER" in text:
        return "container_count"
    if "GROSS WEIGHT" in text or "GROSS WT" in text:
        return "gross_weight_kg"
    return None


class DocumentParser:
    def parse_text(self, text: str) -> ShipmentFields:
        raw_values: dict[str, str] = {}

        for line in text.splitlines():
            match = _LABEL_LINE_RE.match(line)
            if not match:
                continue

            label, value = match.groups()
            value = value.strip()
            if not value:
                continue

            field = _canonical_field_for_label(label)
            if field and field not in raw_values:
                raw_values[field] = value

        fields: dict[str, str | int | float | None] = {}
        for field in ("shipper", "consignee", "notify_party", "port_of_loading", "port_of_discharge"):
            if field in raw_values:
                fields[field] = normalize_whitespace_unicode(raw_values[field])

        if "container_count" in raw_values:
            fields["container_count"] = parse_container_count(raw_values["container_count"])
        if "gross_weight_kg" in raw_values:
            fields["gross_weight_kg"] = parse_gross_weight_kg(raw_values["gross_weight_kg"])

        return ShipmentFields(**fields)
