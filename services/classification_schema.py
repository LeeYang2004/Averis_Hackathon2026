from dataclasses import asdict, dataclass


BL_COMPARISON = "BL_COMPARISON"
SI_REQUEST = "SI_REQUEST"
INVOICE_QUERY = "INVOICE_QUERY"
GENERAL = "GENERAL"
SPAM = "SPAM"

ALLOWED_CATEGORIES = (
    BL_COMPARISON,
    SI_REQUEST,
    INVOICE_QUERY,
    GENERAL,
    SPAM,
)


@dataclass(frozen=True)
class ClassificationResult:
    category: str
    confidence: float
    source: str
    reason: str | None = None

    def to_dict(self) -> dict[str, str | float | None]:
        return asdict(self)


def normalize_category(value: object) -> str | None:
    if not isinstance(value, str):
        return None

    normalized = value.strip().upper()
    return normalized if normalized in ALLOWED_CATEGORIES else None
