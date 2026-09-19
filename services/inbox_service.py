from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import Any

from app.config import get_settings


class InboxService:
    def __init__(self, source: str | None = None) -> None:
        self.source = source or get_settings().data_source
        self._inbox = self._load_inbox_class()(self.source)

    def list_emails(self) -> list[dict[str, Any]]:
        return self._inbox.emails()

    def get_email(self, email_id: str) -> dict[str, Any]:
        return self._inbox.get(email_id)

    def read_attachment_bytes(self, attachment_path: str) -> bytes:
        return self._inbox.read_bytes(attachment_path)

    def read_attachment_text(self, attachment_path: str) -> str:
        return self._inbox.read_text(attachment_path)

    def sample_submission(self) -> dict[str, Any]:
        return self._inbox.sample_submission()

    def attachment_size(self, attachment_path: str) -> int | None:
        if self.source.startswith(("http://", "https://")):
            return None

        full_path = Path(self.source) / attachment_path
        if not full_path.exists():
            return None
        return full_path.stat().st_size

    def _load_inbox_class(self):
        if self.source.startswith(("http://", "https://")):
            loader_path = Path(__file__).resolve().parents[2] / "loader.py"
        else:
            loader_path = Path(self.source) / "loader.py"

        module = self._load_module(loader_path)
        return module.Inbox

    @staticmethod
    def _load_module(loader_path: Path) -> ModuleType:
        if not loader_path.exists():
            raise FileNotFoundError(f"Cannot find input loader at {loader_path}")

        spec = spec_from_file_location("sdoc_loader", loader_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot import input loader from {loader_path}")

        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
