from __future__ import annotations

import io


class OCRService:
    """OCR seam for scanned PDFs and images.

    Uses Pillow + pytesseract when available. Falls back to an empty string
    when the libraries or the Tesseract binary are not installed so the rest
    of the pipeline can degrade gracefully.
    """

    def extract_text(self, file_path: str) -> str:
        try:
            with open(file_path, "rb") as handle:
                return self.extract_text_from_bytes(handle.read())
        except OSError:
            return ""

    def extract_text_from_bytes(self, data: bytes) -> str:
        try:
            from PIL import Image
            import pytesseract
        except ImportError:
            return ""

        try:
            image = Image.open(io.BytesIO(data))
            # Light preprocessing: grayscale improves OCR accuracy.
            image = image.convert("L")
            return pytesseract.image_to_string(image)
        except Exception:
            return ""
