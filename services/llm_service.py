from app.config import get_settings


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def is_configured(self) -> bool:
        return bool(self.settings.deepseek_api_key)

    def classify_email(self, subject: str, body: str) -> str | None:
        # Phase 4 will call DeepSeek when an API key is configured.
        _ = (subject, body)
        return None
