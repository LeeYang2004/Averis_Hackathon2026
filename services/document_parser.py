from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path
from typing import Callable
from pydantic import BaseModel

from services.field_normalizer import (
    normalize_whitespace_unicode,
    parse_container_count,
    parse_gross_weight_kg,
)


# snake_case key -> human display key used in the expected output.
DISPLAY_FIELDS = (
    ("shipper", "Shipper"),
    ("consignee", "Consignee"),
    ("notify_party", "Notify Party"),
    ("port_of_loading", "Port of Loading"),
    ("port_of_discharge", "Port of Discharge"),
    ("container_count", "Container Count"),
    ("gross_weight_kg", "Gross Weight (kg)"),
)

SNAKE_FIELDS = tuple(snake for snake, _ in DISPLAY_FIELDS)

FIELD_PATTERNS = {
    "shipper": re.compile(
        r"^\s*SHIPPER(?:\s*/\s*EXPORTER)?\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "consignee": re.compile(
        r"^\s*CONSIGNEE(?:\s*\([^)\n]*\))?\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "notify_party": re.compile(
        r"^\s*(?:NOTIFY(?:\s+PARTY)?)\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "port_of_loading": re.compile(
        r"^\s*(?:PORT\s+OF\s+LOADING(?:\s*\(\s*POL\s*\))?|LOAD\s+PORT|POL)\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "port_of_discharge": re.compile(
        r"^\s*(?:PORT\s+OF\s+DISCHARGE|DISCHARGE\s+PORT|POD)\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "container_count": re.compile(
        r"^\s*(?:CONTAINER\s+COUNT|TOTAL\s+CONTAINERS?|NO\.?\s+OF\s+CONTAINERS?(?:\s+OR\s+PACKAGES)?)\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "gross_weight_kg": re.compile(
        r"^\s*GROSS\s+(?:WT|WEIGHT)(?:\s*\(\s*(?:KGS?|KG)\s*\))?\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
}

TEXT_EXTENSIONS = {"txt", "text"}
DOCX_EXTENSIONS = {"docx"}
PDF_EXTENSIONS = {"pdf"}
XLSX_EXTENSIONS = {"xlsx", "xls", "xlsm"}
IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp"}


# snake_case key -> human display key used in the expected output.
DISPLAY_FIELDS = (
    ("shipper", "Shipper"),
    ("consignee", "Consignee"),
    ("notify_party", "Notify Party"),
    ("port_of_loading", "Port of Loading"),
    ("port_of_discharge", "Port of Discharge"),
    ("container_count", "Container Count"),
    ("gross_weight_kg", "Gross Weight (kg)"),
)

SNAKE_FIELDS = tuple(snake for snake, _ in DISPLAY_FIELDS)

FIELD_PATTERNS = {
    "shipper": re.compile(
        r"^\s*SHIPPER(?:\s*/\s*EXPORTER)?\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "consignee": re.compile(
        r"^\s*CONSIGNEE(?:\s*\([^)\n]*\))?\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "notify_party": re.compile(
        r"^\s*(?:NOTIFY(?:\s+PARTY)?)\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "port_of_loading": re.compile(
        r"^\s*(?:PORT\s+OF\s+LOADING(?:\s*\(\s*POL\s*\))?|LOAD\s+PORT|POL)\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "port_of_discharge": re.compile(
        r"^\s*(?:PORT\s+OF\s+DISCHARGE|DISCHARGE\s+PORT|POD)\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "container_count": re.compile(
        r"^\s*(?:CONTAINER\s+COUNT|TOTAL\s+CONTAINERS?|NO\.?\s+OF\s+CONTAINERS?(?:\s+OR\s+PACKAGES)?)\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "gross_weight_kg": re.compile(
        r"^\s*GROSS\s+(?:WT|WEIGHT)(?:\s*\(\s*(?:KGS?|KG)\s*\))?\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
}

TEXT_EXTENSIONS = {"txt", "text"}
DOCX_EXTENSIONS = {"docx"}
PDF_EXTENSIONS = {"pdf"}
XLSX_EXTENSIONS = {"xlsx", "xls", "xlsm"}
IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp"}


class ShipmentFields(BaseModel):
    shipper: str | None = None
    consignee: str | None = None
    notify_party: str | None = None
    port_of_loading: str | None = None
    port_of_discharge: str | None = None
    container_count: str | None = None
    gross_weight_kg: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {snake: getattr(self, snake) for snake in SNAKE_FIELDS}

    def to_display_dict(self) -> dict[str, str | None]:
        return {
            display: getattr(self, snake) for snake, display in DISPLAY_FIELDS
        }

    def missing_fields(self) -> list[str]:
        return [snake for snake in SNAKE_FIELDS if not getattr(self, snake)]

    def is_complete(self) -> bool:
        return not self.missing_fields()


def snake_to_display(fields: dict) -> dict:
    """Convert a snake_case field dict into the expected display-key output."""
    return {display: fields.get(snake) for snake, display in DISPLAY_FIELDS}


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned or None

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
    """Detects document kind, extracts raw text, and parses shipment fields."""

    def __init__(
        self,
        reader: Callable[[str], bytes] | None = None,
        ocr_service: object | None = None,
    ) -> None:
        self._reader = reader
        self._ocr_service = ocr_service

    # -- document type detection ---------------------------------------
    def detect_kind(self, extension: str) -> str:
        ext = extension.lower().lstrip(".")
        if ext in TEXT_EXTENSIONS:
            return "txt"
        if ext in DOCX_EXTENSIONS:
            return "docx"
        if ext in PDF_EXTENSIONS:
            return "pdf"
        if ext in XLSX_EXTENSIONS:
            return "xlsx"
        if ext in IMAGE_EXTENSIONS:
            return "image"
        return "unknown"

    # -- raw text extraction -------------------------------------------
    def extract_text(
        self,
        path: str,
        bytes_data: bytes | None = None,
    ) -> tuple[str, str]:
        """Return (text, extraction_method) for the given attachment."""
        extension = Path(path).suffix
        kind = self.detect_kind(extension)

        if bytes_data is None and self._reader is not None:
            bytes_data = self._reader(path)
        if bytes_data is None:
            return "", "missing"

        if kind == "txt":
            return self._decode(bytes_data), "txt"
        if kind == "docx":
            text = self._extract_docx(bytes_data)
            return text, "docx"
        if kind == "pdf":
            text, method = self._extract_pdf(bytes_data)
            return text, method
        if kind == "xlsx":
            text = self._extract_xlsx(bytes_data)
            return text, "xlsx"
        if kind == "image":
            text = self._extract_image(bytes_data)
            return text, "ocr"
        return self._decode(bytes_data), "unknown"

      
    # -- field parsing --------------------------------------------------
    def parse_text(self, text: str) -> ShipmentFields:
        raw_values: dict[str, str] = {}
    
        if not text:
            return ShipmentFields()

        values: dict[str, str | None] = {}
        for snake, pattern in FIELD_PATTERNS.items():
            match = pattern.search(text)
            values[snake] = _clean(match.group(1)) if match else None

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

        fields: dict[str, str | None] = {}
        for field in ("shipper", "consignee", "notify_party", "port_of_loading", "port_of_discharge"):
            if field in raw_values:
                fields[field] = normalize_whitespace_unicode(raw_values[field])

        if "container_count" in raw_values:
            count = parse_container_count(raw_values["container_count"])
            fields["container_count"] = None if count is None else str(count)
        if "gross_weight_kg" in raw_values:
            weight = parse_gross_weight_kg(raw_values["gross_weight_kg"])
            fields["gross_weight_kg"] = None if weight is None else str(weight)

        return ShipmentFields(**fields)

      
    def merge_fields(
        self,
        base: ShipmentFields,
        extra: dict | None,
    ) -> ShipmentFields:
        """Fill missing base fields with values from an LLM-produced dict."""
        merged = base.to_dict()
        for snake in SNAKE_FIELDS:
            if merged.get(snake):
                continue
            if extra and extra.get(snake):
                merged[snake] = _clean(str(extra.get(snake)))
        return ShipmentFields(**merged)

    # -- helpers --------------------------------------------------------
    @staticmethod
    def _decode(data: bytes) -> str:
        for encoding in ("utf-8", "utf-16", "latin-1"):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="replace")

    @staticmethod
    def _extract_docx(data: bytes) -> str:
        """Extract text from a .docx using only the standard library."""
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                xml = archive.read("word/document.xml").decode(
                    "utf-8", errors="replace"
                )
        except (zipfile.BadZipFile, KeyError):
            return ""

        xml = re.sub(r"<w:p[ >]", "\n", xml)
        xml = re.sub(r"<w:tab[^>]*/>", "\t", xml)
        return re.sub(r"<[^>]+>", "", xml)

    @staticmethod
    def _extract_xlsx(data: bytes) -> str:
        """Best-effort spreadsheet text dump using the standard library."""
        try:
            archive = zipfile.ZipFile(io.BytesIO(data))
        except zipfile.BadZipFile:
            return ""

        shared: list[str] = []
        try:
            shared_xml = archive.read("xl/sharedStrings.xml").decode(
                "utf-8", errors="replace"
            )
            shared = re.findall(r"<t[^>]*>(.*?)</t>", shared_xml, re.DOTALL)
        except KeyError:
            pass

        parts: list[str] = []
        try:
            sheet_xml = archive.read("xl/worksheets/sheet1.xml").decode(
                "utf-8", errors="replace"
            )
            for cell in re.findall(r"<c[^>]*>(.*?)</c>", sheet_xml, re.DOTALL):
                inline = re.search(r"<v[^>]*>(.*?)</v>", cell, re.DOTALL)
                if inline is None:
                    continue
                raw = inline.group(1).strip()
                if cell.find('t="s"') != -1:
                    try:
                        raw = shared[int(raw)]
                    except (ValueError, IndexError):
                        pass
                parts.append(raw)
        except KeyError:
            pass

        return "\n".join(parts)

    def _extract_pdf(self, data: bytes) -> tuple[str, str]:
        # pdfplumber -> pypdf -> PyMuPDF, then OCR as a last resort.
        for extractor in ("pdfplumber", "pypdf", "fitz"):
            text = self._pdf_with_library(extractor, data)
            if text:
                return text, "pdf_text"

        ocr_text = self._extract_image(data)
        if ocr_text:
            return ocr_text, "pdf_ocr"
        return "", "pdf_text"

    @staticmethod
    def _pdf_with_library(library: str, data: bytes) -> str:
        try:
            if library == "pdfplumber":
                import pdfplumber

                with pdfplumber.open(io.BytesIO(data)) as pdf:
                    return "\n".join(
                        page.extract_text() or "" for page in pdf.pages
                    )
            if library == "pypdf":
                from pypdf import PdfReader

                reader = PdfReader(io.BytesIO(data))
                return "\n".join(
                    page.extract_text() or "" for page in reader.pages
                )
            if library == "fitz":
                import fitz

                with fitz.open(stream=data, filetype="pdf") as doc:
                    return "\n".join(page.get_text() for page in doc)
        except Exception:
            return ""
        return ""

    def _extract_image(self, data: bytes) -> str:
        if self._ocr_service is None:
            return ""
        return self._ocr_service.extract_text_from_bytes(data)
