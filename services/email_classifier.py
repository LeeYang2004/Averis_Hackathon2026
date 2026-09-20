from services.classification_schema import (
    BL_COMPARISON,
    GENERAL,
    INVOICE_QUERY,
    SI_REQUEST,
    SPAM,
    ClassificationResult,
)
from services.llm_service import LLMService


class EmailClassifier:
    def __init__(
        self,
        llm_service: LLMService | None = None,
        prefer_llm: bool = True,
    ) -> None:
        self.llm_service = llm_service or LLMService()
        self.prefer_llm = prefer_llm

    def classify(
        self,
        subject: str,
        body: str,
        attachments: list[str] | None = None,
    ) -> ClassificationResult:
        rule_result = self.classify_with_rules(subject, body, attachments)

        if not self.prefer_llm or not self.llm_service.is_configured:
            return rule_result

        llm_result = self.llm_service.classify_email(subject, body, attachments or [])
        if llm_result is not None:
            return llm_result

        return ClassificationResult(
            category=rule_result.category,
            confidence=rule_result.confidence,
            source="rules_fallback",
            reason=rule_result.reason or "deepseek_unavailable",
        )

    def classify_with_rules(
        self,
        subject: str,
        body: str,
        attachments: list[str] | None = None,
    ) -> ClassificationResult:
        attachments = [str(attachment) for attachment in attachments or []]
        haystack = f"{subject}\n{body}".casefold()
        attachment_text = " ".join(attachments).casefold()

        has_si = (
            "shipping instruction" in haystack
            or "_si" in attachment_text
            or " si." in attachment_text
        )
        has_bl = (
            "bill of lading" in haystack
            or "draft bl" in haystack
            or "_bl" in attachment_text
            or " bl." in attachment_text
        )

        if "spam" in haystack or "lottery" in haystack:
            return ClassificationResult(SPAM, 0.93, "rules", "spam_keyword")
        if "invoice" in haystack or "payment" in haystack:
            return ClassificationResult(
                INVOICE_QUERY,
                0.90,
                "rules",
                "invoice_keyword",
            )
        if has_si and has_bl:
            return ClassificationResult(
                BL_COMPARISON,
                0.92,
                "rules",
                "si_and_bl_evidence",
            )
        if has_si:
            return ClassificationResult(SI_REQUEST, 0.85, "rules", "si_evidence")
        if has_bl:
            return ClassificationResult(
                BL_COMPARISON,
                0.78,
                "rules",
                "bl_evidence",
            )
        return ClassificationResult(GENERAL, 0.60, "rules", "no_specific_evidence")
