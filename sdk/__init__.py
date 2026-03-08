"""
Fraud Intelligence SDK

Official Python SDK for interacting with the Fraud Intelligence Platform.

This package provides:

- FraudClient: main interface for interacting with the fraud platform
- Transaction: structured transaction object
- FraudEvaluationResult: structured response returned by the platform
"""

from .fraud_client import FraudClient
from .models import Transaction, FraudEvaluationResult
from .exceptions import (
    FraudPlatformError,
    APIConnectionError,
    APIResponseError,
)

__all__ = [
    "FraudClient",
    "Transaction",
    "FraudEvaluationResult",
    "FraudPlatformError",
    "APIConnectionError",
    "APIResponseError",
]

__version__ = "1.0.0"