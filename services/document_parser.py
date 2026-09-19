from pydantic import BaseModel


class ShipmentFields(BaseModel):
    shipper: str | None = None
    consignee: str | None = None
    notify_party: str | None = None
    port_of_loading: str | None = None
    port_of_discharge: str | None = None
    container_count: int | None = None
    gross_weight_kg: float | None = None


class DocumentParser:
    def parse_text(self, text: str) -> ShipmentFields:
        # Phase 5 will replace this with extraction logic.
        _ = text
        return ShipmentFields()
