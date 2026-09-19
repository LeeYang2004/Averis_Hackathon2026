import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_ROOT = PROJECT_ROOT.parent


class Settings(BaseModel):
    app_name: str = "Shipping Document Verification AI"
    app_version: str = "0.1.0"
    database_url: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./averis.db")
    )
    deepseek_api_key: str | None = Field(
        default_factory=lambda: os.getenv("DEEPSEEK_API_KEY")
    )
    upload_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("UPLOAD_DIR", "uploads"))
    )
    data_source: str = Field(
        default_factory=lambda: os.getenv("DATA_SOURCE", str(BUNDLE_ROOT))
    )

    class Config:
        arbitrary_types_allowed = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
