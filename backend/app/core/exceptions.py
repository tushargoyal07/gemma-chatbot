class LLMServiceError(Exception):
    """Raised when the LLM provider fails to generate a response."""

    def __init__(self, message: str, status_code: int = 503) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
