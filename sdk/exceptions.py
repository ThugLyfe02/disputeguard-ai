class FraudPlatformError(Exception):
    """Base exception for the Fraud Intelligence SDK."""
    pass


class APIConnectionError(FraudPlatformError):
    """Raised when the SDK cannot connect to the fraud platform."""
    pass


class APIResponseError(FraudPlatformError):
    """Raised when the fraud platform returns an unexpected response."""
    pass
