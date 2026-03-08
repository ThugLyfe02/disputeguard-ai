import requests
from typing import Optional

from .models import Transaction, FraudEvaluationResult
from .exceptions import APIConnectionError, APIResponseError


class FraudClient:
    """
    Official Python SDK client for the Fraud Intelligence Platform.
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 10
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self):

        headers = {
            "Content-Type": "application/json"
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    def _post(self, endpoint, payload):

        url = f"{self.base_url}{endpoint}"

        try:

            response = requests.post(
                url,
                json=payload,
                headers=self._headers(),
                timeout=self.timeout
            )

        except requests.RequestException as e:
            raise APIConnectionError(str(e))

        if response.status_code != 200:
            raise APIResponseError(
                f"API returned {response.status_code}: {response.text}"
            )

        return response.json()

    # -------------------------------------------------------
    # Core Fraud Evaluation
    # -------------------------------------------------------

    def evaluate_transaction(
        self,
        transaction: Transaction,
        device_hash: str
    ) -> FraudEvaluationResult:

        payload = {
            "transaction": {
                "id": transaction.id,
                "customer_id": transaction.customer_id,
                "amount": transaction.amount
            },
            "device_hash": device_hash
        }

        result = self._post(
            "/fraud/platform/evaluate",
            payload
        )

        return FraudEvaluationResult(**result)

    # -------------------------------------------------------
    # Threat Intelligence
    # -------------------------------------------------------

    def lookup_threat(self, indicator_type, indicator_value):

        url = f"{self.base_url}/fraud/threat/{indicator_type}/{indicator_value}"

        try:

            response = requests.get(
                url,
                headers=self._headers(),
                timeout=self.timeout
            )

        except requests.RequestException as e:
            raise APIConnectionError(str(e))

        if response.status_code != 200:
            raise APIResponseError(response.text)

        return response.json()

    # -------------------------------------------------------
    # Fraud Simulation
    # -------------------------------------------------------

    def simulate_attack(self, scenario):

        url = f"{self.base_url}/fraud/simulate/{scenario}"

        try:

            response = requests.post(
                url,
                headers=self._headers(),
                timeout=self.timeout
            )

        except requests.RequestException as e:
            raise APIConnectionError(str(e))

        if response.status_code != 200:
            raise APIResponseError(response.text)

        return response.json()
