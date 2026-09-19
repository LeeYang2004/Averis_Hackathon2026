class EmailClassifier:
    def classify(
        self,
        subject: str,
        body: str,
        attachments: list[str] | None = None,
    ) -> str:
        attachments = attachments or []
        haystack = f"{subject}\n{body}".casefold()
        attachment_text = " ".join(attachments).casefold()

        if "spam" in haystack or "lottery" in haystack:
            return "SPAM"
        if "invoice" in haystack:
            return "INVOICE_QUERY"
        if "shipping instruction" in haystack or "_si" in attachment_text:
            if "_bl" in attachment_text or "bill of lading" in haystack:
                return "BL_COMPARISON"
            return "SI_REQUEST"
        if "bill of lading" in haystack or "_bl" in attachment_text:
            return "BL_COMPARISON"
        return "GENERAL"
